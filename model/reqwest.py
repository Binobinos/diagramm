import datetime
from uuid import uuid4  # Используем UUID вместо int

from pydantic import BaseModel


class Reqwest(BaseModel):
    id_: str = str(uuid4())[:8]
    user_id: int
    username: str
    datetime:datetime.date=datetime.datetime.now()
    messages:str
    type:str
