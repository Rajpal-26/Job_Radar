from scrapers.indeed import scrape_indeed, _scrape_with
from playwright.sync_api import sync_playwright

print("Testing Indeed scrape directly...")
with sync_playwright() as p:
    jobs, blocked = _scrape_with(
        p,
        role="associate software engineer",
        fromage_days=10,
        internal_limit=50,
        locations=["Bengaluru", "Pune", "Noida", "Gurugram", "Indore", "Ahmedabad"],
        apply_mode="include_easy",
        headless=False
    )
    print(f"Direct _scrape_with returned {len(jobs)} jobs, blocked={blocked}")
    for j in jobs[:5]:
        print(" -", j.get("Job Title"), "@", j.get("Company"), "[", j.get("Location"), "]")
