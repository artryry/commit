from abc import ABC, abstractmethod
from typing import List, Optional

import redis.asyncio as redis

from config.settings import settings


class IRedisStackRepository(ABC):
    @abstractmethod
    async def delete_stack(self, user_id: int) -> None:
        pass

    @abstractmethod
    async def rpop_id(self, user_id: int) -> Optional[int]:
        pass

    @abstractmethod
    async def rebuild(self, user_id: int, ordered_ids: List[int]) -> None:
        pass


class RedisStackRepository(IRedisStackRepository):
    def __init__(self, client: redis.Redis):
        self._r = client

    def _key(self, user_id: int) -> str:
        return f"rec:{user_id}:stack"

    async def delete_stack(self, user_id: int) -> None:
        await self._r.delete(self._key(user_id))

    async def rpop_id(self, user_id: int) -> Optional[int]:
        raw = await self._r.rpop(self._key(user_id))
        if raw is None:
            return None
        if isinstance(raw, bytes):
            return int(raw.decode())
        return int(raw)

    async def rebuild(self, user_id: int, ordered_ids: List[int]) -> None:
        key = self._key(user_id)
        await self._r.delete(key)
        if not ordered_ids:
            return
        pipe = self._r.pipeline()
        for uid in reversed(ordered_ids):
            pipe.rpush(key, str(uid))
        pipe.expire(key, settings.REDIS_STACK_TTL_SECONDS)
        await pipe.execute()
