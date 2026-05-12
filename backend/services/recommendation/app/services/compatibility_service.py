import json
import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from db.models import UserFeature
from repositories.user_feature_repository import SqlUserFeatureRepository
from services.ollama_client import OllamaClient

logger = logging.getLogger(__name__)

# One JSON object per call — works with Ollama `format: "json"` (see OllamaClient.chat_json_array).
_SYSTEM_PROMPT = (
    "Текст о совместимости по знаку зодиака (солнце) и дате рождения — не полная натальная карта, "
    "без категоричных предсказаний. Напиши **7–10 полноценных предложений** на русском, тон тёплый и лёгкий. "
    'Верни один JSON-объект строго вида {"user_id": <целое число как во входе>, "text": "<строка>"}. '
    "Поле text — только русский; названия знаков по-русски (Овен, Телец, Близнецы, …). "
    "Число user_id должно совпадать с полем user_id во входном JSON."
)


def _birthday_label(ts: int) -> str:
    try:
        dt = datetime.fromtimestamp(int(ts), tz=timezone.utc)
        return dt.date().isoformat()
    except (OSError, OverflowError, ValueError):
        return "unknown"


def _normalize_other_ids(viewer_id: int, raw_ids: list[int]) -> list[int]:
    seen: set[int] = set()
    out: list[int] = []
    for uid in raw_ids:
        try:
            i = int(uid)
        except (TypeError, ValueError):
            continue
        if i == viewer_id:
            continue
        if i in seen:
            continue
        seen.add(i)
        out.append(i)
        if len(out) >= settings.COMPATIBILITY_MAX_IDS:
            break
    return out


def _row_user_id(raw: object) -> int | None:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, int):
        return raw
    if isinstance(raw, float):
        return int(raw)
    if isinstance(raw, str) and raw.strip():
        s = raw.strip()
        if s.isdigit() or (s.startswith("-") and s[1:].isdigit()):
            try:
                return int(s)
            except ValueError:
                return None
    try:
        return int(raw)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _feature_snapshot(uf: UserFeature) -> dict:
    return {
        "sign": (uf.sign or "").strip() or "unknown",
        "birth_date": _birthday_label(uf.birthday),
    }


class CompatibilityService:
    def __init__(self, session: AsyncSession, ollama: OllamaClient | None = None):
        self._session = session
        self._repo = SqlUserFeatureRepository(session)
        self._ollama = ollama or OllamaClient()

    async def build_texts(self, viewer_user_id: int, other_user_ids: list[int]) -> list[tuple[int, str]]:
        default = settings.COMPATIBILITY_DEFAULT_TEXT
        ordered = _normalize_other_ids(viewer_user_id, other_user_ids)
        if not ordered:
            return []

        viewer = await self._repo.get(viewer_user_id)
        others_map = await self._repo.get_many(ordered)

        if viewer is None:
            return [(uid, default) for uid in ordered]

        viewer_snap = _feature_snapshot(viewer)
        texts_by_id: dict[int, str] = {}
        for uid in ordered:
            if uid not in others_map:
                texts_by_id[uid] = default

        pairs_for_model: list[dict] = []
        for uid in ordered:
            other = others_map.get(uid)
            if other is None:
                continue
            pairs_for_model.append(
                {
                    "user_id": uid,
                    "viewer": viewer_snap,
                    "other": _feature_snapshot(other),
                },
            )

        # One Ollama request per pair: avoids truncation, improves JSON validity (especially with format=json).
        predict = settings.COMPATIBILITY_NUM_PREDICT
        timeout = float(settings.OLLAMA_TIMEOUT_SEC)
        for pair in pairs_for_model:
            uid = int(pair["user_id"])
            user_msg = json.dumps(pair, ensure_ascii=False)
            try:
                rows = await self._ollama.chat_json_array(
                    _SYSTEM_PROMPT,
                    user_msg,
                    options={
                        "num_predict": predict,
                        "temperature": 0.35,
                        "top_k": 40,
                    },
                    timeout_sec=timeout,
                    format_json=True,
                )
                matched = False
                for row in rows:
                    got_uid = _row_user_id(row.get("user_id"))
                    text = row.get("text")
                    if got_uid == uid and isinstance(text, str) and text.strip():
                        texts_by_id[uid] = text.strip()
                        matched = True
                        break
                if not matched:
                    logger.warning(
                        "compatibility: no valid object for user_id=%s (parsed %s row(s))",
                        uid,
                        len(rows),
                    )
            except Exception:
                logger.exception("ollama compatibility failed for user_id=%s", uid)

        out: list[tuple[int, str]] = []
        for uid in ordered:
            out.append((uid, texts_by_id.get(uid, default)))
        return out
