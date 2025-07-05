from pydantic import BaseModel

from app.models import Status


class GameBase(BaseModel):
    title: str
    platform: str
    status: Status = Status.OWNED
    swap_id: int | None = None


class GameCreate(GameBase):
    pass


class GameUpdate(BaseModel):
    title: str | None = None
    platform: str | None = None
    status: Status | None = None
    swap_id: int | None = None


class Game(GameBase):
    id: int
