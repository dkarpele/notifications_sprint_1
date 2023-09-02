from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session


@lru_cache()
def get_postgres(
        pg: AsyncSession = Depends(get_session)) -> AsyncSession:
    return pg
