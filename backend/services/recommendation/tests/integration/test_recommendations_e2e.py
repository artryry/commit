import asyncio
import os
import time

import grpc
import pytest
from aiokafka import AIOKafkaProducer

from transport.grpc.proto.gen import recommendation_pb2, recommendation_pb2_grpc


def _grpc_target() -> str:
    return os.getenv("RECOMMENDATIONS_GRPC_TARGET", "localhost:50052")


def _bootstrap_servers() -> str:
    return os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


def _topic_profile_updated() -> str:
    return os.getenv("KAFKA_TOPIC_PROFILE_UPDATED", "profile.updated")


@pytest.mark.asyncio
async def test_grpc_set_filters_roundtrip() -> None:
    async with grpc.aio.insecure_channel(_grpc_target()) as channel:
        stub = recommendation_pb2_grpc.RecommendationServiceStub(channel)

        uid = int(time.time()) % 1_000_000 + 1000
        set_resp = await stub.SetFilters(
            recommendation_pb2.SetFiltersRequest(
                user_id=uid,
                age_from=18,
                age_to=99,
                city="TestCity",
                sign="TestSign",
                tags=["tag-a", "tag-b"],
            )
        )
        assert set_resp.success is True

        get_resp = await stub.GetFilters(recommendation_pb2.GetFiltersRequest(user_id=uid))
        assert get_resp.age_from == 18
        assert get_resp.age_to == 99
        assert get_resp.city == "TestCity"
        assert get_resp.sign == "TestSign"
        assert set(get_resp.tags) == {"tag-a", "tag-b"}


@pytest.mark.asyncio
async def test_kafka_profile_updated_drives_recommendations() -> None:
    # Create two users via Kafka, then ensure gRPC can recommend candidate to viewer.
    viewer_id = int(time.time()) % 1_000_000 + 2000
    candidate_id = viewer_id + 1

    producer = AIOKafkaProducer(bootstrap_servers=_bootstrap_servers())
    await producer.start()
    try:
        await producer.send_and_wait(
            _topic_profile_updated(),
            {
                "event_type": _topic_profile_updated(),
                "payload": {
                    "user_id": viewer_id,
                    "bio": "I like coffee and hiking",
                    "search_for": "someone who likes hiking",
                    "birthday": 946684800,  # 2000-01-01
                    "gender": "MALE",
                    "relationship_type": "FRIENDSHIP",
                    "city": "TestTown",
                    "sign": "aries",
                    "tags": ["hiking", "coffee"],
                },
            },
        )
        await producer.send_and_wait(
            _topic_profile_updated(),
            {
                "event_type": _topic_profile_updated(),
                "payload": {
                    "user_id": candidate_id,
                    "bio": "Hiking is my favorite weekend activity",
                    "search_for": "new friends for outdoor activities",
                    "birthday": 946684800,  # 2000-01-01
                    "gender": "FEMALE",
                    "relationship_type": "FRIENDSHIP",
                    "city": "TestTown",
                    "sign": "aries",
                    "tags": ["hiking"],
                },
            },
        )
    finally:
        await producer.stop()

    deadline = time.time() + 25
    async with grpc.aio.insecure_channel(_grpc_target()) as channel:
        stub = recommendation_pb2_grpc.RecommendationServiceStub(channel)

        while time.time() < deadline:
            resp = await stub.GetRecommendationsForUser(
                recommendation_pb2.GetRecommendationsForUserRequest(user_id=viewer_id)
            )
            if candidate_id in resp.candidate_user_ids:
                return
            await asyncio.sleep(1.0)

    pytest.fail("candidate did not appear in recommendations within timeout")

