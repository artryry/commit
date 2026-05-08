import redis.asyncio as redis

from config.settings import settings


def create_redis() -> redis.Redis:
    return redis.from_url(settings.redis_url, decode_responses=False)
