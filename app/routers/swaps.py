from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import app.crud.swaps as swaps
from app.dependencies.database import get_session
from app.schemas.game import Game
from app.schemas.gamer import Gamer
from app.schemas.swap import Swap, SwapCreate


router = APIRouter()


@router.post("/swaps", response_model=Swap)
def create_swap(swap: SwapCreate, session: Session = Depends(get_session)):
    try:
        return swaps.create_swap(session, swap)
    except swaps.InvalidSwapError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/swaps", response_model=list[Swap]) 
def get_swaps(session: Session = Depends(get_session)):
    return swaps.get_swaps(session)


@router.get("/swaps/{swap_id}", response_model=Swap) 
def get_swap(swap_id: int, session: Session = Depends(get_session)):
    try:
        return swaps.get_swap(session, swap_id)
    except swaps.SwapNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
    

@router.delete("/swaps/{swap_id}", status_code=status.HTTP_204_NO_CONTENT) 
def delete_swap(swap_id: int, session: Session = Depends(get_session)):
    try:
        swaps.delete_swap(session, swap_id)
    except swaps.SwapNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
    