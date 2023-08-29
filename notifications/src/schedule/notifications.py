import time
from datetime import datetime

import aiohttp
from aiohttp.web_exceptions import HTTPException
from fastapi import status as st
from sqlalchemy.exc import SQLAlchemyError

import core.config as conf
from models.schemas import Notification, NotificationContent
from services.connections import get_broker, get_db, DbHelpers
from services.exceptions import db_bad_request

routing_key = 'user-reporting.v1.likes-for-reviews'


async def likes_for_reviews():
    db = await get_db()
    conn = DbHelpers(db)
    data: dict = await users_daily_likes()
    correlation_id = round(time.time())

    # if not data:
    #     logging.info('If 0 users received 0 likes - don\'t need to send any'
    #                  ' notifications. Exiting')
    #     return

    # Add initial notification to db
    try:
        await conn.insert(Notification(str(correlation_id),
                                       'Initiated'))
        await conn.insert(NotificationContent(str(correlation_id),
                                              str(data)))
    except SQLAlchemyError as err:
        raise db_bad_request(err)

    # Produce message to the queue
    broker = await get_broker()
    await broker.produce(routing_key=routing_key,
                         data=data,
                         correlation_id=correlation_id)

    # Update notification status in DB after producing message
    try:
        await conn.update(model=Notification,
                          model_column=Notification.content_id,
                          column_value=str(correlation_id),
                          update_values={'status': 'Produced',
                                         'modified': datetime.utcnow()})
    except SQLAlchemyError as err:
        raise db_bad_request(err)


async def users_daily_likes() -> dict:
    url = f'http://{conf.settings.host_ugc}:'\
          f'{conf.settings.port_ugc}'\
          f'/api/v1/reviews/users-daily-likes'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as response:
                body = await response.json()
                status_code = response.status
                if status_code != st.HTTP_200_OK:
                    raise HTTPException(
                        reason=body['detail'],
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                return body
    except ConnectionRefusedError as err:
        raise HTTPException(reason=err.strerror)
    except aiohttp.ServerTimeoutError as err:
        raise HTTPException(reason=err.strerror)
    except aiohttp.TooManyRedirects as err:
        raise HTTPException(reason=err.strerror)
    except aiohttp.ClientError as err:
        raise HTTPException(reason=err.strerror)
