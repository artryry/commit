from datetime import datetime
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, DateTime, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from config.settings import settings
from db.base import Base


class UserFeature(Base):
    __tablename__ = "user_features"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    birthday: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sign: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    relationship_type: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    gender: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    bio_vector: Mapped[Optional[list]] = mapped_column(Vector(settings.EMBEDDING_DIM), nullable=True)
    search_for_vector: Mapped[Optional[list]] = mapped_column(Vector(settings.EMBEDDING_DIM), nullable=True)
    combined_vector: Mapped[Optional[list]] = mapped_column(Vector(settings.EMBEDDING_DIM), nullable=True)

    embedding_model: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
