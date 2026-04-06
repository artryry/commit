import os
from functools import cached_property

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    if os.environ.get("IS_DOCKER") is None or os.environ.get("IS_DOCKER") == "false":
        model_config = SettingsConfigDict(
            env_file="../auth_service/.env"
        )

    DB_HOST: str = ""
    DB_PORT: int = 1
    DB_USER: str = ""
    DB_PASS: str = ""
    DB_NAME: str = ""

    PRIVATE_KEY_PATH: str = ""
    PUBLIC_KEY_PATH: str = ""
    ALGORITHM: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1

    # Sites allowed to request
    ORIGINS: list[str] = ["*"]

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = ""
    # Topics
    KAFKA_PUBLIC_KEY_TOPIC: str = ""
    KAFKA_USERS_TOPIC: str = ""

    LOG_LVL: str = ""
    
    IS_DOCKER: bool = True

    @cached_property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @cached_property
    def PRIVATE_KEY(self) -> bytes:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../keys/private.pem"), "rb") as f:
            return f.read()

    @cached_property
    def PUBLIC_KEY(self) -> bytes:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../keys/public.pem"), "rb") as f:
            return f.read()


settings = Settings()
