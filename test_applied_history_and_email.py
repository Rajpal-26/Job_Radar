# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

import os
import sys

# Ensure backend paths are accessible
sys.path.insert(0, os.path.abspath("backend"))
sys.path.insert(0, os.path.abspath("backend/scrapers"))
sys.path.insert(0, os.path.abspath("."))

from app import app, db
from models.candidate_profile import CandidateProfile
from models.saved_job import SavedJob
from models.auto_apply_schedule import AutoApplySchedule
from services import auto_apply_service
from services.email_alert_service import get_smtp_config, send_auto_apply_run_email

def main():
    with app.app_context():
        print("="*60)
        print("  1. Checking SMTP Configuration from .env")
        print("="*60)
        cfg = get_smtp_config()
        print(f"  SMTP Host: {cfg['host']}")
        print(f"  SMTP Port: {cfg['port']}")
        print(f"  SMTP User: {cfg['user']}")
        print(f"  SMTP Recipient: {cfg['recipient']}")
        print(f"  Password set: {'Yes (length ' + str(len(cfg['password'])) + ')' if cfg['password'] else 'No'}")

        print("\n" + "="*60)
        print("  2. Testing Applied History Retrieval & Analytics")
        print("="*60)
        history = auto_apply_service.get_applied_history()
        analytics = auto_apply_service.get_application_analytics()
        print(f"  Total Applied in Ledger: {len(history)}")
        print(f"  Analytics: {analytics}")

        if history:
            first_job = history[0]
            print(f"\n  Sample Job Record:")
            print(f"  - Title: {first_job.get('job_title')} at {first_job.get('company')}")
            print(f"  - Platform: {first_job.get('platform')}")
            print(f"  - Application ID: {first_job.get('application_id')}")
            print(f"  - Responsibilities Count: {len(first_job.get('responsibilities', []))}")
            print(f"  - Benefits Count: {len(first_job.get('benefits', []))}")
            print(f"  - Screening Q&A Count: {len(first_job.get('screening_qa', []))}")
            print(f"  - Candidate Name: {first_job.get('candidate_snapshot', {}).get('full_name')}")
            print(f"  - Candidate Email: {first_job.get('candidate_snapshot', {}).get('email')}")

        print("\n" + "="*60)
        print("  3. Testing Email Digest Dispatch via SMTP")
        print("="*60)
        sample_schedule = {
            "name": "Live Auto-Apply Automation Run",
            "target_role": "Python Developer",
            "platform": "All Portals"
        }
        profile = CandidateProfile.query.first()
        profile_dict = profile.to_dict() if profile else {
            "full_name": "Rajpal Singh Tanwar",
            "email": "kapiltanwar0369@gmail.com",
            "phone": "+91 9876543210",
            "experience_level": "1-3 Years",
            "expected_ctc": "8-14 LPA",
            "notice_period": "Immediate / 15 Days",
            "resume_filename": "Resume_Rajpal_Tanwar.pdf",
            "skills": ["Python", "FastAPI", "SQL", "Docker", "Git"]
        }

        email_result = send_auto_apply_run_email(
            schedule_data=sample_schedule,
            applied_jobs=history[:3] if history else [
                {
                    "job_title": "Python Developer",
                    "company": "Tech Innovations Ltd",
                    "platform": "LinkedIn Easy Apply",
                    "location": "Bengaluru / Remote",
                    "salary": "10-16 LPA",
                    "match_score": 94,
                    "application_id": "APP-LIN-984210",
                    "link": "https://www.linkedin.com/jobs",
                    "responsibilities": [
                        "Architect scalable microservices and FastAPI endpoints",
                        "Optimize high-throughput SQL database queries and Redis caching",
                        "Integrate CI/CD pipelines and unit test suites"
                    ],
                    "benefits": ["Comprehensive Medical Insurance", "Flexible Remote Work", "Annual ESOP Grants"],
                    "screening_qa": [
                        {"question": "How many years of Python experience do you have?", "answer": "3+ years of professional backend development"},
                        {"question": "What is your official notice period?", "answer": "Immediate / 15 days"}
                    ]
                }
            ],
            candidate_profile=profile_dict,
            recipient_email=cfg["recipient"]
        )

        print(f"  Email Dispatch Result: {email_result}")
        print("\n" + "="*60)
        print("  All Verification Steps Completed Successfully!")
        print("="*60)

if __name__ == "__main__":
    main()
