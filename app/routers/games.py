from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import app.crud.gamers as gamers
import app.crud.games as games
import app.crud.mixed as mixed
from app.dependencies.database import get_session
from app.schemas.game import Game, GameCreate, GameUpdate
from app.schemas.gamer import Gamer 


router = APIRouter()


@router.post("/games", response_model=Game)
def create_game(game: GameCreate, session: Session = Depends(get_session)):
    return games.create_game(session, game)


@router.get("/games", response_model=list[Game]) 
def get_games(title: str | None = None, session: Session = Depends(get_session)):
    if title is None:
        return games.get_games(session)
    return games.get_games_by_title(session, title)


@router.get("/games/{game_id}", response_model=Game) 
def get_game(game_id: int, session: Session = Depends(get_session)):
    try:
        return games.get_game(session, game_id)
    except games.GameNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
    

@router.get("/games/{game_id}/gamers", response_model=list[Gamer]) 
def get_gamers_for_given_game(game_id: int, session: Session = Depends(get_session)):
    try:
        game = games.get_game(session, game_id)
    except games.GameNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
    return game.gamers


@router.patch("/games/{game_id}", response_model=Game)
def update_game(game_id: int, params: GameUpdate, session: Session = Depends(get_session)):
    try:
        return games.update_game(session, game_id, params)
    except games.GameNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
    

@router.put("/games/{game_id}/gamers/{gamer_id}", response_model=Game)
def assign_gamer_to_game(game_id: int, gamer_id: int, session: Session = Depends(get_session)):
    try:
        return mixed.assign_gamer_to_game(session, game_id, gamer_id)
    except games.GameNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
    except gamers.GamerNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
    except mixed.DuplicateAssignmentError as exc:
        raise HTTPException(status_code=422) from exc


@router.delete("/games/{game_id}", response_model=Game) 
def delete_game(game_id: int, session: Session = Depends(get_session)):
    try:
        return games.delete_game(session, game_id)
    except games.GameNotFoundError as exc:
        raise HTTPException(status_code=404) from exc
