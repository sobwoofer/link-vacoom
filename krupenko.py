import argparse
import requests
from bs4 import BeautifulSoup
import re
import csv
from queue import Queue
from threading import Thread
import progressbar
from urllib.parse import urlparse

default_max_count_links = 50000
default_count_threads = 4


def run():
    while True:
        if links_queue.empty() or len(results) >= max_count_links:
            return True

        links = get_links_from_page(links_queue.get())

        process_links(links)


def is_unsuitable_link(link):
    unsuitable_path_ends = ['.json', '.xml', '.png', '.jpg', '.css']
    main_link_args = urlparse(url)

    for unsuitable_path_end in unsuitable_path_ends:
        if link.endswith(unsuitable_path_end):
            return True

    if main_link_args.netloc.replace('www.', '') in link:
        return False

    return True


def get_links_from_page(url):
    content = requests.get(url).text
    soup = BeautifulSoup(content, 'html.parser')

    links = []

    for link in soup.find_all(attrs={'href': re.compile("^http")}):
        links.append(link.get('href'))

    return links


def process_links(links):
    for link in links:
        content = requests.get(link)

        if content.status_code != 200:
            continue

        if 'Content-Type' in content.headers and 'text/html' not in content.headers['Content-Type']:
            continue

        if link in results or is_unsuitable_link(link):
            continue

        links_queue.put(link)
        results.append(link)


def write_data_to_csv(file_name):
    with open(file_name, 'w') as file:
        fieldnames = ['link']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        for res in results:
            writer.writerow({'link': res})


def run_threads():
    threads = []

    for i in range(count_threads):
        t = Thread(target=run)
        t.start()
        threads.append(t)

    progress = progressbar.ProgressBar()

    while max_count_links > len(results) and not links_queue.empty():
        progress.update(len(results))

    progress.finish()

    for t in threads:
        t.join()


if __name__ == "__main__":
    arguments = argparse.ArgumentParser()
    arguments.add_argument('--urls', '-u', help='Input site url', required=True, type=str, action='append')
    arguments.add_argument('--max_count_links', '-c', help='Max count links, default:' + str(default_max_count_links),
                           default=default_max_count_links, type=int)
    arguments.add_argument('--count_threads', '-ct', help='Count threads, default:' + str(default_count_threads),
                           default=default_count_threads, type=int)
    args = arguments.parse_args()

    urls = args.urls
    max_count_links = args.max_count_links
    count_threads = args.count_threads

    for url in urls:
        results = []
        print('parse:' + url)
        links_queue = Queue()

        process_links(get_links_from_page(url))

        try:
            run_threads()
        except KeyboardInterrupt:
            print('catch KeyboardInterrupt, break and save data to file')

        main_link_args = urlparse(url)
        write_data_to_csv(main_link_args.netloc + '.csv')

