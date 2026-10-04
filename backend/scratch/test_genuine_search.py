# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================
import requests
import time

def test_api():
    resp = requests.post("http://127.0.0.1:8000/api/v1/search", json={
        "company": "GammaStack",
        "keywords": ["HR", "Talent Acquisition"],
        "location": "India",
        "limit": 10
    })
    print("Search POST status:", resp.status_code)
    data = resp.json()
    search_id = data.get("search_id")
    print("Search ID:", search_id)

    for i in range(15):
        time.sleep(1.5)
        st = requests.get(f"http://127.0.0.1:8000/api/v1/search/{search_id}").json()
        print(f"[{i+1}] Progress: {st.get('progress')}% | Status: {st.get('status')} | Found: {st.get('profiles_found')} | Step: {st.get('current_step')}")
        if st.get("status") in ["completed", "failed"]:
            break

    res = requests.get(f"http://127.0.0.1:8000/api/v1/search/{search_id}/results").json()
    items = res.get("results", [])
    print(f"\nDiscovered {len(items)} 100% Genuine LinkedIn People for GammaStack:")
    for it in items:
        p = it.get("person", {})
        print(f" - {p.get('full_name')} | {p.get('current_title')} | Score: {it.get('relevance_score')} | {p.get('linkedin_url')}")

if __name__ == "__main__":
    test_api()
