# python 3
import scrapy
from urllib.parse import urljoin


class PycoderSpider(scrapy.Spider):
    name = "pycoder"
    start_urls = [
        'http://pycoder.ru',
    ]

    def parse(self, response):
        for post_link in response.xpath(
                '//div[@class="post mb-2"]/h2/a/@href').extract():
            url = urljoin(response.url, post_link)
            print(url)