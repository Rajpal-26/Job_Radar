import sys, os
import json
sys.path.insert(0, os.path.abspath("."))

from services.daily_job_cron import run_daily_scraper_pipeline

print("Starting full scraping test (Target: up to 50 jobs per platform)...")
result = run_daily_scraper_pipeline(portal_limit=50, recipient_email="kapiltanwar0369@gmail.com")

print("\n\n========================= FULL JOB SUMMARY =========================")
print(f"Total Jobs Gathered: {result.get('total_jobs')}")
print(f"ATS Jobs: {result.get('ats_count')}")
print(f"LinkedIn Jobs: {result.get('linkedin_count')}")
print(f"Indeed Jobs: {result.get('indeed_count')}")
print(f"Elapsed Time: {result.get('elapsed_seconds')}s")
print("====================================================================\n")
