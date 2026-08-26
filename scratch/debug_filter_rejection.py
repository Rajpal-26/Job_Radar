from utils.search_engine import execute_parallel_search, deduplicate_jobs, evaluate_keywords
from scrapers import (scrape_linkedin, scrape_glassdoor, scrape_indeed,
                      scrape_hirist, scrape_naukri, scrape_foundit,
                      scrape_apna, scrape_shine)
import re

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

raw_jobs = execute_parallel_search(
    scrapers_map=scrapers_map,
    role="Associate Software Engineer",
    fromage_days=14,
    limit=20,
    locations=["Bengaluru", "Pune", "Noida"],
    apply_mode="include_easy",
    experience=None,
    selected_portals=["indeed", "naukri", "glassdoor", "foundit", "apna", "shine", "hirist", "linkedin"]
)

deduped = deduplicate_jobs(raw_jobs)
print(f"\n--- SCRAPED {len(raw_jobs)} RAW JOBS, {len(deduped)} DEDUPLICATED JOBS ---")

inc = "python developer"
exc = "senior,lead,QA"

for idx, j in enumerate(deduped):
    title = j.get("Job Title", "")
    comp = j.get("Company", "")
    desc = j.get("Description", "")
    skills = j.get("Skills", "")

    combo = f"{title} {skills} {desc} {comp}".lower()
    res = evaluate_keywords(j, include_kw=inc, exclude_kw=exc)

    print(f"\nJOB {idx+1}: Title='{title}', Company='{comp}'")
    print(f"   Skills: {skills!r}")
    print(f"   Description: {desc[:100]!r}")
    print(f"   Evaluate Result: {res}")
    
    if not res:
        ex_terms = [k.strip().lower() for k in exc.split(",") if k.strip()]
        for t in ex_terms:
            pat = r"\b" + re.escape(t) + r"\b"
            if re.search(pat, title.lower()):
                print(f"   REASON REJECTED: Exclude term '{t}' found in title '{title}'")
        
        tokens = [t.strip().lower() for t in re.split(r"[\s,]+", inc) if t.strip()]
        matched = [t for t in tokens if re.search(r"\b" + re.escape(t) + r"\b", combo)]
        missing = [t for t in tokens if t not in matched]
        print(f"   Include Tokens Matched: {matched}, Missing: {missing}")
