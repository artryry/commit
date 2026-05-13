from models.message import Message


def message_to_public_dict(m: Message) -> dict:
    return {
        "id": str(m.id),
        "sender_id": m.sender_id,
        "body": m.body,
        "image_storage_key": m.image_storage_key,
        "created_at": m.created_at.isoformat(),
    }
