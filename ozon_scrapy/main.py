import asyncio
import json
from concurrent.futures import ProcessPoolExecutor

import aio_pika
import aio_pika.abc
from aio_pika import Message, connect_robust
from aio_pika.robust_connection import AbstractRobustConnection
from config import config
from pipelines import OzonScrapyPipeline
from scrapy import signals
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.signalmanager import dispatcher
from spiders import OzonCrawlSpider, OzonItemSpider
from twisted.internet import reactor


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

    async def listen(self, event_loop):
        """
        MessageBody
        {
            "job_id": UUID,
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
            queue_out = await channel.declare_queue("save-parse", durable=True)

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        result = message.body.decode()
                        parse_param = json.loads(result)
                        with ProcessPoolExecutor(max_workers=1) as executor:
                            urls = await event_loop.run_in_executor(
                                executor,
                                Consumer.execute_links,
                                parse_param["start_url"],
                            )
                            print(urls, type(urls), "243324324432324432")
                        with ProcessPoolExecutor(max_workers=1) as executor:
                            items = await event_loop.run_in_executor(
                                executor,
                                Consumer.execute_items,
                                urls[0]["urls"],
                            )
                        print(parse_param)
                        items = {parse_param["job_id"]: items}
                        message = json.dumps(items).encode("utf-8")
                        await channel.default_exchange.publish(
                            aio_pika.Message(
                                message,
                                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                            ),
                            routing_key="save-parse",
                        )

    async def write_data_to_queue(self, items: list[dict]):
        channel: aio_pika.abc.AbstractChannel = await self.connect.channel()
        message = json.dumps(items).encode("utf-8")
        async with self.connect:
            await channel.default_exchange.publish(
                Message(body=message),
                routing_key="save_items",
            )

    @staticmethod
    def execute_links(start_url, product_type=None):
        process = CrawlerProcess()
        pipeline = OzonScrapyPipeline()

        def urls_scraped(item, response, spider):
            pipeline.urls.append(item)

        dispatcher.connect(urls_scraped, signal=signals.item_scraped)

        process.crawl(OzonCrawlSpider, start_urls=[start_url])
        process.start()

        return pipeline.urls

    @staticmethod
    def execute_items(urls: list[str]):
        process = CrawlerProcess()
        pipeline = OzonScrapyPipeline()

        def items_scraped(item, response, spider):
            pipeline.results.append(item)

        dispatcher.connect(items_scraped, signal=signals.item_scraped)

        process.crawl(OzonItemSpider, start_urls=urls)
        process.start()

        return pipeline.results


async def main():
    event_loop = asyncio.get_event_loop()
    async with Consumer(
        user=config.rabbit_mq.user,
        host=config.rabbit_mq.host,
        port=config.rabbit_mq.port,
        password=config.rabbit_mq.password,
    ) as consumer:
        await consumer.listen(event_loop)


if __name__ == "__main__":
    asyncio.run(main())
