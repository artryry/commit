from pydantic import BaseModel, Field


class SendTextMessageBody(BaseModel):
    body: str = Field(..., min_length=1, max_length=10_000)
