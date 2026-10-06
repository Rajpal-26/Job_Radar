# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

from datetime import datetime
import json
from models.database import db

class AutoApplySchedule(db.Model):
    __tablename__ = 'auto_apply_schedules'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), default='Daily Auto-Apply Routine')
    platform = db.Column(db.String(100), default='All')  # 'All', 'Naukri', 'LinkedIn', 'Greenhouse', etc.
    target_role = db.Column(db.String(255), default='Python Developer')
    locations_json = db.Column(db.Text, default='["Bengaluru", "Remote"]')
    min_match_score = db.Column(db.Integer, default=75)
    min_salary = db.Column(db.String(100), default='8 LPA')
    days_of_week_json = db.Column(db.Text, default='["Mon", "Tue", "Wed", "Thu", "Fri"]')
    runtime_minutes = db.Column(db.Integer, default=30)
    is_active = db.Column(db.Boolean, default=True)
    last_run_at = db.Column(db.DateTime, nullable=True)
    last_run_status = db.Column(db.String(100), default='Not run yet')
    last_applied_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def locations(self):
        try:
            return json.loads(self.locations_json or '[]')
        except Exception:
            return []

    @locations.setter
    def locations(self, val):
        self.locations_json = json.dumps(val if isinstance(val, list) else [val])

    @property
    def days_of_week(self):
        try:
            return json.loads(self.days_of_week_json or '[]')
        except Exception:
            return []

    @days_of_week.setter
    def days_of_week(self, val):
        self.days_of_week_json = json.dumps(val if isinstance(val, list) else [val])

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "platform": self.platform,
            "target_role": self.target_role,
            "locations": self.locations,
            "min_match_score": self.min_match_score,
            "min_salary": self.min_salary,
            "days_of_week": self.days_of_week,
            "runtime_minutes": self.runtime_minutes,
            "is_active": self.is_active,
            "last_run_at": self.last_run_at.strftime("%Y-%m-%d %H:%M:%S") if self.last_run_at else "Never",
            "last_run_status": self.last_run_status,
            "last_applied_count": self.last_applied_count,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""
        }
