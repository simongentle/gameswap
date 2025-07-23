from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.gamers import get_gamer
from app.crud.games import get_game
from app.models import Game, Gamer


class DuplicateAssignmentError(Exception):
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