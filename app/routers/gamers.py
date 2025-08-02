from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import app.crud.gamers as gamers
from app.dependencies.database import get_session
from app.schemas.game import Game
from app.schemas.gamer import Gamer, GamerCreate, GamerUpdate


router = APIRouter()


@router.post("/gamers", response_model=Gamer)
def create_gamer(gamer: GamerCreate, session: Session = Depends(get_session)):
    try:
        return gamers.create_gamer(session, gamer)
    except gamers.DuplicateGamerError as exc:
        raise HTTPException(status_code=422) from exc


@router.get("/gamers", response_model=list[Gamer]) 
def get_gamers(
    title: str | None = None, 
    platform: str | None = None,
    session: Session = Depends(get_session),
):
    if title or platform:
        return gamers.get_gamers_who_own_game(session, title, platform)
    return gamers.get_gamers(session)


@router.get("/gamers/{gamer_id}", response_model=Gamer) 
def get_gamer(gamer_id: int, session: Session = Depends(get_session)):
    try:
        return gamers.get_gamer(session, gamer_id)
    except gamers.GamerNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
    

@router.patch("/gamers/{gamer_id}", response_model=Gamer)
def update_gamer(gamer_id: int, params: GamerUpdate, session: Session = Depends(get_session)):
    try:
        return gamers.update_gamer(session, gamer_id, params)
    except gamers.GamerNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
    except gamers.DuplicateGamerError as exc:
        raise HTTPException(status_code=422) from exc
    

@router.delete("/gamers/{gamer_id}", response_model=Gamer) 
def delete_gamer(gamer_id: int, session: Session = Depends(get_session)):
    try:
        return gamers.delete_gamer(session, gamer_id)
    except gamers.GamerNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
    

@router.get("/gamers/{gamer_id}/games", response_model=list[Game]) 
def get_games_owned_by_gamer(gamer_id: int, session: Session = Depends(get_session)):
    return gamers.get_games_owned_by_gamer(session, gamer_id)
