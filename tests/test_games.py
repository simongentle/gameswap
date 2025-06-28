import pytest

from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

from app.models.game import Base
from app.main import app
from app.dependencies.database import get_db_session


DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db_session():
    database = TestingSessionLocal()
    yield database
    database.close()


app.dependency_overrides[get_db_session] = override_get_db_session
client = TestClient(app)


def test_create_game(test_db) -> None:
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


def test_get_game(test_db) -> None:
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


def test_get_game_not_exists(test_db):
    response = client.get(f"/games/{0}")
    assert response.status_code == 404, response.text


def test_delete_game_not_exists(test_db):
    response = client.delete(f"/games/{0}")
    assert response.status_code == 404, response.text
