import ast
import logging
import time
from datetime import datetime

from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError

import core.config as conf
from db.rabbit import get_broker
from models.schemas import Notification, NotificationContent
from services.connections import get_db, DbHelpers
from services.exceptions import db_bad_request
from services.helpers import process_notifications_helper, \
    initiate_notification_helper, api_get_helper, api_post_helper
from message_worker.send_emails import Email


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
            "movie_title",
            "review_text shortened to 20 signs",
            "likes amount for the last 24 hours"
        ],
        [
            "user_email",
            "first_name",
            "last_name",
        ] - only last element
    ]
    }
    """
    db = await get_db()
    conn = DbHelpers(db)
    broker = await get_broker()
    routing_key = 'user-reporting.v1.likes-for-reviews'

    """
    API /api/v1/reviews/users-daily-likes returns:
    {
    "user_id": [
        [
            "movie_id",
            "movie_title"
            "review_text shortened to 20 signs",
            "likes amount for the last 24 hours"
        ]
    ]
    }
    """
    url = f'http://{conf.settings.host_ugc}:' \
          f'{conf.settings.port_ugc}' \
          f'/api/v1/reviews/users-daily-likes'
    data_likes: dict = await api_get_helper(url)

    """
    API /api/v1/users_unauth/user_ids returns:
    [
    {
        "first_name": "admin",
        "last_name": "admin",
        "email": "admin@example.com",
        "id": "00791e6e-638e-4dcd-beee-15d6f1bf4571",
        "disabled": false,
        "is_admin": true,
        "roles": []
    }
    ]
    """
    url = f'http://{conf.settings.host_auth}:' \
          f'{conf.settings.port_auth}' \
          f'/api/v1/users_unauth/user_ids'
    user_ids_list: list = list(data_likes.keys())
    data_users: list = await api_post_helper(url, user_ids_list)

    # Adding user_data as a last element of dict where key is user_id
    for user_key in data_likes.keys():
        for user in data_users:
            if user_key == user['id']:
                data_likes[user_key].append([user['email'],
                                             user['first_name'],
                                             user['last_name']])

    correlation_id = str(round(time.time()))

    if not data_likes:
        logging.info('If 0 users received 0 likes - don\'t need to send any'
                     ' notifications. Exiting.')
        return

    await initiate_notification_helper(conn,
                                       broker,
                                       correlation_id,
                                       routing_key,
                                       data_likes)


async def process_initiated_notifications():
    """
    Process unfinished notifications in Initiated state
    :return:
    """
    db = await get_db()
    conn = DbHelpers(db)
    routing_key = 'user-reporting.v1.likes-for-reviews'
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
                    NotificationContent.id == content_id)
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
                            f'content_id: {content_id}')


async def process_consumed_notifications():
    """
    Process unfinished notifications in Consumed state
    :return:
    """
    db = await get_db()
    conn = DbHelpers(db)

    status = 'Consumed'
    unprocessed = await process_notifications_helper(status,
                                                     10)
    if not unprocessed:
        success_message(status)
    else:
        for notification in unprocessed:
            notification_dict = jsonable_encoder(*notification)
            content_id: str = notification_dict['content_id']
            routing_key: str = notification_dict['routing_key']

            message = await conn.select(
                model=NotificationContent,
                filter_=NotificationContent.id == content_id)
            message = message.scalar_one()
            body = ast.literal_eval(message.content)

            if routing_key == 'user-reporting.v1.registered':
                await Email().send_registered(body, content_id)
            elif routing_key == 'user-reporting.v1.likes-for-reviews':
                await Email().send_likes(body, content_id)
