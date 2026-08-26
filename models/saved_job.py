# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

from datetime import datetime
from models.database import db

class SavedJob(db.Model):
    __tablename__ = 'saved_jobs'

    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), default='')
    link = db.Column(db.Text, unique=True, nullable=False)
    platform = db.Column(db.String(100), default='JobRadar')
    salary = db.Column(db.String(100), default='')
    status = db.Column(db.String(50), default='Bookmarked')
    match_score = db.Column(db.Integer, default=75)
    notes = db.Column(db.Text, default='')
    cover_letter = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "job_title": self.job_title,
            "company": self.company,
            "location": self.location,
            "link": self.link,
            "platform": self.platform,
            "salary": self.salary,
            "status": self.status,
            "match_score": self.match_score,
            "notes": self.notes,
            "cover_letter": self.cover_letter,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""
        }
