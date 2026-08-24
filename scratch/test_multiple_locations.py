import json
from app import app

client = app.test_client()

multi_loc_tests = [
    ("Indeed", "/search/indeed", {
        "role": "DevOps Engineer",
        "locations": ["Bengaluru", "Mumbai"],
        "fromage": "7",
        "experience": "1-3",
        "limit": "5"
    }),
    ("Glassdoor", "/search/glassdoor", {
        "role": "DevOps Engineer",
        "locations": ["Bengaluru", "Mumbai"],
        "from_age": "7",
        "experience": "1-3",
        "limit": "5"
    }),
    ("Naukri", "/search/naukri", {
        "role": "DevOps Engineer",
        "locations": ["Bengaluru", "Mumbai"],
        "job_age": "7",
        "experience": "1-3",
        "limit": "5"
    }),
    ("Foundit", "/search/foundit", {
        "role": "DevOps Engineer",
        "locations": ["Bengaluru", "Mumbai"],
        "freshness": "7",
        "experience": "1-3",
        "limit": "5"
    }),
    ("Apna", "/search/apna", {
        "role": "DevOps Engineer",
        "locations": ["Bengaluru", "Mumbai"],
        "posted_in": "7",
        "experience": "1-3",
        "limit": "5"
    }),
    ("Shine", "/search/shine", {
        "role": "DevOps Engineer",
        "locations": ["Bengaluru", "Mumbai"],
        "posting_days": "7",
        "experience": "1-3",
        "limit": "5"
    }),
    ("Hirist", "/search/hirist", {
        "role": "devops-sre-jobs",
        "locations": ["Bengaluru", "Mumbai"],
        "posting": "7",
        "experience": "1-3",
        "limit": "5"
    }),
]

print("==========================================================")
print("TESTING MULTIPLE LOCATION FILTER ACROSS ALL 7 PLATFORMS")
print("Locations: ['Bengaluru', 'Mumbai']")
print("==========================================================")

summary_results = {}

for name, endpoint, data in multi_loc_tests:
    print(f"\n---> Testing {name} endpoint: {endpoint}")
    print(f"     Payload: {data}")
    try:
        res = client.post(endpoint, data=data)
        res_json = res.get_json() or {}
        count = res_json.get("count", 0)
        jobs = res_json.get("jobs", [])
        error = res_json.get("error")

        print(f"     Status: {res.status_code}")
        print(f"     Count: {count}, Error: {error}")

        if jobs:
            cities_found = set(j.get("Location", "N/A") for j in jobs)
            print(f"     First Job: '{jobs[0].get('Job Title')}' @ {jobs[0].get('Company')} [{jobs[0].get('Location')}]")
            print(f"     Unique Locations in Results: {list(cities_found)}")
            summary_results[name] = {"status": "SUCCESS", "count": count, "first_job": f"{jobs[0].get('Job Title')} @ {jobs[0].get('Company')}", "locations_found": list(cities_found)}
        else:
            print("     WARNING: No jobs returned!")
            summary_results[name] = {"status": "NO RESULTS", "count": 0, "error": error}
    except Exception as e:
        print(f"     EXCEPTION: {e}")
        summary_results[name] = {"status": "EXCEPTION", "error": str(e)}

print("\n" + "="*60)
print("SUMMARY RESULTS FOR MULTIPLE LOCATIONS TEST")
print("="*60)
for name, info in summary_results.items():
    print(f"{name:<12}: Status={info['status']:<10} Count={info.get('count', 0)} Details={info.get('first_job', info.get('error', ''))}")
