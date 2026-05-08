from datetime import datetime

from sqlalchemy import BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class SeenPair(Base):
    __tablename__ = "seen_pairs"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    seen_user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
