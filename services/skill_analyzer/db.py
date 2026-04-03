"""База данных и ORM-конфигурация.

Здесь определяется:
- асинхронный SQLAlchemy движок
- декоратор `connection` для управления сессией
- базовые типы для моделей (int_pk, str_uniq и т.д.)
- базовый класс модели `Base` с автоматическим табличным именем.
"""

from datetime import datetime
from typing import Annotated
import logging

from sqlalchemy import func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column
from skill_analyzer.settings import settings
from skill_analyzer.exceptions import DatabaseError

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
        session = await async_session_maker()
        try:
            logger.debug(f"Executing database operation: {method.__name__}")
            result = await method(*args, session=session, **kwargs)
            await session.commit()
            return result
        except DatabaseError:
            # Re-raise our own exceptions
            await session.rollback()
            raise
        except Exception as e:
            logger.error(f"Database error in {method.__name__}: {str(e)}")
            await session.rollback()
            raise DatabaseError(f"Database operation failed: {str(e)}")
        finally:
            await session.close()

    return wrapper


# Базовые типы для моделей (для удобства и единообразия).
int_pk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[datetime, mapped_column(server_default=func.now(), onupdate=datetime.now)]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]
str_null_true = Annotated[str, mapped_column(nullable=True)]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        # Имя таблицы формируется автоматически из имени класса (например, Skill -> skills).
        return f"{cls.__name__.lower()}s"
    

