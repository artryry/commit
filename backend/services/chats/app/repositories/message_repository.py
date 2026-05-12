import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.message import Message


class MessageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_message(
        self,
        *,
        chat_id: uuid.UUID,
        sender_id: int,
        body: str | None,
        image_storage_key: str | None,
    ) -> Message:
        now = datetime.now(timezone.utc)
        msg = Message(
            id=uuid.uuid4(),
            chat_id=chat_id,
            sender_id=sender_id,
            body=body,
            image_storage_key=image_storage_key,
            created_at=now,
        )
        self._session.add(msg)
        await self._session.flush()
        return msg

    async def create_text_message(
        self, chat_id: uuid.UUID, sender_id: int, body: str
    ) -> Message:
        return await self.create_message(
            chat_id=chat_id,
            sender_id=sender_id,
            body=body,
            image_storage_key=None,
        )

    async def list_for_chat(self, chat_id: uuid.UUID) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
