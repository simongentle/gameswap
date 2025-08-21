from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from app.crud.swaps import delete_expired_swaps
from app.dependencies.database import configured_session, init_db
from app.routers import games, gamers, swaps


PROJECT_NAME = "gameswap"
PROJECT_SUMMARY = "track game swaps with friends"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    scheduler = AsyncIOScheduler()

    with configured_session() as session:
        scheduler.add_job(delete_expired_swaps, "cron", args=(session,), hour="0", minute="1")

    scheduler.start()
    yield
    scheduler.shutdown()


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
