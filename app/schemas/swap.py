from pydantic import BaseModel, FutureDate, model_validator

from app.schemas.game import Game


class SwapBase(BaseModel):
    return_date: FutureDate
    proposer_id: int
    acceptor_id: int


class SwapCreate(SwapBase):
    games: list[Game]

    @model_validator(mode='after')
    def games_are_valid(self) -> 'SwapCreate':
        if len(self.games) < 2:
            raise ValueError("A swap must involve at least two games.")
        
        if any([game.swap_id is not None for game in self.games]):
            raise ValueError("A game can be in at most one swap at a time.")

        if any([game.gamer_id not in (self.proposer_id, self.acceptor_id) for game in self.games]):
            raise ValueError("Every game in a swap must be owned by either the proposer or the acceptor.")

        games_are_owned_by_proposer = [game.gamer_id == self.proposer_id for game in self.games]
        if all(games_are_owned_by_proposer) or not any(games_are_owned_by_proposer):
            raise ValueError(
                "A swap must involve at least one of the proposer's games and at least one of the acceptor's gmaes."
            )
        
        game_info = [(game.title, game.platform) for game in self.games]
        if len(game_info) != len(set(game_info)):
            raise ValueError("A swap involves at most one game with a given (title, platform).")

        return self


class SwapUpdate(BaseModel):
    return_date: FutureDate | None = None


class Swap(SwapBase):
    id: int
    games: list[Game]
