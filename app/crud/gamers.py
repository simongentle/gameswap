from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Game, Gamer
from app.schemas.gamer import GamerCreate, GamerUpdate


class GamerNotFoundError(Exception):
    pass


class DuplicateGamerError(Exception):
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


def get_games_owned_by_gamer(session: Session, gamer_id: int) -> list[Game]:
    result = session.execute(select(Game).where(Game.gamer_id == gamer_id))
    games = result.scalars().all()
    return games


def get_gamers_who_own_game(session: Session, title: str | None, platform: str | None) -> list[Gamer]:
    if title is None and platform is None:
        raise ValueError("At least one filter parameter should be provided.")
    
    query = session.query(Gamer)
    if title:
        query = query.filter(Gamer.games.any(Game.title == title))
    if platform:
        query = query.filter(Gamer.games.any(Game.platform == platform))

    gamers = query.all()
    return gamers
