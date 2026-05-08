import json
import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

import redis.asyncio as redis

from config.settings import settings
from services.embedding_service import IEmbeddingEncoder
from services.factory import build_recommendation_service
from services.recommendation_service import RecommendationService
from utils.profile_payload import ProfilePayloadParser

logger = logging.getLogger(__name__)


class ProfileIngestionService:
    """Turn Kafka profile / auth events into DB + Redis updates."""

    def __init__(self, embedding: IEmbeddingEncoder):
        self._embedding = embedding

    async def handle_kafka_envelope(
        self,
        session: AsyncSession,
        redis_client: redis.Redis,
        envelope: dict[str, Any],
    ) -> None:
        event_type = envelope.get("event_type") or envelope.get("EventType")
        payload = envelope.get("payload")
        if isinstance(payload, str):
            payload = json.loads(payload)
        if not isinstance(payload, dict):
            logger.warning("ignored envelope (bad payload): %s", envelope)
            return

        svc = build_recommendation_service(session, redis_client)

        if event_type == settings.KAFKA_TOPIC_PROFILE_UPDATED:
            await self._profile_updated(svc, payload)
        elif event_type == settings.KAFKA_TOPIC_USER_DELETED:
            await self._user_deleted(svc, payload)
        else:
            logger.debug("ignored kafka event_type=%s", event_type)

    async def _profile_updated(self, svc: RecommendationService, payload: dict[str, Any]) -> None:
        p = ProfilePayloadParser.parse(payload)
        bio_v, sf_v, comb_v = await self._embedding.encode_three(p.bio, p.search_for)
        await svc.upsert_user_from_profile_event(
            user_id=p.user_id,
            bio=p.bio,
            search_for=p.search_for,
            birthday=p.birthday,
            gender=p.gender,
            sign=p.sign,
            city=p.city,
            relationship_type=p.relationship_type,
            tag_names=p.tags,
            bio_vec=bio_v,
            search_vec=sf_v,
            combined_vec=comb_v,
        )

    async def _user_deleted(self, svc: RecommendationService, payload: dict[str, Any]) -> None:
        raw = payload.get("id")
        if raw is None:
            logger.warning("user.deleted missing id: %s", payload)
            return
        await svc.delete_user(int(raw))
