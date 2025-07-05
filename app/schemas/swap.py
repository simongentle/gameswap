import datetime as dt
from pydantic import BaseModel, Field, FutureDate

from app.schemas.game import Game


class SwapBase(BaseModel):
    friend: str
    return_date: FutureDate


class SwapCreate(SwapBase):
    pass


class SwapUpdate(BaseModel):
    friend: str | None = None
    return_date: FutureDate | None = None


class Swap(SwapBase):
    id: int


class SwapWithGames(Swap):
    games: list[Game] = Field(default_factory=list)
