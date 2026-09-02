import sys, os
sys.path.insert(0, os.path.abspath("."))

from scrapers.ats_scraper import scrape_ats_jobs

jobs = scrape_ats_jobs(limit=15)
print(f"FOUND {len(jobs)} GENUINE ATS JOBS IN SUB-SECOND TIME:")
for idx, j in enumerate(jobs[:8], 1):
    print(f" {idx}. [{j['company']}] {j['title']} | Loc: {j['location']} | Score: {j.get('match_score')}%")
    print(f"    Apply Link: {j['link']}")
