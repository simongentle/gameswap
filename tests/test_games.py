from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Game as DBGame


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
        and not data["swap_id"]
    )


def test_create_game_incomplete(client: TestClient) -> None:
    response = client.post("/games", json={"title": "Sonic The Hedehog"})
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
    )


def test_get_game_not_exists(client: TestClient) -> None:
    response = client.get(f"/games/{0}")
    assert response.status_code == 404, response.text


def test_get_games_by_title(session: Session, client: TestClient) -> None:
    game_1 = DBGame(title="Sonic The Hedehog", platform="SEGA Mega Drive")
    session.add(game_1)
    game_2 = DBGame(title="Super Mario Land", platform="GAME BOY")
    session.add(game_2)
    session.commit()

    response = client.get(f"/games?title={game_1.title}")
    data = response.json()

    assert response.status_code == 200, response.text
    assert len(data) == 1


def test_update_game(session: Session, client: TestClient) -> None:
    game = DBGame(title="Sonic The Hedehog", platform="SEGA Mega Drive")
    session.add(game)
    session.commit()

    updated_title = "Ristar"
    response = client.patch(f"/games/{game.id}", json={"title": updated_title})
    data = response.json()
    
    assert response.status_code == 200, response.text
    assert (
        data["id"] == game.id
        and data["title"] == game.title == updated_title
        and data["platform"] == game.platform
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
