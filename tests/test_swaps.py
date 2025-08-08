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


def test_create_swap_past_return_date(session: Session, client: TestClient) -> None:
    return_date = dt.date.today() - dt.timedelta(weeks=2)
    
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

    assert response.status_code == 422, response.text


def test_create_swap_duplicate_game_info(session: Session, client: TestClient) -> None:
    return_date = dt.date.today() + dt.timedelta(weeks=2)
    
    proposer = Gamer(name="Player One", email="press@start.com")
    acceptor = Gamer(name="Player Two", email="insert@coin.com")
    session.add_all([proposer, acceptor])
    session.commit()

    proposer_game = Game(title="Sonic The Hedgehog", platform="SEGA Mega Drive", gamer_id=proposer.id)
    acceptor_game = Game(title="Sonic The Hedgehog", platform="SEGA Mega Drive", gamer_id=acceptor.id)
    session.add_all([proposer_game, acceptor_game])
    session.commit()

    swap_data = {
        "return_date": return_date.strftime("%Y-%m-%d"),
        "proposer_id": proposer.id,
        "acceptor_id": acceptor.id,
        "games": [to_dict(game) for game in (proposer_game, acceptor_game)]
    }
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
    

def test_get_gamers_for_given_swap(session: Session, client: TestClient) -> None:
    swap = Swap(return_date=dt.date.today() + dt.timedelta(weeks=2))
    gamer1 = Gamer(name="Player One", email="press@start.com")
    gamer2 = Gamer(name="Player Two", email="insert@coin.com")
    session.add_all([swap, gamer1, gamer2])
    session.commit()

    swap.gamers = [gamer1, gamer2]

    response = client.get(f"/swaps/{swap.id}/gamers")
    data = response.json()

    assert response.status_code == 200, response.text
    assert len(data) == 2


def test_get_games_for_given_swap(session: Session, client: TestClient) -> None:
    swap = Swap(return_date=dt.date.today() + dt.timedelta(weeks=2))
    session.add(swap)
    session.commit()

    gamer1 = Gamer(name="Player One", email="press@start.com")
    gamer2 = Gamer(name="Player Two", email="insert@coin.com")
    session.add_all([gamer1, gamer2])
    session.commit()

    lent_game = Game(
        title="Sonic The Hedgehog", 
        platform="SEGA Mega Drive", 
        gamer_id=1,
        swap_id=swap.id,
    )
    borrowed_game = Game(
        title="Super Mario Land", 
        platform="GAME BOY", 
        gamer_id=2,
        swap_id=swap.id,
    )
    session.add_all([lent_game, borrowed_game])
    session.commit()

    response = client.get(f"/swaps/{swap.id}/games")
    data = response.json()

    assert response.status_code == 200, response.text
    assert len(data) == 2


def test_assign_game_of_gamer_to_swap(session: Session, client: TestClient) -> None:
    swap = Swap(return_date=dt.date.today() + dt.timedelta(weeks=2))
    gamer = Gamer(name="Player One", email="press@start.com")
    session.add_all([swap, gamer])
    session.commit()

    game = Game(title="Sonic The Hedgehog", platform="SEGA Mega Drive", gamer_id=gamer.id)
    session.add(game)
    session.commit()

    swap.gamers.append(gamer)

    response = client.put(f"/swaps/{swap.id}/gamers/{gamer.id}/games/{game.id}")
    assert response.status_code == 200, response.text
    assert len(swap.games) == 1


def test_remove_game_of_gamer_from_swap(session: Session, client: TestClient) -> None:
    swap = Swap(return_date=dt.date.today() + dt.timedelta(weeks=2))
    gamer = Gamer(name="Player One", email="press@start.com")
    session.add_all([swap, gamer])
    session.commit()

    game = Game(title="Sonic The Hedgehog", platform="SEGA Mega Drive", gamer_id=gamer.id)
    session.add(game)
    session.commit()
    
    swap.gamers.append(gamer)
    swap.games.append(game)

    response = client.delete(f"/swaps/{swap.id}/gamers/{gamer.id}/games/{game.id}")
    assert response.status_code == 204, response.text
    assert game not in swap.games

    response = client.delete(f"/swaps/{swap.id}/gamers/{gamer.id}/games/{game.id}")
    assert response.status_code == 422, response.text
