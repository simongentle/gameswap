from sqlalchemy import event
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base


DBSession = sessionmaker(autocommit=False, autoflush=False)


def init_db(file: str):
    engine = create_engine(file, connect_args={"check_same_thread": False})
    event.listen(engine, 'connect', lambda c, _: c.execute('pragma foreign_keys=on'))
    DBSession.configure(bind=engine)
    Base.metadata.create_all(bind=engine)


def get_session():
    session = DBSession()
    try:
        yield session
    finally:
        session.close()
