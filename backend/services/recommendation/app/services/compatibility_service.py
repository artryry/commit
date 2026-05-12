import json
import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from db.models import UserFeature
from repositories.user_feature_repository import SqlUserFeatureRepository
from services.ollama_client import OllamaClient

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "Развлекательный текст о совместимости по знаку зодиака (солнце) и дате рождения — не полная натальная карта, "
    "без категоричных предсказаний. На каждую пару из входа напиши **7–10 полноценных предложений** на русском, "
    "тон тёплый и лёгкий. "
    'Ответ — только JSON-массив вида [{"user_id":число,"text":"строка"},...] по всем user_id из входа. '
    "Поле text — только русский; названия знаков по-русски (Овен, Телец, …). Без markdown, кода и текста вне JSON."
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

        texts_by_id: dict[int, str] = {}
        for uid in ordered:
            if uid not in others_map:
                texts_by_id[uid] = default

        if pairs_for_model:
            n = len(pairs_for_model)
            user_msg = (
                f"Ровно {n} объектов в массиве. Только JSON.\n"
                + json.dumps(pairs_for_model, ensure_ascii=False)
            )
            try:
                rows = await self._ollama.chat_json_array(
                    _SYSTEM_PROMPT,
                    user_msg,
                    options={
                        "num_predict": 12288,
                        "temperature": 0.3,
                        "top_k": 32,
                    },
                    timeout_sec=float(settings.OLLAMA_TIMEOUT_SEC),
                )
                for row in rows:
                    uid = _row_user_id(row.get("user_id"))
                    text = row.get("text")
                    if uid is not None and isinstance(text, str) and text.strip():
                        texts_by_id[uid] = text.strip()
            except Exception:
                logger.exception("ollama compatibility generation failed")

        out: list[tuple[int, str]] = []
        for uid in ordered:
            out.append((uid, texts_by_id.get(uid, default)))
        return out
