from datetime import datetime, timezone
from typing import Optional


class AgeCalculator:
    @staticmethod
    def from_birthday_unix(ts: int) -> int:
        bd = datetime.fromtimestamp(ts, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        years = now.year - bd.year
        if (now.month, now.day) < (bd.month, bd.day):
            years -= 1
        return years

    @staticmethod
    def from_birthday_unix_for_filter(ts: int) -> Optional[int]:
        """Age in years for filter logic; None if timestamp is unusable or out of sane range."""
        try:
            bd = datetime.fromtimestamp(int(ts), tz=timezone.utc)
        except (OSError, OverflowError, ValueError):
            return None
        now = datetime.now(timezone.utc)
        years = now.year - bd.year
        if (now.month, now.day) < (bd.month, bd.day):
            years -= 1
        if years < 0 or years > 150:
            return None
        return years
