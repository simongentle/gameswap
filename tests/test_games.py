from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Status, Game as DBGame


def test_create_game(client: TestClient) -> None:
    game_data = {
        "title": "Sonic The Hedehog",
        "platform": "SEGA Mega Drive",
    }
    response = client.post("/games", json=game_data)
    data = response.json()

    assert response.status_code == 200, response.text
    assert (
        "id" in data
        and data["title"] == game_data["title"]
        and data["platform"] == game_data["platform"]
        and data["status"] == Status.OWNED.value
        and not data["swap_id"]
    )


def test_create_game_incomplete(client: TestClient) -> None:
    response = client.post("/games", json={"title": "Sonic The Hedehog"})
    assert response.status_code == 422, response.text


def test_create_game_invalid_status(client: TestClient) -> None:
    game_data = {
        "title": "Crash Bandicoot",
        "platform": "PlayStation",
        "status": "stolen",
    }
    response = client.post("/games", json=game_data)
    assert response.status_code == 422, response.text


def test_get_game(session: Session, client: TestClient) -> None:
    game = DBGame(title="Sonic The Hedehog", platform="SEGA Mega Drive")
    session.add(game)
    session.commit()

    response = client.get(f"/games/{game.id}")
    data = response.json()

    assert response.status_code == 200, response.text
    assert (
        data["id"] == game.id
        and data["title"] == game.title
        and data["platform"] == game.platform
        and data["status"] == Status.OWNED.value
    )


def test_get_game_not_exists(client: TestClient) -> None:
    response = client.get(f"/games/{0}")
    assert response.status_code == 404, response.text


def test_update_game(session: Session, client: TestClient) -> None:
    game = DBGame(title="Sonic The Hedehog", platform="SEGA Mega Drive")
    session.add(game)
    session.commit()

    response = client.patch(f"/games/{game.id}", json={"status": "borrowed"})
    data = response.json()
    
    assert response.status_code == 200, response.text
    assert (
        data["id"] == game.id
        and data["title"] == game.title
        and data["platform"] == game.platform
        and data["status"] == Status.BORROWED.value
    )


def test_delete_game(session: Session, client: TestClient) -> None:
    game = DBGame(title="Sonic The Hedehog", platform="SEGA Mega Drive")
    session.add(game)
    session.commit()

    response = client.delete(f"/games/{game.id}")
    assert response.status_code == 200, response.text

    game_in_db = session.get(DBGame, game.id)
    assert game_in_db is None
    

def test_delete_game_not_exists(client: TestClient) -> None:
    response = client.delete(f"/games/{0}")
    assert response.status_code == 404, response.text
