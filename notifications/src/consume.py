import asyncio
import logging

from core.config import amqp_settings, db_settings
from db.rabbit import Rabbit
from db import postgres as db


async def startup_db():
    logging.info("Connecting to database...")
    # Connecting to DB
    db.postgres = db.Postgres(
        f'postgresql+asyncpg://'
        f'{db_settings.user}:{db_settings.password}@'
        f'{db_settings.host}:{db_settings.port}/'
        f'{db_settings.dbname}')


async def startup_consumer():
    logging.info("Starting consumer...")
    rabbit = Rabbit()
    await rabbit.connect(amqp_settings.get_amqp_uri(),
                         queue_name='email_worker')
    await rabbit.consume(routing_key="user-reporting.v1.registered")
    await rabbit.consume(routing_key="user-reporting.v1.likes-for-reviews")
    try:
        await rabbit.iterate()
    except Exception:
        await rabbit.close()


async def main():
    await asyncio.gather(startup_consumer(), startup_db())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Consumer has been closed.')
