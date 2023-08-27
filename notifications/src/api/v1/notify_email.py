from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder

from models.email import RequestUserModel
from services.connections import BrokerDep


# Объект router, в котором регистрируем обработчики
router = APIRouter()


@router.post('/user-sign-up',
             status_code=status.HTTP_201_CREATED,
             description="send welcome email to user", )
async def user_welcome(user: RequestUserModel,
                       broker: BrokerDep):
    await broker.produce(routing_key='user-reporting.v1.registered',
                         data=jsonable_encoder(user),
                         correlation_id=user.user_id)
