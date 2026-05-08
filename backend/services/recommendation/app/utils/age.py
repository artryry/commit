from datetime import datetime, timezone


class AgeCalculator:
    @staticmethod
    def from_birthday_unix(ts: int) -> int:
        bd = datetime.fromtimestamp(ts, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        years = now.year - bd.year
        if (now.month, now.day) < (bd.month, bd.day):
            years -= 1
        return years
