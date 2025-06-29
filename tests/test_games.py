import pytest

from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session

from app.models.game import Base
from app.main import app
from app.dependencies.database import get_session


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

    app.dependency_overrides[get_session] = get_session_override  

    client = TestClient(app)  
    yield client  
    app.dependency_overrides.clear()  


def test_create_game(client: TestClient) -> None:
    game_data = {
        "title": "Sonic The Hedehog",
        "platform": "SEGA Mega Drive",
    }
    response = client.post("/games", json=game_data)
    game = response.json()
    assert (
        "id" in game
        and game["title"] == game_data["title"]
        and game["platform"] == game_data["platform"]
    )


def test_get_game(client: TestClient) -> None:
    game_data = {
        "title": "Sonic The Hedehog",
        "platform": "SEGA Mega Drive",
    }
    response = client.post("/games", json=game_data)
    assert response.status_code == 200, response.text

    response = client.get(f"/games/{1}")
    game = response.json()
    assert (
        game["id"] == 1
        and game["title"] == game_data["title"]
        and game["platform"] == game_data["platform"]
    )


def test_get_game_not_exists(client: TestClient):
    response = client.get(f"/games/{0}")
    assert response.status_code == 404, response.text


def test_delete_game(client: TestClient) -> None:
    game_data = {
        "title": "Sonic The Hedehog",
        "platform": "SEGA Mega Drive",
    }
    response = client.post("/games", json=game_data)
    assert response.status_code == 200, response.text

    response = client.delete(f"/games/{1}")
    response = client.get(f"/games/{1}")
    assert response.status_code == 404, response.text
    

def test_delete_game_not_exists(client: TestClient):
    response = client.delete(f"/games/{0}")
    assert response.status_code == 404, response.text
