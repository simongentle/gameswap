from enum import StrEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Status(StrEnum):
    OWNED = "owned"
    BORROWED = "borrowed"
    LENT = "lent"


class Game(Base):
    __tablename__ = "game"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    platform: Mapped[str]
    status: Mapped[str] = mapped_column(default=Status.OWNED.value)
