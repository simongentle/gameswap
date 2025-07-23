from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.gamers import get_gamer
from app.models import Game 
from app.schemas.game import GameCreate, GameUpdate


class GameNotFoundError(Exception):
    pass


class GamerAlreadyAssignedToGameError(Exception):
    pass


def get_game(session: Session, game_id: int) -> Game:
    game = session.get(Game, game_id)
    if game is None:
        raise GameNotFoundError
    return game


def get_games(session: Session) -> list[Game]:
    games = session.query(Game).all()
    return games


def get_games_by_title(session: Session, title: str) -> list[Game]:
    result = session.execute(select(Game).where(Game.title == title))
    games = result.scalars().all()
    return games


def create_game(session: Session, params: GameCreate) -> Game:
    game = Game(**params.model_dump())
    session.add(game)
    session.commit()
    session.refresh(game)
    return game
    

def update_game(session: Session, game_id: int, params: GameUpdate) -> Game:
    game = get_game(session, game_id)
    for attr, value in params.model_dump(exclude_unset=True).items():
        setattr(game, attr, value)
    session.add(game)
    session.commit()
    session.refresh(game)
    return game


def assign_gamer_to_game(session: Session, game_id: int, gamer_id: int) -> Game:    
    game = get_game(session, game_id)
    gamer = get_gamer(session, gamer_id)
    game.gamers.append(gamer)
    try:
        session.commit()
    except IntegrityError as exc:
        raise GamerAlreadyAssignedToGameError from exc
    session.refresh(game)
    return game


def delete_game(session: Session, game_id: int) -> Game:    
    game = get_game(session, game_id)
    session.delete(game)
    session.commit()
    return game
