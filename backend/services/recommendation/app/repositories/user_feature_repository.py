from abc import ABC, abstractmethod
from typing import List, Optional, Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import UserFeature


class IUserFeatureRepository(ABC):
    @abstractmethod
    async def get(self, user_id: int) -> Optional[UserFeature]:
        pass

    @abstractmethod
    async def get_many(self, user_ids: Sequence[int]) -> dict[int, UserFeature]:
        pass

    @abstractmethod
    async def add(self, row: UserFeature) -> None:
        pass

    @abstractmethod
    async def flush(self) -> None:
        pass

    @abstractmethod
    async def list_except(self, exclude_user_id: int) -> Sequence[UserFeature]:
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> None:
        pass

    @abstractmethod
    async def update_search_for_vector(self, user_id: int, search_for_vector: List[float]) -> None:
        pass


class SqlUserFeatureRepository(IUserFeatureRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, user_id: int) -> Optional[UserFeature]:
        return await self._session.get(UserFeature, user_id)

    async def get_many(self, user_ids: Sequence[int]) -> dict[int, UserFeature]:
        if not user_ids:
            return {}
        result = await self._session.scalars(select(UserFeature).where(UserFeature.user_id.in_(list(user_ids))))
        rows = result.all()
        return {int(r.user_id): r for r in rows}

    async def add(self, row: UserFeature) -> None:
        self._session.add(row)
        await self._session.flush()

    async def flush(self) -> None:
        await self._session.flush()

    async def list_except(self, exclude_user_id: int) -> Sequence[UserFeature]:
        result = await self._session.scalars(
            select(UserFeature).where(UserFeature.user_id != exclude_user_id),
        )
        return result.all()

    async def delete(self, user_id: int) -> None:
        await self._session.execute(delete(UserFeature).where(UserFeature.user_id == user_id))

    async def update_search_for_vector(self, user_id: int, search_for_vector: List[float]) -> None:
        uf = await self.get(user_id)
        if uf is None:
            return
        uf.search_for_vector = search_for_vector
        await self.flush()
