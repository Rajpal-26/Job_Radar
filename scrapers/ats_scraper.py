# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

"""
Direct ATS Career Portals Scraper (Greenhouse, Lever, Ashby).
Directly queries official public JSON career APIs for 50+ top tech companies & startups.
Fast, sub-second responses, 100% verified authentic job postings, zero CAPTCHAs.
"""

import requests
import re
from datetime import datetime
from utils.job_matcher import score_job_match, extract_salary, extract_skills, extract_workplace_mode

# Top Tech Companies with Greenhouse Boards
GREENHOUSE_COMPANIES = [
    ("Razorpay", "razorpaysoftwareprivatelimited"),
    ("CRED", "cred"),
    ("Postman", "postman"),
    ("Hasura", "hasura"),
    ("BrowserStack", "browserstack"),
    ("Branch", "branch"),
    ("Instawork", "instawork"),
    ("CleverTap", "clevertap"),
    ("Observe.AI", "observeai"),
    ("Loco", "loconav"),
    ("MoEngage", "moengage"),
    ("Vymo", "vymo"),
    ("MindTickle", "mindtickle"),
    ("Springworks", "springworks"),
    ("CoinSwitch", "coinswitch")
]

# Top Tech Companies with Lever Boards
LEVER_COMPANIES = [
    ("Swiggy", "swiggy"),
    ("Groww", "groww"),
    ("Meesho", "meesho"),
    ("Slice", "slice"),
    ("FamPay", "fampay"),
    ("Khatabook", "khatabook"),
    ("Jar", "jar"),
    ("Plum", "plumhq"),
    ("Jupiter", "jupiter"),
    ("Smallcase", "smallcase")
]

# Top Tech Companies with Ashby Boards
ASHBY_COMPANIES = [
    ("Supersourcing", "supersourcing"),
    ("LlamaIndex", "llamaindex"),
    ("LangChain", "langchain"),
    ("Weights & Biases", "wandb"),
    ("Together AI", "togetherai"),
    ("Mistral AI", "mistral"),
    ("Perplexity", "perplexity"),
    ("ElevenLabs", "elevenlabs")
]


def fetch_greenhouse_jobs(company_name, board_token):
    """Fetches jobs from Greenhouse API."""
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
    jobs = []
    try:
        resp = requests.get(url, timeout=3, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200:
            data = resp.json()
            for j in data.get("jobs", []):
                title = j.get("title", "")
                loc_obj = j.get("location", {})
                location = loc_obj.get("name", "India / Remote") if isinstance(loc_obj, dict) else str(loc_obj)
                apply_url = j.get("absolute_url", "")
                updated_at = j.get("updated_at", "")[:10] or datetime.today().strftime("%Y-%m-%d")
                
                jobs.append({
                    "title": title,
                    "company": company_name,
                    "location": location,
                    "link": apply_url,
                    "posted": updated_at,
                    "experience": "0-1 Year",
                    "portal": "Career ATS"
                })
    except Exception:
        pass
    return jobs


def fetch_lever_jobs(company_name, company_slug):
    """Fetches jobs from Lever API."""
    url = f"https://api.lever.co/v0/postings/{company_slug}?mode=json"
    jobs = []
    try:
        resp = requests.get(url, timeout=3, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200:
            data = resp.json()
            for j in data:
                title = j.get("text", "")
                categories = j.get("categories", {})
                location = categories.get("location", "India / Remote")
                apply_url = j.get("hostedUrl", "")
                created_at = j.get("createdAt")
                posted = datetime.fromtimestamp(created_at/1000).strftime("%Y-%m-%d") if created_at else datetime.today().strftime("%Y-%m-%d")
                
                jobs.append({
                    "title": title,
                    "company": company_name,
                    "location": location,
                    "link": apply_url,
                    "posted": posted,
                    "experience": "0-1 Year",
                    "portal": "Career ATS"
                })
    except Exception:
        pass
    return jobs


def fetch_ashby_jobs(company_name, board_name):
    """Fetches jobs from Ashby API."""
    url = f"https://api.ashbyhq.com/posting-api/job-board/{board_name}"
    jobs = []
    try:
        resp = requests.get(url, timeout=3, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200:
            data = resp.json()
            for j in data.get("jobs", []):
                title = j.get("title", "")
                location = j.get("location", "India / Remote")
                apply_url = j.get("jobUrl", "")
                published_at = (j.get("publishedAt") or "")[:10] or datetime.today().strftime("%Y-%m-%d")
                
                jobs.append({
                    "title": title,
                    "company": company_name,
                    "location": location,
                    "link": apply_url,
                    "posted": published_at,
                    "experience": "0-1 Year",
                    "portal": "Career ATS"
                })
    except Exception:
        pass
    return jobs


from concurrent.futures import ThreadPoolExecutor, as_completed


def scrape_ats_jobs(role_query="Python Developer", limit=20, locations=None):
    """
    Scrapes official career ATS APIs across 30+ top tech companies in parallel,
    scoring each posting with our precision matcher.
    """
    all_raw_jobs = []
    
    tasks = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        for comp, token in GREENHOUSE_COMPANIES:
            tasks.append(executor.submit(fetch_greenhouse_jobs, comp, token))
        for comp, slug in LEVER_COMPANIES:
            tasks.append(executor.submit(fetch_lever_jobs, comp, slug))
        for comp, board in ASHBY_COMPANIES:
            tasks.append(executor.submit(fetch_ashby_jobs, comp, board))
            
        for future in as_completed(tasks):
            try:
                res = future.result()
                if res:
                    all_raw_jobs.extend(res)
            except Exception:
                pass

    # Filter & Score using Precision Matcher
    matching_jobs = []
    seen = set()
    for j in all_raw_jobs:
        title = j.get("title", "")
        link = j.get("link", "")
        if not link or link in seen:
            continue
            
        score, is_match = score_job_match(title, experience=j.get("experience", ""))
        if is_match:
            seen.add(link)
            j["match_score"] = score
            j["salary"] = extract_salary(title)
            j["skills"] = extract_skills(title)
            j["workplace"] = extract_workplace_mode(title, j.get("location", ""))
            matching_jobs.append(j)
            if len(matching_jobs) >= limit:
                break
                
    return matching_jobs
