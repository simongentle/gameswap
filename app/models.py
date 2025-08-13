import datetime as dt
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, validates
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
    
    @validates("games")
    def validate_game(self, _, game: Game):
        if game.gamer_id not in (self.proposer_id, self.acceptor_id):
            raise ValueError(
                f"Game {game.id} not owned by gamer {self.proposer_id} of {self.acceptor_id}."
            )
        if any([game.title == swap_game.title and game.platform == swap_game.platform 
                for swap_game in self.games]):
            raise ValueError(
                f"Duplicate game in swap with title='{game.title}' and platform='{game.platform}'."
            )
        if game.swap_id is not None:
            raise ValueError(
                f"Game {game.id} is already in swap {game.swap_id}."
            )
        return game
    