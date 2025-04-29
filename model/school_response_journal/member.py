from typing import List

from pydantic import BaseModel


class Movement(BaseModel):
    date_in: str
    date_out: str


class Member(BaseModel):
    alias: str
    dm: list
    id: str
    movements: List[Movement]
    type_id: str
