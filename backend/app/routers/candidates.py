import os

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.candidate import CandidateProfile, ResumeData
from app.models.job import Job, JobStatusEnum
from app.schemas.candidate import CandidateProfileOut, CandidateProfileUpdate, JobRecommendation
from app.utils.security import require_candidate
from app.utils.file_utils import save_resume
from app.services.resume_parser import parse_resume
from app.services.ats_engine import calculate_ats_score, calculate_profile_completion
from app.services.recommendation_engine import recommend_jobs_for_candidate
from app.services.skill_data import normalize_skill_list

router = APIRouter(prefix="/api/candidates", tags=["Candidates"])


def _get_profile_or_404(db: Session, user_id: int) -> CandidateProfile:
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    return profile


def _to_profile_out(profile: CandidateProfile) -> CandidateProfileOut:
    return CandidateProfileOut(
        id=profile.id, user_id=profile.user_id,
        full_name=profile.user.full_name, email=profile.user.email, phone=profile.user.phone,
        current_company=profile.current_company, current_designation=profile.current_designation,
        years_experience=profile.years_experience or 0, highest_qualification=profile.highest_qualification,
        location=profile.location, preferred_job_role=profile.preferred_job_role,
        expected_salary=profile.expected_salary, linkedin_url=profile.linkedin_url,
        github_url=profile.github_url, portfolio_url=profile.portfolio_url,
        technical_skills=profile.technical_skills or [], soft_skills=profile.soft_skills or [],
        profile_picture_path=profile.profile_picture_path, resume_path=profile.resume_path,
        profile_completion=profile.profile_completion or 0, ats_score=profile.ats_score or 0,
        ats_breakdown=profile.ats_breakdown or {}, resume_data=profile.resume_data,
    )


def _recalculate(db: Session, profile: CandidateProfile):
    """Recalculate ATS score + profile completion. Called after any resume/profile change."""
    score, breakdown = calculate_ats_score(profile, profile.resume_data)
    profile.ats_score = score
    profile.ats_breakdown = breakdown
    profile.profile_completion = calculate_profile_completion(profile, profile.resume_data)
    db.commit()
    db.refresh(profile)


@router.get("/me", response_model=CandidateProfileOut)
def get_my_profile(db: Session = Depends(get_db), current_user: User = Depends(require_candidate)):
    profile = _get_profile_or_404(db, current_user.id)
    return _to_profile_out(profile)


@router.put("/me", response_model=CandidateProfileOut)
def update_my_profile(payload: CandidateProfileUpdate, db: Session = Depends(get_db),
                       current_user: User = Depends(require_candidate)):
    profile = _get_profile_or_404(db, current_user.id)
    data = payload.model_dump(exclude_unset=True)

    if "full_name" in data and data["full_name"]:
        current_user.full_name = data.pop("full_name")
    if "phone" in data:
        current_user.phone = data.pop("phone")

    if "technical_skills" in data and data["technical_skills"] is not None:
        data["technical_skills"] = normalize_skill_list(data["technical_skills"])

    for field, value in data.items():
        setattr(profile, field, value)

    db.commit()
    _recalculate(db, profile)
    return _to_profile_out(profile)


@router.post("/me/resume", response_model=CandidateProfileOut)
def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db),
                   current_user: User = Depends(require_candidate)):
    profile = _get_profile_or_404(db, current_user.id)

    # Remove old resume file from disk if present, to avoid orphaned files
    if profile.resume_path and os.path.exists(profile.resume_path):
        try:
            os.remove(profile.resume_path)
        except OSError:
            pass

    saved_path = save_resume(file, current_user.id)
    profile.resume_path = saved_path
    db.commit()

    parsed = parse_resume(saved_path)

    if profile.resume_data:
        for key, value in parsed.items():
            setattr(profile.resume_data, key, value)
    else:
        resume_data = ResumeData(candidate_id=profile.id, **parsed)
        db.add(resume_data)

    # Merge resume-extracted skills into the candidate's skill list automatically
    merged_skills = normalize_skill_list(list(profile.technical_skills or []) + parsed["skills"])
    profile.technical_skills = merged_skills

    db.commit()
    db.refresh(profile)
    _recalculate(db, profile)
    return _to_profile_out(profile)


@router.get("/me/resume/download")
def download_my_resume(db: Session = Depends(get_db), current_user: User = Depends(require_candidate)):
    profile = _get_profile_or_404(db, current_user.id)
    if not profile.resume_path or not os.path.exists(profile.resume_path):
        raise HTTPException(status_code=404, detail="No resume uploaded yet")
    return FileResponse(profile.resume_path, media_type="application/pdf", filename="resume.pdf")


@router.delete("/me/resume", response_model=CandidateProfileOut)
def delete_my_resume(db: Session = Depends(get_db), current_user: User = Depends(require_candidate)):
    profile = _get_profile_or_404(db, current_user.id)
    if profile.resume_path and os.path.exists(profile.resume_path):
        try:
            os.remove(profile.resume_path)
        except OSError:
            pass
    profile.resume_path = None
    if profile.resume_data:
        db.delete(profile.resume_data)
    db.commit()
    db.refresh(profile)
    _recalculate(db, profile)
    return _to_profile_out(profile)


@router.get("/me/recommendations", response_model=list[JobRecommendation])
def get_recommended_jobs(db: Session = Depends(get_db), current_user: User = Depends(require_candidate)):
    """
    Cross-job recommendation: scans EVERY open job, not just ones matching the
    candidate's preferred title — so a candidate with Java + React + Node skills
    shows up as recommended for Java, React, AND Node postings.
    """
    profile = _get_profile_or_404(db, current_user.id)
    skills = list(profile.technical_skills or [])
    open_jobs = db.query(Job).filter(Job.status == JobStatusEnum.open).all()

    matches = recommend_jobs_for_candidate(skills, profile.years_experience or 0, open_jobs)

    return [
        JobRecommendation(
            job_id=m["job"].id, title=m["job"].title, company=m["job"].company,
            matched_skills=m["matched_skills"], missing_skills=m["missing_skills"],
            recommendation_score=m["recommendation_score"],
        )
        for m in matches
    ]
