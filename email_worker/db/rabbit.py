import asyncio
import logging

import orjson
from aio_pika import Exchange, ExchangeType, connect_robust
from aio_pika.abc import AbstractQueue, AbstractChannel
from aio_pika.channel import Channel
from aio_pika.connection import Connection


class Rabbit:
    def __init__(self) -> None:
        self.connection: Connection | None = None
        self.channel: Channel | None = None
        self.exchange: Exchange | None = None
        self.topic_name: str | None = None
        self.queue_name: str | None = None
        self.queue: AbstractQueue | None = None

    async def connect(self,
                      url: str,
                      topic_name: str = 'topic_v1',
                      queue_name: str = 'queue_v1'):
        self.topic_name = topic_name
        self.queue_name = queue_name
        self.connection = await connect_robust(
            url=url,
            loop=asyncio.get_running_loop()
        )

    async def consume(
        self,
        routing_key: str,
    ):
        """
        Send data to queue according to routing key
        :param routing_key:
        :return:
        """

        # Creating channel
        self.channel: AbstractChannel = await self.connection.channel()

        self.exchange = await self.channel.declare_exchange(
            self.topic_name,
            ExchangeType.TOPIC
        )

        # Declaring queue
        self.queue: AbstractQueue = await self.channel.declare_queue(
            self.queue_name,
            durable=True)
        await self.queue.bind(self.exchange, routing_key=routing_key)

    async def iterate(self):
        async with self.connection:
            async with self.queue.iterator() as queue_iter:
                # Cancel consuming after __aexit__
                async for message in queue_iter:
                    async with message.process():
                        logging.info('Message arrived.')
                        logging.info(message)
                        logging.info(orjson.loads(message.body))

                        if self.queue.name in message.body.decode():
                            break

    async def close(self):
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()


rabbit: Rabbit | None = None


async def get_rabbit() -> Rabbit | None:
    return rabbit
