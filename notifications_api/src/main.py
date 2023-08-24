import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import notify_email
from core.config import settings, rabbit_settings
from core.logger import LOGGING
from db import rabbit


# sentry_sdk.init(integrations=[FastApiIntegration()])


async def startup():
    rabbit.rabbit = rabbit.Rabbit()
    await rabbit.rabbit.connect(rabbit_settings.get_amqp_uri(),
                                queue_name='email_worker')


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
    lifespan=lifespan,)


app.include_router(notify_email.router,
                   prefix='/api/v1/notify_email',
                   tags=['notify_email'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=f'{settings.host}',
        port=settings.port,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
