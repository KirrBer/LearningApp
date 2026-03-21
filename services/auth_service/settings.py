from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "4362"
    POSTGRES_DB: str = "auth_db"
    DB_HOST: str = "auth_db"
    DB_PORT: str = "5432"
    
    # JWT
    SECRET_KEY: str = "pmpu"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    class Config:
        env_file = ".env"

settings = Settings()