import datetime as dt

from sqlalchemy import delete, event
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.models import Base, Swap


DB_FILE = "sqlite:///gameswap.db"
engine = create_engine(DB_FILE, connect_args={"check_same_thread": False})
event.listen(engine, 'connect', lambda c, _: c.execute('pragma foreign_keys=on'))
configured_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def delete_expired_swaps(session: Session) -> None:    
    session.execute(delete(Swap).where(Swap.return_date < dt.date.today()))
    session.commit()


def init_db(session: Session) -> None:
    Base.metadata.create_all(bind=engine)

    delete_expired_swaps(session)    


def get_session():
    with configured_session() as session:
        yield session
