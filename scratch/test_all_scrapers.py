import sys
import json

from scrapers.apna import scrape_apna
from scrapers.shine import scrape_shine
from scrapers.foundit import scrape_foundit
from scrapers.naukri import scrape_naukri
from scrapers.glassdoor import scrape_glassdoor
from scrapers.indeed import scrape_indeed
from scrapers.hirist import scrape_hirist

print("--- Testing APNA ---")
try:
    apna_jobs = scrape_apna(role="DevOps", city="Bengaluru", posted_in_days=3, limit=5, min_experience=0, max_experience=1)
    print(f"Apna count: {len(apna_jobs)}")
    if apna_jobs:
        print(apna_jobs[0])
except Exception as e:
    print(f"Apna error: {e}")

print("\n--- Testing SHINE ---")
try:
    shine_jobs = scrape_shine(role="DevOps", city="Bengaluru", fexp=["1"], posting_days=3, limit=5)
    print(f"Shine count: {len(shine_jobs)}")
    if shine_jobs:
        print(shine_jobs[0])
except Exception as e:
    print(f"Shine error: {e}")

print("\n--- Testing FOUNDIT ---")
try:
    foundit_jobs = scrape_foundit(role="DevOps", city="Bengaluru", job_freshness_days=7, limit=5, experience=1)
    print(f"Foundit count: {len(foundit_jobs)}")
    if foundit_jobs:
        print(foundit_jobs[0])
except Exception as e:
    print(f"Foundit error: {e}")

print("\n--- Testing NAUKRI ---")
try:
    naukri_jobs = scrape_naukri(role="DevOps", city="Bengaluru", job_age_days=7, limit=5, experience=1)
    print(f"Naukri count: {len(naukri_jobs)}")
    if naukri_jobs:
        print(naukri_jobs[0])
except Exception as e:
    print(f"Naukri error: {e}")

print("\n--- Testing GLASSDOOR ---")
try:
    gd_jobs = scrape_glassdoor(role="DevOps", from_age_days=7, limit=5, locations=["Bengaluru"], apply_mode="include_easy", experience="1-2")
    print(f"Glassdoor count: {len(gd_jobs)}")
    if gd_jobs:
        print(gd_jobs[0])
except Exception as e:
    print(f"Glassdoor error: {e}")

print("\n--- Testing INDEED ---")
try:
    indeed_jobs = scrape_indeed(role="DevOps", fromage_days=7, limit=5, locations=["Bengaluru"], apply_mode="include_easy", experience="1-2")
    print(f"Indeed count: {len(indeed_jobs)}")
    if indeed_jobs:
        print(indeed_jobs[0])
except Exception as e:
    print(f"Indeed error: {e}")

print("\n--- Testing HIRIST ---")
try:
    hirist_jobs = scrape_hirist(category="devops-sre-jobs", city="Bengaluru", exp_key="0-1", posting_days=7, limit=5)
    print(f"Hirist count: {len(hirist_jobs)}")
    if hirist_jobs:
        print(hirist_jobs[0])
except Exception as e:
    print(f"Hirist error: {e}")
