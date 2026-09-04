from models.database import db, migrate
from models.saved_job import SavedJob
from models.watchdog import Watchdog
from models.candidate_profile import CandidateProfile

__all__ = ["db", "migrate", "SavedJob", "Watchdog", "CandidateProfile"]
