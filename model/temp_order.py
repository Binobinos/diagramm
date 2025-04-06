from typing import Optional
from uuid import uuid4

from pydantic import BaseModel


class TempOrder(BaseModel):
    id: str = str(uuid4())
    object: str
    quarter: str
    type: str
    estimation: str
    price: float = 0.00
    discount: Optional[float] = 1.00
