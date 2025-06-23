from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Game(Base):
    __tablename__ = "game"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str]
    platform: Mapped[str]
