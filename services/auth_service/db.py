from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column
from typing import Annotated
import logging
from sqlalchemy import func
from auth_service.settings import settings
from datetime import datetime

logger = logging.getLogger(__name__)


DATABASE_URL = settings.get_db_url()
engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


def connection(method):
    """Декоратор для выполнения функции в контексте DB-сессии.

    Позволяет не передавать сессию явно, упрощает работу с async SQLAlchemy.
    Обрабатывает ошибки и откатывает сессию при необходимости.
    
    Raises:
        DatabaseError: If database operation fails
    """

    async def wrapper(*args, **kwargs):
        async with async_session_maker() as session:
            logger.debug(f"Executing database operation: {method.__name__}")
            result = await method(*args, session=session, **kwargs)
            await session.commit()
            return result
    return wrapper

int_pk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[datetime, mapped_column(server_default=func.now(), onupdate=datetime.now)]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]
str_null_true = Annotated[str, mapped_column(nullable=True)]

class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True