from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class CandidateProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    current_company: Optional[str] = None
    current_designation: Optional[str] = None
    years_experience: Optional[float] = None
    highest_qualification: Optional[str] = None
    location: Optional[str] = None
    preferred_job_role: Optional[str] = None
    expected_salary: Optional[float] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    technical_skills: Optional[List[str]] = None
    soft_skills: Optional[List[str]] = None


class ResumeDataOut(BaseModel):
    extracted_name: Optional[str] = None
    extracted_email: Optional[str] = None
    extracted_phone: Optional[str] = None
    skills: List[str] = []
    education: List[str] = []
    experience: List[str] = []
    projects: List[str] = []
    certifications: List[str] = []
    summary: Optional[str] = None
    parsed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CandidateProfileOut(BaseModel):
    id: int
    user_id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    current_company: Optional[str] = None
    current_designation: Optional[str] = None
    years_experience: float = 0
    highest_qualification: Optional[str] = None
    location: Optional[str] = None
    preferred_job_role: Optional[str] = None
    expected_salary: Optional[float] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    technical_skills: List[str] = []
    soft_skills: List[str] = []
    profile_picture_path: Optional[str] = None
    resume_path: Optional[str] = None
    profile_completion: float = 0
    ats_score: float = 0
    ats_breakdown: dict = {}
    resume_data: Optional[ResumeDataOut] = None

    class Config:
        from_attributes = True


class CandidateListItem(BaseModel):
    """Lightweight row for admin candidate table."""
    id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    years_experience: float = 0
    ats_score: float = 0
    technical_skills: List[str] = []
    location: Optional[str] = None
    resume_path: Optional[str] = None
    applied_jobs_count: int = 0

    class Config:
        from_attributes = True


class JobRecommendation(BaseModel):
    job_id: int
    title: str
    company: str
    matched_skills: List[str]
    missing_skills: List[str]
    recommendation_score: float
