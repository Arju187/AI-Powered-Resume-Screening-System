from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class JobCreate(BaseModel):
    title: str
    company: Optional[str] = "OctoSafes"
    location: Optional[str] = None
    employment_type: Optional[str] = "Full-time"
    salary: Optional[float] = None
    required_experience: Optional[float] = 0
    required_skills: List[str] = []
    responsibilities: Optional[str] = None
    description: Optional[str] = None
    closing_date: Optional[datetime] = None


class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    salary: Optional[float] = None
    required_experience: Optional[float] = None
    required_skills: Optional[List[str]] = None
    responsibilities: Optional[str] = None
    description: Optional[str] = None
    closing_date: Optional[datetime] = None
    status: Optional[str] = None  # "open" / "closed"


class JobOut(BaseModel):
    id: int
    title: str
    company: str
    location: Optional[str] = None
    employment_type: str
    salary: Optional[float] = None
    required_experience: float
    required_skills: List[str] = []
    responsibilities: Optional[str] = None
    description: Optional[str] = None
    posted_date: datetime
    closing_date: Optional[datetime] = None
    status: str
    applicants_count: int = 0

    class Config:
        from_attributes = True


class RankedCandidateOut(BaseModel):
    application_id: int
    candidate_id: int
    full_name: str
    email: str
    ats_score: float
    recommendation_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    years_experience: float
    application_status: str
