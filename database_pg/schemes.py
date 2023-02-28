from pydantic import BaseModel


class ResultBase(BaseModel):
    key: str
    order_number: int
    result: str


class Result(ResultBase):
    id: int

    class Config:
        orm_mode = True
