from typing import Annotated

from fastapi import Depends
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session, Base
from db.rabbit import Rabbit, get_rabbit
from services.postgres import get_postgres
from services.rabbit import get_rabbit_service

BrokerDep = Annotated[Rabbit, Depends(get_rabbit_service)]
DbDep = Annotated[AsyncSession, Depends(get_postgres)]


async def get_broker():
    res = await get_rabbit()
    return res


async def get_db():
    res = await get_session()
    return res


class DbHelpers:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def insert(self, notification: str):
        async with self.db:
            self.db.add(notification)
            await self.db.commit()
            await self.db.refresh(notification)

    async def update(self,
                     model: Base,
                     model_column,
                     column_value: str,
                     update_values: dict):
        async with self.db:
            await self.db.execute(update(model).
                                  where(model_column == column_value).
                                  values(**update_values))
            await self.db.commit()
