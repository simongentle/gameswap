from fastapi import APIRouter, HTTPException

import app.crud.gamers as gamers
import app.crud.games as games
from app.dependencies.database import SessionDep
from app.schemas.game import Game, GameCreate, GameUpdate


router = APIRouter()


@router.post("/games", response_model=Game)
def create_game(game: GameCreate, session: SessionDep):
    try:
        return games.create_game(session, game)
    except gamers.GamerNotFoundError as exc:
        raise HTTPException(status_code=422) from exc


@router.get("/games", response_model=list[Game]) 
def get_games(session: SessionDep, available: bool | None = None):
    if available is not None:
        return games.get_games_by_availability(session, available)
    return games.get_games(session)


@router.get("/games/{game_id}", response_model=Game) 
def get_game(game_id: int, session: SessionDep):
    try:
        return games.get_game(session, game_id)
    except games.GameNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
    

@router.patch("/games/{game_id}", response_model=Game)
def update_game(game_id: int, params: GameUpdate, session: SessionDep):
    try:
        return games.update_game(session, game_id, params)
    except games.GameNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
    

@router.delete("/games/{game_id}", response_model=Game) 
def delete_game(game_id: int, session: SessionDep):
    try:
        return games.delete_game(session, game_id)
    except games.GameNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
