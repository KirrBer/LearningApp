from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "4362"
    POSTGRES_DB: str = "auth_db"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    
    # JWT
    SECRET_KEY: str = "pmpu"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
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