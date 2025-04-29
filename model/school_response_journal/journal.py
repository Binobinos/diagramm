from pydantic import BaseModel


class Journal(BaseModel):
    chat_id: str
    copp: str
    date_end: str
    date_start: str
    daymask: str
    duration: str
    grade_id: str
    grade_name: str
    grade_type: str
    id: str
    is_cm: str
    is_corr: str
    is_ind: str
    name: str
    ou_type: str
    ptp_id: str
    ptp_pending: str
    rcm_mode: str
    role_id: str
    stage: str
    subject_id: str
    subject_name: str
    teacher_id: str
    teacher_name: str
    type_id: str
    vk_enabled: str
