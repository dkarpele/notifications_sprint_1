import orjson

from fastapi import Query
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Model(BaseModel):
    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        allow_population_by_field_name = True


class PaginateModel:
    def __init__(self,
                 page_number: int = Query(1,
                                          ge=1,
                                          le=1000),
                 page_size: int = Query(10,
                                        ge=1,
                                        le=50),
                 ):
        self.page_number = page_number
        self.page_size = page_size
