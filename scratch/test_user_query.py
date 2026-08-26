import requests

url = "http://127.0.0.1:5000/search/all"
payload = {
    "role": "Associate Software Engineer",
    "locations": "Bengaluru, Pune, Noida",
    "fromage": "14",
    "limit": "20",
    "portals": "indeed,naukri,glassdoor,foundit,apna,shine,hirist,linkedin",
    "include_keywords": "python developer",
    "exclude_keywords": "senior,lead,QA",
    "min_salary": "0",
    "workplace_mode": "all",
    "resume_text": "Python, Django, FastAPI, SQL, Docker"
}

print("Testing POST /search/all with User's Exact Query...")
res = requests.post(url, data=payload)
print(f"Status Code: {res.status_code}")
data = res.json()
jobs = data.get("jobs", [])
print(f"Total Jobs Received from Unified Search: {len(jobs)}")
print(f"Raw Total Scraped: {data.get('raw_total')}, Duplicates Removed: {data.get('duplicates_removed')}")
for idx, j in enumerate(jobs[:10]):
    print(f"{idx+1}. [{j.get('Location')}] {j.get('Job Title')} @ {j.get('Company')} (Match: {j.get('Match_Score')}%, Platforms: {j.get('Platforms')})")
