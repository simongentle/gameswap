from pydantic import BaseModel, FutureDate


class SwapBase(BaseModel):
    friend: str
    return_date: FutureDate


class SwapCreate(SwapBase):
    pass


class SwapUpdate(BaseModel):
    friend: str | None = None
    return_date: FutureDate | None = None


class Swap(SwapBase):
    id: int
