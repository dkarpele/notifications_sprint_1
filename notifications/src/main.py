import logging
import uuid
from contextlib import asynccontextmanager

import uvicorn
from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.middleware import is_valid_uuid4
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse

from api.v1 import notify_email
from core.config import settings, amqp_settings, db_settings
from core.logger import LOGGING
from db import rabbit as amqp, scheduler, postgres as db
from tasks import jobs


async def startup():
    # Connecting to DB
    db.postgres = db.Postgres(
        f'postgresql+asyncpg://'
        f'{db_settings.user}:{db_settings.password}@'
        f'{db_settings.host}:{db_settings.port}/'
        f'{db_settings.dbname}')

    # Connecting to AMQP
    amqp.rabbit = amqp.Rabbit()
    await amqp.rabbit.connect(amqp_settings.get_amqp_uri(),
                              queue_name='email_worker')

    # Connecting to scheduler
    job = await scheduler.get_scheduler()
    await jobs(job)
    job.start()
    logging.info(f'List of scheduled jobs: {job.get_jobs()}')


async def shutdown():
    if amqp.rabbit:
        await amqp.rabbit.close()
    if db.postgres:
        await db.postgres.close()


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

app.add_middleware(
    CorrelationIdMiddleware,
    header_name='X-Request-ID',
    update_request_header=True,
    generator=lambda: uuid.uuid4().hex,
    validator=is_valid_uuid4,
    transformer=lambda a: a,
)


@app.middleware('http')
async def before_request(request: Request, call_next):
    response = await call_next(request)
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                              content={'detail': 'X-Request-Id is required'})
    return response

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
