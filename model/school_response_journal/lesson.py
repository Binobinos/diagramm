from pydantic import BaseModel


class Lesson(BaseModel):
    completed: str
    date: str
    duration: str
    homework: str
    id: str
    inst: str
    lesson_ptp_id: str
    lesson_type: str
    lt: str
    num: str
    teacher_id: str
    teacher_name: str
    theme: str
