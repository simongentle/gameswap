import datetime as dt
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session

from app.models import Base, Swap as DBSwap
from app.main import app
from app.dependencies.database import get_session


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)

    with Session(engine, autocommit=False, autoflush=False) as session:
        yield session


@pytest.fixture(name="client")  
def client_fixture(session: Session):  
    def get_session_override():  
        return session

    app.dependency_overrides[get_session] = get_session_override  

    client = TestClient(app)  
    yield client  
    app.dependency_overrides.clear()  


def test_create_swap(client: TestClient) -> None:
    swap_data = {
        "friend": "Jeroen",
        "return_date": "2025-12-31",
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


def test_get_swap(session: Session, client: TestClient) -> None:
    swap = DBSwap(friend="Jeroen", return_date=dt.date(2025, 12, 31))
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


def test_get_swap_not_exists(client: TestClient) -> None:
    response = client.get(f"/swaps/{0}")
    assert response.status_code == 404, response.text


def test_update_swap(session: Session, client: TestClient) -> None:
    swap = DBSwap(friend="Jeroen", return_date=dt.date(2025, 12, 31))
    session.add(swap)
    session.commit()

    response = client.patch(f"/swaps/{swap.id}", json={"return_date": "2025-10-31"})
    data = response.json()
    
    assert response.status_code == 200, response.text
    assert (
        data["id"] == swap.id
        and data["friend"] == swap.friend
        and data["return_date"] == swap.return_date.strftime("%Y-%m-%d")
    )


def test_delete_swap(session: Session, client: TestClient) -> None:
    swap = DBSwap(friend="Jeroen", return_date=dt.date(2025, 12, 31))
    session.add(swap)
    session.commit()

    response = client.delete(f"/swaps/{swap.id}")
    assert response.status_code == 200, response.text

    swap_in_db = session.get(DBSwap, swap.id)
    assert swap_in_db is None
    

def test_delete_swap_not_exists(client: TestClient) -> None:
    response = client.delete(f"/swaps/{0}")
    assert response.status_code == 404, response.text
