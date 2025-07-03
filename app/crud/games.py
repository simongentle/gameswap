from sqlalchemy.orm import Session

from app.models import Game as DBGame
from app.schemas.game import Game, GameCreate, GameUpdate


class GameNotFoundError(Exception):
    pass


def get_game(session: Session, game_id: int) -> Game:
    game = session.get(DBGame, game_id)
    if game is None:
        raise GameNotFoundError
    return game


def get_games(session: Session) -> list[Game]:
    games = session.query(DBGame).all()
    return games


def create_game(session: Session, params: GameCreate) -> Game:
    game = DBGame(**params.model_dump())
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


def delete_game(session: Session, game_id: int) -> Game:    
    game = get_game(session, game_id)
    session.delete(game)
    session.commit()
    return game
