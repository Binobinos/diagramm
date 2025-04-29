from pydantic import BaseModel


class Period(BaseModel):
    date_from: str
    date_to: str
    type_id: str
