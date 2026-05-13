# Chats service

FastAPI service for 1:1 chats: Postgres persistence, MinIO for chat images, Kafka (`chat.message`, `chat.deleted`), and an in-memory **chat room** WebSocket registry.

Canonical HTTP API documentation for clients lives in the repo root **`api-gateway-openapi/openapi.yaml`** (paths under `/api/v1/chats/*`). This file describes behaviour the OpenAPI spec cannot fully express (WebSocket frames).

## Client flow (recommended)

1. **List chats:** `GET /api/v1/chats` (via API gateway + JWT).
2. **Open a thread:** `GET /api/v1/chats/{peer_user_id}` — returns `chat_id`, `peer_user_id`, and `messages[]`.
3. **Open the chat room WebSocket:** same host as REST, path `/api/v1/chats/{peer_user_id}/ws`, query **`token=<access_token>`** (browsers cannot set `Authorization` on WebSocket; the gateway accepts `?token=` and forwards `X-User-Id` to this service).
4. **Send while in the room:** send **JSON text frames** (see frame types below), or use **`POST /api/v1/chats/{peer_user_id}/messages`** (JSON or **multipart** for large images).
5. **Receive live messages:** the server pushes **`chat.new_message`** JSON on the chat WebSocket to every connected tab for that `(viewer, peer)` pair.

## WebSocket frames

### Server → client: `chat.new_message`

```json
{
  "type": "chat.new_message",
  "chat_id": "<uuid>",
  "message": {
    "id": "<uuid>",
    "sender_id": 1,
    "body": "hello",
    "image_storage_key": null,
    "created_at": "2026-01-01T12:00:00+00:00"
  }
}
```

The `message` object matches items in `GET /api/v1/chats/{peer_user_id}`.

### Client → server: text

```json
{ "type": "text", "body": "hello" }
```

### Client → server: image

```json
{
  "type": "image",
  "body": "optional caption",
  "image_base64": "<base64>",
  "content_type": "image/jpeg"
}
```

`content_type` is optional. If it is missing or `application/octet-stream`, the service infers JPEG/PNG/WebP from magic bytes (same idea as multipart uploads from browsers that omit a precise type).

### Server → client: error (bad client frame or validation)

```json
{ "type": "error", "detail": "human-readable reason" }
```

## Kafka `chat.message` and notifications

After each persisted message, the service:

1. **Broadcasts** `chat.new_message` to open **chat room** sockets for `(sender_id, peer)` and, if the recipient is in-room, `(recipient_id, sender_id)`.
2. Publishes **`chat.message`** to Kafka **only if** the recipient does **not** have an active chat room WebSocket with the sender. The notifications service consumes that topic and may push to **`/api/v1/notifications/ws`**.

There is **no** buffering of Kafka events when the user leaves the room: if they were in-room, they already saw the message on the chat socket and no `chat.message` is emitted for that send.

## Limits and operations notes

- **In-memory room registry:** multiple tabs = multiple sockets per `(viewer, peer)`; all receive broadcasts. Scaling **multiple replicas** of this service would require a shared presence store (e.g. Redis) instead of the current process-local registry.
- **Images:** max decoded size **10 MiB**; allowed types **JPEG, PNG, WebP** (after sniffing when needed).
- **Gateway:** chat routes are mounted like other protected routes; WebSockets use the same **`?token=`** pattern as notifications.
