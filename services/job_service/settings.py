"""Конфигурация приложения Job Service.

Загружает переменные окружения из `.env` и формирует URL для подключения к PostgreSQL.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: str = 'postgres'
    DB_HOST: str = 'localhost'
    DB_PORT: int = '5432'
    POSTGRES_DB: str = 'vacancies'
    PGDATA: str = 'pgdata:/var/lib/postgresql/data'

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Игнорировать лишние переменные
    )

    def get_db_url(self):
        """Возвращает URL подключения к PostgreSQL (asyncpg)."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()