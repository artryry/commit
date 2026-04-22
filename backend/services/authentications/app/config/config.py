from functools import cached_property
import os

from pydantic_settings import BaseSettings

class Config(BaseSettings):
    """Configuration for the application."""

    # Application settings
    APP_NAME: str = "Authentication Service"
    APP_VERSION: str = "1.0.0"

    # Sites allowed to request
    ORIGINS: list[str] = ["http://localhost:8000"]

    # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "user"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "auth_db"
    
    # JWT settings
    JWT_SECRET_KEY: str = "your_secret_key"
    JWT_ALGORITHM: str = "RC256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15

    @cached_property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"

cfg = Config()
