import asyncio
from pickle import FRAME

import aio_pika
import aio_pika.abc
from aio_pika import Message, connect_robust
from aio_pika.robust_connection import AbstractRobustConnection
from scrapy.crawler import CrawlerProcess

from ozon_scrapy.config import config
from ozon_scrapy.spiders import CrawlSpider, OzonCrawlSpider


class Consumer:
    def __init__(self, host, port, user, password, repository):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.connect: AbstractRobustConnection | None = None
        self.repository = repository

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
            "state": "Complete",
            "Message": "Complete"
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

    async def execute(self, start_url, product_type=None):
        process = CrawlerProcess(
            {"USER_AGENT": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)"}
        )
        urls = process.crawl(OzonCrawlSpider(start_urls=[start_url]))
        print(urls)


async def main(loop):
    async with Consumer(
        user=config.rabbit_mq.user,
        host=config.rabbit_mq.host,
        port=config.rabbit_mq.port,
        password=config.rabbit_mq.password,
    ) as consumer:
        await consumer.listen(loop)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
