import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.message import Message


class MessageRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_for_chat(self, chat_id: uuid.UUID, limit: int = 100) -> list[Message]:
        result = await self._session.scalars(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())
            .limit(limit),
        )
        return list(result.all())

    async def create_text_message(self, chat_id: uuid.UUID, sender_id: int, body: str) -> Message:
        msg = Message(chat_id=chat_id, sender_id=sender_id, body=body, image_storage_key=None)
        self._session.add(msg)
        await self._session.flush()
        return msg
