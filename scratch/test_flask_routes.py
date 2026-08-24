from app import app

client = app.test_client()

routes = [
    ("/search/apna", {"role": "DevOps Engineer", "city": "Bengaluru", "posted_in": "7", "experience": "1-3", "limit": "5"}),
    ("/search/shine", {"role": "DevOps Engineer", "city": "Bengaluru", "posting_days": "7", "experience": "1-3", "limit": "5"}),
    ("/search/foundit", {"role": "DevOps Engineer", "city": "Bengaluru", "freshness": "7", "experience": "1-3", "limit": "5"}),
    ("/search/hirist", {"role": "devops-sre-jobs", "city": "Bengaluru", "posting": "7", "experience": "1-3", "limit": "5"}),
    ("/search/naukri", {"role": "DevOps Engineer", "city": "Bengaluru", "job_age": "7", "experience": "1-3", "limit": "5"}),
    ("/search/glassdoor", {"role": "DevOps Engineer", "locations": ["Bengaluru"], "from_age": "7", "experience": "1-3", "limit": "5", "apply_mode": "include_easy"}),
    ("/search/indeed", {"role": "DevOps Engineer", "locations": ["Bengaluru"], "fromage": "7", "experience": "1-3", "limit": "5", "apply_mode": "include_easy"}),
]

for endpoint, data in routes:
    print(f"\n==========================================")
    print(f"POST {endpoint} with data: {data}")
    print(f"==========================================")
    try:
        response = client.post(endpoint, data=data)
        res_json = response.get_json()
        print(f"Status Code: {response.status_code}")
        print(f"Response: count={res_json.get('count') if res_json else None}, error={res_json.get('error') if res_json else None}")
        if res_json and "jobs" in res_json and res_json["jobs"]:
            print(f"First job: {res_json['jobs'][0]['Job Title']} @ {res_json['jobs'][0]['Company']}")
        elif res_json and "jobs" in res_json:
            print("WARNING: jobs list is EMPTY!")
    except Exception as e:
        print(f"EXCEPTION: {e}")
