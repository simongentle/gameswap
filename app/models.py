import datetime as dt
from enum import StrEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class Status(StrEnum):
    OWNED = "owned"
    BORROWED = "borrowed"
    LENT = "lent"


class Game(Base):
    __tablename__ = "game"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)
    platform: Mapped[str]
    status: Mapped[str] = mapped_column(default=Status.OWNED.value)

    swap_id: Mapped[int | None] = mapped_column(ForeignKey("swap.id"))
    swap: Mapped["Swap | None"] = relationship(back_populates="games")


class Swap(Base):
    __tablename__ = "swap"
    id: Mapped[int] = mapped_column(primary_key=True)
    friend: Mapped[str]
    return_date: Mapped[dt.date] 

    games: Mapped[list[Game]] = relationship(back_populates="swap")
