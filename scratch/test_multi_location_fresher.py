from scrapers.indeed import scrape_indeed

print("Testing scrape_indeed with multi-location & Fresher experience...")
jobs = scrape_indeed(
    role="associate software engineer",
    fromage_days=10,
    limit=50,
    locations=["Bengaluru", "Pune", "Noida", "Gurugram", "Indore", "Ahmedabad"],
    apply_mode="include_easy",
    experience="fresher"
)

print(f"\nResult Count: {len(jobs)}")
for idx, j in enumerate(jobs[:10]):
    print(f"{idx+1}. [{j.get('Location')}] {j.get('Job Title')} @ {j.get('Company')} (Posted {j.get('Posted')})")
