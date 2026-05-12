"""Unit tests for recommendation candidate matching rules."""

import pytest

from services.candidate_rules import CandidateRules
from utils.age import AgeCalculator


def _feature(
    user_id: int,
    *,
    birthday: int,
    gender: int = 0,
    relationship_type: int = 1,
    city: str = "X",
    sign: str = "y",
):
    from types import SimpleNamespace

    return SimpleNamespace(
        user_id=user_id,
        birthday=birthday,
        gender=gender,
        relationship_type=relationship_type,
        city=city,
        sign=sign,
    )


@pytest.mark.asyncio
async def test_partner_gender_applies_without_relationship_filter_on_row():
    """Partner gender must apply even when relationship_type filter is unset."""
    viewer = _feature(1, birthday=946684800, gender=1, relationship_type=1)
    cand = _feature(2, birthday=946684800, gender=1, relationship_type=1)
    filt = type("F", (), {})()
    filt.relationship_type = None
    filt.age_from = None
    filt.age_to = None
    filt.city = None
    filt.sign = None
    filt.partner_gender = 0  # MALE

    class DummyTags:
        async def user_has_any_of_tags(self, user_id, names):
            return True

    ok = await CandidateRules.matches(viewer, filt, [], cand, DummyTags())
    assert ok is False


@pytest.mark.asyncio
async def test_partner_gender_male_allows_male_candidate():
    viewer = _feature(1, birthday=946684800, gender=1, relationship_type=1)
    cand = _feature(2, birthday=946684800, gender=0, relationship_type=1)
    filt = type("F", (), {})()
    filt.relationship_type = None
    filt.age_from = None
    filt.age_to = 100
    filt.city = None
    filt.sign = None
    filt.partner_gender = 0

    class DummyTags:
        async def user_has_any_of_tags(self, user_id, names):
            return True

    ok = await CandidateRules.matches(viewer, filt, [], cand, DummyTags())
    assert ok is True


def test_age_filter_skips_unusable_birthday():
    assert AgeCalculator.from_birthday_unix_for_filter(10**15) is None
