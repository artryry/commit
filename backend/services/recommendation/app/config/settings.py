from functools import cached_property

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    GRPC_HOST: str = "0.0.0.0"
    GRPC_PORT: int = 50052

    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "recommendations"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_STACK_TTL_SECONDS: int = 86400

    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_GROUP_ID: str = "recommendation-service"
    KAFKA_TOPIC_PROFILE_UPDATED: str = "profile.updated"
    KAFKA_TOPIC_USER_DELETED: str = "user.deleted"

    EMBEDDING_MODEL_NAME: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DIM: int = 384

    RECOMMENDATIONS_BATCH_SIZE: int = 25
    STACK_PREFETCH_LIMIT: int = 500

    DEBUG: bool = False

    @cached_property
    def async_database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @cached_property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


settings = Settings()
