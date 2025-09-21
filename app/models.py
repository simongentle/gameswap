from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, validates


class Base(DeclarativeBase):
    pass


class Game(Base):
    __tablename__ = "game"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)
    platform: Mapped[str]

    gamer_id: Mapped[int] = mapped_column(ForeignKey("gamer.id", ondelete="CASCADE"))
    gamer: Mapped["Gamer"] = relationship(back_populates="games")

    swap_id: Mapped[int | None] = mapped_column(ForeignKey("swap.id", ondelete="SET NULL"))
    swap: Mapped["Swap | None"] = relationship(back_populates="games")

    @classmethod
    def is_available(cls) -> bool:
        return cls.swap_id is not None


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

    games: Mapped[list[Game]] = relationship(back_populates="swap")

    proposer_id: Mapped[int] = mapped_column(ForeignKey("gamer.id"))
    proposer: Mapped[Gamer] = relationship(back_populates="proposer_swaps", foreign_keys=proposer_id)

    acceptor_id: Mapped[int] = mapped_column(ForeignKey("gamer.id"))
    acceptor: Mapped[Gamer] = relationship(back_populates="acceptor_swaps", foreign_keys=acceptor_id)

    @validates("games")
    def validate_game(self, _, game: Game):
        if game.gamer_id not in (self.proposer_id, self.acceptor_id):
            raise ValueError(
                f"Game {game.id} not owned by gamer {self.proposer_id} or {self.acceptor_id}."
            )
        if not game.is_available():
            raise ValueError(
                f"Game {game.id} is already in swap {game.swap_id}."
            )
        if any([game.title == swap_game.title and game.platform == swap_game.platform 
                for swap_game in self.games]):
            raise ValueError(
                f"Duplicate game in swap with title='{game.title}' and platform='{game.platform}'."
            )
        return game
