import asyncio
import logging

from core.config import rabbit_settings
from db.rabbit import Rabbit


async def startup_consumer():
    logging.info("Starting consumer...")
    rabbit = Rabbit()
    await rabbit.connect(rabbit_settings.get_amqp_uri(),
                         queue_name='email_worker')
    await rabbit.consume(routing_key="user-reporting.v1.registered")
    await rabbit.consume(routing_key="user-reporting.v1.likes-for-reviews")
    try:
        await rabbit.iterate()
    except Exception:
        await rabbit.close()


if __name__ == "__main__":
    try:
        asyncio.run(startup_consumer())
    except KeyboardInterrupt:
        logging.info('Consumer has been closed.')
