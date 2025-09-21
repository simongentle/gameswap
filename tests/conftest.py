from collections.abc import Generator
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine, event
from sqlalchemy.orm import Session

from app.dependencies.database import get_session
from app.dependencies.notifications import Notification, get_notification_service
from app.main import app
from app.models import Base, Game, Gamer, Swap


class NotificationServiceMock:
    def post(self, notification: Notification) -> None:
        pass
    

@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    event.listen(engine, 'connect', lambda c, _: c.execute('pragma foreign_keys=on'))
    Base.metadata.create_all(engine)

    with Session(engine, autocommit=False, autoflush=False) as session:
        yield session


@pytest.fixture(name="client")  
def client_fixture(session: Session) -> Generator[TestClient, None, None]:  
    def get_session_override():  
        return session
    
    def get_notification_service_override():
        return NotificationServiceMock()
    
    app.dependency_overrides[get_session] = get_session_override  
    app.dependency_overrides[get_notification_service] = get_notification_service_override

    client = TestClient(app)  
    yield client  
    app.dependency_overrides.clear()  


@pytest.fixture
def swap(session: Session) -> Swap:
    proposer = Gamer(name="Player One", email="press@start.com")
    acceptor = Gamer(name="Player Two", email="insert@coin.com")
    session.add_all([proposer, acceptor])
    session.commit()

    proposer_game = Game(title="Sonic The Hedgehog", platform="SEGA Mega Drive", gamer_id=proposer.id)
    acceptor_game = Game(title="Super Mario Land", platform="Nintendo GAME BOY", gamer_id=acceptor.id)
    session.add_all([proposer_game, acceptor_game])
    session.commit()

    swap = Swap(proposer_id=proposer.id, acceptor_id=acceptor.id)
    session.add(swap)
    session.commit()
    swap.games.append(proposer_game)
    swap.games.append(acceptor_game)
    session.commit()

    return swap
    