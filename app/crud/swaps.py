from sqlalchemy.orm import Session
from typing import Protocol

from app.crud.gamers import get_gamer
from app.dependencies.notifications import Event, Notification
from app.models import Game, Gamer, Swap
from app.schemas.swap import SwapCreate, SwapUpdate


class SwapNotFoundError(Exception):
    pass


class MaxGamersInSwapError(Exception):
    pass


class GamerNotLinkedToSwapError(Exception):
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
                message=f"Warning: Swap with {swap.friend} due by {swap.return_date}!"
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
    swap = Swap(**params.model_dump())
    session.add(swap)
    session.commit()
    session.refresh(swap)

    notification_service.post(
        Notification(
            event=Event.SWAP_CREATED,
            message=f"Created swap with {swap.friend}! Return games by {swap.return_date}."
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


def assign_gamer_to_swap(session: Session, swap_id: int, gamer_id: int) -> Swap:    
    swap = find_swap(session, swap_id)
    if swap.has_max_gamers():
        raise MaxGamersInSwapError
    gamer = get_gamer(session, gamer_id)
    swap.gamers.append(gamer)
    session.commit()
    session.refresh(swap)
    return swap


def find_gamer_in_swap(session: Session, swap: Swap, gamer_id: int) -> Gamer:
    gamer = get_gamer(session, gamer_id)
    if gamer not in swap.gamers:
        raise GamerNotLinkedToSwapError
    return gamer


def remove_games_of_gamer_from_swap(session: Session, gamer: Gamer, swap: Swap) -> list[Game]:
    games_of_gamer_in_swap = [game for game in swap.games if game in gamer.games]
    for game in games_of_gamer_in_swap:
        swap.games.remove(game)
    session.commit()


def remove_gamer_from_swap(session: Session, swap_id: int, gamer_id: int) -> None:    
    swap = find_swap(session, swap_id)
    gamer = find_gamer_in_swap(session, swap, gamer_id)
    swap.gamers.remove(gamer)
    session.commit()

    remove_games_of_gamer_from_swap(session, gamer, swap)    
