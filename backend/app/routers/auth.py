from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, RoleEnum
from app.models.candidate import CandidateProfile
from app.models.application import Notification
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, CurrentUserResponse, ChangePasswordRequest
from app.utils.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    # Rule from the spec: only candidates may self-register, regardless of
    # what the client sends for "role". Admins are seeded separately (see seed.py).
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists")

    user = User(
        full_name=payload.full_name.strip(),
        email=payload.email.lower(),
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        role=RoleEnum.candidate,
    )
    db.add(user)
    db.flush()  # get user.id before commit

    tech_skills = [s.strip() for s in (payload.technical_skills or "").split(",") if s.strip()]
    soft_skills = [s.strip() for s in (payload.soft_skills or "").split(",") if s.strip()]

    profile = CandidateProfile(
        user_id=user.id,
        current_company=payload.current_company,
        current_designation=payload.current_designation,
        years_experience=payload.years_experience or 0,
        highest_qualification=payload.highest_qualification,
        location=payload.location,
        preferred_job_role=payload.preferred_job_role,
        expected_salary=payload.expected_salary,
        linkedin_url=payload.linkedin_url,
        github_url=payload.github_url,
        portfolio_url=payload.portfolio_url,
        technical_skills=tech_skills,
        soft_skills=soft_skills,
    )
    db.add(profile)

    db.add(Notification(
        user_id=user.id,
        title="Welcome to OctoSafes ATS",
        message="Your account was created. Upload your resume to get your ATS score and job recommendations.",
        notif_type="success",
    ))

    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return TokenResponse(access_token=token, role=user.role.value, full_name=user.full_name, user_id=user.id)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="This account has been deactivated")

    expires = 60 * 24 * 7 if payload.remember_me else None  # 7 days if "remember me"
    token = create_access_token({"sub": str(user.id), "role": user.role.value}, expires_minutes=expires)
    return TokenResponse(access_token=token, role=user.role.value, full_name=user.full_name, user_id=user.id)


@router.get("/me", response_model=CurrentUserResponse)
def me(current_user: User = Depends(get_current_user)):
    return CurrentUserResponse(
        id=current_user.id, full_name=current_user.full_name,
        email=current_user.email, role=current_user.role.value,
    )


@router.put("/change-password")
def change_password(payload: ChangePasswordRequest, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.password_hash = hash_password(payload.new_password)
    db.commit()
    return {"message": "Password updated successfully"}
