# python 3
import scrapy
from urllib.parse import urljoin


class LinkVacuumSpider(scrapy.Spider):
    name = "linkVacuum"
    start_urls = [
        'http://pycoder.ru/?page=1',
    ]
    visited_urls = []

    def parse(self, response):
        if response.url not in self.visited_urls:
            self.visited_urls.append(response.url)
            for post_link in response.xpath('//a/@href').extract():
                url = urljoin(response.url, post_link)
                print(url)


            next_pages = response.xpath(
                    '//li[contains(@class, "page-item") and'
                    ' not(contains(@class, "active"))]/a/@href').extract()
            next_page = next_pages[-1]

            next_page_url = urljoin(response.url+'/', next_page)
            yield response.follow(next_page_url, callback=self.parse)