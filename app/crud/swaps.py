from sqlalchemy.orm import Session

from app.crud.gamers import GamerNotFoundError, get_gamer
from app.crud.games import GameNotFoundError, get_game
from app.dependencies.notifications import Event, Notification, NotificationService
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
    

def create_swap(
        session: Session, 
        params: SwapCreate,
        notification_service: NotificationService,
    ) -> Swap:
    # Load gamers for swap (and notification) unless proposer/acceptor does not exist
    try:
        proposer = get_gamer(session, params.proposer.id) 
        acceptor = get_gamer(session, params.acceptor.id) 
    except GamerNotFoundError as exc:
        raise InvalidSwapError(str(exc)) from exc
    
    # Initialise swap
    swap = Swap(proposer_id=params.proposer.id, acceptor_id=params.acceptor.id)
    session.add(swap)
    session.commit()
    
    # Load games for swap unless a game does not exist
    try:
        games = [get_game(session, game_id) 
                 for game_id in params.proposer.game_ids | params.acceptor.game_ids]
    except GameNotFoundError as exc:
        raise InvalidSwapError(str(exc)) from exc
    
    # Assign games to swap unless validation rules broken
    try:
        for game in games:
            swap.games.append(game)
    except ValueError as exc:
        raise InvalidSwapError(str(exc)) from exc
    session.commit()
    session.refresh(swap)

    notification_service.post(
        Notification(
            event=Event.SWAP_CREATED,
            message=f"Swap created between {proposer.name} and {acceptor.name}!"
        )
    )
    return swap
    

def delete_swap(session: Session, swap_id: int) -> None:    
    swap = get_swap(session, swap_id)
    session.delete(swap)
    session.commit()
