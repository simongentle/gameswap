from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from app.dependencies.database import init_db
from app.routers import games, gamers, swaps


PROJECT_NAME = "gameswap"
PROJECT_SUMMARY = "track game swaps with friends"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=PROJECT_NAME, 
    summary=PROJECT_SUMMARY,
    lifespan=lifespan,
)


@app.get("/", tags=["root"])
def read_root():
    return "The server is running."


app.include_router(gamers.router, tags=["gamers"])
app.include_router(games.router, tags=["games"])
app.include_router(swaps.router, tags=["swaps"])


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
