from datetime import datetime

from pydantic import BaseModel


class Event(BaseModel):
    event_id: str
    event_type: str
    occurred_at: datetime
    payload: dict
