from abc import ABC, abstractmethod
from typing import Optional, Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import UserFeature


class IUserFeatureRepository(ABC):
    @abstractmethod
    async def get(self, user_id: int) -> Optional[UserFeature]:
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


class SqlUserFeatureRepository(IUserFeatureRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, user_id: int) -> Optional[UserFeature]:
        return await self._session.get(UserFeature, user_id)

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
