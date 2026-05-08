from dataclasses import dataclass
from typing import Any, List, Optional


class RelationshipMapping:
    _MAP = {
        "UNSPECIFIED": 0,
        "SEARCH_FOR_UNSPECIFIED": 0,
        "FRIENDSHIP": 1,
        "SEARCH_FOR_FRIENDSHIP": 1,
        "RELATIONSHIP": 2,
        "SEARCH_FOR_RELATIONSHIP": 2,
        "NETWORKING": 3,
        "SEARCH_FOR_NETWORKING": 3,
    }

    @staticmethod
    def from_payload(value: Optional[str]) -> int:
        if not value:
            return 0
        return RelationshipMapping._MAP.get(str(value).strip().upper(), 0)


class GenderMapping:
    @staticmethod
    def from_payload(value: Optional[str]) -> int:
        if not value:
            return 0
        v = str(value).strip().upper()
        if v in ("F", "FEMALE"):
            return 1
        return 0


@dataclass(frozen=True)
class ParsedProfile:
    user_id: int
    bio: str
    search_for: str
    birthday: int
    sign: Optional[str]
    city: Optional[str]
    relationship_type: int
    gender: int
    tags: List[str]


class ProfilePayloadParser:
    @staticmethod
    def parse(payload: dict[str, Any]) -> ParsedProfile:
        uid = int(payload["user_id"])
        bio = str(payload.get("bio") or "")
        search_for = str(payload.get("search_for") or "")
        birthday = int(payload["birthday"])
        sign = payload.get("sign")
        city = payload.get("city")
        raw_tags = payload.get("tags") or []
        if isinstance(raw_tags, str):
            raw_tags = [raw_tags]
        tags = [str(t).strip() for t in raw_tags if str(t).strip()]
        return ParsedProfile(
            user_id=uid,
            bio=bio,
            search_for=search_for,
            birthday=birthday,
            sign=sign,
            city=city,
            relationship_type=RelationshipMapping.from_payload(payload.get("relationship_type")),
            gender=GenderMapping.from_payload(payload.get("gender")),
            tags=tags,
        )
