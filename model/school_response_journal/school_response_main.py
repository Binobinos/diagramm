from typing import List

from pydantic import BaseModel

from model.school_response_journal.change_reason import ChangeReason
from model.school_response_journal.control_type import ControlType
from model.school_response_journal.control import Control
from model.school_response_journal.journal import Journal
from model.school_response_journal.lesson import Lesson
from model.school_response_journal.lesson_type import LessonType
from model.school_response_journal.mark_type import MarkType
from model.school_response_journal.marks import Mark
from model.school_response_journal.member import Member
from model.school_response_journal.period import Period


class Response(BaseModel):
    change_reasons: List[ChangeReason]
    control_types: List[ControlType]
    controls: List[Control]
    deleted_controls: list = []
    deleted_lessons: list = []
    deleted_marks: list = []
    holidays: list = []
    journal: Journal
    lesson_types: List[LessonType]
    lessons: List[Lesson]
    mark_types: List[MarkType]
    marks: List[Mark]
    members: List[Member]
    periods: List[Period]
    timestamp: str
