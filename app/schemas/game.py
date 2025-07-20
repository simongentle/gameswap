from pydantic import BaseModel


class GameBase(BaseModel):
    title: str
    platform: str
    swap_id: int | None = None


class GameCreate(GameBase):
    pass


class GameUpdate(BaseModel):
    title: str | None = None
    platform: str | None = None
    swap_id: int | None = None


class Game(GameBase):
    id: int
