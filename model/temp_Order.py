from uuid import uuid4, UUID
from pydantic import BaseModel
from typing import Optional

class Temp_order(BaseModel):
    id: str = str(uuid4())
    object: str
    quarter: str
    type: str
    estimation: str
    price: float = 0.00
    discount: Optional[float] = 1.00
