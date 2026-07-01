from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.user import User
from app.models.candidate import CandidateProfile
from app.models.job import Job, JobStatusEnum
from app.models.application import Application
from app.schemas.job import JobCreate, JobUpdate, JobOut, RankedCandidateOut
from app.utils.security import require_admin, get_current_user
from app.services.skill_data import normalize_skill_list
from app.services.recommendation_engine import rank_candidates_for_job

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


def _to_job_out(job: Job) -> JobOut:
    return JobOut(
        id=job.id, title=job.title, company=job.company, location=job.location,
        employment_type=job.employment_type, salary=job.salary,
        required_experience=job.required_experience or 0, required_skills=job.required_skills or [],
        responsibilities=job.responsibilities, description=job.description,
        posted_date=job.posted_date, closing_date=job.closing_date, status=job.status.value,
        applicants_count=len(job.applications),
    )


@router.get("", response_model=list[JobOut])
def list_jobs(
    search: Optional[str] = Query(None, description="Search title/company/location"),
    location: Optional[str] = None,
    employment_type: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Job)
    if status_filter:
        query = query.filter(Job.status == status_filter)
    else:
        query = query.filter(Job.status == JobStatusEnum.open)  # public listing defaults to open jobs
    if search:
        like = f"%{search}%"
        query = query.filter(
            (Job.title.ilike(like)) | (Job.company.ilike(like)) | (Job.location.ilike(like))
        )
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if employment_type:
        query = query.filter(Job.employment_type == employment_type)

    query = query.order_by(Job.posted_date.desc())
    jobs = query.offset((page - 1) * page_size).limit(page_size).all()
    return [_to_job_out(j) for j in jobs]


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _to_job_out(job)


@router.post("", response_model=JobOut, status_code=201)
def create_job(payload: JobCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    job = Job(
        title=payload.title, company=payload.company or "OctoSafes", location=payload.location,
        employment_type=payload.employment_type or "Full-time", salary=payload.salary,
        required_experience=payload.required_experience or 0,
        required_skills=normalize_skill_list(payload.required_skills),
        responsibilities=payload.responsibilities, description=payload.description,
        closing_date=payload.closing_date, created_by=admin.id,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return _to_job_out(job)


@router.put("/{job_id}", response_model=JobOut)
def update_job(job_id: int, payload: JobUpdate, db: Session = Depends(get_db),
                admin: User = Depends(require_admin)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    data = payload.model_dump(exclude_unset=True)
    if "required_skills" in data and data["required_skills"] is not None:
        data["required_skills"] = normalize_skill_list(data["required_skills"])
    if "status" in data and data["status"]:
        data["status"] = JobStatusEnum(data["status"])

    for field, value in data.items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)
    return _to_job_out(job)


@router.delete("/{job_id}", status_code=204)
def delete_job(job_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return None


@router.get("/{job_id}/candidates", response_model=list[RankedCandidateOut])
def get_ranked_candidates(job_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """Admin view: every candidate who applied to this job, ranked by recommendation score."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    applications = (
        db.query(Application)
        .options(
            joinedload(Application.candidate).joinedload(CandidateProfile.user),
            joinedload(Application.candidate).joinedload(CandidateProfile.resume_data),
        )
        .filter(Application.job_id == job_id)
        .all()
    )

    ranked = rank_candidates_for_job(job.required_skills or [], job.required_experience or 0, applications)

    return [
        RankedCandidateOut(
            application_id=r["application"].id, candidate_id=r["candidate"].id,
            full_name=r["candidate"].user.full_name, email=r["candidate"].user.email,
            ats_score=r["candidate"].ats_score or 0, recommendation_score=r["recommendation_score"],
            matched_skills=r["matched_skills"], missing_skills=r["missing_skills"],
            years_experience=r["candidate"].years_experience or 0,
            application_status=r["application"].status.value,
        )
        for r in ranked
    ]
