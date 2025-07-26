import datetime as dt

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Game, Gamer, Swap


def test_create_swap(client: TestClient) -> None:
    return_date = dt.date.today() + dt.timedelta(weeks=2)
    swap_data = {
        "return_date": return_date.strftime("%Y-%m-%d"),
    }
    response = client.post("/swaps", json=swap_data)
    data = response.json()

    assert response.status_code == 200, response.text
    assert (
        "id" in data
        and data["return_date"] == swap_data["return_date"]
    )


def test_create_swap_incomplete(client: TestClient) -> None:
    response = client.post("/swaps", json={})
    assert response.status_code == 422, response.text


def test_create_swap_past_return_date(client: TestClient) -> None:
    return_date = dt.date.today() - dt.timedelta(weeks=2)
    swap_data = {
        "return_date": return_date.strftime("%Y-%m-%d"),
    }
    response = client.post("/swaps", json=swap_data)
    assert response.status_code == 422, response.text


def test_get_swap(session: Session, client: TestClient) -> None:
    swap = Swap(return_date=dt.date.today() + dt.timedelta(weeks=2))
    session.add(swap)
    session.commit()

    response = client.get(f"/swaps/{swap.id}")
    data = response.json()

    assert response.status_code == 200, response.text
    assert (
        data["id"] == swap.id
        and data["return_date"] == swap.return_date.strftime("%Y-%m-%d")
    )


def test_get_swap_not_exists(client: TestClient) -> None:
    response = client.get(f"/swaps/{0}")
    assert response.status_code == 404, response.text


def test_update_swap(session: Session, client: TestClient) -> None:
    initial_return_date = dt.date.today() + dt.timedelta(weeks=2)
    swap = Swap(return_date=initial_return_date)
    session.add(swap)
    session.commit()

    later_return_date = initial_return_date + dt.timedelta(weeks=2)
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


def test_delete_swap(session: Session, client: TestClient) -> None:
    swap = Swap(return_date=dt.date.today() + dt.timedelta(weeks=2))
    session.add(swap)
    session.commit()

    lent_game = Game(
        title="Sonic The Hedgehog", 
        platform="SEGA Mega Drive", 
        swap_id=swap.id,
    )
    borrowed_game = Game(
        title="Super Mario Land", 
        platform="GAME BOY", 
        swap_id=swap.id,
    )
    session.add_all([lent_game, borrowed_game])
    session.commit()

    response = client.delete(f"/swaps/{swap.id}")
    assert response.status_code == 200, response.text

    swap_in_db = session.get(Swap, swap.id)
    assert swap_in_db is None

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

    lent_game = Game(
        title="Sonic The Hedgehog", 
        platform="SEGA Mega Drive", 
        swap_id=swap.id,
    )
    borrowed_game = Game(
        title="Super Mario Land", 
        platform="GAME BOY", 
        swap_id=swap.id,
    )
    session.add_all([swap, lent_game, borrowed_game])
    session.commit()

    response = client.get(f"/swaps/{swap.id}/games")
    data = response.json()

    assert response.status_code == 200, response.text
    assert len(data) == 2
    

def test_assign_gamer_to_swap(session: Session, client: TestClient) -> None:
    swap = Swap(return_date=dt.date.today() + dt.timedelta(weeks=2))
    gamer = Gamer(name="Player One", email="press@start.com")
    session.add_all([swap, gamer])
    session.commit()

    response = client.put(f"/swaps/{swap.id}/gamers/{gamer.id}")
    assert response.status_code == 200, response.text
    assert len(swap.gamers) == 1


def test_cannot_exceed_two_gamers_in_swap(session: Session, client: TestClient) -> None:
    swap = Swap(return_date=dt.date.today() + dt.timedelta(weeks=2))
    gamer1 = Gamer(name="Player One", email="gamer1@email.com")
    gamer2 = Gamer(name="Player Two", email="gamer2@email.com")
    gamer3 = Gamer(name="Player Three", email="gamer3@email.com")
    session.add_all([swap, gamer1, gamer2, gamer3])
    session.commit()

    response = client.put(f"/swaps/{swap.id}/gamers/{gamer1.id}")
    assert response.status_code == 200, response.text
    assert len(swap.gamers) == 1

    response = client.put(f"/swaps/{swap.id}/gamers/{gamer2.id}")
    assert response.status_code == 200, response.text
    assert len(swap.gamers) == 2

    response = client.put(f"/swaps/{swap.id}/gamers/{gamer3.id}")
    assert response.status_code == 422, response.text


def test_assign_game_of_gamer_to_swap(session: Session, client: TestClient) -> None:
    swap = Swap(return_date=dt.date.today() + dt.timedelta(weeks=2))
    gamer = Gamer(name="Player One", email="press@start.com")
    game = Game(title="Sonic The Hedgehog", platform="SEGA Mega Drive")
    session.add_all([swap, gamer, game])
    session.commit()

    gamer.games.append(game)
    swap.gamers.append(gamer)

    response = client.put(f"/swaps/{swap.id}/gamers/{gamer.id}/games/{game.id}")
    assert response.status_code == 200, response.text
    assert len(swap.games) == 1


def test_remove_gamer_from_swap(session: Session, client: TestClient) -> None:
    swap = Swap(return_date=dt.date.today() + dt.timedelta(weeks=2))
    gamer = Gamer(name="Player One", email="press@start.com")
    game1 = Game(title="Sonic The Hedgehog", platform="SEGA Mega Drive")
    game2 = Game(title="Super Mario Land", platform="GAME BOY")
    session.add_all([swap, gamer, game1, game2])
    session.commit()

    for game in [game1, game2]:
        gamer.games.append(game)
    swap.gamers.append(gamer)
    for game in [game1, game2]:
        swap.games.append(game)

    response = client.delete(f"/swaps/{swap.id}/gamers/{gamer.id}")
    assert response.status_code == 204, response.text
    
    assert gamer not in swap.gamers
    assert len(swap.games) == 0

    response = client.delete(f"/swaps/{swap.id}/gamers/{gamer.id}")
    assert response.status_code == 422, response.text


def test_remove_game_of_gamer_from_swap(session: Session, client: TestClient) -> None:
    swap = Swap(return_date=dt.date.today() + dt.timedelta(weeks=2))
    gamer = Gamer(name="Player One", email="press@start.com")
    game = Game(title="Sonic The Hedgehog", platform="SEGA Mega Drive")
    session.add_all([swap, gamer, game])
    session.commit()
    
    gamer.games.append(game)
    swap.gamers.append(gamer)
    swap.games.append(game)

    response = client.delete(f"/swaps/{swap.id}/gamers/{gamer.id}/games/{game.id}")
    assert response.status_code == 204, response.text
    assert game not in swap.games

    response = client.delete(f"/swaps/{swap.id}/gamers/{gamer.id}/games/{game.id}")
    assert response.status_code == 422, response.text
