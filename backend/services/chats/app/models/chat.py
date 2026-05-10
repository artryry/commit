import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class Chat(Base):
    __tablename__ = "chats"
    __table_args__ = (UniqueConstraint("user_low", "user_high", name="uq_chats_pair"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_low: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    user_high: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    match_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
