import datetime as dt
from sqlalchemy.orm import Session
from typing import Protocol

from app.dependencies.notifications import Event, Notification
from app.models import Swap as DBSwap
from app.schemas.swap import Swap, SwapCreate, SwapUpdate


SWAP_DUE_THRESHOLD_IN_DAYS = 7


class SwapNotFoundError(Exception):
    pass


class NotificationService(Protocol):
    def post(self, notification: Notification) -> None:
        return


def swap_is_due(return_date: dt.date) -> bool:
    days_remaining = (return_date - dt.date.today()).days
    if days_remaining <= SWAP_DUE_THRESHOLD_IN_DAYS:
        return True
    return False


def find_swap(session: Session, swap_id: int) -> Swap:
    swap = session.get(DBSwap, swap_id)
    if swap is None:
        raise SwapNotFoundError
    return swap


def get_swap(
        session: Session, 
        swap_id: int, 
        notification_service: NotificationService,
    ) -> Swap:
    swap = find_swap(session, swap_id)
    if swap_is_due(swap.return_date):
        notification_service.post(
            Notification(
                event=Event.SWAP_DUE,
                message=f"Warning: Swap with {swap.friend} due by {swap.return_date}!"
            )
        )
    return swap


def get_swaps(session: Session) -> list[Swap]:
    swaps = session.query(DBSwap).all()
    return swaps


def create_swap(
        session: Session, 
        params: SwapCreate, 
        notification_service: NotificationService,
    ) -> Swap:
    swap = DBSwap(**params.model_dump())
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
