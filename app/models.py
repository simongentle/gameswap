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

    swap_id: Mapped[int | None] = mapped_column(ForeignKey("swap.id"))
    swap: Mapped["Swap | None"] = relationship(back_populates="gamers")


class Swap(Base):
    __tablename__ = "swap"
    id: Mapped[int] = mapped_column(primary_key=True)
    return_date: Mapped[dt.date] 

    games: Mapped[list[Game]] = relationship(back_populates="swap")
    gamers: Mapped[list[Gamer]] = relationship(back_populates="swap")

    def is_due(self) -> bool:
        days_remaining = (self.return_date - dt.date.today()).days
        return days_remaining <= SWAP_DUE_THRESHOLD_IN_DAYS
    
    def has_max_gamers(self) -> bool:
        if len(self.gamers) >= 2:
            return True
        return False
    