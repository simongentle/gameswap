# gameswap

API to swap games with friends

## Requirements

- Python 3.11
- FastAPI
- Pydantic
- SQLAlchemy

## Documentation

Start the uvicorn session by running

`python3 -m app.main`

and then navigate to the interactive Swagger UI documentation:

> <http://localhost:8000/docs>

NB: Must manually remove database file `gameswap.db` after closing the session.


## Tests

Endpoint tests rely on FastAPI's `TestClient` and use an in-memory SQLite database where necessary.

Run tests in the terminal via

`pytest tests`
