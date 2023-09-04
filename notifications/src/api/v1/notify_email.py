from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder

from models.email import RequestUserModel
from services.connections import DbDep, DbHelpers
from db.rabbit import BrokerDep
from services.helpers import initiate_notification_helper

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
    data = jsonable_encoder(user)
    await initiate_notification_helper(conn,
                                       broker,
                                       correlation_id,
                                       routing_key,
                                       data)
