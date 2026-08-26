# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

from models.database import db
from models.saved_job import SavedJob

def init_db():
    """Create all database tables using SQLAlchemy ORM models."""
    db.create_all()

def get_all_saved_jobs():
    """Retrieve all saved jobs from ORM ordered by creation date descending."""
    jobs = SavedJob.query.order_by(SavedJob.created_at.desc()).all()
    return [j.to_dict() for j in jobs]

def save_job(job_data):
    """Save a job to the tracker using SQLAlchemy ORM. Returns (inserted_id, is_new)."""
    title = job_data.get("Job Title") or job_data.get("title") or "Unknown Role"
    company = job_data.get("Company") or job_data.get("company") or "Unknown Company"
    location = job_data.get("Location") or job_data.get("location") or ""
    link = job_data.get("Link") or job_data.get("link") or f"https://jobradar.local/{hash(title+company)}"
    platform = job_data.get("Platform") or job_data.get("platform") or "JobRadar"
    salary = job_data.get("Salary") or job_data.get("salary") or ""
    match_score = int(job_data.get("Match_Score") or job_data.get("match_score") or 75)
    status = job_data.get("status") or "Bookmarked"
    notes = job_data.get("notes") or ""
    cover_letter = job_data.get("cover_letter") or ""

    existing = SavedJob.query.filter_by(link=link).first()
    if existing:
        return existing.id, False

    new_job = SavedJob(
        job_title=title,
        company=company,
        location=location,
        link=link,
        platform=platform,
        salary=salary,
        status=status,
        match_score=match_score,
        notes=notes,
        cover_letter=cover_letter
    )
    db.session.add(new_job)
    db.session.commit()
    return new_job.id, True

def update_job_status(job_id, status=None, notes=None, cover_letter=None):
    """Update status, notes, or cover letter of a saved job using ORM session."""
    job = SavedJob.query.get(job_id)
    if not job:
        return False

    if status is not None:
        job.status = status
    if notes is not None:
        job.notes = notes
    if cover_letter is not None:
        job.cover_letter = cover_letter

    db.session.commit()
    return True

def delete_saved_job(job_id):
    """Delete a saved job by ID using ORM session."""
    job = SavedJob.query.get(job_id)
    if not job:
        return False

    db.session.delete(job)
    db.session.commit()
    return True
