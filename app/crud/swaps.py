from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import Protocol

from app.crud.gamers import GamerNotFoundError
from app.crud.games import get_game
from app.dependencies.notifications import Event, Notification
from app.models import Swap
from app.schemas.swap import SwapCreate, SwapUpdate


class SwapNotFoundError(Exception):
    pass


class GameLinkedToDifferentGamerError(Exception):
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
    swap = Swap(**params.model_dump(exclude={"games"}))
    session.add(swap)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise GamerNotFoundError from exc

    for game_model in params.games:
        game = get_game(session, game_model.id)
        if game.gamer_id not in (params.proposer_id, params.acceptor_id):
            raise GameLinkedToDifferentGamerError
        game.swap_id = swap.id
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
