import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON, Enum, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class ApplicationStatusEnum(str, enum.Enum):
    applied = "applied"
    shortlisted = "shortlisted"
    interview_scheduled = "interview_scheduled"
    selected = "selected"
    rejected = "rejected"
    offer_released = "offer_released"
    joined = "joined"


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("candidate_id", "job_id", name="uq_candidate_job"),)

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidate_profiles.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)

    status = Column(Enum(ApplicationStatusEnum), default=ApplicationStatusEnum.applied)
    cover_letter = Column(Text, nullable=True)
    preferred_salary = Column(Float, nullable=True)
    notice_period = Column(String(50), nullable=True)

    recommendation_score = Column(Float, default=0)  # 0-100, computed at apply time
    matched_skills = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    ats_score_snapshot = Column(Float, default=0)    # candidate's ATS score at time of application

    applied_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    candidate = relationship("CandidateProfile", back_populates="applications")
    job = relationship("Job", back_populates="applications")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(150), nullable=False)
    message = Column(String(500), nullable=False)
    notif_type = Column(String(50), default="info")  # info/success/warning
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")
