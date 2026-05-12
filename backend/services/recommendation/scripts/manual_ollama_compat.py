"""Ручной вызов Ollama — несколько пар, русские тексты (как в CompatibilityService).

Запуск из каталога `services/recommendation`:
  pip install httpx
  python scripts/manual_ollama_compat.py

Переменные: OLLAMA_BASE_URL (по умолчанию http://127.0.0.1:11434), OLLAMA_MODEL (по умолчанию llama3.2:1b).

При 502 на localhost попробуйте 127.0.0.1 или проверьте, что контейнер Ollama слушает порт 11434.
"""
import json
import os
import sys

import httpx

BASE = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")

# Как в app/services/compatibility_service.py
_SYSTEM_PROMPT = (
    "Развлекательный текст о совместимости по знаку зодиака и дате рождения. "
    "На каждую пару — **7–10 полноценных предложений** на русском. "
    'Ответ — только JSON-массив [{"user_id":число,"text":"строка"},...]. '
    "Текст text — только русский; знаки по-русски. Без markdown вне JSON."
)

PAIRS = [
    {
        "user_id": 101,
        "viewer": {"sign": "Leo", "birth_date": "1990-08-01"},
        "other": {"sign": "Aquarius", "birth_date": "1992-02-03"},
    },
    {
        "user_id": 102,
        "viewer": {"sign": "Leo", "birth_date": "1990-08-01"},
        "other": {"sign": "Scorpio", "birth_date": "1988-11-12"},
    },
    {
        "user_id": 103,
        "viewer": {"sign": "Leo", "birth_date": "1990-08-01"},
        "other": {"sign": "Gemini", "birth_date": "1995-06-20"},
    },
]


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    n = len(PAIRS)
    user_msg = f"Ровно {n} объектов. Только JSON.\n" + json.dumps(PAIRS, ensure_ascii=False)
    body = {
        "model": MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        "options": {"num_predict": 12288, "temperature": 0.3, "top_k": 32},
    }
    try:
        # trust_env=False — иначе HTTP(S)_PROXY может отправить localhost на прокси → 502.
        with httpx.Client(timeout=180.0, trust_env=False) as client:
            r = client.post(f"{BASE}/api/chat", json=body)
        r.raise_for_status()
    except httpx.HTTPError as e:
        print(f"HTTP error: {e}", file=sys.stderr)
        sys.exit(1)

    data = r.json()
    content = (data.get("message") or {}).get("content")
    if not content:
        print("empty message", data, file=sys.stderr)
        sys.exit(1)

    raw = content.strip()
    if raw.startswith("```"):
        raw = raw.removeprefix("```json").removeprefix("```").strip()
        if raw.endswith("```"):
            raw = raw[: raw.rfind("```")].strip()

    parsed = json.loads(raw)
    if isinstance(parsed, dict):
        if "items" in parsed:
            parsed = parsed["items"]
        elif "data" in parsed:
            parsed = parsed["data"]

    # как OllamaClient: один объект → список
    if isinstance(parsed, dict) and "user_id" in parsed and "text" in parsed:
        parsed = [parsed]

    if not isinstance(parsed, list):
        print("unexpected shape:", parsed, file=sys.stderr)
        sys.exit(1)

    print(json.dumps(parsed, ensure_ascii=False, indent=2))
    if len(parsed) != n:
        print(f"warning: ожидалось {n} объектов, пришло {len(parsed)}", file=sys.stderr)


if __name__ == "__main__":
    main()
