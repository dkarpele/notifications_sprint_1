from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from db.rabbit import get_rabbit, Rabbit


@lru_cache()
def get_rabbit_service(
        rabbit: Rabbit = Depends(get_rabbit)) -> Rabbit:
    return rabbit


BrokerDep = Annotated[Rabbit, Depends(get_rabbit_service)]
