import pytest

from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session

from app.dependencies.database import get_session
from app.dependencies.notifications import Notification, get_notification_service
from app.models import Base
from app.main import app


class NotificationServiceMock:
    @staticmethod
    def post(notification: Notification) -> None:
        return
    

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)

    with Session(engine, autocommit=False, autoflush=False) as session:
        yield session


@pytest.fixture(name="client")  
def client_fixture(session: Session):  
    def get_session_override():  
        return session
    
    def get_notification_service_override():
        return NotificationServiceMock()
    
    app.dependency_overrides[get_session] = get_session_override  
    app.dependency_overrides[get_notification_service] = get_notification_service_override

    client = TestClient(app)  
    yield client  
    app.dependency_overrides.clear()  
    