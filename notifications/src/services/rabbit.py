from functools import lru_cache

from fastapi import Depends

from db.rabbit import get_rabbit, Rabbit


@lru_cache()
def get_rabbit_service(
        rabbit: Rabbit = Depends(get_rabbit)) -> Rabbit:
    return rabbit
