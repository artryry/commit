from functools import cached_property
import os
from pathlib import Path

from pydantic_settings import BaseSettings

class Config(BaseSettings):
    """Configuration for the application."""

    # Application settings
    APP_NAME: str = "Authentication Service"
    APP_VERSION: str = "1.0.0"

    # Sites allowed to request
    ORIGINS: list[str] = ["http://localhost:8000"]

    #Kafka settings
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_USER_CREATED_TOPIC: str = "user.created"
    KAFKA_USER_DELETED_TOPIC: str = "user.deleted"

    # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "user"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "auth_db"
    
    # JWT settings
    JWT_PRIVATE_KEY_PATH: str = "keys/private.pem"
    JWT_PUBLIC_KEY_PATH: str = "keys/public.pem"
    JWT_ALGORITHM: str = "RS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Password settings
    MIN_PASSWORD_LENGTH: int = 8

    # Debug settings
    DEBUG: bool = False


    @property
    def LOGGING_LEVEL(self) -> str:
        return "INFO" if not self.DEBUG else "DEBUG"


    @property
    def DB_ECHO(self) -> bool:
        return self.DEBUG


    @cached_property
    def JWT_PRIVATE_KEY(self) -> str:
        return Path(
            self.JWT_PRIVATE_KEY_PATH
        ).read_text()


    @cached_property
    def JWT_PUBLIC_KEY(self) -> str:
        return Path(
            self.JWT_PUBLIC_KEY_PATH
        ).read_text()


    @cached_property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


    class Config:
        env_file = ".env"

cfg = Config()
