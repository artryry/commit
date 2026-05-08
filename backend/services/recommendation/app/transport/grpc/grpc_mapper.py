from typing import Optional, Sequence

from db.models import UserFilter
from transport.grpc.proto.gen import recommendation_pb2


class GrpcRecommendationMapper:
    """Build protobuf messages from domain rows."""

    @staticmethod
    def filter_to_proto_dict(filt: Optional[UserFilter], tag_names: Sequence[str]) -> dict:
        if filt is None:
            return {
                "relationship_type": None,
                "age_from": None,
                "age_to": None,
                "city": None,
                "sign": None,
                "partner_gender": None,
                "tags": list(tag_names),
            }
        return {
            "relationship_type": filt.relationship_type,
            "age_from": filt.age_from,
            "age_to": filt.age_to,
            "city": filt.city,
            "sign": filt.sign,
            "partner_gender": filt.partner_gender,
            "tags": list(tag_names),
        }

    @staticmethod
    def fill_get_recommendations(
        filt: Optional[UserFilter],
        tag_names: Sequence[str],
        ids: list[int],
    ) -> recommendation_pb2.GetRecommendationsForUserResponse:
        resp = recommendation_pb2.GetRecommendationsForUserResponse()
        resp.candidate_user_ids.extend(ids)
        data = GrpcRecommendationMapper.filter_to_proto_dict(filt, tag_names)
        if data["relationship_type"] is not None:
            resp.relationship_type = int(data["relationship_type"])
        if data["age_from"] is not None:
            resp.age_from = int(data["age_from"])
        if data["age_to"] is not None:
            resp.age_to = int(data["age_to"])
        if data["city"]:
            resp.city = data["city"]
        if data["sign"]:
            resp.sign = data["sign"]
        if data["partner_gender"] is not None:
            resp.partner_gender = int(data["partner_gender"])
        resp.tags.extend(data["tags"])
        return resp

    @staticmethod
    def fill_get_filters(
        filt: Optional[UserFilter],
        tag_names: Sequence[str],
    ) -> recommendation_pb2.GetFiltersResponse:
        resp = recommendation_pb2.GetFiltersResponse()
        data = GrpcRecommendationMapper.filter_to_proto_dict(filt, tag_names)
        if data["relationship_type"] is not None:
            resp.relationship_type = int(data["relationship_type"])
        if data["age_from"] is not None:
            resp.age_from = int(data["age_from"])
        if data["age_to"] is not None:
            resp.age_to = int(data["age_to"])
        if data["city"]:
            resp.city = data["city"]
        if data["sign"]:
            resp.sign = data["sign"]
        if data["partner_gender"] is not None:
            resp.partner_gender = int(data["partner_gender"])
        resp.tags.extend(data["tags"])
        return resp
