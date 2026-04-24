from sqlalchemy import DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    token: Mapped[str] = mapped_column(unique=True, nullable=False)
    expires_at: Mapped[DateTime] = mapped_column(nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        server_default=func.now(), 
        nullable=False,
    )
