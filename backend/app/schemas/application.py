from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class ApplicationCreate(BaseModel):
    job_id: int
    cover_letter: Optional[str] = None
    preferred_salary: Optional[float] = None
    notice_period: Optional[str] = None


class ApplicationStatusUpdate(BaseModel):
    status: str  # one of ApplicationStatusEnum values


class ApplicationOut(BaseModel):
    id: int
    job_id: int
    job_title: str
    company: str
    status: str
    recommendation_score: float
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    ats_score_snapshot: float
    applied_at: datetime

    class Config:
        from_attributes = True


class NotificationOut(BaseModel):
    id: int
    title: str
    message: str
    notif_type: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
