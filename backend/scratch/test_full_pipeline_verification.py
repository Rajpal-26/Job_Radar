# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================
import requests
import time

def test_full_pipeline(company, keywords):
    print(f"\n=======================================================")
    print(f" TESTING RECRUITER PIPELINE: {company} | {keywords}")
    print(f"=======================================================")
    
    # 1. Test FastAPI Backend (Port 8000)
    resp = requests.post("http://127.0.0.1:8000/api/v1/search", json={
        "company": company,
        "keywords": keywords,
        "location": "India",
        "limit": 10
    })
    s_id = resp.json().get("search_id")
    print(f"[FastAPI] Created Search ID: {s_id}")
    for _ in range(15):
        time.sleep(1.5)
        st = requests.get(f"http://127.0.0.1:8000/api/v1/search/{s_id}").json()
        if st.get("status") in ["completed", "failed"]:
            print(f"[FastAPI] Search Finished: {st.get('status')} | Found {st.get('profiles_found')} profiles")
            break

    res_fastapi = requests.get(f"http://127.0.0.1:8000/api/v1/search/{s_id}/results").json()
    items = res_fastapi.get("results", [])
    print(f"[FastAPI] Validated Discovered Profiles ({len(items)}):")
    for it in items[:5]:
        p = it.get("person", {})
        print(f"  * {p.get('full_name')} | {p.get('current_title')} | {p.get('location')} | {p.get('linkedin_url')}")

    # 2. Test Flask App (Port 5000)
    resp_flask = requests.post("http://127.0.0.1:5000/api/search_recruiters", json={
        "company": company,
        "recruiter_keyword": keywords[0] if keywords else "HR",
        "location": "India"
    })
    flask_data = resp_flask.json().get("data", {})
    members = flask_data.get("members", [])
    print(f"[Flask] Validated Discovered Profiles ({len(members)}):")
    for m in members[:5]:
        print(f"  * {m.get('name')} | {m.get('position')} | {m.get('location')} | {m.get('profile_url')}")

if __name__ == "__main__":
    test_full_pipeline("Thoughtwin", ["Talent Acquisition", "Technical Recruiter"])
    test_full_pipeline("GammaStack", ["Talent Acquisition", "HR"])
    test_full_pipeline("Infosys", ["Talent Acquisition", "HR Manager"])
