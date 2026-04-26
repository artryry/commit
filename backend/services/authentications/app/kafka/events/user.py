from pydantic import BaseModel, EmailStr


class UserCreatedPayload(BaseModel):
    id: int
    email: EmailStr


class UserDeletedPayload(BaseModel):
    id: int
