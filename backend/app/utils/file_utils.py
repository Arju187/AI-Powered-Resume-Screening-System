import os
import uuid

from fastapi import UploadFile, HTTPException

from app.config import settings


def ensure_upload_dirs():
    os.makedirs(settings.resume_dir, exist_ok=True)
    os.makedirs(settings.profile_picture_dir, exist_ok=True)


def save_resume(file: UploadFile, candidate_user_id: int) -> str:
    if file.content_type != "application/pdf" and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF resumes are accepted")

    contents = file.file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_RESUME_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"Resume exceeds the maximum size of {settings.MAX_RESUME_SIZE_MB} MB"
        )

    ensure_upload_dirs()
    safe_name = f"candidate_{candidate_user_id}_{uuid.uuid4().hex[:8]}.pdf"
    full_path = os.path.join(settings.resume_dir, safe_name)
    with open(full_path, "wb") as f:
        f.write(contents)

    return full_path


def save_profile_picture(file: UploadFile, candidate_user_id: int) -> str:
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Profile picture must be JPG, PNG, or WEBP")

    contents = file.file.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Profile picture must be under 2MB")

    ensure_upload_dirs()
    ext = file.filename.rsplit(".", 1)[-1].lower()
    safe_name = f"candidate_{candidate_user_id}_{uuid.uuid4().hex[:8]}.{ext}"
    full_path = os.path.join(settings.profile_picture_dir, safe_name)
    with open(full_path, "wb") as f:
        f.write(contents)

    return full_path
