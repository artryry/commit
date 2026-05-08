import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from repositories import (
    RedisStackRepository,
    SqlSeenPairRepository,
    SqlTagRepository,
    SqlUserFeatureRepository,
    SqlUserFilterRepository,
)
from services.recommendation_service import RecommendationService


def build_recommendation_service(
    session: AsyncSession,
    redis_client: redis.Redis,
) -> RecommendationService:
    users = SqlUserFeatureRepository(session)
    filters = SqlUserFilterRepository(session)
    tags = SqlTagRepository(session)
    seen = SqlSeenPairRepository(session)
    stack = RedisStackRepository(redis_client)
    return RecommendationService(users, filters, tags, seen, stack)
