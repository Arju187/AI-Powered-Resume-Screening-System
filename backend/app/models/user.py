import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship

from app.database import Base


class RoleEnum(str, enum.Enum):
    admin = "admin"
    candidate = "candidate"


class User(Base):
    """
    Holds login + role info only. Candidate-specific professional details
    live in CandidateProfile (one-to-one) so the auth table stays lean.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.candidate)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate_profile = relationship(
        "CandidateProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
