from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import app.crud.gamers as gamers
from app.dependencies.database import get_session
from app.schemas.game import Game
from app.schemas.gamer import Gamer, GamerCreate, GamerUpdate


router = APIRouter()


@router.post("/gamers", response_model=Gamer)
def create_gamer(gamer: GamerCreate, session: Session = Depends(get_session)) -> Gamer:
    try:
        return gamers.create_gamer(session, gamer)
    except gamers.DuplicateGamerError as exc:
        raise HTTPException(status_code=422) from exc


@router.get("/gamers", response_model=list[Gamer]) 
def get_gamers(session: Session = Depends(get_session)) -> list[Gamer]:
    return gamers.get_gamers(session)


@router.get("/gamers/{gamer_id}", response_model=Gamer) 
def get_gamer(gamer_id: int, session: Session = Depends(get_session)) -> Gamer:
    try:
        return gamers.get_gamer(session, gamer_id)
    except gamers.GamerNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
    

@router.get("/gamers/{gamer_id}/games", response_model=list[Game]) 
def get_games_for_given_gamer(gamer_id: int, session: Session = Depends(get_session)) -> list[Game]:
    try:
        gamer = gamers.get_gamer(session, gamer_id)
    except gamers.GamerNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
    return gamer.games


@router.patch("/gamers/{gamer_id}", response_model=Gamer)
def update_gamer(gamer_id: int, params: GamerUpdate, session: Session = Depends(get_session)) -> Gamer:
    try:
        return gamers.update_gamer(session, gamer_id, params)
    except gamers.GamerNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
    except gamers.DuplicateGamerError as exc:
        raise HTTPException(status_code=422) from exc


@router.delete("/gamers/{gamer_id}", response_model=Gamer) 
def delete_gamer(gamer_id: int, session: Session = Depends(get_session)) -> Gamer:
    try:
        return gamers.delete_gamer(session, gamer_id)
    except gamers.GamerNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
