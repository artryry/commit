import asyncio
import logging

from aiokafka import AIOKafkaProducer
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from kafka.publisher import publish_chat_deleted, publish_chat_message
from models.message import Message
from repositories.chat_repository import ChatRepository
from repositories.message_repository import MessageRepository
from services.minio_storage import ChatImageStorage

logger = logging.getLogger(__name__)

_MAX_IMAGE_BYTES = 10 * 1024 * 1024
_ALLOWED_IMAGE_CT = frozenset({"image/jpeg", "image/png", "image/webp"})


class ChatAppService:
    def __init__(
        self,
        session: AsyncSession,
        kafka_producer: AIOKafkaProducer,
        storage: ChatImageStorage,
    ):
        self._session = session
        self._kafka_producer = kafka_producer
        self._storage = storage
        self._chats = ChatRepository(session)
        self._messages = MessageRepository(session)

    @staticmethod
    def _preview_for_kafka(body: str | None, has_image: bool) -> str:
        if body:
            return body if len(body) <= 200 else body[:197] + "..."
        if has_image:
            return "[image]"
        return ""

    async def send_chat_message(
        self,
        sender_id: int,
        peer_user_id: int,
        *,
        body: str | None,
        image_bytes: bytes | None,
        image_content_type: str | None,
    ) -> Message:
        if peer_user_id == sender_id:
            raise HTTPException(status_code=400, detail="invalid peer")

        body_clean = body.strip() if body else None
        has_raw_file = bool(image_bytes)

        if has_raw_file and len(image_bytes) > _MAX_IMAGE_BYTES:
            raise HTTPException(status_code=400, detail="image too large")

        image_key: str | None = None
        if has_raw_file:
            if not image_content_type or image_content_type not in _ALLOWED_IMAGE_CT:
                raise HTTPException(
                    status_code=400,
                    detail="unsupported or missing image content type",
                )
            try:
                image_key = await asyncio.to_thread(
                    self._storage.upload_chat_image,
                    image_bytes,
                    image_content_type,
                )
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e)) from e
            except RuntimeError as e:
                raise HTTPException(status_code=502, detail="storage error") from e

        if not body_clean and not image_key:
            raise HTTPException(status_code=400, detail="body or file required")

        chat = await self._chats.get_chat_between(sender_id, peer_user_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="chat not found")

        msg = await self._messages.create_message(
            chat_id=chat.id,
            sender_id=sender_id,
            body=body_clean,
            image_storage_key=image_key,
        )
        await self._session.commit()

        recipient_id = peer_user_id
        preview = self._preview_for_kafka(body_clean, bool(image_key))

        try:
            await publish_chat_message(
                self._kafka_producer,
                chat_id=str(chat.id),
                message_id=str(msg.id),
                sender_id=sender_id,
                recipient_id=recipient_id,
                preview=preview,
            )
        except Exception:
            logger.exception(
                "kafka publish chat.message failed chat_id=%s message_id=%s",
                chat.id,
                msg.id,
            )
        return msg

    async def send_text_message(self, sender_id: int, peer_user_id: int, body: str) -> Message:
        body = body.strip()
        if not body:
            raise HTTPException(status_code=400, detail="body required")
        return await self.send_chat_message(
            sender_id,
            peer_user_id,
            body=body,
            image_bytes=None,
            image_content_type=None,
        )

    async def delete_chat_for_both_users(self, current_user_id: int, peer_user_id: int) -> None:
        if peer_user_id == current_user_id:
            raise HTTPException(status_code=400, detail="invalid peer")

        chat = await self._chats.get_chat_between(current_user_id, peer_user_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="chat not found")

        chat_uuid = chat.id
        low, high = chat.user_low, chat.user_high

        image_keys = await self._chats.collect_image_keys_and_delete_chat(chat)
        await self._session.commit()

        await asyncio.to_thread(self._storage.remove_keys, image_keys)

        try:
            await publish_chat_deleted(
                self._kafka_producer,
                chat_id=str(chat_uuid),
                user_low=low,
                user_high=high,
            )
        except Exception:
            logger.exception("kafka publish chat.deleted failed after DB delete chat_id=%s", chat_uuid)
