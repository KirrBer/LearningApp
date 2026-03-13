from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    POSTGRES_DB: str
    PGDATA: str
    KAFKA_BOOTSTRAP_SERVERS: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Игнорировать лишние переменные
    )
    def get_db_url(self):
        return (f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}")

        
settings = Settings()