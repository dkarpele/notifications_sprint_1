import ast
import logging
from typing import Annotated

from fastapi import APIRouter, status, Depends
from fastapi.encoders import jsonable_encoder

import core.config as conf
from db.rabbit import BrokerDep
from models.email import RequestUserModel
from models.model import PaginateModel
from models.notifications import NotificationsHistoryModel
from services.connections import DbDep, DbHelpers
from services.exceptions import user_doesnt_exist
from services.helpers import initiate_notification_helper, api_post_helper, \
    get_notification_history_helper, api_get_helper
from services.token import security_jwt

# Объект router, в котором регистрируем обработчики
router = APIRouter()
Paginate = Annotated[PaginateModel, Depends(PaginateModel)]


@router.post('/user-sign-up',
             status_code=status.HTTP_201_CREATED,
             description="send welcome email to user", )
async def user_welcome(user: RequestUserModel,
                       broker: BrokerDep,
                       db: DbDep):
    conn = DbHelpers(db)
    correlation_id = str(user.user_id)
    routing_key = 'user-reporting.v1.registered'

    url = f'http://{conf.settings.host_auth}:' \
          f'{conf.settings.port_auth}' \
          f'/api/v1/users_unauth/user_ids'
    user_ids_list: list = [str(user.user_id)]
    data_users: list = await api_post_helper(url, user_ids_list)
    if not data_users:
        logging.error(f'User {user.user_id} doesn\'t exist!!!')
        raise user_doesnt_exist

    data = jsonable_encoder(data_users[0])
    await initiate_notification_helper(conn,
                                       broker,
                                       correlation_id,
                                       routing_key,
                                       data)


@router.get('/get-notifications-history',
            response_model=list[NotificationsHistoryModel],
            status_code=status.HTTP_200_OK,
            description="получение истории уведомлений",
            response_description="user_email, message")
async def get_history(pagination: Paginate,
                      token: Annotated[str, Depends(security_jwt)],
                      db: DbDep) -> list[NotificationsHistoryModel]:
    page = pagination.page_number
    size = pagination.page_size

    conn = DbHelpers(db)

    # Getting user id from token
    url = f'http://{conf.settings.host_auth}:'\
          f'{conf.settings.port_auth}'\
          f'/api/v1/users/me'
    headers = {'Authorization': f'Bearer {token}'}
    user_data = await api_get_helper(url, headers)

    data = await get_notification_history_helper(conn,
                                                 user_data['id'],
                                                 page,
                                                 size)

    res = []
    for notification in data:
        notification = jsonable_encoder(*notification)
        res.append(
            NotificationsHistoryModel(
                user_email=notification['user_email'],
                message_content=ast.literal_eval(
                    notification['message_content']),
                html_content=notification['html_content'],
                last_notification_send=notification['last_notification_send']
            )
        )
    return res
