import datetime as dt
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


SWAP_DUE_THRESHOLD_IN_DAYS = 7
MAX_GAMERS_IN_SWAP = 2


class Base(DeclarativeBase):
    pass


game_gamer_link = Table('game_gamer_link', Base.metadata,
    Column('game_id', ForeignKey('game.id'), primary_key=True),
    Column('gamer_id', ForeignKey('gamer.id'), primary_key=True)
)


class Game(Base):
    __tablename__ = "game"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)
    platform: Mapped[str]

    gamers: Mapped[list["Gamer"]] = relationship(secondary=game_gamer_link, back_populates="games")

    swap_id: Mapped[int | None] = mapped_column(ForeignKey("swap.id"))
    swap: Mapped["Swap | None"] = relationship(back_populates="games")


class Gamer(Base):
    __tablename__ = "gamer"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] 
    email: Mapped[str] = mapped_column(unique=True)

    games: Mapped[list[Game]] = relationship(secondary=game_gamer_link, back_populates="gamers")

    swap_id: Mapped[int | None] = mapped_column(ForeignKey("swap.id"))
    swap: Mapped["Swap | None"] = relationship(back_populates="gamers")


class Swap(Base):
    __tablename__ = "swap"
    id: Mapped[int] = mapped_column(primary_key=True)
    friend: Mapped[str]
    return_date: Mapped[dt.date] 

    games: Mapped[list[Game]] = relationship(back_populates="swap")
    gamers: Mapped[list[Gamer]] = relationship(back_populates="swap")

    def is_due(self) -> bool:
        days_remaining = (self.return_date - dt.date.today()).days
        return days_remaining <= SWAP_DUE_THRESHOLD_IN_DAYS
    
    def has_max_gamers(self) -> bool:
        if len(self.gamers) >= MAX_GAMERS_IN_SWAP:
            return True
        return False
    