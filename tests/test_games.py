from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Game, Gamer


def test_create_game(client: TestClient) -> None:
    game_data = {
        "title": "Sonic The Hedgehog",
        "platform": "SEGA Mega Drive",
        "gamer_id": 1,
    }
    response = client.post("/games", json=game_data)
    data = response.json()

    assert response.status_code == 200, response.text
    assert (
        "id" in data
        and data["title"] == game_data["title"]
        and data["platform"] == game_data["platform"]
        and data["gamer_id"] == game_data["gamer_id"]
    )


def test_create_game_incomplete(client: TestClient) -> None:
    response = client.post("/games", json={"title": "Sonic The Hedgehog"})
    assert response.status_code == 422, response.text


def test_get_game(session: Session, client: TestClient) -> None:
    game = Game(title="Sonic The Hedgehog", platform="SEGA Mega Drive", gamer_id=1)
    session.add(game)
    session.commit()

    response = client.get(f"/games/{game.id}")
    data = response.json()

    assert response.status_code == 200, response.text
    assert (
        data["id"] == game.id
        and data["title"] == game.title
        and data["platform"] == game.platform
        and data["gamer_id"] == game.gamer_id
    )


def test_get_game_not_exists(client: TestClient) -> None:
    response = client.get(f"/games/{0}")
    assert response.status_code == 404, response.text


def test_get_games_by_title(session: Session, client: TestClient) -> None:
    game1 = Game(title="Sonic The Hedgehog", platform="SEGA Mega Drive", gamer_id=1)
    game2 = Game(title="Super Mario Land", platform="GAME BOY", gamer_id=1)
    session.add_all([game1, game2])
    session.commit()

    response = client.get(f"/games?title={game1.title}")
    data = response.json()

    assert response.status_code == 200, response.text
    assert len(data) == 1


def test_update_game(session: Session, client: TestClient) -> None:
    game = Game(title="Sonic The Hedgehog", platform="SEGA Mega Drive", gamer_id=1)
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
    game = Game(title="Sonic The Hedgehog", platform="SEGA Mega Drive", gamer_id=1)
    session.add(game)
    session.commit()

    response = client.delete(f"/games/{game.id}")
    assert response.status_code == 200, response.text

    game_in_db = session.get(Game, game.id)
    assert game_in_db is None
    

def test_delete_game_not_exists(client: TestClient) -> None:
    response = client.delete(f"/games/{0}")
    assert response.status_code == 404, response.text
    