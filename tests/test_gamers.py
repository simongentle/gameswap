from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Game, Gamer


def test_create_gamer(client: TestClient) -> None:
    gamer_data = {
        "name": "Player One",
        "email": "press@start.com",
    }
    response = client.post("/gamers", json=gamer_data)
    data = response.json()

    assert response.status_code == 200, response.text
    assert (
        "id" in data
        and data["name"] == gamer_data["name"]
        and data["email"] == gamer_data["email"]
    )


def test_create_gamer_invalid_email(client: TestClient) -> None:
    gamer_data = {
        "name": "Player Zero",
        "email": "gameover.com",
    }
    response = client.post("/gamers", json=gamer_data)
    assert response.status_code == 422, response.text


def test_get_gamer(session: Session, client: TestClient) -> None:
    gamer = Gamer(name="Player One", email="press@start.com")
    session.add(gamer)
    session.commit()

    response = client.get(f"/gamers/{gamer.id}")
    data = response.json()

    assert response.status_code == 200, response.text
    assert (
        data["id"] == gamer.id
        and data["name"] == gamer.name
        and data["email"] == gamer.email
    )


def test_get_gamer_not_exists(client: TestClient) -> None:
    response = client.get(f"/gamers/{0}")
    assert response.status_code == 404, response.text


def test_gamer_email_not_unique(session: Session, client: TestClient) -> None:
    test_email = "press@start.com"

    gamer1 = Gamer(name="Player One", email=test_email)
    session.add(gamer1)
    session.commit()

    gamer2_data = {
        "name": "Player Two",
        "email": test_email,
    }
    response = client.post("/gamers", json=gamer2_data)
    assert response.status_code == 422, response.text


def test_update_gamer(session: Session, client: TestClient) -> None:
    gamer = Gamer(name="Player One", email="press@start.com")
    session.add(gamer)
    session.commit()

    updated_name = "Player One Thousand"
    response = client.patch(f"/gamers/{gamer.id}", json={"name": updated_name})
    data = response.json()
    
    assert response.status_code == 200, response.text
    assert (
        data["id"] == gamer.id
        and data["name"] == gamer.name == updated_name
        and data["email"] == gamer.email
    )


def test_delete_gamer(session: Session, client: TestClient) -> None:
    gamer = Gamer(name="Player One", email="press@start.com")
    session.add(gamer)
    session.commit()

    response = client.delete(f"/gamers/{gamer.id}")
    assert response.status_code == 200, response.text

    gamer_in_db = session.get(Gamer, gamer.id)
    assert gamer_in_db is None
    

def test_delete_gamer_not_exists(client: TestClient) -> None:
    response = client.delete(f"/gamers/{0}")
    assert response.status_code == 404, response.text


def test_get_games_for_given_gamer(session: Session, client: TestClient) -> None:
    gamer = Gamer(name="Player One", email="press@start.com")
    session.add(gamer)
    session.commit()
    
    game1 = Game(title="Sonic The Hedgehog", platform="SEGA Mega Drive", gamer_id=gamer.id)
    game2 = Game(title="Super Mario Land", platform="GAME BOY", gamer_id=gamer.id)
    session.add_all([game1, game2])
    session.commit()

    response = client.get(f"/gamers/{gamer.id}/games")
    data = response.json()

    assert response.status_code == 200, response.text
    assert len(data) == 2


def test_get_gamers_who_own_game(session: Session, client: TestClient) -> None:
    gamer1 = Gamer(name="Player One", email="press@start.com")
    gamer2 = Gamer(name="Player Two", email="insert@coin.com")
    session.add_all([gamer1, gamer2])
    session.commit()
    
    title = "Sonic The Hedgehog"
    platform = "SEGA Mega Drive"
    game1 = Game(title=title, platform=platform, gamer_id=1)
    game2 = Game(title=title, platform=platform, gamer_id=2)
    session.add_all([game1, game2])
    session.commit()

    game_query = {"title": title, "platform": platform}

    response = client.get(f"/gamers?game={game_query}")
    data = response.json()

    assert response.status_code == 200, response.text
    assert len(data) == 2
