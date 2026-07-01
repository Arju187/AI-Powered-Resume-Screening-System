"""
Importing every model here ensures Base.metadata.create_all() in main.py
discovers all tables, even though main.py only directly imports this package.
"""
from app.models.user import User, RoleEnum
from app.models.candidate import CandidateProfile, ResumeData
from app.models.job import Job, JobStatusEnum
from app.models.application import Application, ApplicationStatusEnum, Notification

__all__ = [
    "User", "RoleEnum",
    "CandidateProfile", "ResumeData",
    "Job", "JobStatusEnum",
    "Application", "ApplicationStatusEnum", "Notification",
]
