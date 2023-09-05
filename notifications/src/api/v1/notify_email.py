import logging

from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder

import core.config as conf
from models.email import RequestUserModel
from services.connections import DbDep, DbHelpers
from db.rabbit import BrokerDep
from services.exceptions import user_doesnt_exist
from services.helpers import initiate_notification_helper, api_post_helper

# Объект router, в котором регистрируем обработчики
router = APIRouter()


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
