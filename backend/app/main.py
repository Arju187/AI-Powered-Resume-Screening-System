"""
Application entrypoint.

Run with:  uvicorn app.main:app --reload --port 8000   (from the backend/ folder)
Interactive API docs will be at http://127.0.0.1:8000/docs
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine
from app import models  # noqa: F401  (registers all models with Base.metadata)
from app.routers import auth, candidates, jobs, applications, admin, notifications
from app.utils.file_utils import ensure_upload_dirs
from app.seed import run_seed

app = FastAPI(
    title="AI Resume Screening API",
    description="AI-assisted Resume Screening & Applicant Tracking System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(candidates.router)
app.include_router(jobs.router)
app.include_router(applications.router)
app.include_router(admin.router)
app.include_router(notifications.router)


@app.on_event("startup")
def on_startup():
    ensure_upload_dirs()
    Base.metadata.create_all(bind=engine)
    run_seed()


@app.get("/")
def root():
    return {
        "message": "OctoSafes ATS API is running",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


# Serve uploaded files (resumes, profile pictures) so the frontend can
# preview/download them directly. In production, swap this for signed
# URLs from cloud storage (see docs/ARCHITECTURE.md).
if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
