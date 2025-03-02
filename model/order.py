from typing import List, Union
from uuid import uuid4

from pydantic import BaseModel

from model.temp_Order import Temp_order


class Orders(BaseModel):
    id: str = str(uuid4())
    price: Union[float] = 0.00
    discount: Union[float] = 1.00
    products: List[Temp_order] = []
