from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from db.models import UserFilter


class IUserFilterRepository(ABC):
    @abstractmethod
    async def get(self, user_id: int) -> Optional[UserFilter]:
        pass

    @abstractmethod
    async def ensure_row(self, user_id: int, now: datetime) -> UserFilter:
        pass

    @abstractmethod
    async def apply_fields(
        self,
        row: UserFilter,
        *,
        relationship_type: Optional[int],
        age_from: Optional[int],
        age_to: Optional[int],
        city: Optional[str],
        sign: Optional[str],
        partner_gender: Optional[int],
        now: datetime,
    ) -> None:
        pass


class SqlUserFilterRepository(IUserFilterRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, user_id: int) -> Optional[UserFilter]:
        return await self._session.get(UserFilter, user_id)

    async def ensure_row(self, user_id: int, now: datetime) -> UserFilter:
        row = await self.get(user_id)
        if row is None:
            row = UserFilter(user_id=user_id, updated_at=now)
            self._session.add(row)
            await self._session.flush()
        return row

    async def apply_fields(
        self,
        row: UserFilter,
        *,
        relationship_type: Optional[int],
        age_from: Optional[int],
        age_to: Optional[int],
        city: Optional[str],
        sign: Optional[str],
        partner_gender: Optional[int],
        now: datetime,
    ) -> None:
        # Align with profile.v1: SEARCH_FOR_UNSPECIFIED (0) means no constraint — store NULL.
        rt = relationship_type
        if rt == 0:
            rt = None
        row.relationship_type = rt
        row.age_from = age_from
        row.age_to = age_to
        row.city = city
        row.sign = sign
        row.partner_gender = partner_gender
        row.updated_at = now
