from pydantic import BaseModel


class ChangeReason(BaseModel):
    id: str
    name: str
