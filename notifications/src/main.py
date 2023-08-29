import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import notify_email
from core.config import settings, rabbit_settings, cron_settings
from core.logger import LOGGING
from db import rabbit, scheduler
from schedule.notifications import likes_for_reviews


async def startup():
    rabbit.rabbit = rabbit.Rabbit()
    await rabbit.rabbit.connect(rabbit_settings.get_amqp_uri(),
                                queue_name='email_worker')
    job = await scheduler.get_scheduler()

    job.add_job(likes_for_reviews,
                trigger='cron',
                hour=cron_settings.likes_for_reviews['hour'],
                minute=cron_settings.likes_for_reviews['minute'],
                timezone=cron_settings.likes_for_reviews['timezone'])

    job.start()


async def shutdown():
    if rabbit.rabbit:
        await rabbit.rabbit.close()


@asynccontextmanager  # type: ignore[arg-type]
async def lifespan(app: FastAPI):
    await startup()
    yield
    await shutdown()


app = FastAPI(
    title="Api for notifications sending",
    description="Api for notifications sending",
    version="1.0.0",
    docs_url='/api/openapi-notify',
    openapi_url='/api/openapi-notify.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan, )

app.include_router(notify_email.router,
                   prefix='/api/v1/notify-email',
                   tags=['notify-email'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=f'{settings.host}',
        port=settings.port,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
