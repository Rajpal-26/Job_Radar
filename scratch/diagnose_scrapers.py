import os
import json
import traceback
from datetime import datetime

# Make sure scrapers can be imported
from scrapers.indeed import scrape_indeed, INDEED_CITIES
from scrapers.apna import scrape_apna, APNA_CITIES
from scrapers.shine import scrape_shine, SHINE_CITIES
from scrapers.foundit import scrape_foundit, FOUNDIT_CITIES
from scrapers.naukri import scrape_naukri, NAUKRI_CITIES
from scrapers.glassdoor import scrape_glassdoor, GLASSDOOR_CITIES
from scrapers.hirist import scrape_hirist, HIRIST_CATEGORIES, HIRIST_CITIES

def run_test(name, fn, *args, **kwargs):
    print(f"\n==========================================")
    print(f"TESTING: {name}")
    print(f"Args: {args}, Kwargs: {kwargs}")
    print(f"==========================================")
    try:
        results = fn(*args, **kwargs)
        print(f"SUCCESS! Got {len(results)} jobs.")
        if results:
            print("Sample job:", json.dumps(results[0], indent=2))
        else:
            print("WARNING: Returned 0 jobs!")
    except Exception as e:
        print(f"FAILED with exception: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    # Test 1: Indeed
    run_test("Indeed default", scrape_indeed, role="DevOps", fromage_days=7, limit=10, locations=["Bengaluru"], apply_mode="include_easy", experience="")
    run_test("Indeed with experience filter", scrape_indeed, role="DevOps", fromage_days=7, limit=10, locations=["Bengaluru"], apply_mode="include_easy", experience="1-3")

    # Test 2: Glassdoor
    run_test("Glassdoor default", scrape_glassdoor, role="DevOps", from_age_days=7, limit=10, locations=["Bengaluru"], apply_mode="include_easy", experience="")
    run_test("Glassdoor with experience filter", scrape_glassdoor, role="DevOps", from_age_days=7, limit=10, locations=["Bengaluru"], apply_mode="include_easy", experience="1-3")

    # Test 3: Naukri
    run_test("Naukri default", scrape_naukri, role="DevOps", city="Bengaluru", job_age_days=7, limit=10, experience=None)
    run_test("Naukri with experience filter", scrape_naukri, role="DevOps", city="Bengaluru", job_age_days=7, limit=10, experience=1)

    # Test 4: Foundit
    run_test("Foundit default", scrape_foundit, role="DevOps", city="Bengaluru", job_freshness_days=7, limit=10, experience=None)
    run_test("Foundit with experience filter", scrape_foundit, role="DevOps", city="Bengaluru", job_freshness_days=7, limit=10, experience=1)

    # Test 5: Apna
    run_test("Apna default", scrape_apna, role="DevOps", city="Bengaluru", posted_in_days=7, limit=10, min_experience=None, max_experience=None)
    run_test("Apna with experience filter", scrape_apna, role="DevOps", city="Bengaluru", posted_in_days=7, limit=10, min_experience=1, max_experience=3)

    # Test 6: Shine
    run_test("Shine default", scrape_shine, role="DevOps", city="Bengaluru", fexp=[], posting_days=7, limit=10)
    run_test("Shine with experience filter", scrape_shine, role="DevOps", city="Bengaluru", fexp=["2"], posting_days=7, limit=10)

    # Test 7: Hirist
    run_test("Hirist default", scrape_hirist, category="devops-sre-jobs", city="Bengaluru", exp_key="any", posting_days=7, limit=10)
    run_test("Hirist with experience filter", scrape_hirist, category="devops-sre-jobs", city="Bengaluru", exp_key="2-3", posting_days=7, limit=10)
