from pydantic import BaseModel


class ControlType(BaseModel):
    cost: str
    desc: str
    id: str
    mask: str
    master: str
    name: str
    shortname: str
