from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.games import GameNotFoundError, get_game
from app.models import Swap
from app.schemas.swap import SwapCreate


class SwapNotFoundError(Exception):
    pass


class InvalidSwapError(Exception):
    pass


def get_swap(session: Session, swap_id: int) -> Swap:
    swap = session.get(Swap, swap_id)
    if swap is None:
        raise SwapNotFoundError
    return swap


def get_swaps(session: Session) -> list[Swap]:
    swaps = session.query(Swap).all()
    return swaps
    

def create_swap(session: Session, params: SwapCreate) -> Swap:
    # Construct swap without games unless proposer/acceptor does not exist:
    swap = Swap(
        proposer_id=params.proposer.id,
        acceptor_id=params.acceptor.id,
    )
    session.add(swap)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise InvalidSwapError(
            f"Gamer {params.proposer.id} or {params.acceptor.id} not found."
        ) from exc
    
    # Load games for swap unless a game does not exist:
    try:
        games = [get_game(session, game_id) 
                 for game_id in params.proposer.game_ids | params.acceptor.game_ids]
    except GameNotFoundError as exc:
        raise InvalidSwapError(str(exc)) from exc
    
    # Assign games to swap unless validation rules broken:
    try:
        for game in games:
            swap.games.append(game)
    except ValueError as exc:
        raise InvalidSwapError(str(exc)) from exc

    session.commit()
    session.refresh(swap)
    return swap
    

def delete_swap(session: Session, swap_id: int) -> Swap:    
    swap = get_swap(session, swap_id)
    session.delete(swap)
    session.commit()
    return swap
