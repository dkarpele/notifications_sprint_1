import asyncio
import logging
import orjson

from aio_pika import DeliveryMode, Exchange, ExchangeType, connect_robust
from aio_pika.abc import AbstractQueue
from aio_pika.channel import Channel
from aio_pika.connection import Connection
from aio_pika.message import Message

from db import AbstractQueueInternal

from smtp.send_emails import send_email_registered, send_email_likes


class Rabbit(AbstractQueueInternal):
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

        self.channel = await self.connection.channel()

        self.exchange = \
            await self.channel.declare_exchange(  # type: ignore[union-attr]
                self.topic_name,
                ExchangeType.TOPIC
            )

    async def produce(
            self,
            routing_key: str,
            data: dict,
            correlation_id,
    ) -> None:
        """
        Send data to queue according to routing key
        :param routing_key:
        :param data:
        :param correlation_id:
        :return:
        """
        queue = await self.channel.declare_queue(  # type: ignore[union-attr]
            self.queue_name,
            durable=True)
        await queue.bind(self.exchange, routing_key=routing_key)

        message = Message(
            body=orjson.dumps(data),
            content_type="application/json",
            correlation_id=correlation_id,
            delivery_mode=DeliveryMode.PERSISTENT
        )
        await self.exchange.publish(message,  # type: ignore[union-attr]
                                    routing_key,
                                    timeout=10)
        logging.info(f'Published to queue {self.queue_name}. with routing_key'
                     f' {routing_key}.')

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
        self.channel = \
            await self.connection.channel()  # type: ignore[union-attr]

        self.exchange = await self.channel.declare_exchange(
            self.topic_name,
            ExchangeType.TOPIC
        )

        # Declaring queue
        self.queue = await self.channel.declare_queue(
            self.queue_name,
            durable=True)
        await self.queue.bind(self.exchange, routing_key=routing_key)

    async def iterate(self):
        async with self.connection:
            async with self.queue.iterator() as queue_iter:
                # Cancel consuming after __aexit__
                logging.info(f'Listening queue {self.queue_name} ...')
                async for message in queue_iter:
                    async with message.process():
                        body = orjson.loads(message.body)
                        logging.info('Message arrived.')
                        if message.routing_key == \
                                'user-reporting.v1.registered':
                            send_email_registered(body)
                        elif message.routing_key == \
                                'user-reporting.v1.likes-for-reviews':
                            send_email_likes(body)
                        logging.info(f'Message with routing-key '
                                     f'{message.routing_key} has been sent.')

    async def close(self):
        logging.info('Closing all connections to rabbit...')
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()


rabbit: Rabbit | None = None


async def get_rabbit() -> AbstractQueueInternal | None:
    return rabbit
