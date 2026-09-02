# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

"""
Daily Job Alert Cron & Multi-Source Scraping Pipeline (LinkedIn, Indeed, Career ATS).
Scrapes up to 50 jobs for LinkedIn, up to 50 for Indeed, and verified direct Company ATS jobs:
- Roles: Python Developer, Associate Software Engineer, Software Engineer, AI/LLM Engineer, AI Engineer
- Experience: 0-6 months, 0-1 year, Fresher (strictly junior/entry-level)
- Locations: All configured tech locations (Indore, Bengaluru, Pune, Hyderabad, Noida, Gurugram, Mumbai, Remote, India)
- Time Window: Posted within last 7 days (Startups, Mid-size, MNCs)
- Features: Anti-bot stealth evasion, salary extraction, skills detection, precision matching.
"""

import os
import sys
import argparse
import time
import re
from datetime import datetime

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scrapers.linkedin import scrape_linkedin
from scrapers.indeed import scrape_indeed
from scrapers.ats_scraper import scrape_ats_jobs
from utils.job_matcher import score_job_match, extract_salary, extract_skills, extract_workplace_mode
from services.email_alert_service import send_job_digest_email, DEFAULT_RECIPIENT, get_smtp_config

# Target Roles requested by user
TARGET_ROLES = [
    "Python Developer",
    "Associate Software Engineer",
    "Software Engineer",
    "AI/LLM Engineer",
    "AI Engineer"
]

# Target Experience Levels
TARGET_EXPERIENCE = [
    "Fresher",
    "0-6 Months",
    "0-1 Year"
]

# Standard Target Locations
TARGET_LOCATIONS = [
    "Indore",
    "Bengaluru",
    "Pune",
    "Hyderabad",
    "Noida",
    "Gurugram",
    "Mumbai",
    "Remote",
    "India"
]


def normalize_job_dict(job, portal):
    """Normalize and enrich keys across different scrapers."""
    title = job.get("title") or job.get("Job Title") or "Software Engineer"
    desc = job.get("Description") or job.get("description") or ""
    exp = job.get("experience") or job.get("Experience") or "Fresher / 0-1 Yr"
    loc = job.get("location") or job.get("Location") or "India"
    
    score, is_match = score_job_match(title, desc, exp)
    salary = job.get("salary") or job.get("Salary") or extract_salary(title + " " + desc)
    skills = job.get("skills") or extract_skills(title + " " + desc)
    workplace = job.get("workplace") or extract_workplace_mode(desc, loc)
    
    return {
        "title": title,
        "company": job.get("company") or job.get("Company") or "Tech Company",
        "location": loc,
        "experience": exp,
        "posted": job.get("posted") or job.get("Posted") or "Recent (within 7d)",
        "link": job.get("link") or job.get("Link") or "#",
        "portal": portal,
        "match_score": score,
        "is_match": is_match,
        "salary": salary,
        "skills": skills,
        "workplace": workplace
    }


def run_daily_scraper_pipeline(portal_limit=50, recipient_email=None, time_filter=604800, smtp_config=None):
    """
    Runs the multi-source scraping pipeline across LinkedIn, Indeed, and Direct Company ATS portals,
    strictly filtering for Python, Associate Software Engineer, Software Engineer, AI/LLM, AI roles
    with 0-6m, 0-1yr, Fresher experience posted in the last 7 days.
    """
    start_time = time.time()
    cfg = get_smtp_config()
    recipient = recipient_email or cfg["recipient"]
    
    print(f"\n=======================================================")
    print(f"[Daily Job Alert Cron] Starting execution at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Volume Target: Up to {portal_limit} for LinkedIn + Up to {portal_limit} for Indeed + Direct ATS")
    print(f"Target Roles: {', '.join(TARGET_ROLES)}")
    print(f"Target Exp: {', '.join(TARGET_EXPERIENCE)}")
    print(f"Target Locations: {', '.join(TARGET_LOCATIONS[:5])}...")
    print(f"Time Window: Last 7 Days (Startups, Mid-size, MNCs)")
    print(f"Recipient: {recipient}")
    print(f"=======================================================\n")
    
    linkedin_jobs = []
    indeed_jobs = []
    ats_jobs = []
    seen_urls = set()
    
    # 1. Scrape Direct Company ATS Portals (Sub-second response)
    print("--- [1/3] Scraping Official Career ATS Portals (Greenhouse/Lever/Ashby) ---")
    try:
        raw_ats = scrape_ats_jobs(limit=25)
        for rj in raw_ats:
            j = normalize_job_dict(rj, "Career ATS")
            link = j.get("link", "")
            if link and link not in seen_urls and j.get("is_match"):
                seen_urls.add(link)
                ats_jobs.append(j)
        print(f"-> Career ATS Verified Jobs: {len(ats_jobs)}\n")
    except Exception as e:
        print(f"[ATS Scraper Warning] {e}\n")

    # 2. Scrape LinkedIn (Target: up to 50 jobs)
    print(f"--- [2/3] Scraping LinkedIn with Stealth Evasion (Target: up to {portal_limit} jobs) ---")
    per_role_linkedin = max(10, portal_limit // len(TARGET_ROLES) + 2)
    for role_query in TARGET_ROLES:
        if len(linkedin_jobs) >= portal_limit:
            break
        try:
            print(f"[LinkedIn] Searching: '{role_query}' in India/Remote (Time: 7 days, Exp: Entry/Intern)...")
            raw_jobs = scrape_linkedin(
                role=role_query,
                time_filter=time_filter,
                limit=per_role_linkedin,
                locations=["India", "Bengaluru", "Indore", "Remote", "Pune"],
                experience="1,2"
            )
            print(f"   -> Fetched {len(raw_jobs)} LinkedIn raw jobs for '{role_query}'")
            for rj in raw_jobs:
                j = normalize_job_dict(rj, "LinkedIn")
                link = j.get("link", "")
                if link and link not in seen_urls and j.get("is_match"):
                    seen_urls.add(link)
                    linkedin_jobs.append(j)
                    if len(linkedin_jobs) >= portal_limit:
                        break
        except Exception as e:
            print(f"   [LinkedIn Warning] Error scraping '{role_query}': {e}")
            
    print(f"-> LinkedIn Final Curated Jobs: {len(linkedin_jobs)} / {portal_limit}\n")

    # 3. Scrape Indeed (Target: up to 50 jobs)
    print(f"--- [3/3] Scraping Indeed with Stealth Evasion (Target: up to {portal_limit} jobs) ---")
    fromage_days = max(1, time_filter // 86400)
    per_role_indeed = max(10, portal_limit // len(TARGET_ROLES) + 2)
    for role_query in TARGET_ROLES:
        if len(indeed_jobs) >= portal_limit:
            break
        try:
            print(f"[Indeed] Searching: '{role_query}' across cities (Time: {fromage_days} days, Exp: 0-1)...")
            raw_jobs = scrape_indeed(
                role=role_query,
                fromage_days=fromage_days,
                limit=per_role_indeed,
                locations=["Bengaluru", "Indore", "Pune", "Noida", "Hyderabad"],
                experience="0-1"
            )
            print(f"   -> Fetched {len(raw_jobs)} Indeed raw jobs for '{role_query}'")
            for rj in raw_jobs:
                j = normalize_job_dict(rj, "Indeed")
                link = j.get("link", "")
                if link and link not in seen_urls and j.get("is_match"):
                    seen_urls.add(link)
                    indeed_jobs.append(j)
                    if len(indeed_jobs) >= portal_limit:
                        break
        except Exception as e:
            print(f"   [Indeed Warning] Error scraping '{role_query}': {e}")

    print(f"-> Indeed Final Curated Jobs: {len(indeed_jobs)} / {portal_limit}\n")

    # Combine all curated jobs
    all_curated_jobs = ats_jobs + linkedin_jobs + indeed_jobs
    print(f"[Summary] Total curated matching jobs: {len(all_curated_jobs)} (ATS: {len(ats_jobs)}, LinkedIn: {len(linkedin_jobs)}, Indeed: {len(indeed_jobs)})")
    
    # Save full curated jobs list to JSON file
    os.makedirs("data", exist_ok=True)
    json_path = os.path.join("data", "latest_scraped_jobs.json")
    try:
        import json
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(all_curated_jobs, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[JSON Save Warning] {e}")

    # 4. Dispatch Email Digest
    print("\n--- Generating and Dispatching Daily Email Digest ---")
    email_result = send_job_digest_email(
        jobs=all_curated_jobs,
        target_roles=TARGET_ROLES,
        target_exp=TARGET_EXPERIENCE,
        target_locations=TARGET_LOCATIONS,
        recipient_email=recipient,
        smtp_config=smtp_config
    )
    
    elapsed = round(time.time() - start_time, 2)
    print(f"\n[Daily Job Alert Cron] Completed in {elapsed}s!")
    print(f"Result: {email_result.get('message')}\n")
    
    return {
        "success": True,
        "total_jobs": len(all_curated_jobs),
        "linkedin_count": len(linkedin_jobs),
        "indeed_count": len(indeed_jobs),
        "ats_count": len(ats_jobs),
        "recipient": recipient,
        "email_status": email_result,
        "elapsed_seconds": elapsed,
        "executed_at": datetime.now().isoformat()
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JobRadar Multi-Source Job Alert Cron")
    parser.add_argument("--now", action="store_true", help="Execute the daily job alert scraper and email dispatch immediately")
    parser.add_argument("--limit", type=int, default=50, help="Target max jobs per portal (default: 50 for LinkedIn + 50 for Indeed)")
    parser.add_argument("--to", type=str, default=None, help="Recipient email address")
    parser.add_argument("--time-filter", type=int, default=604800, help="Seconds filter (default: 604800 = 7 days)")
    
    args = parser.parse_args()
    
    run_daily_scraper_pipeline(
        portal_limit=args.limit,
        recipient_email=args.to,
        time_filter=args.time_filter
    )
