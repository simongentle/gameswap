from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Game, Gamer, Swap


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
        and data["swap_id"] is None
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
        and data["swap_id"] is None
    )


def test_get_game_not_exists(client: TestClient) -> None:
    response = client.get(f"/games/{0}")
    assert response.status_code == 404, response.text


def test_get_games(swap: Swap, session: Session, client: TestClient) -> None:
    new_game = Game(title="Ristar", platform="SEGA Mega Drive", gamer_id=swap.proposer.id)
    session.add(new_game)
    session.commit()

    response = client.get("/games")
    data = response.json()

    assert response.status_code == 200, response.text
    assert len(data) == 3

    response = client.get("/games?only_available=True")
    data = response.json()

    assert response.status_code == 200, response.text
    assert len(data) == 1
    assert data[0]["swap_id"] is None


def test_update_game(session: Session, client: TestClient) -> None:
    gamer = Gamer(name="Player One", email="press@start.com")
    session.add(gamer)
    session.commit()

    game = Game(title="Sonic The Hedgehog", platform="SEGA Mega Drive", gamer_id=gamer.id)
    session.add(game)
    session.commit()

    new_platform = "SEGA Master System"
    response = client.patch(f"/games/{game.id}", json={"platform": new_platform})
    data = response.json()
    
    assert response.status_code == 200, response.text
    assert (
        data["id"] == game.id
        and data["title"] == game.title 
        and data["platform"] == game.platform == new_platform
        and data["swap_id"] is None
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


def test_cannot_delete_game_if_in_swap(swap: Swap, client: TestClient) -> None:
    response = client.delete(f"/games/{swap.games[0].id}")
    assert response.status_code == 422, response.text
