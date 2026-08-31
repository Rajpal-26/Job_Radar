import requests

r = requests.post("http://127.0.0.1:5000/api/search_recruiters", json={
    "company": "supersourcing technologies pvt ltd",
    "recruiter_keyword": "HR Manager",
    "location": "India"
})

data = r.json()
print("STATUS:", r.status_code)
print("COMPANY:", data['data']['company'])
print("KEYWORD:", data['data']['keyword'])
print("TOTAL MEMBERS:", len(data['data']['members']))
for m in data['data']['members']:
    print(f"- {m['name']} | {m['position']} | {m['company']} | {m['experience']}")
    print(f"  Profile Link: {m['profile_url']}")
