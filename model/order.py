from typing import List, Union,Optional
from uuid import uuid4

from pydantic import BaseModel

from model.temp_Order import Temp_order


class Orders(BaseModel):
    id: str = str(uuid4())
    user_id: Optional[int] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    parallel: Optional[int] = None
    class_name: Optional[str] = None
    price: Union[float] = 0.00
    discount: Union[float] = 1.00
    products: List[Temp_order] = []
