from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from app.dependencies.database import init_db
from app.routers import games


DB_FILE = "sqlite:///gameswap.db"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(DB_FILE)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return "The server is running."


app.include_router(games.router)


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
