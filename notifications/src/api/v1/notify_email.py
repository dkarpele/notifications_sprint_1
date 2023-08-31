from datetime import datetime

from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError

from models.email import RequestUserModel
from models.schemas import Notification, NotificationContent
from services.connections import BrokerDep, DbDep, DbHelpers
from services.exceptions import db_bad_request

# Объект router, в котором регистрируем обработчики
router = APIRouter()


@router.post('/user-sign-up',
             status_code=status.HTTP_201_CREATED,
             description="send welcome email to user", )
async def user_welcome(user: RequestUserModel,
                       broker: BrokerDep,
                       db: DbDep):
    conn = DbHelpers(db)
    # Add initial notification to db
    try:
        await conn.insert(NotificationContent(str(user.user_id),
                                              str(jsonable_encoder(user))))
        await conn.insert(Notification(str(user.user_id),
                                       'Initiated'))
    except SQLAlchemyError as err:
        raise db_bad_request(err)

    # Produce message to the queue
    await broker.produce(routing_key='user-reporting.v1.registered',
                         data=jsonable_encoder(user),
                         correlation_id=user.user_id)

    # Update notification status in DB after producing message
    try:
        await conn.update(model=Notification,
                          model_column=Notification.content_id,
                          column_value=str(user.user_id),
                          update_values={'status': 'Produced',
                                         'modified': datetime.utcnow()})
    except SQLAlchemyError as err:
        raise db_bad_request(err)
