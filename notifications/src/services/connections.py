from typing import Annotated

from fastapi import Depends

from db.rabbit import Rabbit, get_rabbit
from services.rabbit import get_rabbit_service

BrokerDep = Annotated[Rabbit, Depends(get_rabbit_service)]


async def get_broker():
    res = await get_rabbit()
    return res
