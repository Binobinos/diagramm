from pydantic import BaseModel


class MarkId(BaseModel):
    cost: str
    id: str
    key: str
    mask: str
    name: str
    shortname: str
