from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from models.chat import Chat
from models.message import Message
from utils.pair import peer_user_id, sorted_pair


class ChatRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def ensure_chat_for_match(self, match_id: int, user_a: int, user_b: int) -> Chat:
        low, high = sorted_pair(user_a, user_b)
        stmt = (
            insert(Chat)
            .values(user_low=low, user_high=high, match_id=match_id)
            .on_conflict_do_nothing(constraint="uq_chats_pair")
        )
        await self._session.execute(stmt)
        await self._session.flush()
        row = await self._session.scalar(select(Chat).where(Chat.user_low == low, Chat.user_high == high))
        assert row is not None
        return row

    async def get_chat_between(self, uid: int, peer_id: int) -> Chat | None:
        low, high = sorted_pair(uid, peer_id)
        return await self._session.scalar(select(Chat).where(Chat.user_low == low, Chat.user_high == high))

    async def list_chats_summary(self, viewer_id: int) -> list[dict]:
        result = await self._session.scalars(
            select(Chat).where(or_(Chat.user_low == viewer_id, Chat.user_high == viewer_id)),
        )
        chats = list(result.all())
        rows: list[dict] = []
        for c in chats:
            peer = peer_user_id(c.user_low, c.user_high, viewer_id)
            last_msg = await self._session.scalar(
                select(Message)
                .where(Message.chat_id == c.id)
                .order_by(Message.created_at.desc())
                .limit(1),
            )
            last_at = None
            preview = None
            if last_msg:
                last_at = last_msg.created_at
                if last_msg.body:
                    preview = last_msg.body
                elif last_msg.image_storage_key:
                    preview = "[image]"
            rows.append(
                {
                    "chat_id": str(c.id),
                    "peer_user_id": peer,
                    "last_message_at": last_at.isoformat() if last_at else None,
                    "last_message_preview": preview,
                },
            )

        def sort_key(r: dict) -> datetime:
            raw = r["last_message_at"]
            if raw is None:
                return datetime.min.replace(tzinfo=timezone.utc)
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))

        rows.sort(key=sort_key, reverse=True)
        return rows

    async def collect_image_keys_and_delete_chat(self, chat: Chat) -> list[str]:
        res = await self._session.scalars(
            select(Message.image_storage_key).where(
                Message.chat_id == chat.id,
                Message.image_storage_key.is_not(None),
            ),
        )
        keys = [k for k in res.all() if k]
        await self._session.delete(chat)
        await self._session.flush()
        return keys
