from collections import Counter
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.user import User, RoleEnum
from app.models.candidate import CandidateProfile
from app.models.job import Job, JobStatusEnum
from app.models.application import Application, ApplicationStatusEnum
from app.schemas.candidate import CandidateListItem, CandidateProfileOut
from app.utils.security import require_admin
from app.routers.candidates import _to_profile_out

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/dashboard")
def dashboard_stats(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    total_candidates = db.query(CandidateProfile).count()
    total_jobs = db.query(Job).count()
    open_jobs = db.query(Job).filter(Job.status == JobStatusEnum.open).count()
    total_applications = db.query(Application).count()

    status_counts = {status.value: 0 for status in ApplicationStatusEnum}
    for status_value, count in (
        db.query(Application.status, func.count(Application.id)).group_by(Application.status).all()
    ):
        status_counts[status_value.value] = count

    pending = status_counts.get("applied", 0)

    # Applications over the last 6 months, bucketed by month
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    recent_apps = (
        db.query(Application.applied_at)
        .filter(Application.applied_at >= six_months_ago)
        .all()
    )
    month_buckets = Counter()
    for (applied_at,) in recent_apps:
        key = applied_at.strftime("%Y-%m")
        month_buckets[key] += 1
    applications_by_month = [{"month": k, "count": v} for k, v in sorted(month_buckets.items())]

    # Top skills across all candidates
    skill_counter = Counter()
    for (skills,) in db.query(CandidateProfile.technical_skills).all():
        for s in (skills or []):
            skill_counter[s] += 1
    top_skills = [{"skill": s, "count": c} for s, c in skill_counter.most_common(10)]

    avg_ats = db.query(func.avg(CandidateProfile.ats_score)).scalar() or 0

    recent_applications = (
        db.query(Application)
        .options(joinedload(Application.job), joinedload(Application.candidate))
        .order_by(Application.applied_at.desc())
        .limit(8)
        .all()
    )
    recent_activity = [
        {
            "candidate_name": a.candidate.user.full_name,
            "job_title": a.job.title,
            "status": a.status.value,
            "applied_at": a.applied_at.isoformat(),
        }
        for a in recent_applications
    ]

    return {
        "total_candidates": total_candidates,
        "total_jobs": total_jobs,
        "open_jobs": open_jobs,
        "total_applications": total_applications,
        "selected": status_counts.get("selected", 0),
        "rejected": status_counts.get("rejected", 0),
        "shortlisted": status_counts.get("shortlisted", 0),
        "pending": pending,
        "average_ats_score": round(avg_ats, 1),
        "applications_by_month": applications_by_month,
        "top_skills": top_skills,
        "status_breakdown": status_counts,
        "recent_activity": recent_activity,
    }


@router.get("/candidates", response_model=list[CandidateListItem])
def list_candidates(
    search: Optional[str] = None,
    skill: Optional[str] = None,
    min_experience: Optional[float] = None,
    location: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    query = db.query(CandidateProfile).join(User, CandidateProfile.user_id == User.id)

    if search:
        like = f"%{search}%"
        query = query.filter((User.full_name.ilike(like)) | (User.email.ilike(like)))
    if location:
        query = query.filter(CandidateProfile.location.ilike(f"%{location}%"))
    if min_experience is not None:
        query = query.filter(CandidateProfile.years_experience >= min_experience)

    candidates = query.order_by(CandidateProfile.ats_score.desc()).offset((page - 1) * page_size).limit(page_size).all()

    if skill:
        skill_lower = skill.lower()
        candidates = [c for c in candidates if any(skill_lower in s.lower() for s in (c.technical_skills or []))]

    return [
        CandidateListItem(
            id=c.id, full_name=c.user.full_name, email=c.user.email, phone=c.user.phone,
            years_experience=c.years_experience or 0, ats_score=c.ats_score or 0,
            technical_skills=c.technical_skills or [], location=c.location,
            resume_path=c.resume_path, applied_jobs_count=len(c.applications),
        )
        for c in candidates
    ]


@router.get("/candidates/{candidate_id}", response_model=CandidateProfileOut)
def get_candidate_detail(candidate_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == candidate_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return _to_profile_out(profile)


@router.delete("/candidates/{candidate_id}", status_code=204)
def delete_candidate(candidate_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == candidate_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate not found")
    user = db.query(User).filter(User.id == profile.user_id).first()
    db.delete(profile)
    if user:
        db.delete(user)
    db.commit()
    return None
