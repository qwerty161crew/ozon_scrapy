# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class OzonScrapyPipeline:
    def __init__(self):
        self.results = []
        self.urls = []

    def process_item(self, item, spider):
        self.results.append(item)
        return item
