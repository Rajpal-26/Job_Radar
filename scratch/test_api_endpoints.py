import requests

BASE_URL = "http://127.0.0.1:5000"

print("--- 1. Testing POST /api/saved_jobs ---")
sample_job = {
    "Job Title": "Senior Python Engineer",
    "Company": "AI Innovations",
    "Location": "Bengaluru",
    "Link": "https://jobradar.test/job123",
    "Platform": "Indeed",
    "Salary": "18 LPA",
    "Match_Score": 96,
    "status": "Bookmarked"
}

res = requests.post(f"{BASE_URL}/api/saved_jobs", json=sample_job)
print(f"Save Status Code: {res.status_code}, Response: {res.json()}")
assert res.status_code == 200
job_id = res.json().get("id")

print("\n--- 2. Testing GET /api/saved_jobs ---")
res_get = requests.get(f"{BASE_URL}/api/saved_jobs")
print(f"GET Saved Jobs Count: {len(res_get.json())}")
assert res_get.status_code == 200

print("\n--- 3. Testing PUT /api/saved_jobs/<id> ---")
res_put = requests.put(f"{BASE_URL}/api/saved_jobs/{job_id}", json={"status": "Applied", "notes": "Applied via company site"})
print(f"PUT Status Code: {res_put.status_code}")
assert res_put.status_code == 200

print("\n--- 4. Testing POST /api/generate_cover_letter ---")
res_cl = requests.post(f"{BASE_URL}/api/generate_cover_letter", json={
    "job": sample_job,
    "resume_text": "Experienced Python Backend Developer skilled in FastAPI, SQL, Docker, AWS"
})
print(f"Cover Letter Generated Length: {len(res_cl.json().get('cover_letter', ''))}")
assert res_cl.status_code == 200

print("\n--- 5. Testing DELETE /api/saved_jobs/<id> ---")
res_del = requests.delete(f"{BASE_URL}/api/saved_jobs/{job_id}")
print(f"DELETE Status Code: {res_del.status_code}")
assert res_del.status_code == 200

print("\nALL API ENDPOINT INTEGRATION TESTS PASSED!")
