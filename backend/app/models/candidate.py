from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class CandidateProfile(Base):
    """Professional profile + latest ATS score for a candidate user."""
    __tablename__ = "candidate_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    current_company = Column(String(150), nullable=True)
    current_designation = Column(String(150), nullable=True)
    years_experience = Column(Float, default=0)
    highest_qualification = Column(String(150), nullable=True)
    location = Column(String(150), nullable=True)
    preferred_job_role = Column(String(150), nullable=True)
    expected_salary = Column(Float, nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    github_url = Column(String(255), nullable=True)
    portfolio_url = Column(String(255), nullable=True)

    technical_skills = Column(JSON, default=list)   # list[str], manually entered + resume-extracted (merged)
    soft_skills = Column(JSON, default=list)         # list[str]

    profile_picture_path = Column(String(255), nullable=True)
    resume_path = Column(String(255), nullable=True)

    profile_completion = Column(Float, default=0)    # 0-100
    ats_score = Column(Float, default=0)              # 0-100, latest computed score
    ats_breakdown = Column(JSON, default=dict)        # {"skill_match": .., "experience": .., ...}

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="candidate_profile")
    resume_data = relationship(
        "ResumeData", back_populates="candidate", uselist=False, cascade="all, delete-orphan"
    )
    applications = relationship("Application", back_populates="candidate", cascade="all, delete-orphan")


class ResumeData(Base):
    """
    Structured output of the resume parser. In the original enterprise spec
    this lives in MongoDB; here it's a JSON-bearing SQL table so the whole
    system runs on one database (see docs/ARCHITECTURE.md).
    """
    __tablename__ = "resume_data"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidate_profiles.id"), unique=True, nullable=False)

    raw_text = Column(Text, nullable=True)
    extracted_name = Column(String(150), nullable=True)
    extracted_email = Column(String(150), nullable=True)
    extracted_phone = Column(String(30), nullable=True)

    skills = Column(JSON, default=list)          # list[str] normalized skills found in resume
    education = Column(JSON, default=list)       # list[str] lines under education section
    experience = Column(JSON, default=list)      # list[str] lines under experience section
    projects = Column(JSON, default=list)        # list[str]
    certifications = Column(JSON, default=list)  # list[str]
    summary = Column(Text, nullable=True)

    parsed_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("CandidateProfile", back_populates="resume_data")
