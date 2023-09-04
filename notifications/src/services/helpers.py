from datetime import datetime, timedelta
from typing import Any

import aiohttp
from aiohttp.web_exceptions import HTTPException

from sqlalchemy import Result, and_
from sqlalchemy.exc import SQLAlchemyError
from starlette import status as st

from db import AbstractQueueInternal
from models.schemas import Notification, NotificationContent
from services.connections import get_db, DbHelpers
from services.exceptions import db_bad_request


async def process_notifications_helper(status: str,
                                       wait_minutes: int,
                                       ) -> Result[tuple[Any]]:
    """
    Helper for unfinished notifications
    :return:
    """
    db = await get_db()
    conn = DbHelpers(db)
    utcnow = datetime.utcnow()
    try:
        expressions: tuple = \
            (Notification.status.like(status),
             Notification.modified.between(
                 utcnow - timedelta(days=1),
                 utcnow - timedelta(minutes=wait_minutes))
             )
        unprocessed = await conn.select(
            Notification,
            and_(True, *expressions))
        return unprocessed
    except SQLAlchemyError as err:
        raise db_bad_request(err)


async def initiate_notification_helper(db_conn: DbHelpers,
                                       broker: AbstractQueueInternal,
                                       correlation_id: str,
                                       routing_key: str,
                                       data: dict) -> None:
    """
    Helper to initiate notification
    :param db_conn: Relation DB
    :param broker: AMQP
    :param correlation_id:
    :param routing_key:
    :param data:
    :return:
    """
    # Add initial notification to db
    try:
        await db_conn.insert(Notification(correlation_id,
                                          routing_key,
                                          'Initiated'))
        await db_conn.insert(NotificationContent(correlation_id,
                                                 str(data)))

    except SQLAlchemyError as err:
        raise db_bad_request(err)

    # Produce message to the queue
    await broker.produce(routing_key=routing_key,
                         data=data,
                         correlation_id=correlation_id)

    # Update notification status in DB after producing message
    try:
        await db_conn.update(model=Notification,
                             model_column=Notification.content_id,
                             column_value=correlation_id,
                             update_values={'status': 'Produced',
                                            'modified': datetime.utcnow()})
    except SQLAlchemyError as err:
        raise db_bad_request(err)


async def api_get_helper(url) -> dict | list:
    """
    API GET helper:
    """
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


async def api_post_helper(url, user_ids_list):
    """
    API POST helper:
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, json=user_ids_list) as response:
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
