from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy import update, select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session, Base
from services.postgres import get_postgres

DbDep = Annotated[AsyncSession, Depends(get_postgres)]


async def get_db():
    res = await get_session()
    return res


class DbHelpers:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def insert(self, notification: str) -> None:
        async with self.db:
            self.db.add(notification)
            await self.db.commit()
            await self.db.refresh(notification)

    async def update(self,
                     model: Base,
                     model_column,
                     column_value: str,
                     update_values: dict) -> None:
        async with self.db:
            await self.db.execute(update(model).
                                  where(model_column == column_value).
                                  values(**update_values))
            await self.db.commit()

    async def select(self,
                     model: Base,
                     filter_) -> Result[tuple[Any]]:
        async with self.db:
            res = await self.db.execute(select(model).
                                        filter(filter_))
            return res
