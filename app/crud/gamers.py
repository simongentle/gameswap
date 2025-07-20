from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Gamer as DBGamer
from app.schemas.gamer import Gamer, GamerCreate, GamerUpdate


class GamerNotFoundError(Exception):
    pass


class DuplicateGamerError(Exception):
    pass


def get_gamer(session: Session, gamer_id: int) -> Gamer:
    gamer = session.get(DBGamer, gamer_id)
    if gamer is None:
        raise GamerNotFoundError
    return gamer


def get_gamers(session: Session) -> list[Gamer]:
    gamers = session.query(DBGamer).all()
    return gamers


def create_gamer(session: Session, params: GamerCreate) -> Gamer:
    gamer = DBGamer(**params.model_dump())
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
