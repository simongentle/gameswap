import datetime as dt
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


SWAP_DUE_THRESHOLD_IN_DAYS = 7


class Base(DeclarativeBase):
    pass


class Game(Base):
    __tablename__ = "game"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)
    platform: Mapped[str]

    swap_id: Mapped[int | None] = mapped_column(ForeignKey("swap.id"))
    swap: Mapped["Swap | None"] = relationship(back_populates="games")


class Swap(Base):
    __tablename__ = "swap"
    id: Mapped[int] = mapped_column(primary_key=True)
    friend: Mapped[str]
    return_date: Mapped[dt.date] 

    games: Mapped[list[Game]] = relationship(back_populates="swap")

    def is_due(self) -> bool:
        days_remaining = (self.return_date - dt.date.today()).days
        return days_remaining <= SWAP_DUE_THRESHOLD_IN_DAYS
