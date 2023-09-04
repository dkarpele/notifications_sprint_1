import asyncio
import logging
from datetime import datetime
from functools import lru_cache
from typing import Annotated

import orjson

from aio_pika import DeliveryMode, Exchange, ExchangeType, connect_robust
from aio_pika.abc import AbstractQueue
from aio_pika.channel import Channel
from aio_pika.connection import Connection
from aio_pika.message import Message
from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError

from db import AbstractQueueInternal
from models.schemas import Notification
from services.connections import get_db, DbHelpers
from services.exceptions import db_bad_request

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
        db = await get_db()
        conn = DbHelpers(db)
        async with self.connection:
            async with self.queue.iterator() as queue_iter:
                logging.info(f'Listening queue {self.queue_name} ...')
                async for message in queue_iter:
                    async with message.process():
                        body = orjson.loads(message.body)
                        correlation_id = str(message.correlation_id)
                        # Update notification status in DB after consuming
                        # message
                        try:
                            await conn.update(
                                model=Notification,
                                model_column=Notification.content_id,
                                column_value=correlation_id,
                                update_values={
                                    'status': 'Consumed',
                                    'failures': 0,
                                    'modified': datetime.utcnow()})
                        except SQLAlchemyError as err:
                            raise db_bad_request(err)

                        logging.info(f'Message arrived to queue:\n{body}\n'
                                     f'Trying to send an email.')
                        if message.routing_key == \
                                'user-reporting.v1.registered':
                            await send_email_registered(body,
                                                        correlation_id)
                        elif message.routing_key == \
                                'user-reporting.v1.likes-for-reviews':
                            await send_email_likes(body,
                                                   correlation_id)
                        logging.info(f'Message with routing-key '
                                     f'{message.routing_key} has been '
                                     f'processed.')

    async def close(self):
        logging.info('Closing all connections to rabbit...')
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()


rabbit: Rabbit | None = None


async def get_rabbit() -> AbstractQueueInternal | None:
    return rabbit


async def get_broker() -> AbstractQueueInternal:
    res = await get_rabbit()
    return res


@lru_cache()
def get_rabbit_service(
        rabbit_: Rabbit = Depends(get_rabbit)) -> Rabbit:
    return rabbit_


BrokerDep = Annotated[AbstractQueueInternal, Depends(get_rabbit_service)]
