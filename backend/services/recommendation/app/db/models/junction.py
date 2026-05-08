from sqlalchemy import BigInteger, Column, ForeignKey, Table

from db.base import Base

filter_tags = Table(
    "filter_tags",
    Base.metadata,
    Column("user_id", BigInteger, ForeignKey("filters.user_id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", BigInteger, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

user_tags = Table(
    "user_tags",
    Base.metadata,
    Column("user_id", BigInteger, ForeignKey("user_features.user_id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", BigInteger, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)
