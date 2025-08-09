import datetime as dt
import pytest

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Game, Gamer, Swap, to_dict


@pytest.fixture
def swap(session: Session) -> Swap:
    return_date = dt.date.today() + dt.timedelta(weeks=2)

    proposer = Gamer(name="Player One", email="press@start.com")
    acceptor = Gamer(name="Player Two", email="insert@coin.com")
    session.add_all([proposer, acceptor])
    session.commit()

    proposer_game = Game(title="Sonic The Hedgehog", platform="SEGA Mega Drive", gamer_id=proposer.id)
    acceptor_game = Game(title="Super Mario Land", platform="GAME BOY", gamer_id=acceptor.id)
    session.add_all([proposer_game, acceptor_game])
    session.commit()

    swap = Swap(return_date=return_date, proposer_id=proposer.id, acceptor_id=acceptor.id)
    session.add(swap)
    session.commit()

    for game in (proposer_game, acceptor_game):
        game.swap_id = swap.id
    session.commit()

    return swap


def test_create_swap(session: Session, client: TestClient) -> None:
    return_date = dt.date.today() + dt.timedelta(weeks=2)

    proposer = Gamer(name="Player One", email="press@start.com")
    acceptor = Gamer(name="Player Two", email="insert@coin.com")
    session.add_all([proposer, acceptor])
    session.commit()

    proposer_game = Game(title="Sonic The Hedgehog", platform="SEGA Mega Drive", gamer_id=proposer.id)
    acceptor_game = Game(title="Super Mario Land", platform="GAME BOY", gamer_id=acceptor.id)
    session.add_all([proposer_game, acceptor_game])
    session.commit()

    swap_data = {
        "return_date": return_date.strftime("%Y-%m-%d"),
        "proposer_id": proposer.id,
        "acceptor_id": acceptor.id,
        "games": [to_dict(game) for game in (proposer_game, acceptor_game)]
    }
    response = client.post("/swaps", json=swap_data)
    data = response.json()

    assert response.status_code == 200, response.text
    assert (
        "id" in data
        and data["return_date"] == swap_data["return_date"]
        and len(data["games"]) == 2
        and [game["id"] == data["id"] for game in data["games"]]
    )
    assert len(proposer.proposer_swaps) == 1
    assert len(acceptor.acceptor_swaps) == 1


def test_create_swap_past_return_date(client: TestClient) -> None:
    return_date = dt.date.today() - dt.timedelta(weeks=2)
    proposer_game = {
        "id": 1,
        "title": "Sonic The Hedgehog",
        "platform": "SEGA Mega Drive",
        "gamer_id": 1,
    }
    acceptor_game = {
        "id": 2,
        "title": "Super Mario Land", 
        "platform": "GAME BOY", 
        "gamer_id": 2,
    }
    swap_data = {
        "return_date": return_date.strftime("%Y-%m-%d"),
        "proposer_id": 1,
        "acceptor_id": 2,
        "games": [proposer_game, acceptor_game]
    }
    response = client.post("/swaps", json=swap_data)

    assert response.status_code == 422, response.text


def test_create_swap_duplicate_game_info(client: TestClient) -> None:
    return_date = dt.date.today() + dt.timedelta(weeks=2) 
    proposer_game = {
        "id": 1,
        "title": "Sonic The Hedgehog",
        "platform": "SEGA Mega Drive",
        "gamer_id": 1,
    }
    acceptor_game = {
        "id": 2,
        "title": "Sonic The Hedgehog",
        "platform": "SEGA Mega Drive",
        "gamer_id": 2,
    }
    swap_data = {
        "return_date": return_date.strftime("%Y-%m-%d"),
        "proposer_id": 1,
        "acceptor_id": 2,
        "games": [proposer_game, acceptor_game]
    }
    response = client.post("/swaps", json=swap_data)

    assert response.status_code == 422, response.text


def test_create_swap_valid_request_empty_database(client: TestClient, session: Session) -> None:
    # Valid request:
    return_date = dt.date.today() + dt.timedelta(weeks=2)
    proposer_game = {
        "id": 1,
        "title": "Sonic The Hedgehog",
        "platform": "SEGA Mega Drive",
        "gamer_id": 1,
    }
    acceptor_game = {
        "id": 2,
        "title": "Super Mario Land", 
        "platform": "GAME BOY", 
        "gamer_id": 2,
    }
    swap_data = {
        "return_date": return_date.strftime("%Y-%m-%d"),
        "proposer_id": 1,
        "acceptor_id": 2,
        "games": [proposer_game, acceptor_game]
    }
    
    # Execute request on empty database:
    response = client.post("/swaps", json=swap_data)
    assert response.status_code == 422, response.text

    # Add gamers only and then execute request:
    proposer = Gamer(name="Player One", email="press@start.com")
    acceptor = Gamer(name="Player Two", email="insert@coin.com")
    session.add_all([proposer, acceptor])
    session.commit()

    response = client.post("/swaps", json=swap_data)
    assert response.status_code == 422, response.text


def test_create_swap_valid_request_inconsistent_with_database(
        session: Session,
        client: TestClient, 
    ) -> None:
    # Four gamers, each with a different game:
    gamers = [Gamer(name=f"gamer{n}", email=f"gamer{n}@retro.com") for n in range(1, 5)]
    session.add_all(gamers)
    session.commit()

    games = [Game(title=f"game{n}", platform="platform", gamer_id=n) for n in range(1, 5)]
    session.add_all(games)
    session.commit()

    # Valid request, but wrong game assigned to each gamer:
    return_date = dt.date.today() + dt.timedelta(weeks=2)
    proposer_game = {
        "id": 3,
        "title": "game3",
        "platform": "platform",
        "gamer_id": 1,
    }
    acceptor_game = {
        "id": 4,
        "title": "game4", 
        "platform": "platform", 
        "gamer_id": 2,
    }
    swap_data = {
        "return_date": return_date.strftime("%Y-%m-%d"),
        "proposer_id": 1,
        "acceptor_id": 2,
        "games": [proposer_game, acceptor_game]
    }
    
    # Execute request:
    response = client.post("/swaps", json=swap_data)
    assert response.status_code == 422, response.text


def test_get_swap(swap: Swap, client: TestClient) -> None:
    response = client.get(f"/swaps/{swap.id}")
    data = response.json()

    assert response.status_code == 200, response.text
    assert (
        data["id"] == swap.id
        and data["return_date"] == swap.return_date.strftime("%Y-%m-%d")
        and len(data["games"]) == 2
    )


def test_get_swap_not_exists(client: TestClient) -> None:
    response = client.get(f"/swaps/{0}")
    assert response.status_code == 404, response.text


def test_update_swap(swap: Swap, client: TestClient) -> None:
    later_return_date = swap.return_date + dt.timedelta(weeks=2)
    response = client.patch(
        f"/swaps/{swap.id}", 
        json={"return_date": later_return_date.strftime("%Y-%m-%d")},
    )
    data = response.json()
    
    assert response.status_code == 200, response.text
    assert data["id"] == swap.id
    assert(
        data["return_date"] 
        == later_return_date.strftime("%Y-%m-%d") 
        == swap.return_date.strftime("%Y-%m-%d")
    )


def test_delete_swap(swap: Swap, client: TestClient, session: Session) -> None:
    response = client.delete(f"/swaps/{swap.id}")
    assert response.status_code == 200, response.text

    swap_in_db = session.get(Swap, swap.id)
    assert swap_in_db is None

    response = client.get(f"/gamers")
    data = response.json()

    assert response.status_code == 200, response.text
    assert len(data) == 2

    response = client.get(f"/games")
    data = response.json()

    assert response.status_code == 200, response.text
    assert len(data) == 2
    

def test_delete_swap_not_exists(client: TestClient) -> None:
    response = client.delete(f"/swaps/{0}")
    assert response.status_code == 404, response.text
    

def test_get_gamers_for_given_swap(swap: Swap, client: TestClient) -> None:
    response = client.get(f"/swaps/{swap.id}/gamers")
    data = response.json()

    assert response.status_code == 200, response.text
    assert len(data) == 2
    assert data[0]["name"] == "Player One"
    assert data[1]["name"] == "Player Two"


def test_get_games_for_given_swap(swap: Swap, client: TestClient) -> None:
    response = client.get(f"/swaps/{swap.id}/games")
    data = response.json()

    assert response.status_code == 200, response.text
    assert len(data) == 2
    assert data[0]["title"] == "Sonic The Hedgehog"
    assert data[1]["title"] == "Super Mario Land"
