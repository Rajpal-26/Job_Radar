# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================
import requests

r = requests.get('http://127.0.0.1:8000/api/v1/search/d0e426bd-8acc-4795-a903-91e848d2da04/results').json()
print('Thoughtwin Results Saved in DB:', len(r.get('results', [])))
for item in r.get('results', []):
    p = item['person']
    print(f" * {p['full_name']} | {p['current_title']} | {p['location']} | {p['linkedin_url']}")
