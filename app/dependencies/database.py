from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.game import Base


DBSession = sessionmaker(autocommit=False, autoflush=False)


def init_db(file: str):
    engine = create_engine(file, connect_args={"check_same_thread": False})
    DBSession.configure(bind=engine)
    Base.metadata.create_all(bind=engine)


def get_session():
    session = DBSession()
    try:
        yield session
    finally:
        session.close()
