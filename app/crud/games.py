from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.game import Game as DBGame
from app.schemas.game import Game, GameCreate, GameUpdate


class GameNotFoundError(Exception):
    pass


class DuplicateGameError(Exception):
    pass


def get_game(session: Session, game_id: int) -> Game:
    game = session.get(DBGame, game_id)
    if game is None:
        raise GameNotFoundError
    return game


def get_games(session: Session) -> list[Game]:
    games = session.query(DBGame)
    return games


def create_game(session: Session, params: GameCreate) -> Game:
    game = DBGame(**params.model_dump())
    try:
        session.add(game)
        session.commit()
        session.refresh(game)
        return game
    except IntegrityError as exc:
        session.rollback()
        raise DuplicateGameError from exc
    

def update_game(session: Session, game_id: int, params: GameUpdate) -> Game:
    game = session.get(DBGame, game_id)
    if game is None:
        raise GameNotFoundError
    for attr, value in params.model_dump().items():
        setattr(game, attr, value)
    try:
        session.add(game)
        session.commit()
        session.refresh(game)
        return game
    except IntegrityError as exc:
        session.rollback()
        raise DuplicateGameError from exc


def delete_game(session: Session, game_id: int) -> Game:
    game = session.get(DBGame, game_id)
    if game is None:
        raise GameNotFoundError
    session.delete(game)
    session.commit()
    return game
