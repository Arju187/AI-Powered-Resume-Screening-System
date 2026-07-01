from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.user import User
from app.models.candidate import CandidateProfile
from app.models.job import Job, JobStatusEnum
from app.models.application import Application, ApplicationStatusEnum, Notification
from app.schemas.application import ApplicationCreate, ApplicationStatusUpdate, ApplicationOut
from app.utils.security import require_candidate, require_admin
from app.services.recommendation_engine import compute_match

router = APIRouter(prefix="/api/applications", tags=["Applications"])

STATUS_NOTIFICATION_COPY = {
    ApplicationStatusEnum.shortlisted: ("You've been shortlisted!", "success"),
    ApplicationStatusEnum.interview_scheduled: ("Interview scheduled", "info"),
    ApplicationStatusEnum.selected: ("Congratulations — you've been selected!", "success"),
    ApplicationStatusEnum.rejected: ("Application update", "warning"),
    ApplicationStatusEnum.offer_released: ("Offer released", "success"),
    ApplicationStatusEnum.joined: ("Welcome aboard!", "success"),
}


def _to_application_out(app: Application) -> ApplicationOut:
    return ApplicationOut(
        id=app.id, job_id=app.job_id, job_title=app.job.title, company=app.job.company,
        status=app.status.value, recommendation_score=app.recommendation_score or 0,
        matched_skills=app.matched_skills or [], missing_skills=app.missing_skills or [],
        ats_score_snapshot=app.ats_score_snapshot or 0, applied_at=app.applied_at,
    )


@router.post("", response_model=ApplicationOut, status_code=201)
def apply_to_job(payload: ApplicationCreate, db: Session = Depends(get_db),
                  current_user: User = Depends(require_candidate)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    if not profile.resume_path:
        raise HTTPException(status_code=400, detail="Please upload your resume before applying to jobs")

    job = db.query(Job).filter(Job.id == payload.job_id).first()
    if not job or job.status != JobStatusEnum.open:
        raise HTTPException(status_code=404, detail="Job not found or no longer open")

    existing = db.query(Application).filter(
        Application.candidate_id == profile.id, Application.job_id == job.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already applied to this job")

    skills = list(profile.technical_skills or [])
    match = compute_match(skills, job.required_skills or [], profile.years_experience or 0,
                           job.required_experience or 0)

    application = Application(
        candidate_id=profile.id, job_id=job.id,
        cover_letter=payload.cover_letter, preferred_salary=payload.preferred_salary,
        notice_period=payload.notice_period,
        recommendation_score=match["recommendation_score"],
        matched_skills=match["matched_skills"], missing_skills=match["missing_skills"],
        ats_score_snapshot=profile.ats_score or 0,
    )
    db.add(application)

    db.add(Notification(
        user_id=current_user.id, title="Application submitted",
        message=f"Your application for {job.title} at {job.company} was submitted successfully.",
        notif_type="success",
    ))
    # Notify admins who posted the job (simple version: notify the job creator)
    if job.created_by:
        db.add(Notification(
            user_id=job.created_by, title="New application received",
            message=f"{current_user.full_name} applied for {job.title} (match score: {match['recommendation_score']}%).",
            notif_type="info",
        ))

    db.commit()
    db.refresh(application)
    return _to_application_out(application)


@router.get("/me", response_model=list[ApplicationOut])
def my_applications(db: Session = Depends(get_db), current_user: User = Depends(require_candidate)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    apps = (
        db.query(Application)
        .options(joinedload(Application.job))
        .filter(Application.candidate_id == profile.id)
        .order_by(Application.applied_at.desc())
        .all()
    )
    return [_to_application_out(a) for a in apps]


@router.get("", response_model=list[ApplicationOut])
def list_applications_admin(
    job_id: Optional[int] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    query = db.query(Application).options(joinedload(Application.job))
    if job_id:
        query = query.filter(Application.job_id == job_id)
    if status_filter:
        query = query.filter(Application.status == status_filter)
    apps = query.order_by(Application.applied_at.desc()).all()
    return [_to_application_out(a) for a in apps]


@router.put("/{application_id}/status", response_model=ApplicationOut)
def update_application_status(application_id: int, payload: ApplicationStatusUpdate,
                               db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    try:
        new_status = ApplicationStatusEnum(payload.status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status value")

    application.status = new_status
    db.commit()
    db.refresh(application)

    candidate_user_id = application.candidate.user_id
    title, notif_type = STATUS_NOTIFICATION_COPY.get(new_status, ("Application status updated", "info"))
    db.add(Notification(
        user_id=candidate_user_id, title=title,
        message=f"Your application for {application.job.title} is now '{new_status.value.replace('_', ' ')}'.",
        notif_type=notif_type,
    ))
    db.commit()

    return _to_application_out(application)
