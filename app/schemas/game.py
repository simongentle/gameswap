from pydantic import BaseModel

from app.models.game import Status


class GameBase(BaseModel):
    title: str
    platform: str
    status: Status = Status.OWNED


class GameCreate(GameBase):
    pass


class GameUpdate(GameBase):
    title: str | None = None
    platform: str | None = None
    status: Status | None = None


class Game(GameBase):
    id: int
