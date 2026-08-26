from utils.search_engine import execute_parallel_search, deduplicate_jobs, filter_and_rank_jobs
from scrapers import (scrape_linkedin, scrape_glassdoor, scrape_indeed,
                      scrape_hirist, scrape_naukri, scrape_foundit,
                      scrape_apna, scrape_shine)

scrapers_map = {
    "linkedin": scrape_linkedin,
    "glassdoor": scrape_glassdoor,
    "indeed": scrape_indeed,
    "hirist": scrape_hirist,
    "naukri": scrape_naukri,
    "foundit": scrape_foundit,
    "apna": scrape_apna,
    "shine": scrape_shine,
}

print("Testing execute_parallel_search across ALL 8 portals...")
raw_jobs = execute_parallel_search(
    scrapers_map=scrapers_map,
    role="Associate Software Engineer",
    fromage_days=14,
    limit=40,
    locations=["Bengaluru", "Pune", "Noida"],
    apply_mode="include_easy",
    experience="fresher",
    selected_portals=["indeed", "naukri", "glassdoor", "foundit", "apna", "shine", "hirist", "linkedin"]
)

print(f"\nTotal Raw Jobs Scraped: {len(raw_jobs)}")
deduped = deduplicate_jobs(raw_jobs)
print(f"Deduplicated Jobs: {len(deduped)}")

final_jobs = filter_and_rank_jobs(
    jobs=deduped,
    include_kw="python developer",
    exclude_kw="senior,lead,QA",
    min_salary=0,
    workplace_mode="all",
    resume_text="Python, Django, FastAPI, SQL"
)

print(f"Final Matching Jobs Returned: {len(final_jobs)}")
for idx, j in enumerate(final_jobs[:10]):
    print(f"{idx+1}. [{j.get('Location')}] {j.get('Job Title')} @ {j.get('Company')} (Match: {j.get('Match_Score')}%, Platforms: {j.get('Platforms')})")
