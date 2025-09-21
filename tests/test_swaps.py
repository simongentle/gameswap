from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Game, Gamer, Swap


def test_create_swap(session: Session, client: TestClient) -> None:
    # Populate database with gamers and games
    proposer = Gamer(name="Player One", email="press@start.com")
    acceptor = Gamer(name="Player Two", email="insert@coin.com")
    session.add_all([proposer, acceptor])
    session.commit()

    proposer_game = Game(title="Sonic The Hedgehog", platform="SEGA Mega Drive", gamer_id=proposer.id)
    acceptor_game = Game(title="Super Mario Land", platform="Nintendo GAME BOY", gamer_id=acceptor.id)
    session.add_all([proposer_game, acceptor_game])
    session.commit()

    # Create swap
    swap_data = {
        "proposer": {"id": proposer.id, "game_ids": [proposer_game.id]},
        "acceptor": {"id": acceptor.id, "game_ids": [acceptor_game.id]},
    }
    response = client.post("/swaps", json=swap_data)
    data = response.json()

    assert response.status_code == 200, response.text
    assert (
        "id" in data
        and len(data["games"]) == 2
        and data["proposer"]["name"] == proposer.name
        and data["acceptor"]["name"] == acceptor.name
        and [game["swap_id"] == data["id"] for game in data["games"]]
    )
    assert len(proposer.proposer_swaps) == 1
    assert len(acceptor.acceptor_swaps) == 1


def test_create_swap_duplicate_game_ids(client: TestClient) -> None:
    swap_data = {
        "proposer": {"id": 1, "game_ids": [1, 2]},
        "acceptor": {"id": 2, "game_ids": [2, 3]},
    }
    response = client.post("/swaps", json=swap_data)

    assert response.status_code == 422, response.text


def test_create_swap_valid_request_empty_database(client: TestClient, session: Session) -> None:
    # Valid request:
    swap_data = {
        "proposer": {"id": 1, "game_ids": [1]},
        "acceptor": {"id": 2, "game_ids": [2]},
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


def test_create_swap_valid_request_incorrect_games_assigned_to_gamers(
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
    swap_data = {
        "proposer": {"id": 1, "game_ids": [3]},
        "acceptor": {"id": 2, "game_ids": [4]},
    }

    response = client.post("/swaps", json=swap_data)
    assert response.status_code == 422, response.text


def test_create_swap_valid_request_duplicate_game_info(session: Session, client: TestClient) -> None:
    proposer = Gamer(name="Player One", email="press@start.com")
    acceptor = Gamer(name="Player Two", email="insert@coin.com")
    session.add_all([proposer, acceptor])
    session.commit()

    proposer_game = Game(title="Sonic The Hedgehog", platform="SEGA Mega Drive", gamer_id=proposer.id)
    acceptor_game = Game(title="Sonic The Hedgehog", platform="SEGA Mega Drive", gamer_id=acceptor.id)
    session.add_all([proposer_game, acceptor_game])
    session.commit()

    swap_data = {
        "proposer": {"id": proposer.id, "game_ids": [proposer_game.id]},
        "acceptor": {"id": acceptor.id, "game_ids": [acceptor_game.id]},
    }
    response = client.post("/swaps", json=swap_data)

    assert response.status_code == 422, response.text


def test_create_swap_valid_request_games_in_existing_swap(swap: Swap, client: TestClient) -> None:
    # Find game IDs for existing swap:
    proposer_game_ids = [game.id for game in swap.games if game.gamer_id == swap.proposer_id]
    acceptor_game_ids = [game.id for game in swap.games if game.gamer_id == swap.acceptor_id]

    # Valid request, but games in existing swap: 
    swap_data = {
        "proposer": {"id": swap.proposer_id, "game_ids": proposer_game_ids},
        "acceptor": {"id": swap.acceptor_id, "game_ids": acceptor_game_ids},
    }

    response = client.post("/swaps", json=swap_data)
    assert response.status_code == 422, response.text


def test_get_swap(swap: Swap, client: TestClient) -> None:
    response = client.get(f"/swaps/{swap.id}")
    data = response.json()

    assert response.status_code == 200, response.text
    assert (
        data["id"] == swap.id
        and len(data["games"]) == 2
    )


def test_get_swap_not_exists(client: TestClient) -> None:
    response = client.get(f"/swaps/{0}")
    assert response.status_code == 404, response.text


def test_delete_swap(swap: Swap, client: TestClient, session: Session) -> None:
    response = client.delete(f"/swaps/{swap.id}")
    assert response.status_code == 204, response.text

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
    assert (
        data[0]["swap_id"] is None and data[1]["swap_id"] is None
    )
    

def test_delete_swap_not_exists(client: TestClient) -> None:
    response = client.delete(f"/swaps/{0}")
    assert response.status_code == 404, response.text
    