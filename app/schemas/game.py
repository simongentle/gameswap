from pydantic import BaseModel


class GameBase(BaseModel):
    title: str
    platform: str
    available: bool = True
    gamer_id: int


class GameCreate(GameBase):
    pass


class GameUpdate(BaseModel):
    title: str | None = None
    platform: str | None = None
    available: bool | None = None


class Game(GameBase):
    id: int
