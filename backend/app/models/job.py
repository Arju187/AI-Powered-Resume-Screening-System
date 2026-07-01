import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship

from app.database import Base


class JobStatusEnum(str, enum.Enum):
    open = "open"
    closed = "closed"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False, index=True)
    company = Column(String(150), nullable=False, default="OctoSafes")
    location = Column(String(150), nullable=True)
    employment_type = Column(String(50), default="Full-time")  # Full-time/Part-time/Internship/Contract
    salary = Column(Float, nullable=True)
    required_experience = Column(Float, default=0)  # in years
    required_skills = Column(JSON, default=list)     # list[str]
    responsibilities = Column(Text, nullable=True)
    description = Column(Text, nullable=True)

    posted_date = Column(DateTime, default=datetime.utcnow)
    closing_date = Column(DateTime, nullable=True)
    status = Column(Enum(JobStatusEnum), default=JobStatusEnum.open)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
