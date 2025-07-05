import datetime as dt
from pydantic import BaseModel, Field

from app.schemas.game import Game


class SwapBase(BaseModel):
    friend: str
    return_date: dt.date


class SwapCreate(SwapBase):
    pass


class SwapUpdate(SwapBase):
    friend: str | None = None
    return_date: dt.date | None = None


class Swap(SwapBase):
    id: int


class SwapWithGames(Swap):
    games: list[Game] = Field(default_factory=list)
