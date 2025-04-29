from pydantic import BaseModel


class LessonType(BaseModel):
    id: str
    mask: str
    name: str
