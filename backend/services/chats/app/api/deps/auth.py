from fastapi import Header, HTTPException


async def get_current_user_id(x_user_id: str | None = Header(None, alias="X-User-Id")) -> int:
    if not x_user_id:
        raise HTTPException(status_code=401, detail="missing X-User-Id")
    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="invalid X-User-Id") from None
