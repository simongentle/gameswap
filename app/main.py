from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from app.dependencies.database import init_db
from app.routers import games


PROJECT_NAME = "gameswap"
PROJECT_SUMMARY = "track game swaps with friends"
DB_FILE = "sqlite:///gameswap.db"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(DB_FILE)
    yield


app = FastAPI(
    title=PROJECT_NAME, 
    summary=PROJECT_SUMMARY,
    lifespan=lifespan,
)


@app.get("/", tags=["root"])
def read_root():
    return "The server is running."


app.include_router(games.router, tags=["games"])


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
