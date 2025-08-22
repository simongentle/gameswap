from datetime import date
from typing import Annotated
from pydantic import BaseModel, Field, FutureDate, model_validator

from app.schemas.game import Game


class GamerWithGames(BaseModel):
    id: int
    game_ids: Annotated[set[int], Field(min_length=1)]


class SwapBase(BaseModel):
    return_date: FutureDate


class SwapCreate(SwapBase):
    proposer: GamerWithGames 
    acceptor: GamerWithGames 

    @model_validator(mode="after")
    def swap_is_valid(self) -> 'SwapCreate':
        if self.proposer.id == self.acceptor.id:
            raise ValueError("A swap must involve two gamers.")
        if len(self.proposer.game_ids & self.acceptor.game_ids) > 0:
            raise ValueError("Each game in a swap must have a unique ID.")
        return self


class SwapUpdate(BaseModel):
    return_date: FutureDate | None = None


class Swap(SwapBase):
    id: int
    return_date: date
    games: list[Game]
