"""
SQLAlchemy engine, session factory, and declarative Base.

We use a single relational database (SQLite by default, swappable to
MySQL/Postgres via DATABASE_URL) instead of a MySQL + MongoDB combo.
This is a deliberate scope decision for the intern build: structured
data and parsed-resume JSON both live here, in JSON columns, which
keeps the project runnable with zero external services while still
teaching the same modeling concepts. See docs/ARCHITECTURE.md.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
