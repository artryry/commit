import json
import logging
import re
from typing import Any

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)


class OllamaClient:
    """Local Ollama HTTP API (`/api/chat`). Single model, single request — no fallbacks or retries."""

    def __init__(self) -> None:
        self._base = settings.OLLAMA_BASE_URL.rstrip("/")
        self._model = settings.OLLAMA_MODEL
        self._timeout = settings.OLLAMA_TIMEOUT_SEC

    @staticmethod
    def _strip_code_fences(raw: str) -> str:
        s = raw.strip()
        if s.startswith("```"):
            s = s.removeprefix("```json").removeprefix("```").strip()
            if s.endswith("```"):
                s = s[: s.rfind("```")].strip()
        return s

    @staticmethod
    def _normalize_parsed(parsed: Any) -> list[dict[str, Any]]:
        if isinstance(parsed, dict):
            if "items" in parsed:
                parsed = parsed["items"]
            elif "data" in parsed:
                parsed = parsed["data"]
            elif "user_id" in parsed and "text" in parsed:
                parsed = [parsed]
        if isinstance(parsed, list):
            return [x for x in parsed if isinstance(x, dict)]
        return []

    @staticmethod
    def _slice_to_json_start(raw: str) -> str:
        """Drop JS/markdown before the first JSON array or compatibility object."""
        s = raw.strip()
        for pat in (
            r"\[\s*\{",
            r"\{\s*\"user_id\"\s*:",
            r"\{\s*'user_id'\s*:",
        ):
            m = re.search(pat, s)
            if m:
                return s[m.start() :]
        return s

    def _try_raw_decode_sequence(self, raw: str) -> list[dict[str, Any]]:
        """Parse one or more JSON values glued together: {...}{...} or NDJSON (decoder advances)."""
        dec = json.JSONDecoder()
        idx = 0
        s = raw.strip()
        out: list[dict[str, Any]] = []
        while idx < len(s):
            while idx < len(s) and s[idx] in " \t\n\r,":
                idx += 1
            if idx >= len(s):
                break
            try:
                obj, end = dec.raw_decode(s, idx)
            except json.JSONDecodeError:
                break
            idx = end
            if isinstance(obj, list):
                for item in obj:
                    if isinstance(item, dict) and "user_id" in item and "text" in item:
                        out.append(item)
                if out:
                    return out
                continue
            if isinstance(obj, dict) and "user_id" in obj and "text" in obj:
                out.append(obj)
                continue
        return out

    def _try_ndjson_lines(self, raw: str) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        dec = json.JSONDecoder()
        for line in raw.splitlines():
            line = line.strip().rstrip(",").strip()
            if not line or line.startswith("//"):
                continue
            try:
                obj, _ = dec.raw_decode(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and "user_id" in obj and "text" in obj:
                out.append(obj)
        return out

    def _try_glued_objects(self, raw: str) -> list[dict[str, Any]]:
        """Parse sequences like {...}{...} without commas (common LLM mistake)."""
        if "}{" not in raw:
            return []
        parts = raw.split("}{")
        if len(parts) < 2:
            return []
        out: list[dict[str, Any]] = []
        for i, p in enumerate(parts):
            if i == 0:
                piece = p + "}"
            elif i == len(parts) - 1:
                piece = "{" + p
                if not piece.rstrip().endswith("}"):
                    piece += "}"
            else:
                piece = "{" + p + "}"
            piece = piece.strip()
            try:
                obj = json.loads(piece)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and "user_id" in obj and "text" in obj:
                out.append(obj)
        return out

    def _parse_content_string(self, raw_in: str) -> list[dict[str, Any]]:
        raw = self._strip_code_fences(raw_in)
        if not raw:
            return []

        try:
            v = json.loads(raw)
            got = self._normalize_parsed(v)
            if got:
                return got
        except json.JSONDecodeError:
            pass

        lb, rb = raw.find("["), raw.rfind("]")
        if lb != -1 and rb > lb:
            try:
                v = json.loads(raw[lb : rb + 1])
                got = self._normalize_parsed(v)
                if got:
                    return got
            except json.JSONDecodeError:
                pass

        for chunk in (raw, self._slice_to_json_start(raw)):
            seq = self._try_raw_decode_sequence(chunk)
            if seq:
                return seq

        nd = self._try_ndjson_lines(raw)
        if nd:
            return nd

        glued = self._try_glued_objects(raw)
        if glued:
            return glued

        logger.warning("ollama JSON parse failed, snippet=%s", raw[:500])
        return []

    def _parse_chat_body(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        content = (data.get("message") or {}).get("content")
        if not content:
            logger.warning("ollama empty content: %s", data)
            return []
        if isinstance(content, str):
            return self._parse_content_string(content)
        return self._normalize_parsed(content)

    async def chat_json_array(
        self,
        system: str,
        user: str,
        *,
        options: dict[str, Any] | None = None,
        timeout_sec: float | None = None,
        format_json: bool = False,
    ) -> list[dict[str, Any]]:
        url = f"{self._base}/api/chat"
        model = (self._model or "").strip()
        if not model:
            raise RuntimeError("OLLAMA_MODEL is empty")

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        timeout = self._timeout if timeout_sec is None else timeout_sec
        payload: dict[str, Any] = {"model": model, "stream": False, "messages": messages}
        if options:
            payload["options"] = options
        if format_json:
            # Ollama: constrain decoder to JSON (much more reliable than prompt-only JSON).
            payload["format"] = "json"

        async with httpx.AsyncClient(timeout=timeout, trust_env=False) as client:
            resp = await client.post(url, json=payload)

        if resp.status_code >= 400:
            body = (resp.text or "").strip()[:2000]
            logger.error(
                "ollama HTTP %s %s model=%r body=%s",
                resp.status_code,
                url,
                model,
                body or "(empty)",
            )
            resp.raise_for_status()

        return self._parse_chat_body(resp.json())
