# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

"""
Daily Job Alert Cron & Pipeline for Indeed & LinkedIn Scrapers.
Scrapes 50 targeted daily jobs for:
- Roles: Python Developer, Associate Software Engineer, Software Engineer, AI/LLM Engineer, AI Engineer
- Experience: 0-6 months, 0-1 year, Fresher
- Locations: All configured tech locations (Indore, Bengaluru, Pune, Hyderabad, Noida, Gurugram, Mumbai, Remote, India)
- Portals: Indeed & LinkedIn
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
from services.email_alert_service import send_job_digest_email, DEFAULT_RECIPIENT

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

# Relevant title tokens for strict matching
MATCH_ROLE_PATTERNS = [
    r"\bpython\b",
    r"\bassociate\s+software\s+engineer\b",
    r"\bsoftware\s+engineer\b",
    r"\bsoftware\s+developer\b",
    r"\bllm\b",
    r"\bai\s+engineer\b",
    r"\bai\s+developer\b",
    r"\bgenai\b",
    r"\bjunior\s+developer\b",
    r"\bentry\s+level\b"
]

# Seniority rejection tokens (to exclude Senior/Lead/Staff/10+ Yrs jobs)
EXCLUDE_TITLE_PATTERNS = [
    r"\bsenior\b",
    r"\bsr\.\b",
    r"\blead\b",
    r"\bprincipal\b",
    r"\bstaff\b",
    r"\barchitect\b",
    r"\bdirector\b",
    r"\bmanager\b",
    r"\b5\+\s*years?\b",
    r"\b7\+\s*years?\b",
    r"\b10\+\s*years?\b"
]


def is_matching_job(job):
    """Strictly validates if a job matches the user's role and experience criteria."""
    title = job.get("title", "").lower()
    exp = job.get("experience", "").lower()
    
    # 1. Check for senior/lead exclusion
    for exc in EXCLUDE_TITLE_PATTERNS:
        if re.search(exc, title):
            return False
            
    # 2. Check if experience is senior
    if any(k in exp for k in ["senior", "lead", "3-5", "5-7", "7-10", "10+", "5+", "7+"]):
        return False
        
    # 3. Check role pattern match
    matched_role = False
    for pat in MATCH_ROLE_PATTERNS:
        if re.search(pat, title):
            matched_role = True
            break
            
    return matched_role


def normalize_job_dict(job, portal):
    """Normalize keys across different scrapers."""
    return {
        "title": job.get("title") or job.get("Job Title") or "Software Engineer",
        "company": job.get("company") or job.get("Company") or "Tech Company",
        "location": job.get("location") or job.get("Location") or "India",
        "experience": job.get("experience") or job.get("Experience") or "Fresher / 0-1 Yr",
        "posted": job.get("posted") or job.get("Posted") or "Today",
        "link": job.get("link") or job.get("Link") or "#",
        "portal": portal
    }


def run_daily_scraper_pipeline(limit=50, recipient_email=None, time_filter=86400, smtp_config=None):
    """
    Runs the daily scraper pipeline across LinkedIn and Indeed,
    filters the top matching 50 jobs, and sends the email digest.
    """
    start_time = time.time()
    recipient = recipient_email or DEFAULT_RECIPIENT
    print(f"\n=======================================================")
    print(f"[Daily Job Alert Cron] Starting execution at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target Roles: {', '.join(TARGET_ROLES)}")
    print(f"Target Exp: {', '.join(TARGET_EXPERIENCE)}")
    print(f"Target Locations: {', '.join(TARGET_LOCATIONS[:5])}...")
    print(f"Recipient: {recipient}")
    print(f"=======================================================\n")
    
    collected_jobs = []
    seen_urls = set()
    
    # Subdivide limit roughly across portals and key search queries
    per_query_limit = max(10, limit // len(TARGET_ROLES))
    
    # 1. Scrape LinkedIn for top queries
    print("--- [1/2] Scraping LinkedIn for Junior/Fresher Roles ---")
    for role_query in TARGET_ROLES:
        if len(collected_jobs) >= limit:
            break
        try:
            print(f"[LinkedIn] Searching: '{role_query}' in India/Remote (Time: 24h, Exp: 0-1 Yr)...")
            # Using LinkedIn scraper with 0-1 Yr experience parameter '1,2' (internship/entry level)
            raw_jobs = scrape_linkedin(
                role=role_query,
                time_filter=time_filter,
                limit=per_query_limit,
                locations=["India", "Bengaluru", "Indore", "Remote"],
                experience="1,2"
            )
            print(f"   -> Found {len(raw_jobs)} LinkedIn jobs")
            for rj in raw_jobs:
                j = normalize_job_dict(rj, "LinkedIn")
                link = j.get("link", "")
                if link and link not in seen_urls and is_matching_job(j):
                    seen_urls.add(link)
                    collected_jobs.append(j)
                    if len(collected_jobs) >= limit:
                        break
        except Exception as e:
            print(f"   [LinkedIn Warning] Scrape error for '{role_query}': {e}")
            
    # 2. Scrape Indeed for top queries
    print("\n--- [2/2] Scraping Indeed for Junior/Fresher Roles ---")
    fromage_days = max(1, time_filter // 86400)
    for role_query in TARGET_ROLES:
        if len(collected_jobs) >= limit:
            break
        try:
            print(f"[Indeed] Searching: '{role_query}' in top cities (Time: {fromage_days}d, Exp: 0-1)...")
            raw_jobs = scrape_indeed(
                role=role_query,
                fromage_days=fromage_days,
                limit=per_query_limit,
                locations=["Bengaluru", "Indore", "Pune", "Noida", "Hyderabad"],
                experience="0-1"
            )
            print(f"   -> Found {len(raw_jobs)} Indeed jobs")
            for rj in raw_jobs:
                j = normalize_job_dict(rj, "Indeed")
                link = j.get("link", "")
                if link and link not in seen_urls and is_matching_job(j):
                    seen_urls.add(link)
                    collected_jobs.append(j)
                    if len(collected_jobs) >= limit:
                        break
        except Exception as e:
            print(f"   [Indeed Warning] Scrape error for '{role_query}': {e}")

    print(f"\n[Status] Total strictly matching jobs collected: {len(collected_jobs)} / {limit}")
    
    # Sort jobs by date / portal
    curated_jobs = collected_jobs[:limit]
    
    # Send Email Digest
    print("\n--- [3/3] Generating and Dispatching Daily Email Digest ---")
    email_result = send_job_digest_email(
        jobs=curated_jobs,
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
        "jobs_count": len(curated_jobs),
        "recipient": recipient,
        "email_status": email_result,
        "elapsed_seconds": elapsed,
        "executed_at": datetime.now().isoformat()
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JobRadar Daily Indeed & LinkedIn Scraper Cron")
    parser.add_argument("--now", action="store_true", help="Execute the daily job alert scraper and email dispatch immediately")
    parser.add_argument("--limit", type=int, default=50, help="Target number of jobs to curate (default: 50)")
    parser.add_argument("--to", type=str, default=None, help="Recipient email address")
    parser.add_argument("--time-filter", type=int, default=86400, help="Seconds filter (default: 86400 = 24 hours)")
    
    args = parser.parse_args()
    
    run_daily_scraper_pipeline(
        limit=args.limit,
        recipient_email=args.to,
        time_filter=args.time_filter
    )
