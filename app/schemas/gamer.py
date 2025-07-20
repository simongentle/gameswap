from pydantic import BaseModel, EmailStr


class GamerBase(BaseModel):
    name: str
    email: EmailStr


class GamerCreate(GamerBase):
    pass


class GamerUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None


class Gamer(GamerBase):
    id: int
