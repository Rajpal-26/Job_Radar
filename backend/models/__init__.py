# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================
from models.database import db, migrate
from models.saved_job import SavedJob
from models.watchdog import Watchdog
from models.candidate_profile import CandidateProfile
from models.auto_apply_schedule import AutoApplySchedule

__all__ = ["db", "migrate", "SavedJob", "Watchdog", "CandidateProfile", "AutoApplySchedule"]
