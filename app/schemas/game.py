from pydantic import BaseModel


class GameBase(BaseModel):
    title: str
    platform: str


class GameCreate(GameBase):
    pass


class GameUpdate(GameBase):
    pass


class Game(GameBase):
    id: int
    title: str
    platform: str
