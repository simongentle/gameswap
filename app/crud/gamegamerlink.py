from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.gamers import get_gamer
from app.crud.games import get_game
from app.models import Game, Gamer


class DuplicateAssignmentError(Exception):
    pass


class GameNotLinkedToGamerError(Exception):
    pass


def assign_gamer_to_game(session: Session, game_id: int, gamer_id: int) -> Game:    
    game = get_game(session, game_id)
    gamer = get_gamer(session, gamer_id)
    game.gamers.append(gamer)
    try:
        session.commit()
    except IntegrityError as exc:
        raise DuplicateAssignmentError from exc
    session.refresh(game)
    return game


def remove_gamer_from_game(session: Session, game_id: int, gamer_id: int) -> None:    
    game = get_game(session, game_id)
    gamer = get_gamer(session, gamer_id)
    if gamer not in game.gamers:
        raise GameNotLinkedToGamerError
    game.gamers.remove(gamer)
    session.commit()


def assign_game_to_gamer(session: Session, gamer_id: int, game_id: int) -> Gamer:    
    gamer = get_gamer(session, gamer_id)
    game = get_game(session, game_id)
    gamer.games.append(game)
    try:
        session.commit()
    except IntegrityError as exc:
        raise DuplicateAssignmentError from exc
    session.refresh(gamer)
    return gamer


def remove_game_from_gamer(session: Session, gamer_id: int, game_id: int) -> None:    
    gamer = get_gamer(session, gamer_id)
    game = get_game(session, game_id)
    if game not in gamer.games:
        raise GameNotLinkedToGamerError
    gamer.games.remove(game)
    session.commit()
