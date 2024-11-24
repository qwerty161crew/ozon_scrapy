import scrapy
from scrapy.http import Response
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_splash import SplashRequest


class OzonCrawlSpider(scrapy.Spider):
    name = "extract_links"
    start_urls = ["https://www.ozon.ru/"]

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args={"wait": 2})

    def parse(self, response: Response):
        all_links = response.css("a::attr(href)").getall()
        filtered_links = [
            response.urljoin(link) for link in all_links if link.startswith("/product/")
        ]
        print(filtered_links)
