from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class UserFilter(Base):
    """Stored search filters for a user (table name: filters)."""

    __tablename__ = "filters"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user_features.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    relationship_type: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    age_from: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    age_to: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    sign: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    partner_gender: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)

    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
