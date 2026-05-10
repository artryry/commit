from datetime import datetime, timezone
from typing import Sequence
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.notification import Notification


class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_pending(self, user_id: int, type_: str, message: str) -> Notification:
        row = Notification(user_id=user_id, type=type_, message=message)
        self._session.add(row)
        await self._session.flush()
        return row

    async def list_pending_for_user(self, user_id: int) -> Sequence[Notification]:
        result = await self._session.scalars(
            select(Notification)
            .where(Notification.user_id == user_id, Notification.delivered_at.is_(None))
            .order_by(Notification.created_at.asc()),
        )
        return result.all()

    async def mark_delivered(self, notification_id: UUID) -> None:
        await self._session.execute(
            update(Notification)
            .where(Notification.id == notification_id)
            .values(delivered_at=datetime.now(timezone.utc)),
        )
