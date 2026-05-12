"""Ручной вызов Ollama — как CompatibilityService: одна пара за запрос, format=json.

Запуск из каталога `services/recommendation`:
  pip install httpx
  python scripts/manual_ollama_compat.py

Переменные: OLLAMA_BASE_URL (по умолчанию http://127.0.0.1:11434), OLLAMA_MODEL (по умолчанию qwen2.5:3b).

При 502 на localhost попробуйте 127.0.0.1 или проверьте, что контейнер Ollama слушает порт 11434.
"""
import json
import os
import sys

import httpx

BASE = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:3b")
NUM_PREDICT = int(os.environ.get("COMPATIBILITY_NUM_PREDICT", "4096"))

_SYSTEM_PROMPT = (
    "Текст о совместимости по знаку зодиака и дате рождения. "
    "7–10 предложений на русском. "
    'Один JSON-объект: {"user_id": <int>, "text": "<строка>"}. '
    "user_id как во входе."
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
]


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    with httpx.Client(timeout=180.0, trust_env=False) as client:
        for pair in PAIRS:
            body = {
                "model": MODEL,
                "stream": False,
                "format": "json",
                "messages": [
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": json.dumps(pair, ensure_ascii=False)},
                ],
                "options": {
                    "num_predict": NUM_PREDICT,
                    "temperature": 0.35,
                    "top_k": 40,
                },
            }
            r = client.post(f"{BASE}/api/chat", json=body)
            r.raise_for_status()
            content = (r.json().get("message") or {}).get("content")
            print(content)
            print("---")


if __name__ == "__main__":
    try:
        main()
    except httpx.HTTPError as e:
        print(f"HTTP error: {e}", file=sys.stderr)
        sys.exit(1)
