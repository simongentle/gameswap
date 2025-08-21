from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import Protocol

from app.crud.games import GameNotFoundError, get_game
from app.dependencies.notifications import Event, Notification
from app.models import Swap
from app.schemas.swap import SwapCreate, SwapUpdate


class SwapNotFoundError(Exception):
    pass


class InvalidSwapError(Exception):
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
    # Construct swap without games unless proposer/acceptor does not exist:
    swap = Swap(
        return_date=params.return_date,
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


def delete_expired_swaps(session: Session) -> None:   
    session.execute(delete(Swap).where(Swap.is_expired()))
    session.commit()
