# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app
from models import db, SavedJob, Watchdog
from utils import ai_copilot

def run_tests():
    print("\n" + "="*60)
    print("  RUNNING PRODUCTION SAAS FEATURE VERIFICATION TESTS")
    print("="*60 + "\n")

    with app.app_context():
        # Test 1: ORM Database & SavedJob Model
        print("1. Testing Flask-SQLAlchemy ORM & Models...")
        job = SavedJob(
            job_title="Senior Python Architect",
            company="Google DeepMind",
            location="Bengaluru",
            link="https://jobradar.test/job/101",
            platform="Indeed",
            salary="35-45 LPA",
            status="Bookmarked",
            match_score=95
        )
        db.session.add(job)
        db.session.commit()
        retrieved = SavedJob.query.filter_by(link="https://jobradar.test/job/101").first()
        assert retrieved is not None
        assert retrieved.company == "Google DeepMind"
        print("   [SUCCESS] ORM Database & Models working cleanly!")

        # Test 2: Watchdog Creation
        print("\n2. Testing Watchdog Creation...")
        w = Watchdog(
            name="Python Backend Alert",
            role="Python Backend Developer",
            locations="Bengaluru, Pune",
            min_match_score=80
        )
        db.session.add(w)
        db.session.commit()
        assert Watchdog.query.filter_by(name="Python Backend Alert").first() is not None
        print("   [SUCCESS] Watchdog ORM model working cleanly!")

        # Test 3: AI Skill Gap Analysis
        print("\n3. Testing AI Skill Gap Analysis & Market Demand...")
        test_jobs = [
            {"Job Title": "Python Developer", "Company": "Meta", "Description": "Looking for Python, FastAPI, Docker, and Redis experience."},
            {"Job Title": "Backend Engineer", "Company": "Uber", "Description": "Python, Django, PostgreSQL, and Kubernetes experience required."}
        ]
        user_skills = ["Python", "FastAPI", "SQL"]
        annotated_jobs, market_demand = ai_copilot.analyze_skill_gaps(test_jobs, user_skills)
        assert len(annotated_jobs) == 2
        print(f"   Annotated Missing Skills Job 1: {annotated_jobs[0]['Missing_Skills']}")
        print("   [SUCCESS] Skill Gap Analysis working cleanly!")

        # Test 4: Recruiter Outreach DM Generator
        print("\n4. Testing Recruiter DM Copilot Generator...")
        dm = ai_copilot.generate_recruiter_dm("Python Backend Engineer", "Razorpay", user_skills)
        assert "Razorpay" in dm
        assert "Python" in dm
        print(f"   Generated Recruiter DM:\n   {dm}")
        print("   [SUCCESS] Recruiter DM Copilot working cleanly!")

    print("\n" + "="*60)
    print("  ALL VERIFICATION TESTS PASSED SUCCESSFULLY! (100% OK)")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_tests()
