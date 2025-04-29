from typing import Optional, List

from pydantic import BaseModel

from model.school_response_journal.mark_id import MarkId


class MarkType(BaseModel):
    id: str
    marks: List[MarkId]
    mask: str
    name: str
    scale: str
