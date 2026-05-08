from abc import ABC, abstractmethod
from typing import List

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Tag, filter_tags, user_tags


class ITagRepository(ABC):
    @abstractmethod
    async def get_or_create_id(self, name: str) -> int:
        pass

    @abstractmethod
    async def filter_tag_names_for_user(self, user_id: int) -> List[str]:
        pass

    @abstractmethod
    async def replace_user_tags(self, user_id: int, names: List[str]) -> None:
        pass

    @abstractmethod
    async def replace_filter_tags(self, user_id: int, names: List[str]) -> None:
        pass

    @abstractmethod
    async def user_has_any_of_tags(self, user_id: int, names: List[str]) -> bool:
        pass


class SqlTagRepository(ITagRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_or_create_id(self, name: str) -> int:
        row = await self._session.scalar(select(Tag).where(Tag.name == name))
        if row is None:
            row = Tag(name=name)
            self._session.add(row)
            await self._session.flush()
        return row.id

    async def filter_tag_names_for_user(self, user_id: int) -> List[str]:
        rows = await self._session.execute(
            select(Tag.name)
            .join(filter_tags, Tag.id == filter_tags.c.tag_id)
            .where(filter_tags.c.user_id == user_id),
        )
        return [r[0] for r in rows.all()]

    async def replace_user_tags(self, user_id: int, names: List[str]) -> None:
        await self._session.execute(delete(user_tags).where(user_tags.c.user_id == user_id))
        for raw in names:
            name = str(raw).strip()
            if not name:
                continue
            tid = await self.get_or_create_id(name)
            await self._session.execute(user_tags.insert().values(user_id=user_id, tag_id=tid))

    async def replace_filter_tags(self, user_id: int, names: List[str]) -> None:
        await self._session.execute(delete(filter_tags).where(filter_tags.c.user_id == user_id))
        for raw in names:
            name = str(raw).strip()
            if not name:
                continue
            tid = await self.get_or_create_id(name)
            await self._session.execute(filter_tags.insert().values(user_id=user_id, tag_id=tid))

    async def user_has_any_of_tags(self, user_id: int, names: List[str]) -> bool:
        if not names:
            return True
        row = await self._session.execute(
            select(Tag.id)
            .join(user_tags, Tag.id == user_tags.c.tag_id)
            .where(user_tags.c.user_id == user_id, Tag.name.in_(names))
            .limit(1),
        )
        return row.first() is not None
