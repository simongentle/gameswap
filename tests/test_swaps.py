import datetime as dt

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Game, Swap


def test_create_swap(client: TestClient) -> None:
    return_date = dt.date.today() + dt.timedelta(weeks=2)
    swap_data = {
        "friend": "Jeroen",
        "return_date": return_date.strftime("%Y-%m-%d"),
    }
    response = client.post("/swaps", json=swap_data)
    data = response.json()

    assert response.status_code == 200, response.text
    assert (
        "id" in data
        and data["friend"] == swap_data["friend"]
        and data["return_date"] == swap_data["return_date"]
    )


def test_create_swap_incomplete(client: TestClient) -> None:
    response = client.post("/swaps", json={"friend": "Jeroen"})
    assert response.status_code == 422, response.text


def test_create_swap_past_return_date(client: TestClient) -> None:
    return_date = dt.date.today() - dt.timedelta(weeks=2)
    swap_data = {
        "friend": "Jeroen",
        "return_date": return_date.strftime("%Y-%m-%d"),
    }
    response = client.post("/swaps", json=swap_data)
    assert response.status_code == 422, response.text


def test_get_swap(session: Session, client: TestClient) -> None:
    swap = Swap(
        friend="Jeroen", 
        return_date=dt.date.today() + dt.timedelta(weeks=2),
    )
    session.add(swap)
    session.commit()

    response = client.get(f"/swaps/{swap.id}")
    data = response.json()

    assert response.status_code == 200, response.text
    assert (
        data["id"] == swap.id
        and data["friend"] == swap.friend
        and data["return_date"] == swap.return_date.strftime("%Y-%m-%d")
    )


def test_get_games_for_given_swap(session: Session, client: TestClient) -> None:
    swap = Swap(
        friend="Jeroen", 
        return_date=dt.date.today() + dt.timedelta(weeks=2),
    )
    session.add(swap)
    session.commit()

    lent_game = Game(
        title="Sonic The Hedehog", 
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

    response = client.get(f"/swaps/{swap.id}/games")
    data = response.json()

    assert response.status_code == 200, response.text
    assert len(data) == 2


def test_get_swap_not_exists(client: TestClient) -> None:
    response = client.get(f"/swaps/{0}")
    assert response.status_code == 404, response.text


def test_update_swap(session: Session, client: TestClient) -> None:
    return_date = dt.date.today() + dt.timedelta(weeks=2)
    swap = Swap(friend="Jeroen", return_date=return_date)
    session.add(swap)
    session.commit()

    later_return_date = return_date + dt.timedelta(weeks=2)
    response = client.patch(
        f"/swaps/{swap.id}", 
        json={"return_date": later_return_date.strftime("%Y-%m-%d")},
    )
    data = response.json()
    
    assert response.status_code == 200, response.text
    assert (
        data["id"] == swap.id
        and data["friend"] == swap.friend)
    assert(
        data["return_date"] 
        == later_return_date.strftime("%Y-%m-%d") 
        == swap.return_date.strftime("%Y-%m-%d")
    )


def test_delete_swap(session: Session, client: TestClient) -> None:
    swap = Swap(
        friend="Jeroen", 
        return_date=dt.date.today() + dt.timedelta(weeks=2),
    )
    session.add(swap)
    session.commit()

    lent_game = Game(
        title="Sonic The Hedehog", 
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
