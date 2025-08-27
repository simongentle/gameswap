from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import event
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.models import Base


DB_FILE = "sqlite:///gameswap.db"
engine = create_engine(DB_FILE, connect_args={"check_same_thread": False})
event.listen(engine, 'connect', lambda c, _: c.execute('pragma foreign_keys=on'))
configured_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_session() -> Generator[Session, None, None]:
    with configured_session() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
