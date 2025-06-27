from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Game(Base):
    __tablename__ = "game"
    __table_args__ = ( 
        UniqueConstraint("title", "platform", name="unique_title_platform"), 
    ) 
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    platform: Mapped[str]
