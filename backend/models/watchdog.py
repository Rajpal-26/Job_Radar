# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

from datetime import datetime
from models.database import db

class Watchdog(db.Model):
    __tablename__ = 'watchdogs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable=False)
    locations = db.Column(db.String(255), default='')
    portals = db.Column(db.String(255), default='indeed,naukri,glassdoor')
    min_match_score = db.Column(db.Integer, default=80)
    user_email = db.Column(db.String(255), default='')
    active = db.Column(db.Boolean, default=True)
    last_run = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "locations": self.locations,
            "portals": self.portals,
            "min_match_score": self.min_match_score,
            "user_email": self.user_email,
            "active": self.active,
            "last_run": self.last_run.strftime("%Y-%m-%d %H:%M:%S") if self.last_run else ""
        }
