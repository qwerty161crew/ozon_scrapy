# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class OzonScrapyItem(scrapy.Item):
    # define the fields for your item here like:
    product_name = scrapy.Field()
    ozon_id = scrapy.Field()
    product_type = scrapy.Field()
    description = scrapy.Field()
    price = scrapy.Field()
    full_price = scrapy.Field()
    rating = scrapy.Field()


class OzonUrlsItems(scrapy.Item):
    urls = scrapy.Field()
