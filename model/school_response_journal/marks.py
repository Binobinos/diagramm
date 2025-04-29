from pydantic import BaseModel


class Mark(BaseModel):
    control_id: str
    id: str
    is_used: str
    student_id: str
    text: str
    type_id: str
