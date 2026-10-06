import json
import os
import sys

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure backend directory is in python search path
backend_dir = os.path.join(os.path.dirname(__file__), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import app
from models import CandidateProfile, SavedJob, db

print("================================================================================")
print("  JobRadar: End-to-End Multi-Portal Auto-Apply Pipeline Verification Test")
print("  Watermark: Rajpal Singh Tanwar")
print("================================================================================\n")

print(">>> [Stage 1] Configuring Candidate Profile with Resume Metadata...")
with app.app.app_context():
    profile = CandidateProfile.query.first()
    if not profile:
        profile = CandidateProfile()
        db.session.add(profile)
    
    profile.full_name = "Rajpal Singh Tanwar"
    profile.email = "rajpal.tanwar@jobradar.local"
    profile.phone = "+91 9876543210"
    profile.location = "Bengaluru, India"
    profile.linkedin_url = "https://linkedin.com/in/rajpal-tanwar"
    profile.github_url = "https://github.com/Rajpal-26"
    profile.experience_level = "Fresher / 0-1 Year"
    profile.current_role = "Python Developer"
    profile.target_roles = ["Python Developer", "Backend Engineer", "Associate Software Engineer"]
    profile.skills = ["Python", "FastAPI", "SQL", "PostgreSQL", "Docker", "Git", "REST API", "Redis"]
    profile.notice_period = "Immediate / 15 Days"
    profile.expected_ctc = "8-14 LPA"
    profile.resume_filename = "Resume_Rajpal_Singh_Tanwar.pdf"
    db.session.commit()
    print(f"✓ Candidate: {profile.full_name} | Role: {profile.target_roles[0]} | Skills: {profile.skills[:4]}")

with app.app.test_client() as client:
    print("\n>>> [Stage 2] Executing Dynamic Multi-Portal Scraping from Resume Attributes...")
    res = client.post("/api/pipeline/resume_auto_scrape", json={
        "role": "Python Developer",
        "locations": ["Bengaluru", "Remote"]
    })
    
    assert res.status_code == 200, f"Scrape failed with status {res.status_code}"
    data = res.get_json()
    jobs = data.get("jobs", [])
    print(f"✓ Total Scraped & ATS-Ranked Jobs: {len(jobs)}")

    # Group scraped jobs by portal
    portal_jobs = {}
    for j in jobs:
        p = j.get("Platform") or "Other"
        if p not in portal_jobs:
            portal_jobs[p] = []
        portal_jobs[p].append(j)

    print(f"✓ Active Portals Discovered ({len(portal_jobs)} portals): {list(portal_jobs.keys())}")

    print("\n>>> [Stage 3 & 4] Auto-Applying to 1 Job from EVERY Portal in Scraped Queue...")
    applied_results = []
    
    for portal, plist in portal_jobs.items():
        job_to_apply = plist[0]
        title = job_to_apply.get("Job Title")
        company = job_to_apply.get("Company")
        print(f"\n  ⚡ Applying to [{portal}] -> \"{title}\" at {company}...")
        
        apply_res = client.post("/api/auto_apply/job", json={"job": job_to_apply})
        assert apply_res.status_code == 200, f"Auto-apply failed for {portal}: {apply_res.data}"
        apply_data = apply_res.get_json()
        
        assert apply_data.get("success") is True, f"Auto-apply failed: {apply_data}"
        app_id = apply_data.get("application_id")
        score = apply_data.get("match_score")
        print(f"     ✓ Status: SUCCESS | App ID: {app_id} | ATS Match: {score}%")
        applied_results.append(apply_data)

    print(f"\n✓ Successfully Auto-Applied across {len(applied_results)} distinct portals!")

    print("\n>>> [Stage 5] Querying & Verifying Applied History Dossiers (/api/applied_history)...")
    hist_res = client.get("/api/applied_history")
    assert hist_res.status_code == 200, f"History fetch failed: {hist_res.status_code}"
    hist_data = hist_res.get_json()
    history = hist_data.get("history", [])
    analytics = hist_data.get("analytics", {})

    print(f"✓ Total Applications Recorded in Ledger: {len(history)}")
    print(f"✓ Average ATS Match Score: {analytics.get('average_match_score')}%")
    print(f"✓ Portal Distribution in Ledger: {analytics.get('portal_breakdown')}")

    print("\n================================================================================")
    print("  DETAILED DOSSIER VERIFICATION (SAMPLE APPLICATION RECORD)")
    print("================================================================================")
    sample = history[0]
    print(f"• Application ID:       {sample.get('application_id')}")
    print(f"• Target Role:          {sample.get('job_title')}")
    print(f"• Target Company:       {sample.get('company')}")
    print(f"• Portal Submitted Via: {sample.get('platform')}")
    print(f"• Status:               {sample.get('status')}")
    print(f"• ATS Match Score:      {sample.get('match_score')}%")
    print(f"• Resume Used:          {sample.get('resume_used')}")
    print(f"• Key Responsibilities ({len(sample.get('responsibilities', []))} items):")
    for r in sample.get('responsibilities', [])[:2]:
        print(f"    - {r}")
    print(f"• Benefits & Perks ({len(sample.get('benefits', []))} items):")
    for b in sample.get('benefits', [])[:2]:
        print(f"    - 🎁 {b}")
    print(f"• AI Screening Questions Solved ({len(sample.get('screening_qa', []))} Q&As):")
    for qa in sample.get('screening_qa', [])[:2]:
        print(f"    ❓ Q: {qa.get('question')}")
        print(f"    💡 A: {qa.get('answer')}")
    print(f"• Tailored Cover Letter Excerpt:\n    {sample.get('cover_letter', '')[:140]}...\n")

    print("================================================================================")
    print("  >>> ALL PIPELINE TESTS PASSED 100% WITH ZERO ERRORS! <<<")
    print("================================================================================")
