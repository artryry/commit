import grpc
from grpc import aio

from config.settings import settings
from db.session import async_session_maker
from services.compatibility_service import CompatibilityService
from services.factory import build_recommendation_service
from transport.grpc.grpc_mapper import GrpcRecommendationMapper
from transport.grpc.proto.gen import profile_pb2, recommendation_pb2, recommendation_pb2_grpc


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

    async def GetCompatibilityTexts(self, request, context):
        async with self._session_factory() as session:
            try:
                svc = CompatibilityService(session)
                pairs = await svc.build_texts(
                    int(request.viewer_user_id),
                    list(request.other_user_ids),
                )
                resp = recommendation_pb2.GetCompatibilityTextsResponse()
                for uid, text in pairs:
                    item = resp.items.add()
                    item.user_id = uid
                    item.text = text
                await session.commit()
                return resp
            except Exception as exc:
                await session.rollback()
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(exc))
                return recommendation_pb2.GetCompatibilityTextsResponse()

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
                # Treat UNSPECIFIED / zero ages / blank strings as "no filter" (clear column). Partner gender 0 is MALE — never map to None.
                rt = None
                if request.HasField("relationship_type"):
                    if request.relationship_type != profile_pb2.SEARCH_FOR_UNSPECIFIED:
                        rt = int(request.relationship_type)
                af = None
                if request.HasField("age_from") and request.age_from != 0:
                    af = int(request.age_from)
                at = None
                if request.HasField("age_to") and request.age_to != 0:
                    at = int(request.age_to)
                city = None
                if request.HasField("city"):
                    c = (request.city or "").strip()
                    if c:
                        city = c
                sign = None
                if request.HasField("sign"):
                    s = (request.sign or "").strip()
                    if s:
                        sign = s
                pg = int(request.partner_gender) if request.HasField("partner_gender") else None
                tag_names = [t.strip() for t in request.tags if t and t.strip()]
                await svc.set_filters(
                    request.user_id,
                    rt,
                    af,
                    at,
                    city,
                    sign,
                    pg,
                    tag_names,
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
