from functools import cached_property

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "chats"

    HOST: str = "0.0.0.0"
    PORT: int = 8005

    ORIGINS: list[str] = ["*"]

    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "chats"
    DB_ECHO: bool = False

    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_GROUP_ID: str = "chats-service"
    KAFKA_TOPIC_MATCH_CREATED: str = "match.created"
    KAFKA_TOPIC_CHAT_DELETED: str = "chat.deleted"
    KAFKA_TOPIC_CHAT_MESSAGE: str = "chat.message"

    STORAGE_ENDPOINT: str = "http://localhost:9000"
    STORAGE_ACCESS_KEY: str = "admin"
    STORAGE_SECRET_KEY: str = "password"
    STORAGE_BUCKET: str = "profiles"
    STORAGE_USE_SSL: bool = False

    @cached_property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


cfg = Config()
