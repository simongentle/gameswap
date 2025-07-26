from pydantic import BaseModel, FutureDate


class SwapBase(BaseModel):
    return_date: FutureDate


class SwapCreate(SwapBase):
    pass


class SwapUpdate(BaseModel):
    return_date: FutureDate | None = None


class Swap(SwapBase):
    id: int
