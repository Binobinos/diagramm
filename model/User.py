from typing import Dict, Optional
from uuid import uuid4  # Используем UUID вместо int

from pydantic import BaseModel

from model.order import Orders


class User(BaseModel):
    id: int
    username: str
    ban: bool = False
    password: str = "qwerty123456"
    full_name: str
    parallel: int
    class_name: str
    balance: Optional[float] = 0.00
    user_level: Optional[str] = "Default User"
    desired_rating: Optional[float] = 0.00
    max_limits: Optional[int] = 1
    temp_order: Optional[Dict] = {}
    order: Optional[Orders] = Orders(id=str(uuid4()), product=[])
