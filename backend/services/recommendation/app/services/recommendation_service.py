from datetime import datetime, timezone
from typing import Iterable, List, Optional, Tuple

from config.settings import settings
from db.models import UserFeature, UserFilter
from repositories import (
    IRedisStackRepository,
    ISeenPairRepository,
    ITagRepository,
    IUserFeatureRepository,
    IUserFilterRepository,
)
from services.candidate_rules import CandidateRules, StackRanker
from utils.vectors import VectorMath


class RecommendationService:
    def __init__(
        self,
        users: IUserFeatureRepository,
        filters: IUserFilterRepository,
        tags: ITagRepository,
        seen: ISeenPairRepository,
        stack: IRedisStackRepository,
    ):
        self._users = users
        self._filters = filters
        self._tags = tags
        self._seen = seen
        self._stack = stack

    async def rebuild_stack(self, viewer_id: int) -> None:
        viewer = await self._users.get(viewer_id)
        if viewer is None:
            return

        filt = await self._filters.get(viewer_id)
        filter_tag_names = await self._tags.filter_tag_names_for_user(viewer_id)
        candidates = await self._users.list_except(viewer_id)
        scored: List[Tuple[float, int]] = []

        for cand in candidates:
            if cand.user_id == viewer_id:
                continue
            if await self._seen.exists(viewer_id, cand.user_id):
                continue
            if not await CandidateRules.matches(viewer, filt, filter_tag_names, cand, self._tags):
                continue
            scored.append((StackRanker.score_pair(viewer, cand), cand.user_id))

        scored.sort(key=lambda x: x[0], reverse=True)
        ids = [uid for _, uid in scored[: settings.STACK_PREFETCH_LIMIT]]
        await self._stack.rebuild(viewer_id, ids)

    async def pop_recommendations(self, viewer_id: int, batch: int) -> Tuple[List[int], Optional[UserFilter], List[str]]:
        now = datetime.now(timezone.utc)
        await self._filters.ensure_row(viewer_id, now)
        tag_names = await self._tags.filter_tag_names_for_user(viewer_id)

        out: List[int] = []
        while len(out) < batch:
            cid = await self._stack.rpop_id(viewer_id)
            if cid is None:
                await self.rebuild_stack(viewer_id)
                cid = await self._stack.rpop_id(viewer_id)
                if cid is None:
                    break
            if cid == viewer_id:
                continue
            out.append(cid)

        filt = await self._filters.get(viewer_id)
        names = await self._tags.filter_tag_names_for_user(viewer_id)
        return out, filt, names

    async def upsert_user_from_profile_event(
        self,
        *,
        user_id: int,
        bio: str,
        search_for: str,
        birthday: int,
        gender: int,
        sign: Optional[str],
        city: Optional[str],
        relationship_type: int,
        tag_names: List[str],
        bio_vec: List[float],
        search_vec: List[float],
        combined_vec: List[float],
    ) -> None:
        now = datetime.now(timezone.utc)
        uf = await self._users.get(user_id)
        if uf is None:
            uf = UserFeature(
                user_id=user_id,
                birthday=birthday,
                sign=sign,
                city=city,
                relationship_type=relationship_type,
                gender=gender,
                bio_vector=bio_vec,
                search_for_vector=search_vec,
                combined_vector=combined_vec,
                embedding_model=settings.EMBEDDING_MODEL_NAME,
                updated_at=now,
            )
            await self._users.add(uf)
        else:
            uf.birthday = birthday
            uf.sign = sign
            uf.city = city
            uf.relationship_type = relationship_type
            uf.gender = gender
            uf.bio_vector = bio_vec
            uf.search_for_vector = search_vec
            uf.combined_vector = combined_vec
            uf.embedding_model = settings.EMBEDDING_MODEL_NAME
            uf.updated_at = now
            await self._users.flush()

        await self._tags.replace_user_tags(user_id, tag_names)
        await self._filters.ensure_row(user_id, now)
        await self.rebuild_stack(user_id)

    async def delete_user(self, user_id: int) -> None:
        await self._seen.delete_involving(user_id)
        await self._users.delete(user_id)
        await self._stack.delete_stack(user_id)

    async def get_filter_bundle(self, user_id: int) -> Tuple[Optional[UserFilter], List[str]]:
        filt = await self._filters.get(user_id)
        tags = await self._tags.filter_tag_names_for_user(user_id)
        return filt, tags

    async def set_filters(
        self,
        user_id: int,
        relationship_type: Optional[int],
        age_from: Optional[int],
        age_to: Optional[int],
        city: Optional[str],
        sign: Optional[str],
        partner_gender: Optional[int],
        tag_names: Iterable[str],
    ) -> None:
        now = datetime.now(timezone.utc)
        row = await self._filters.ensure_row(user_id, now)
        await self._filters.apply_fields(
            row,
            relationship_type=relationship_type,
            age_from=age_from,
            age_to=age_to,
            city=city,
            sign=sign,
            partner_gender=partner_gender,
            now=now,
        )
        await self._tags.replace_filter_tags(user_id, list(tag_names))
        await self._stack.delete_stack(user_id)
        await self.rebuild_stack(user_id)

    async def record_swipe_pair(self, viewer_id: int, target_id: int) -> None:
        """Mark (viewer, target) as seen — only called from swipe.created consumer.

        GET /recommendations does not write seen_pairs; swipes do.
        """
        if viewer_id == target_id:
            return
        now = datetime.now(timezone.utc)
        await self._seen.insert_ignore(viewer_id, target_id, now)

    async def apply_swipe_search_nudge(self, viewer_id: int, target_id: int, liked: bool) -> None:
        """Optional tiny rotation of viewer `search_for_vector` toward target `bio_vector` after a like."""
        alpha = settings.SWIPE_SEARCH_NUDGE_ALPHA
        if alpha <= 0 or not liked:
            return
        viewer = await self._users.get(viewer_id)
        target = await self._users.get(target_id)
        if viewer is None or target is None:
            return
        if viewer.search_for_vector is None or target.bio_vector is None:
            return
        new_sf = VectorMath.lerp_unit(viewer.search_for_vector, target.bio_vector, alpha)
        await self._users.update_search_for_vector(viewer_id, new_sf)
