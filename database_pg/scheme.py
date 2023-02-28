from pydantic import BaseModel


class ResultBase(BaseModel):
    order_number: int
    result: str


class Result(ResultBase):
    key: str

    class Config:
        orm_mode = True
