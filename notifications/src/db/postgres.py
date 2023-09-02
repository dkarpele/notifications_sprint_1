import os

from db import AbstractStorage
from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, \
    async_sessionmaker

# Создаём базовый класс для будущих моделей
Base = declarative_base(metadata=MetaData(schema='notify'))


class Postgres(AbstractStorage):
    def __init__(self, url: str):
        echo = (os.getenv('ENGINE_ECHO', 'False') == 'True')
        self.engine = create_async_engine(url,
                                          echo=echo,
                                          future=True)

        self.async_session = async_sessionmaker(self.engine,
                                                class_=AsyncSession,
                                                expire_on_commit=False)

    async def close(self):
        ...


postgres: Postgres | None = None


# Функция понадобится при внедрении зависимостей
# Dependency
async def get_session() -> AsyncSession | None:
    if postgres:
        async with postgres.async_session() as session:
            return session
    else:
        return None
