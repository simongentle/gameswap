from sqlalchemy import exists
from sqlalchemy.orm import Session
from typing import Protocol

from app.crud.games import GameNotFoundError, get_game
from app.dependencies.notifications import Event, Notification
from app.models import Gamer, Swap
from app.schemas.swap import SwapCreate, SwapUpdate


class SwapNotFoundError(Exception):
    pass


class CreateSwapError(Exception):
    pass


class NotificationService(Protocol):
    def post(self, notification: Notification) -> None: 
        ...


def find_swap(session: Session, swap_id: int) -> Swap:
    swap = session.get(Swap, swap_id)
    if swap is None:
        raise SwapNotFoundError
    return swap


def get_swap(
        session: Session, 
        swap_id: int, 
        notification_service: NotificationService,
    ) -> Swap:
    swap = find_swap(session, swap_id)
    if swap.is_due():
        notification_service.post(
            Notification(
                event=Event.SWAP_DUE,
                message=f"Warning: Swap with id {swap.id} due by {swap.return_date}!"
            )
        )
    return swap


def get_swaps(session: Session) -> list[Swap]:
    swaps = session.query(Swap).all()
    return swaps


def create_swap(
        session: Session, 
        params: SwapCreate, 
        notification_service: NotificationService,
    ) -> Swap:
    """
    A swap must involve at least two games
    A game can be in at most one swap at a time.
    Every game in a swap must be owned by either the proposer or the acceptor.
    A swap must involve at least one of the proposer's games and at least one of the acceptor's games.
    A swap involves at most one game with a given (title, platform).
    """
    # Check if gamers exist
    proposer_exists = session.scalar(exists().where(Gamer.id == params.proposer.id).select())
    acceptor_exists = session.scalar(exists().where(Gamer.id == params.acceptor.id).select())
    if not proposer_exists or not acceptor_exists:
        raise CreateSwapError 
    
    # Check if games exist, and load for subsequent checks if they do
    try:
        proposer_games = [get_game(session, game_id) for game_id in params.proposer.game_ids] 
        acceptor_games = [get_game(session, game_id) for game_id in params.acceptor.game_ids] 
    except GameNotFoundError as exc:
        raise CreateSwapError from exc
    
    # Check if games assigned to specified gamers
    if any([game.gamer_id != params.proposer.id for game in proposer_games]):
        raise CreateSwapError
    if any([game.gamer_id != params.acceptor.id for game in acceptor_games]):
        raise CreateSwapError

    # Check if at least one game per gamer with unique info
    game_info = [(game.title, game.platform) for game in proposer_games + acceptor_games]
    if len(game_info) != len(set(game_info)):
        raise CreateSwapError
    
    # Check if games not assigned to another swap
    if any([game.swap_id is not None for game in proposer_games + acceptor_games]):
        raise CreateSwapError

    # Construct valid swap
    swap = Swap(
        return_date=params.return_date,
        proposer_id=params.proposer.id,
        acceptor_id=params.acceptor.id,
    )
    session.add(swap)
    session.commit()
    swap.games = proposer_games + acceptor_games
    session.commit()
    session.refresh(swap)

    notification_service.post(
        Notification(
            event=Event.SWAP_CREATED,
            message=f"Created swap with id {swap.id}! Return games by {swap.return_date}."
        )
    )

    return swap
    

def update_swap(session: Session, swap_id: int, params: SwapUpdate) -> Swap:
    swap = find_swap(session, swap_id)
    for attr, value in params.model_dump(exclude_unset=True).items():
        setattr(swap, attr, value)
    session.add(swap)
    session.commit()
    session.refresh(swap)
    return swap


def delete_swap(session: Session, swap_id: int) -> Swap:    
    swap = find_swap(session, swap_id)
    session.delete(swap)
    session.commit()
    return swap
