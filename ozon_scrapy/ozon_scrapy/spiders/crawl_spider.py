import scrapy
from scrapy.http import Response
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ozon_scrapy.items import OzonScrapyItem


class OzonCrawlSpider(scrapy.Spider):
    name = "extract_links"
    start_urls = ["https://www.ozon.ru/"]

    def parse(self, response: Response):
        all_links = response.css("a::attr(href)").getall()
        filtered_links = [
            response.urljoin(link) for link in all_links if link.startswith("/product/")
        ]
        print(filtered_links)


class OzonItemSpider(scrapy.Spider):
    name = "extract_items"
    start_urls = [
        "https://www.ozon.ru/product/marshrutizator-mikrotik-l009uigs-2haxd-in-1557234143/"
    ]

    def parse(self, response: Response):
        item = OzonScrapyItem()
        item["product_name"] = response.css("h1.t5m_27::text").get()
        item["price"] = response.css("span.m8q_27 span::text").get()
        item["rating"] = response.css("div.u3y_30 span::text").get()
        item["product_type"] = response.css("span.a6.je7_10 span::text").extract()
        item["ozon_id"] = response.css("span.yk6_27::text").get()
        item["description"] = response.css("div.RA-a1::text").get()
        item["full_price"] = response.css("span.mq9_27::text").get()
        yield item


# section-characteristics > div:nth-child(2) > div:nth-child(7) > div:nth-child(2) > dl:nth-child(2) > dd

# //*[@id="layoutPage"]/div[1]/div[4]/div[3]/div[2]/div/div/div[1]/div[3]/div/div[1]/div/div/div[1]/div[2]/div/div[1]/span[2]/text()

# layoutPage > div.b6 > div.container.c > div.ul0_27.lu4_27.lu6_27 > div.nn2_27 > div > div > div.ul0_27.lu7_27.lu4_27.ul4_27 > div.mv8_27.wm_27 > div > div.m8v_27 > div > div > div.s6m_27 > div.s9m_27.m4t_27 > div > div.tm2_27 > span.mt0_27.mt1_27.sm9_27.m0t_27
#  response.xpath('//*[@id="layoutPage"]').extract()
# layoutPage > div.b6<span class="mt0_27 mt1_27 sm9_27 m0t_27">9 590 ₽</span>
# layoutPage > div.b6 > div.container.c > div.ul0_27.lu4_27.lu6_27 > div.nn2_27 > div > div > div.ul0_27.lu7_27.lu4_27.ul4_27 > div.mv8_27.wm_27 > div > div.m8v_27 > div > div > div.s6m_27 > div.s9m_27.m4t_27 > div > div.tm2_27 > span.mt0_27.mt1_27.sm9_27.m0t_27
