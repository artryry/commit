from abc import ABC, abstractmethod
from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import SeenPair


class ISeenPairRepository(ABC):
    @abstractmethod
    async def exists(self, viewer_id: int, seen_id: int) -> bool:
        pass

    @abstractmethod
    async def insert_ignore(self, viewer_id: int, seen_id: int, seen_at: datetime) -> None:
        pass

    @abstractmethod
    async def delete_involving(self, user_id: int) -> None:
        pass


class SqlSeenPairRepository(ISeenPairRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def exists(self, viewer_id: int, seen_id: int) -> bool:
        row = await self._session.get(SeenPair, (viewer_id, seen_id))
        return row is not None

    async def insert_ignore(self, viewer_id: int, seen_id: int, seen_at: datetime) -> None:
        stmt = (
            insert(SeenPair)
            .values(user_id=viewer_id, seen_user_id=seen_id, seen_at=seen_at)
            .on_conflict_do_nothing(index_elements=["user_id", "seen_user_id"])
        )
        await self._session.execute(stmt)

    async def delete_involving(self, user_id: int) -> None:
        await self._session.execute(
            delete(SeenPair).where((SeenPair.user_id == user_id) | (SeenPair.seen_user_id == user_id)),
        )
