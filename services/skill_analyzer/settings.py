import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    POSTGRES_DB: str
    PGDATA: str
    
    # model_config = SettingsConfigDict(
    #     env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    # )
    model_config = SettingsConfigDict()
    def get_db_url(self):
        return (f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}")

        
settings = Settings()