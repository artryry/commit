from typing import List, Optional

from db.models import UserFeature, UserFilter
from repositories import ITagRepository
from utils.age import AgeCalculator
from utils.vectors import VectorMath

# profile.v1.RelationshipType SEARCH_FOR_UNSPECIFIED — treat as "no relationship filter" (same as NULL).
_RELATIONSHIP_UNSPECIFIED = 0


class CandidateRules:
    @staticmethod
    def gender_ok_for_relationship(viewer: UserFeature, filt: Optional[UserFilter], cand: UserFeature) -> bool:
        if filt is None:
            return True
        # Partner gender from filters applies whenever set (not only for relationship-type search).
        if filt.partner_gender is not None:
            return cand.gender == filt.partner_gender
        rt = filt.relationship_type
        if rt is None or rt == _RELATIONSHIP_UNSPECIFIED or rt != 2:
            return True
        # Relationship search without explicit partner gender: infer opposite from viewer.
        if viewer.gender == 0:
            return cand.gender == 1
        if viewer.gender == 1:
            return cand.gender == 0
        return True

    @staticmethod
    async def matches(
        viewer: UserFeature,
        filt: Optional[UserFilter],
        filter_tag_names: List[str],
        cand: UserFeature,
        tags: ITagRepository,
    ) -> bool:
        if filt is None:
            return True

        want_rt = filt.relationship_type
        if (
            want_rt is not None
            and want_rt != _RELATIONSHIP_UNSPECIFIED
            and cand.relationship_type != want_rt
        ):
            return False

        age = AgeCalculator.from_birthday_unix_for_filter(cand.birthday)
        if age is not None:
            if filt.age_from is not None and age < filt.age_from:
                return False
            if filt.age_to is not None and age > filt.age_to:
                return False

        if filt.city and filt.city.lower() not in (cand.city or "").lower():
            return False

        if filt.sign and filt.sign.lower() not in (cand.sign or "").lower():
            return False

        if not CandidateRules.gender_ok_for_relationship(viewer, filt, cand):
            return False

        if filter_tag_names:
            return await tags.user_has_any_of_tags(cand.user_id, filter_tag_names)
        return True


class StackRanker:
    @staticmethod
    def score_pair(viewer: UserFeature, cand: UserFeature) -> float:
        if viewer.search_for_vector is None or cand.bio_vector is None:
            return 0.0
        return VectorMath.cosine(viewer.search_for_vector, cand.bio_vector)
