import datetime as dt
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Any


SWAP_DUE_THRESHOLD_IN_DAYS = 7


class Base(DeclarativeBase):
    pass


def to_dict(obj: Base | None) -> dict[str, Any]:
    if obj is None:
        return {}
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


class Game(Base):
    __tablename__ = "game"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)
    platform: Mapped[str]

    gamer_id: Mapped[int] = mapped_column(ForeignKey("gamer.id", ondelete="CASCADE"))
    gamer: Mapped["Gamer"] = relationship(back_populates="games")

    swap_id: Mapped[int | None] = mapped_column(ForeignKey("swap.id"))
    swap: Mapped["Swap | None"] = relationship(back_populates="games")


class Gamer(Base):
    __tablename__ = "gamer"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] 
    email: Mapped[str] = mapped_column(unique=True)

    games: Mapped[list[Game]] = relationship(back_populates="gamer", cascade="all, delete-orphan")

    proposer_swaps: Mapped[list["Swap"]] = relationship(back_populates="proposer", foreign_keys="Swap.proposer_id")
    acceptor_swaps: Mapped[list["Swap"]] = relationship(back_populates="acceptor", foreign_keys="Swap.acceptor_id")


class Swap(Base):
    __tablename__ = "swap"
    id: Mapped[int] = mapped_column(primary_key=True)
    return_date: Mapped[dt.date] 

    games: Mapped[list[Game]] = relationship(back_populates="swap")

    proposer_id: Mapped[int] = mapped_column(ForeignKey("gamer.id"))
    proposer: Mapped[Gamer] = relationship(back_populates="proposer_swaps", foreign_keys=proposer_id)

    acceptor_id: Mapped[int] = mapped_column(ForeignKey("gamer.id"))
    acceptor: Mapped[Gamer] = relationship(back_populates="acceptor_swaps", foreign_keys=acceptor_id)
    
    def is_due(self) -> bool:
        days_remaining = (self.return_date - dt.date.today()).days
        return days_remaining <= SWAP_DUE_THRESHOLD_IN_DAYS
    