"""Generate Commit.postman_collection.json from api-gateway paths (single source of truth with openapi)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Commit.postman_collection.json"


def req(
    name: str,
    method: str,
    url: str,
    *,
    body: str | None = None,
    auth: str = "inherit",
    desc: str = "",
    formdata: list | None = None,
) -> dict:
    r: dict = {
        "name": name,
        "request": {
            "method": method,
            "header": [],
            "url": url,
        },
        "response": [],
    }
    if desc:
        r["request"]["description"] = desc
    if auth == "noauth":
        r["request"]["auth"] = {"type": "noauth"}
    if formdata is not None:
        r["request"]["body"] = {"mode": "formdata", "formdata": formdata}
    elif body is not None:
        r["request"]["header"] = [{"key": "Content-Type", "value": "application/json", "type": "text"}]
        r["request"]["body"] = {
            "mode": "raw",
            "raw": body,
            "options": {"raw": {"language": "json"}},
        }
    return r


def folder(name: str, items: list, desc: str = "") -> dict:
    f: dict = {"name": name, "item": items}
    if desc:
        f["description"] = desc
    return f


token_save_script = {
    "listen": "test",
    "script": {
        "exec": [
            "try {",
            "  const j = pm.response.json();",
            '  if (j.access_token) pm.environment.set("access_token", j.access_token);',
            '  if (j.refresh_token) pm.environment.set("refresh_token", j.refresh_token);',
            "} catch (e) { console.warn(e); }",
        ],
        "type": "text/javascript",
    },
}


def main() -> None:
    b = "{{base_url}}"
    gw = "{{gateway_url}}"
    wsb = "{{ws_base}}"
    peer = "{{peer_user_id}}"
    puid = "{{profile_user_id}}"

    items: list = []

    items.append(folder("Health", [req("GET /health", "GET", f"{gw}/health", auth="noauth")]))

    auth_items = [
        {
            **req(
                "POST /api/v1/auth/register",
                "POST",
                f"{b}/auth/register",
                body=json.dumps(
                    {"email": "user@example.com", "password": "Password123"},
                    indent=2,
                ),
                auth="noauth",
            ),
            "event": [token_save_script],
        },
        {
            **req(
                "POST /api/v1/auth/login",
                "POST",
                f"{b}/auth/login",
                body=json.dumps(
                    {"email": "user@example.com", "password": "Password123"},
                    indent=2,
                ),
                auth="noauth",
            ),
            "event": [token_save_script],
        },
        {
            **req(
                "POST /api/v1/auth/token (refresh)",
                "POST",
                f"{b}/auth/token",
                body='{\n  "refresh_token": "{{refresh_token}}"\n}',
                auth="noauth",
            ),
            "event": [token_save_script],
        },
        req(
            "POST /api/v1/auth/logout",
            "POST",
            f"{b}/auth/logout",
            body='{\n  "refresh_token": "{{refresh_token}}"\n}',
        ),
        req(
            "DELETE /api/v1/auth/me (delete account)",
            "DELETE",
            f"{b}/auth/me",
            body='{\n  "refresh_token": "{{refresh_token}}"\n}',
        ),
    ]
    items.append(
        folder(
            "Auth",
            auth_items,
            "OpenAPI: register, login, token, logout, delete account. Login/register/token tests save tokens to environment.",
        ),
    )

    profiles = [
        req("GET /api/v1/profiles/me", "GET", f"{b}/profiles/me"),
        req(
            "PUT /api/v1/profiles/me",
            "PUT",
            f"{b}/profiles/me",
            body=json.dumps({"username": "new_name", "bio": "Updated bio"}, indent=2),
        ),
        req(
            "POST /api/v1/profiles (create)",
            "POST",
            f"{b}/profiles",
            body=json.dumps(
                {
                    "username": "myusername",
                    "bio": "Hello",
                    "birthday": 946684800,
                    "gender": "MALE",
                    "relationship_type": "FRIENDSHIP",
                    "tags": ["music"],
                },
                indent=2,
            ),
        ),
        req(
            "GET /api/v1/profiles?ids=…",
            "GET",
            f"{b}/profiles?ids={{profile_ids_query}}",
        ),
        req("GET /api/v1/profiles/{user_id}", "GET", f"{b}/profiles/{puid}"),
        {
            "name": "POST /api/v1/profiles/images (multipart)",
            "request": {
                "method": "POST",
                "header": [],
                "body": {
                    "mode": "formdata",
                    "formdata": [
                        {
                            "key": "images",
                            "type": "file",
                            "src": [],
                            "description": "Preferred: multiple files",
                        },
                    ],
                },
                "url": f"{b}/profiles/images",
            },
            "response": [],
        },
        req(
            "DELETE /api/v1/profiles/images",
            "DELETE",
            f"{b}/profiles/images",
            body=json.dumps({"image_ids": [1]}, indent=2),
        ),
        req(
            "POST /api/v1/profiles/tags (attach)",
            "POST",
            f"{b}/profiles/tags",
            body=json.dumps({"tags": ["tag1", "tag2"]}, indent=2),
        ),
        req(
            "DELETE /api/v1/profiles/tags (detach)",
            "DELETE",
            f"{b}/profiles/tags",
            body=json.dumps({"tags": ["tag1"]}, indent=2),
        ),
    ]
    items.append(folder("Profiles", profiles))

    rec = [
        req("GET /api/v1/recommendations", "GET", f"{b}/recommendations"),
        req(
            "POST /api/v1/recommendations/compatibility",
            "POST",
            f"{b}/recommendations/compatibility",
            body=json.dumps({"user_ids": [2, 3]}, indent=2),
        ),
        req("GET /api/v1/recommendations/filters", "GET", f"{b}/recommendations/filters"),
        req(
            "POST /api/v1/recommendations/filters",
            "POST",
            f"{b}/recommendations/filters",
            body=json.dumps(
                {"relationship_type": "FRIENDSHIP", "city": "Berlin", "tags": ["art"]},
                indent=2,
            ),
        ),
    ]
    items.append(folder("Recommendations", rec))

    swipes = [
        req("GET /api/v1/swipes", "GET", f"{b}/swipes"),
        req(
            "POST /api/v1/swipes",
            "POST",
            f"{b}/swipes",
            body='{\n  "target_user_id": {{swipe_target_user_id}},\n  "liked": true\n}',
        ),
    ]
    items.append(folder("Swipes", swipes))

    items.append(folder("Matches", [req("GET /api/v1/matches", "GET", f"{b}/matches")]))

    notif_ws = {
        "name": "GET /api/v1/notifications/ws (WebSocket)",
        "request": {
            "method": "GET",
            "auth": {"type": "noauth"},
            "header": [],
            "url": f"{wsb}/api/v1/notifications/ws?token={{access_token}}",
            "description": "WebSocket per OpenAPI. Connect in Postman; use Messages tab.",
        },
        "response": [],
    }
    items.append(folder("Notifications", [notif_ws], "Single WebSocket path in OpenAPI."))

    chats = [
        req("GET /api/v1/chats", "GET", f"{b}/chats"),
        req("GET /api/v1/chats/{peer_user_id}", "GET", f"{b}/chats/{peer}"),
        req("DELETE /api/v1/chats/{peer_user_id}", "DELETE", f"{b}/chats/{peer}"),
        {
            "name": "GET /api/v1/chats/{peer_user_id}/ws (WebSocket)",
            "request": {
                "method": "GET",
                "auth": {"type": "noauth"},
                "header": [],
                "url": f"{wsb}/api/v1/chats/{peer}/ws?token={{access_token}}",
                "description": "Chat room WebSocket. Send e.g. {\"type\":\"text\",\"body\":\"hi\"}",
            },
            "response": [],
        },
        req(
            "POST /api/v1/chats/{peer_user_id}/messages (application/json)",
            "POST",
            f"{b}/chats/{peer}/messages",
            body='{\n  "body": "Hello from Postman"\n}',
        ),
        {
            "name": "POST /api/v1/chats/{peer_user_id}/messages (multipart/form-data)",
            "request": {
                "method": "POST",
                "header": [],
                "body": {
                    "mode": "formdata",
                    "formdata": [
                        {
                            "key": "body",
                            "type": "text",
                            "value": "optional caption",
                            "disabled": True,
                        },
                        {"key": "file", "type": "file", "src": []},
                    ],
                },
                "url": f"{b}/chats/{peer}/messages",
            },
            "response": [],
        },
    ]
    items.append(folder("Chats", chats))

    coll = {
        "info": {
            "_postman_id": "05512007-1c42-44f7-b653-3a591de4e26d",
            "name": "Commit API Gateway (OpenAPI)",
            "description": (
                "Generated from `api-gateway-openapi/openapi.yaml` paths. "
                "Use a Postman **Environment** so login/register can save `access_token` / `refresh_token`. "
                "WebSockets use `?token={{access_token}}` (no Bearer on WS). "
                "Re-run `python scripts/gen_postman_collection.py` after OpenAPI changes."
            ),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": items,
        "auth": {
            "type": "bearer",
            "bearer": [{"key": "token", "value": "{{access_token}}", "type": "string"}],
        },
        "variable": [
            {"key": "gateway_url", "value": "http://localhost:18000", "type": "string"},
            {"key": "base_url", "value": "http://localhost:18000/api/v1", "type": "string"},
            {"key": "ws_base", "value": "ws://localhost:18000", "type": "string"},
            {"key": "peer_user_id", "value": "2", "type": "string"},
            {"key": "profile_user_id", "value": "2", "type": "string"},
            {"key": "profile_ids_query", "value": "1,2", "type": "string"},
            {"key": "swipe_target_user_id", "value": "3", "type": "string"},
        ],
    }

    OUT.write_text(json.dumps(coll, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
