from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import app.crud.games as games
from app.dependencies.database import get_db_session
from app.schemas.game import Game, GameCreate, GameUpdate


router = APIRouter()


@router.post("/games", response_model=Game)
def create_game(game: GameCreate, session: Session = Depends(get_db_session)) -> Game:
    return games.create_game(session, game)


@router.get("/games", response_model=list[Game]) 
def get_games(session: Session = Depends(get_db_session)) -> list[Game]:
    return games.get_games(session)


@router.get("/games/{game_id}", response_model=Game) 
def get_game(game_id: int, session) -> Game:
    return games.get_game(session, game_id)


@router.patch("/games/{game_id}", response_model=Game)
def update_game(game_id: int, params: GameUpdate, session: Session = Depends(get_db_session)) -> Game:
    return games.update_game(session, game_id, params)


@router.delete("/games/{game_id}", response_model=Game) 
def delete_game(game_id: int, session: Session = Depends(get_db_session)) -> Game:
    return games.delete_game(session, game_id)
