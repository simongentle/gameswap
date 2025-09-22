from typing import Annotated
from pydantic import BaseModel, Field, model_validator

from app.schemas.game import Game
from app.schemas.gamer import Gamer


class GamerWithGames(BaseModel):
    id: int
    game_ids: Annotated[set[int], Field(min_length=1)]    


class SwapCreate(BaseModel):
    proposer: GamerWithGames 
    acceptor: GamerWithGames 

    @model_validator(mode="after")
    def swap_is_valid(self) -> 'SwapCreate':
        if self.proposer.id == self.acceptor.id:
            raise ValueError("A swap must involve two gamers.")
        if len(self.proposer.game_ids & self.acceptor.game_ids) > 0:
            raise ValueError("Each game in a swap must have a unique ID.")
        return self


class Swap(BaseModel):
    id: int
    proposer: Gamer
    acceptor: Gamer
    games: list[Game]
