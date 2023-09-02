import logging
import time
from datetime import datetime

import aiohttp
from aiohttp.web_exceptions import HTTPException
from fastapi import status as st
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError

import core.config as conf
from models.schemas import Notification, NotificationContent
from services.connections import get_broker, get_db, DbHelpers
from services.exceptions import db_bad_request
from services.helpers import process_notifications_helper, \
    initiate_notification_helper

routing_key = 'user-reporting.v1.likes-for-reviews'


def success_message(status: str):
    return logging.info(f'No messages left in {status} state. Everything is'
                        f' good.')


async def likes_for_reviews():
    """
    Produces message that will be scheduled:
    {
    "user_id": [
        [
            "movie_id",
            "review_text shortened to 20 signs",
            likes amount for the last 24 hours
        ]
    ]
    }
    """
    db = await get_db()
    conn = DbHelpers(db)
    broker = await get_broker()
    data: dict = await users_daily_likes()
    correlation_id = str(round(time.time()))

    if not data:
        logging.info('If 0 users received 0 likes - don\'t need to send any'
                     ' notifications. Exiting.')
        return

    await initiate_notification_helper(conn,
                                       broker,
                                       correlation_id,
                                       routing_key,
                                       data)


async def users_daily_likes() -> dict:
    """
    API returns:
    {
    "user_id": [
        [
            "movie_id",
            "review_text shortened to 20 signs",
            likes amount for the last 24 hours
        ]
    ]
    }
    """
    url = f'http://{conf.settings.host_ugc}:' \
          f'{conf.settings.port_ugc}' \
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


async def process_initiated_notifications():
    """
    Process unfinished notifications in Initiated state
    :return:
    """
    db = await get_db()
    conn = DbHelpers(db)
    status = 'Initiated'
    unprocessed = await process_notifications_helper(status, 15)
    if not unprocessed:
        success_message(status)
    else:
        for notification in unprocessed:
            notification_dict = jsonable_encoder(*notification)
            failure = notification_dict['failures']
            # If there are more than 2 failures in 'Initiated' state - try to
            # produce message again
            if failure >= 2:
                # Get content
                content_id: str = notification_dict['content_id']
                content = await conn.select(
                    NotificationContent,
                    NotificationContent.id.like(content_id))
                content = content.scalar_one()

                # Produce message to the queue
                broker = await get_broker()
                await broker.produce(routing_key=routing_key,
                                     data=jsonable_encoder(content)['content'],
                                     correlation_id=content_id)

                # Update notification status in DB after producing message
                try:
                    await conn.update(model=Notification,
                                      model_column=Notification.content_id,
                                      column_value=str(content_id),
                                      update_values={
                                          'status': 'Produced',
                                          'failures': 0,
                                          'modified': datetime.utcnow()})
                except SQLAlchemyError as err:
                    raise db_bad_request(err)
            else:
                id_: str = notification_dict['id']
                try:
                    await conn.update(model=Notification,
                                      model_column=Notification.id,
                                      column_value=str(id_),
                                      update_values={
                                          'failures': int(failure) + 1,
                                          'modified': datetime.utcnow()}
                                      )
                except SQLAlchemyError as err:
                    raise db_bad_request(err)


async def process_produced_notifications():
    """
    Process unfinished notifications in Produced state
    :return:
    """
    status = 'Produced'
    unprocessed = await process_notifications_helper(status, 10)
    if not unprocessed:
        success_message(status)
    else:
        for notification in unprocessed:
            notification_dict = jsonable_encoder(*notification)
            id_: str = notification_dict['id']
            content_id: str = notification_dict['content_id']
            logging.warning(f'Achtung!!1 The message stays in {status} state'
                            f' too long! Take action immediately!\n'
                            f'id: {id_}\n'
                            f'content_id {content_id}')


async def process_consumed_notifications():
    """
    Process unfinished notifications in Consumed state
    :return:
    """
    status = 'Consumed'
    unprocessed = await process_notifications_helper(status,
                                                     10)
    if not unprocessed:
        success_message(status)
    else:
        ...
        # send message via smtp again
        # don't forget to check idempotency before sending
