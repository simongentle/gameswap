from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.games import get_game
from app.models import Gamer
from app.schemas.gamer import GamerCreate, GamerUpdate


class GamerNotFoundError(Exception):
    pass


class DuplicateGamerError(Exception):
    pass


class DuplicateAssignmentError(Exception):
    pass


class GameNotLinkedToGamerError(Exception):
    pass


def get_gamer(session: Session, gamer_id: int) -> Gamer:
    gamer = session.get(Gamer, gamer_id)
    if gamer is None:
        raise GamerNotFoundError
    return gamer


def get_gamers(session: Session) -> list[Gamer]:
    gamers = session.query(Gamer).all()
    return gamers


def create_gamer(session: Session, params: GamerCreate) -> Gamer:
    gamer = Gamer(**params.model_dump())
    session.add(gamer)
    try:
        session.commit()
    except IntegrityError as exc:
        raise DuplicateGamerError from exc
    session.refresh(gamer)
    return gamer
    

def update_gamer(session: Session, gamer_id: int, params: GamerUpdate) -> Gamer:
    gamer = get_gamer(session, gamer_id)
    for attr, value in params.model_dump(exclude_unset=True).items():
        setattr(gamer, attr, value)
    session.add(gamer)
    try:
        session.commit()
    except IntegrityError as exc:
        raise DuplicateGamerError from exc
    session.refresh(gamer)
    return gamer


def delete_gamer(session: Session, gamer_id: int) -> Gamer:    
    gamer = get_gamer(session, gamer_id)
    session.delete(gamer)
    session.commit()
    return gamer


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
