import scrapy
from items import OzonScrapyItem, OzonUrlsItems
from scrapy.http import Response
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class OzonCrawlSpider(scrapy.Spider):
    name = "extract_links"
    # start_urls = ["https://www.ozon.ru/"]
    # def __init__(self, start_urls: list = "https://www.ozon.ru/", *args, **kwargs):
    #     self.start_urls = start_urls
    #     super(OzonCrawlSpider, self).__init__(*args, **kwargs)

    def parse(self, response: Response):
        item = OzonUrlsItems()
        all_links = response.css("a::attr(href)").getall()
        filtered_links = [
            response.urljoin(link) for link in all_links if link.startswith("/product/")
        ]
        item["urls"] = filtered_links
        yield item


class OzonItemSpider(scrapy.Spider):
    name = "extract_items"

    def __init__(self, start_urls: list, *args, **kwargs):
        self.start_urls = start_urls
        super(OzonItemSpider, self).__init__(*args, **kwargs)

    def parse(self, response: Response):
        item = {}
        item["product_name"] = response.css("h1.t5m_27::text").get()
        item["price"] = response.css("span.m8q_27 span::text").get()
        item["rating"] = response.css("div.u3y_30 span::text").get()
        item["product_type"] = response.css("span.a6.je7_10 span::text").extract()
        item["ozon_id"] = response.css("span.yk6_27::text").get()
        item["description"] = response.css("div.RA-a1::text").get()
        item["full_price"] = response.css("span.mq9_27::text").get()
        yield item
