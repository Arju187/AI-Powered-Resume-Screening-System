"""
Seeds the database with:
  - one admin account (from .env ADMIN_EMAIL / ADMIN_PASSWORD)
  - a handful of sample job postings, so the recommendation engine and
    admin dashboard have something to show on first run.

Safe to run multiple times — checks for existing records before inserting.
Runs automatically on app startup (see main.py), or manually via:
    python -m app.seed
"""
from datetime import datetime, timedelta

from app.database import SessionLocal, Base, engine
from app.models.user import User, RoleEnum
from app.models.job import Job, JobStatusEnum
from app.config import settings
from app.utils.security import hash_password

SAMPLE_JOBS = [
    {
        "title": "Java Developer",
        "location": "Coimbatore,Tamilnadu",
        "employment_type": "Full-time",
        "salary": 85000,
        "required_experience": 2,
        "required_skills": ["Java", "Spring Boot", "SQL", "Git", "REST API"],
        "responsibilities": "Design and build backend services for the platform; write unit tests; participate in code reviews.",
        "description": "We're looking for a Java Developer to join our backend team building secure, scalable services.",
    },
    {
        "title": "React Frontend Developer",
        "location": "Remote",
        "employment_type": "Full-time",
        "salary": 80000,
        "required_experience": 1.5,
        "required_skills": ["React", "JavaScript", "HTML", "CSS", "REST API"],
        "responsibilities": "Build responsive UI components; collaborate with designers; optimize performance.",
        "description": "Join our frontend team building dashboards used by security analysts every day.",
    },
    {
        "title": "Node.js Backend Developer",
        "location": "Coimbatore,Tamilnadu",
        "employment_type": "Full-time",
        "salary": 82000,
        "required_experience": 2,
        "required_skills": ["Node.js", "Express.js", "MongoDB", "JavaScript", "REST API"],
        "responsibilities": "Develop and maintain Node.js microservices; integrate with third-party APIs.",
        "description": "We need a backend developer comfortable with the Node.js ecosystem and microservice design.",
    },
    {
        "title": "Full Stack Developer",
        "location": "Coimbatore,Tamilnadu",
        "employment_type": "Full-time",
        "salary": 90000,
        "required_experience": 3,
        "required_skills": ["JavaScript", "React", "Node.js", "SQL", "Git", "Docker"],
        "responsibilities": "Own features end to end across frontend and backend; mentor junior developers.",
        "description": "A generalist role for someone who enjoys working across the whole stack.",
    },
    {
        "title": "Python / FastAPI Developer",
        "location": "Coimbatore,Tamilnadu",
        "employment_type": "Full-time",
        "salary": 88000,
        "required_experience": 2,
        "required_skills": ["Python", "FastAPI", "SQL", "Docker", "Git"],
        "responsibilities": "Build and maintain FastAPI services powering our cybersecurity platform.",
        "description": "Work on the API layer of our white-labeled cybersecurity product.",
    },
    {
        "title": "Cybersecurity Analyst Intern",
        "location": "Coimbatore,Tamilnadu",
        "employment_type": "Internship",
        "salary": 35000,
        "required_experience": 0,
        "required_skills": ["Networking", "Linux", "Cybersecurity", "Python"],
        "responsibilities": "Assist the security team with monitoring, triage, and reporting.",
        "description": "A great entry point into cybersecurity for students or recent graduates.",
    },
    {
        "title": "DevOps Engineer",
        "location": "Coimbatore,Tamilnadu",
        "employment_type": "Full-time",
        "salary": 95000,
        "required_experience": 3,
        "required_skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Git"],
        "responsibilities": "Own CI/CD pipelines, infrastructure automation, and deployment reliability.",
        "description": "Help us scale our infrastructure as we grow our client base.",
    },
]


def run_seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL.lower()).first()
        if not admin:
            admin = User(
                full_name=settings.ADMIN_NAME,
                email=settings.ADMIN_EMAIL.lower(),
                password_hash=hash_password(settings.ADMIN_PASSWORD),
                role=RoleEnum.admin,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"[seed] Created default admin: {settings.ADMIN_EMAIL}")

        if db.query(Job).count() == 0:
            for job_data in SAMPLE_JOBS:
                job = Job(
                    company="G2 Technologies",
                    status=JobStatusEnum.open,
                    closing_date=datetime.utcnow() + timedelta(days=45),
                    created_by=admin.id,
                    **job_data,
                )
                db.add(job)
            db.commit()
            print(f"[seed] Inserted {len(SAMPLE_JOBS)} sample job postings")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
