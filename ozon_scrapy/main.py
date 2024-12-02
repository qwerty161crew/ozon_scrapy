import asyncio
import json

import aio_pika
import aio_pika.abc
from aio_pika import Message, connect_robust
from aio_pika.robust_connection import AbstractRobustConnection
from config import config
from pipelines import OzonScrapyPipeline
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher
from spiders import CrawlSpider, OzonCrawlSpider


class Consumer:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.connect: AbstractRobustConnection | None = None

    async def create_connection(self):
        if self.connect is None:
            self.connect = await connect_robust(
                f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/",
            )

    async def close_connection(self):

        if self.connect is not None:
            await self.connect.close()

    async def __aenter__(self):
        await self.create_connection()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_connection()

    async def listen(self):
        """
        MessageBody
        {
            "task_id": UUID,
            "start_url": "https://www.ozon.ru/",
            "product_type": ""
        }
        """
        async with self.connect:
            queue_name = "ozon_api"
            channel: aio_pika.abc.AbstractChannel = await self.connect.channel()
            queue: aio_pika.abc.AbstractQueue = await channel.declare_queue(
                queue_name, auto_delete=False
            )

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        result = message.body.decode()
                        print(result, type(result))
                        parse_param = json.loads(result)
                        await self.execute(start_url=[parse_param["start_url"]])

    async def execute(self, start_url, product_type=None):
        process = CrawlerProcess()
        pipeline = OzonScrapyPipeline()

        def item_scraped(item, response, spider):
            pipeline.results.append(item)

        dispatcher.connect(item_scraped, signal=signals.item_scraped)

        process.crawl(OzonCrawlSpider, start_urls=start_url)
        process.start()


async def main():
    async with Consumer(
        user=config.rabbit_mq.user,
        host=config.rabbit_mq.host,
        port=config.rabbit_mq.port,
        password=config.rabbit_mq.password,
    ) as consumer:
        await consumer.listen()


if __name__ == "__main__":
    asyncio.run(main())
