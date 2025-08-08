from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import app.crud.gamers as gamers
import app.crud.games as games
import app.crud.swaps as swaps
from app.dependencies.database import get_session
from app.dependencies.notifications import NotificationService, get_notification_service
from app.schemas.game import Game
from app.schemas.gamer import Gamer
from app.schemas.swap import Swap, SwapCreate, SwapUpdate


router = APIRouter()


@router.post("/swaps", response_model=Swap)
def create_swap(
    swap: SwapCreate, 
    session: Session = Depends(get_session),
    notification_service: NotificationService = Depends(get_notification_service),
):
    try:
        return swaps.create_swap(session, swap, notification_service)
    except gamers.GamerNotFoundError as exc:
        raise HTTPException(status_code=422) from exc
    except games.GameNotFoundError as exc:
        raise HTTPException(status_code=422) from exc
    except swaps.GameLinkedToDifferentGamerError as exc:
        raise HTTPException(status_code=422) from exc


@router.get("/swaps", response_model=list[Swap]) 
def get_swaps(session: Session = Depends(get_session)):
    return swaps.get_swaps(session)


@router.get("/swaps/{swap_id}", response_model=Swap) 
def get_swap(
    swap_id: int, 
    session: Session = Depends(get_session),
    notification_service: NotificationService = Depends(get_notification_service),
):
    try:
        return swaps.get_swap(session, swap_id, notification_service)
    except swaps.SwapNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
    

@router.patch("/swaps/{swap_id}", response_model=Swap)
def update_swap(swap_id: int, params: SwapUpdate, session: Session = Depends(get_session)):
    try:
        return swaps.update_swap(session, swap_id, params)
    except swaps.SwapNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
    

@router.delete("/swaps/{swap_id}", response_model=Swap) 
def delete_swap(swap_id: int, session: Session = Depends(get_session)):
    try:
        return swaps.delete_swap(session, swap_id)
    except swaps.SwapNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
    

@router.get("/swaps/{swap_id}/gamers", response_model=list[Gamer]) 
def get_gamers_in_swap(
    swap_id: int, 
    session: Session = Depends(get_session),
    notification_service: NotificationService = Depends(get_notification_service),
):
    try:
        swap = swaps.get_swap(session, swap_id, notification_service)
    except swaps.SwapNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
    return [swap.proposer, swap.acceptor]


@router.get("/swaps/{swap_id}/games", response_model=list[Game]) 
def get_games_in_swap(
    swap_id: int, 
    session: Session = Depends(get_session),
    notification_service: NotificationService = Depends(get_notification_service),
):
    try:
        swap = swaps.get_swap(session, swap_id, notification_service)
    except swaps.SwapNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
    return swap.games
    