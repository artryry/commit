"""Tests for recommendation stack rebuild (filters + ranking)."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from services.recommendation_service import RecommendationService


@pytest.mark.asyncio
async def test_rebuild_stack_includes_candidate_when_filter_relationship_type_is_zero():
    """DB may store SEARCH_FOR_UNSPECIFIED as 0; candidate must still enter the Redis stack."""
    users = AsyncMock()
    filters = AsyncMock()
    tags = AsyncMock()
    seen = AsyncMock()
    stack = AsyncMock()

    viewer = MagicMock()
    viewer.user_id = 2
    viewer.search_for_vector = None

    cand = MagicMock()
    cand.user_id = 1
    cand.bio_vector = None

    users.get.return_value = viewer
    users.list_except.return_value = [cand]

    filt = MagicMock()
    filt.relationship_type = 0
    filt.age_from = None
    filt.age_to = None
    filt.city = None
    filt.sign = None
    filt.partner_gender = None
    filters.get.return_value = filt

    tags.filter_tag_names_for_user.return_value = []
    seen.exists.return_value = False

    svc = RecommendationService(users, filters, tags, seen, stack)
    await svc.rebuild_stack(2)

    stack.rebuild.assert_called_once_with(2, [1])


@pytest.mark.asyncio
async def test_rebuild_stack_empty_when_viewer_missing():
    users = AsyncMock()
    filters = AsyncMock()
    tags = AsyncMock()
    seen = AsyncMock()
    stack = AsyncMock()
    users.get.return_value = None

    svc = RecommendationService(users, filters, tags, seen, stack)
    await svc.rebuild_stack(99)

    stack.rebuild.assert_not_called()


@pytest.mark.asyncio
async def test_pop_recommendations_does_not_mark_seen():
    """Seen pairs are written only from swipe.created → record_swipe_pair, not when returning ids."""
    users = AsyncMock()
    filters = AsyncMock()
    filters.ensure_row = AsyncMock()
    filters.get = AsyncMock(return_value=None)
    tags = AsyncMock()
    tags.filter_tag_names_for_user = AsyncMock(return_value=[])
    seen = AsyncMock()
    stack = AsyncMock()
    stack.rpop_id = AsyncMock(side_effect=[42, None, None])

    svc = RecommendationService(users, filters, tags, seen, stack)
    svc.rebuild_stack = AsyncMock()

    out, _, _ = await svc.pop_recommendations(1, 25)

    assert out == [42]
    seen.insert_ignore.assert_not_called()


@pytest.mark.asyncio
async def test_set_filters_rebuilds_stack_without_touching_seen():
    users = AsyncMock()
    filters = AsyncMock()
    filters.ensure_row = AsyncMock(return_value=MagicMock())
    filters.apply_fields = AsyncMock()
    tags = AsyncMock()
    tags.replace_filter_tags = AsyncMock()
    seen = AsyncMock()
    stack = AsyncMock()

    svc = RecommendationService(users, filters, tags, seen, stack)
    svc.rebuild_stack = AsyncMock()

    await svc.set_filters(2, None, None, None, None, None, None, [])

    seen.delete_where_viewer.assert_not_called()
    stack.delete_stack.assert_awaited_once_with(2)
    svc.rebuild_stack.assert_awaited_once_with(2)
