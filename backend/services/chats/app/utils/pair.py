def sorted_pair(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def peer_user_id(chat_user_low: int, chat_user_high: int, viewer_id: int) -> int:
    return chat_user_high if viewer_id == chat_user_low else chat_user_low
