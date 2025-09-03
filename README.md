# gameswap

API to swap games with friends

## Requirements

- Python 3.11
- FastAPI
- Pydantic
- SQLAlchemy

## Usage

To explore the API:

1. Start the uvicorn session: 
    ```
    python3 -m app.main
    ```

2. Navigate to the interactive Swagger UI documentation:
    > <http://localhost:8000/docs>

3. It's game time.

4. After closing the session, don't forget to manually remove the database file `gameswap.db`.


## Tests

Endpoint tests rely on FastAPI's `TestClient` and use an in-memory SQLite database where necessary.

To run tests in the terminal:
```
pytest tests
```
