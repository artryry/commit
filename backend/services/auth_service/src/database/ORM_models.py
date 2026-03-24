from typing import Annotated

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


str_256 = Annotated[str, 256]


class Base(DeclarativeBase):
    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__}: {', '.join(cols)}>"


class UsersOrm(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str_256] = mapped_column(unique=True)
    email: Mapped[str_256] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    disabled: Mapped[bool]
