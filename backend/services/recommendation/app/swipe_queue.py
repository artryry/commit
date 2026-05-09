"""Redis-backed swipe job queue (Kafka fast-path → LPUSH; background worker ← BRPOP)."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import redis.asyncio as redis

from config.settings import settings
from db.session import async_session_maker
from services.factory import build_recommendation_service

logger = logging.getLogger(__name__)


def _parse_payload(envelope: dict[str, Any]) -> dict[str, Any] | None:
    payload = envelope.get("payload")
    if isinstance(payload, str):
        payload = json.loads(payload)
    if not isinstance(payload, dict):
        return None
    viewer = payload.get("viewer_id")
    target = payload.get("target_user_id")
    liked = payload.get("liked")
    if viewer is None or target is None or liked is None:
        logger.warning("swipe envelope missing fields: %s", envelope)
        return None
    return {
        "viewer_id": int(viewer),
        "target_user_id": int(target),
        "liked": bool(liked),
    }


async def enqueue_swipe_from_kafka(redis_client: redis.Redis, envelope: dict[str, Any]) -> None:
    """LPUSH one JSON job so the consumer commits Kafka quickly."""
    job = _parse_payload(envelope)
    if job is None:
        return
    raw = json.dumps(job, separators=(",", ":"))
    await redis_client.lpush(settings.SWIPE_QUEUE_REDIS_KEY, raw)


async def run_swipe_worker(redis_client: redis.Redis) -> None:
    """BRPOP loop: DB updates + optional vector nudge off the hot Kafka path."""
    key = settings.SWIPE_QUEUE_REDIS_KEY
    timeout = settings.SWIPE_QUEUE_BRPOP_TIMEOUT_SEC
    logger.info("swipe worker started key=%s brpop_timeout=%s", key, timeout)
    while True:
        try:
            item = await redis_client.brpop(key, timeout=timeout)
        except asyncio.CancelledError:
            logger.info("swipe worker cancelled")
            raise
        except Exception:
            logger.exception("swipe worker brpop failed")
            await asyncio.sleep(1.0)
            continue

        if not item:
            continue

        _, raw = item
        try:
            job = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            logger.warning("bad swipe job bytes: %r", raw[:200])
            continue

        viewer_id = job.get("viewer_id")
        target_id = job.get("target_user_id")
        liked = job.get("liked")
        if viewer_id is None or target_id is None or liked is None:
            logger.warning("bad swipe job shape: %s", job)
            continue

        async with async_session_maker() as session:
            try:
                svc = build_recommendation_service(session, redis_client)
                await svc.record_swipe_pair(int(viewer_id), int(target_id))
                await svc.apply_swipe_search_nudge(int(viewer_id), int(target_id), bool(liked))
                await session.commit()
            except Exception:
                await session.rollback()
                logger.exception("swipe job failed viewer=%s target=%s", viewer_id, target_id)
