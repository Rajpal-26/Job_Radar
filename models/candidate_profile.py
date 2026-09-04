# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

from models.database import db
from datetime import datetime
import json

class CandidateProfile(db.Model):
    __tablename__ = 'candidate_profiles'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), default='Job Candidate')
    email = db.Column(db.String(255), default='')
    phone = db.Column(db.String(50), default='')
    location = db.Column(db.String(255), default='')
    linkedin_url = db.Column(db.String(500), default='')
    github_url = db.Column(db.String(500), default='')
    portfolio_url = db.Column(db.String(500), default='')
    experience_level = db.Column(db.String(100), default='Fresher / 0-1 Year')
    current_role = db.Column(db.String(255), default='')
    target_roles_json = db.Column(db.Text, default='[]')
    skills_json = db.Column(db.Text, default='[]')
    skill_categories_json = db.Column(db.Text, default='{}')
    summary = db.Column(db.Text, default='')
    raw_resume_text = db.Column(db.Text, default='')
    resume_filename = db.Column(db.String(255), default='')
    notice_period = db.Column(db.String(100), default='Immediate / 15 Days')
    current_ctc = db.Column(db.String(100), default='')
    expected_ctc = db.Column(db.String(100), default='6-10 LPA')
    work_authorization = db.Column(db.String(100), default='Authorized to work in India')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def target_roles(self):
        try:
            return json.loads(self.target_roles_json or '[]')
        except Exception:
            return []

    @target_roles.setter
    def target_roles(self, val):
        self.target_roles_json = json.dumps(val if isinstance(val, list) else [val])

    @property
    def skills(self):
        try:
            return json.loads(self.skills_json or '[]')
        except Exception:
            return []

    @skills.setter
    def skills(self, val):
        self.skills_json = json.dumps(val if isinstance(val, list) else [val])

    @property
    def skill_categories(self):
        try:
            return json.loads(self.skill_categories_json or '{}')
        except Exception:
            return {}

    @skill_categories.setter
    def skill_categories(self, val):
        self.skill_categories_json = json.dumps(val if isinstance(val, dict) else {})

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "location": self.location,
            "linkedin_url": self.linkedin_url,
            "github_url": self.github_url,
            "portfolio_url": self.portfolio_url,
            "experience_level": self.experience_level,
            "current_role": self.current_role,
            "target_roles": self.target_roles,
            "skills": self.skills,
            "skill_categories": self.skill_categories,
            "summary": self.summary,
            "resume_filename": self.resume_filename,
            "notice_period": self.notice_period,
            "current_ctc": self.current_ctc,
            "expected_ctc": self.expected_ctc,
            "work_authorization": self.work_authorization,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else ""
        }
