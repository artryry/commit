import grpc
from grpc import aio

from config.settings import settings
from db.session import async_session_maker
from services.factory import build_recommendation_service
from transport.grpc.grpc_mapper import GrpcRecommendationMapper
from transport.grpc.proto.gen import recommendation_pb2, recommendation_pb2_grpc


class RecommendationGrpcHandler(recommendation_pb2_grpc.RecommendationServiceServicer):
    def __init__(self, redis_client, session_factory):
        self._redis = redis_client
        self._session_factory = session_factory

    async def GetRecommendationsForUser(self, request, context):
        async with self._session_factory() as session:
            try:
                svc = build_recommendation_service(session, self._redis)
                ids, filt, tags = await svc.pop_recommendations(request.user_id, settings.RECOMMENDATIONS_BATCH_SIZE)
                await session.commit()
                return GrpcRecommendationMapper.fill_get_recommendations(filt, tags, ids)
            except Exception as exc:
                await session.rollback()
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(exc))
                return recommendation_pb2.GetRecommendationsForUserResponse()

    async def GetFilters(self, request, context):
        async with self._session_factory() as session:
            try:
                svc = build_recommendation_service(session, self._redis)
                filt, tags = await svc.get_filter_bundle(request.user_id)
                await session.commit()
                return GrpcRecommendationMapper.fill_get_filters(filt, tags)
            except Exception as exc:
                await session.rollback()
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(exc))
                return recommendation_pb2.GetFiltersResponse()

    async def SetFilters(self, request, context):
        async with self._session_factory() as session:
            try:
                svc = build_recommendation_service(session, self._redis)
                rt = request.relationship_type if request.HasField("relationship_type") else None
                af = request.age_from if request.HasField("age_from") else None
                at = request.age_to if request.HasField("age_to") else None
                city = request.city if request.HasField("city") else None
                sign = request.sign if request.HasField("sign") else None
                pg = request.partner_gender if request.HasField("partner_gender") else None
                await svc.set_filters(
                    request.user_id,
                    rt,
                    af,
                    at,
                    city,
                    sign,
                    pg,
                    request.tags,
                )
                await session.commit()
                return recommendation_pb2.SetFiltersResponse(success=True)
            except Exception as exc:
                await session.rollback()
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(exc))
                return recommendation_pb2.SetFiltersResponse(success=False)


async def create_and_start_grpc_server(redis_client) -> aio.Server:
    server = aio.server()
    handler = RecommendationGrpcHandler(redis_client, async_session_maker)
    recommendation_pb2_grpc.add_RecommendationServiceServicer_to_server(handler, server)
    addr = f"{settings.GRPC_HOST}:{settings.GRPC_PORT}"
    server.add_insecure_port(addr)
    await server.start()
    return server
