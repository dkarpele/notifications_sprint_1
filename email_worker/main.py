import asyncio
import logging

from db.rabbit import Rabbit
from core.config import rabbit_settings

logging.basicConfig(level=logging.DEBUG)


async def main():
    rabbit = Rabbit()

    await rabbit.connect(rabbit_settings.get_amqp_uri(),
                         queue_name="email_worker")

    await rabbit.consume(routing_key="user-reporting.v1.registered")
    await rabbit.consume(routing_key="one-more-routing-key")

    await rabbit.iterate()

if __name__ == "__main__":
    logging.info('Starting consumer...')
    asyncio.run(main())
