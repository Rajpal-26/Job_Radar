import requests

url = "http://127.0.0.1:5000/search/indeed"
payload = {
    "role": "associate software engineer",
    "fromage": "10",
    "limit": "50",
    "experience": "fresher",
    "apply_mode": "include_easy",
    "locations": "Bengaluru, Pune, Noida, Gurugram, Indore, Ahmedabad"
}

print("Posting to Flask server /search/indeed...")
res = requests.post(url, data=payload)
print(f"Status Code: {res.status_code}")
data = res.json()
jobs = data.get("jobs", [])
print(f"Total Jobs Received from Server: {len(jobs)}")
for idx, j in enumerate(jobs[:5]):
    print(f"{idx+1}. [{j.get('Location')}] {j.get('Job Title')} @ {j.get('Company')}")
