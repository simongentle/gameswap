from fastapi import APIRouter, HTTPException, status

import app.crud.swaps as swaps
from app.dependencies.database import SessionDep
from app.dependencies.notifications import NotificationServiceDep

from app.schemas.swap import Swap, SwapCreate


router = APIRouter()


@router.post("/swaps", response_model=Swap)
def create_swap(
    swap: SwapCreate, 
    session: SessionDep,
    notification_service: NotificationServiceDep,
    ):
    try:
        return swaps.create_swap(session, swap, notification_service)
    except swaps.InvalidSwapError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/swaps", response_model=list[Swap]) 
def get_swaps(session: SessionDep):
    return swaps.get_swaps(session)


@router.get("/swaps/{swap_id}", response_model=Swap) 
def get_swap(swap_id: int, session: SessionDep):
    try:
        return swaps.get_swap(session, swap_id)
    except swaps.SwapNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
    

@router.delete("/swaps/{swap_id}", status_code=status.HTTP_204_NO_CONTENT) 
def delete_swap(swap_id: int, session: SessionDep):
    try:
        swaps.delete_swap(session, swap_id)
    except swaps.SwapNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
    