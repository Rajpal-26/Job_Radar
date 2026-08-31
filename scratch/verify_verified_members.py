import requests

companies = ["supersourcing technologies pvt ltd", "Razorpay", "Swiggy", "Google", "Zomato", "Meesho", "Zerodha"]

for comp in companies:
    r = requests.post("http://127.0.0.1:5000/api/search_recruiters", json={
        "company": comp,
        "recruiter_keyword": "HR Manager",
        "location": "India"
    })
    data = r.json()
    print(f"\n=== {data['data']['company']} ===")
    for m in data['data']['members'][:3]:
        print(f"- {m['name']} ({m['position']}) | Verified: {m.get('verified', False)}")
        print(f"  URL: {m['profile_url']}")
