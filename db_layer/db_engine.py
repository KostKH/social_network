from sqlalchemy import Integer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import (declarative_base, declared_attr, mapped_column,
                            sessionmaker)
from sqlalchemy.sql import text

from config import settings


class PreBase:

    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()

    id = mapped_column(Integer, primary_key=True)


Base = declarative_base(cls=PreBase)
engine = create_async_engine(settings.database_url)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)


async def get_async_session():
    """Функция для генерации сессий к БД."""
    async with AsyncSessionLocal() as async_session:
        await async_session.execute(text('PRAGMA foreign_keys = ON'))
        yield async_session
