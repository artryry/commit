"""Create notifications, push when possible, persist `delivered_at` when sent."""

from sqlalchemy.ext.asyncio import AsyncSession

from repositories.notification_repository import NotificationRepository
from services.connection_manager import ConnectionManager


class DeliveryService:
    def __init__(
        self,
        repo: NotificationRepository,
        cm: ConnectionManager,
        session: AsyncSession,
    ):
        self._repo = repo
        self._cm = cm
        self._session = session

    async def enqueue_and_try_deliver(self, user_id: int, type_: str, message: str) -> None:
        row = await self._repo.create_pending(user_id, type_, message)
        await self._session.flush()
        body = {"type": type_, "message": message}
        if await self._cm.send_json_to_user(user_id, body):
            await self._repo.mark_delivered(row.id)

    async def flush_pending_for_user(self, user_id: int) -> None:
        pending = await self._repo.list_pending_for_user(user_id)
        for row in pending:
            body = {"type": row.type, "message": row.message}
            if await self._cm.send_json_to_user(user_id, body):
                await self._repo.mark_delivered(row.id)
