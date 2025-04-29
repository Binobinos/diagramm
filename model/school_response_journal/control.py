from pydantic import BaseModel


class Control(BaseModel):
    completed: str
    cost: str
    ext_id: str
    id: str
    lesson_id: str
    system_id: str
    text: str
    type_id: str
