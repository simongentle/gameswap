from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import app.crud.games as games
from app.dependencies.database import get_session
from app.schemas.game import Game, GameCreate, GameUpdate


router = APIRouter()


@router.post("/games", response_model=Game)
def create_game(game: GameCreate, session: Session = Depends(get_session)):
    return games.create_game(session, game)


@router.get("/games", response_model=list[Game]) 
def get_games(session: Session = Depends(get_session)):
    return games.get_games(session)


@router.get("/games/{game_id}", response_model=Game) 
def get_game(game_id: int, session: Session = Depends(get_session)):
    try:
        return games.get_game(session, game_id)
    except games.GameNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
    

@router.patch("/games/{game_id}", response_model=Game)
def update_game(game_id: int, params: GameUpdate, session: Session = Depends(get_session)):
    try:
        return games.update_game(session, game_id, params)
    except games.GameNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
    

@router.delete("/games/{game_id}", response_model=Game) 
def delete_game(game_id: int, session: Session = Depends(get_session)):
    try:
        return games.delete_game(session, game_id)
    except games.GameNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
