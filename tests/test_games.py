from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Game, Gamer


def test_create_game(session: Session, client: TestClient) -> None:
    gamer = Gamer(name="Player One", email="press@start.com")
    session.add(gamer)
    session.commit()
    
    game_data = {
        "title": "Sonic The Hedgehog",
        "platform": "SEGA Mega Drive",
        "gamer_id": gamer.id,
    }
    response = client.post("/games", json=game_data)
    data = response.json()

    assert response.status_code == 200, response.text
    assert (
        "id" in data
        and data["title"] == game_data["title"]
        and data["platform"] == game_data["platform"]
        and data["gamer_id"] == game_data["gamer_id"]
        and data["available"] == True
    )


def test_create_game_incomplete(client: TestClient) -> None:
    response = client.post("/games", json={"title": "Sonic The Hedgehog"})
    assert response.status_code == 422, response.text


def test_create_game_nonexistent_gamer(client: TestClient) -> None:
    game_data = {
        "title": "Sonic The Hedgehog",
        "platform": "SEGA Mega Drive",
        "gamer_id": 1,
    }
    response = client.post("/games", json=game_data)
    assert response.status_code == 422, response.text


def test_get_game(session: Session, client: TestClient) -> None:
    gamer = Gamer(name="Player One", email="press@start.com")
    session.add(gamer)
    session.commit()
    
    game = Game(title="Sonic The Hedgehog", platform="SEGA Mega Drive", gamer_id=gamer.id)
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
        and data["available"] == True
    )


def test_get_game_not_exists(client: TestClient) -> None:
    response = client.get(f"/games/{0}")
    assert response.status_code == 404, response.text


def test_get_games(session: Session, client: TestClient) -> None:
    gamer = Gamer(name="Player One", email="press@start.com")
    session.add(gamer)
    session.commit()

    game1 = Game(title="Sonic The Hedgehog", platform="SEGA Mega Drive", gamer_id=gamer.id)
    game2 = Game(title="Super Mario Land", platform="GAME BOY", gamer_id=gamer.id)
    session.add_all([game1, game2])
    session.commit()

    response = client.get("/games")
    data = response.json()

    assert response.status_code == 200, response.text
    assert len(data) == 2


def test_update_game(session: Session, client: TestClient) -> None:
    gamer = Gamer(name="Player One", email="press@start.com")
    session.add(gamer)
    session.commit()

    game = Game(title="Sonic The Hedgehog", platform="SEGA Mega Drive", gamer_id=gamer.id)
    session.add(game)
    session.commit()

    response = client.patch(f"/games/{game.id}", json={"available": False})
    data = response.json()
    
    assert response.status_code == 200, response.text
    assert (
        data["id"] == game.id
        and data["title"] == game.title 
        and data["platform"] == game.platform
        and data["available"] == False
    )


def test_delete_game(session: Session, client: TestClient) -> None:
    gamer = Gamer(name="Player One", email="press@start.com")
    session.add(gamer)
    session.commit()
    
    game = Game(title="Sonic The Hedgehog", platform="SEGA Mega Drive", gamer_id=gamer.id)
    session.add(game)
    session.commit()

    response = client.delete(f"/games/{game.id}")
    assert response.status_code == 200, response.text

    game_in_db = session.get(Game, game.id)
    assert game_in_db is None
    

def test_delete_game_not_exists(client: TestClient) -> None:
    response = client.delete(f"/games/{0}")
    assert response.status_code == 404, response.text
    