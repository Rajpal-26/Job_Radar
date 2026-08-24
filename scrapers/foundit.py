# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

"""Foundit (Monster India) public job search scraper (no login required).

We fetch directly from Foundit's internal JSON middleware API endpoint:
    https://www.foundit.in/middleware/jobsearch

This endpoint is clean, fast, and does not require Playwright browser automation,
bypassing Akamai Access Denied blocks entirely.
"""

import requests
import json
import time
import re
from urllib.parse import quote_plus
from datetime import datetime, timedelta

# Display name -> (URL path slug, location query param value)
FOUNDIT_CITIES = {
    "Bengaluru":  ("bengaluru-bangalore", "bengaluru / bangalore"),
    "Hyderabad":  ("hyderabad",            "hyderabad"),
    "Mumbai":     ("mumbai",               "mumbai"),
    "Pune":       ("pune",                 "pune"),
    "Chennai":    ("chennai",              "chennai"),
    "Delhi":      ("delhi-ncr",            "delhi ncr"),
    "Noida":      ("noida",                "noida"),
    "Gurugram":   ("gurugram",             "gurugram"),
    "Indore":     ("indore",               "indore"),
    "Ahmedabad":  ("ahmedabad",            "ahmedabad"),
    "Nagpur":     ("nagpur",               "nagpur"),
    "Chandigarh": ("chandigarh",           "chandigarh"),
    "Mohali":     ("mohali",               "mohali"),
    "Kochi":      ("kochi",                "kochi"),
    "Kolkata":    ("kolkata",              "kolkata"),
    "Surat":      ("surat",                "surat"),
    "Jaipur":     ("jaipur",               "jaipur"),
    "Coimbatore": ("coimbatore",           "coimbatore"),
}

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
)


def _slug(text):
    text = (text or "").lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def _parse_last_updated(ts):
    if not ts:
        return datetime.today().strftime("%Y-%m-%d")
    try:
        # ts is millisecond timestamp
        dt = datetime.fromtimestamp(int(ts) / 1000.0)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return datetime.today().strftime("%Y-%m-%d")


def _build_qs(role, city, job_freshness, min_exp, max_exp, start=1):
    _, loc_query = FOUNDIT_CITIES[city]
    qs = [
        f"start={int(start)}",
        "limit=20",
        f"query={quote_plus(role)}",
        f"location={quote_plus(loc_query)}",
        "queryDerived=true",
    ]
    if job_freshness and int(job_freshness) > 0:
        qs.append(f"jobFreshness={int(job_freshness)}")
    if min_exp is not None and max_exp is not None:
        qs.append(f"experience={int(min_exp)}")
        qs.append(f"experienceRanges={int(min_exp)}~{int(max_exp)}")
    elif min_exp is not None:
        qs.append(f"experience={int(min_exp)}")
        qs.append(f"experienceRanges={int(min_exp)}~30")
    return "&".join(qs)


def _normalize_locations(locations_input, valid_cities_dict):
    if not locations_input:
        return list(valid_cities_dict.keys())[:1]
    if isinstance(locations_input, str):
        raw = [c.strip() for c in locations_input.split(",") if c.strip()]
    else:
        raw = []
        for item in locations_input:
            for part in str(item).split(","):
                if part.strip():
                    raw.append(part.strip())
    valid = []
    for loc in raw:
        for k in valid_cities_dict:
            if loc.lower() == k.lower():
                if k not in valid:
                    valid.append(k)
                break
    return valid or [list(valid_cities_dict.keys())[0]]


def scrape_foundit(role, city="Bengaluru", job_freshness_days=7, limit=10, min_experience=None, max_experience=None, experience=None):
    """
    role:               free-text role (e.g. "devops")
    city:               display city name, list of cities, or comma-separated string
    job_freshness_days: int (1, 3, 7, 15, 30) or 0/None for any
    limit:              max results
    min_experience:     optional int (0..30 yrs)
    max_experience:     optional int (0..30 yrs)
    """
    if not role.strip():
        raise ValueError("role is required")

    locations = _normalize_locations(city, FOUNDIT_CITIES)

    if min_experience is None and max_experience is None and experience is not None and experience != "":
        try:
            n = int(experience)
            min_experience, max_experience = n, n
        except Exception:
            pass

    all_jobs = []
    seen_links = set()

    # Support multiple job roles separated by commas
    roles = [r.strip() for r in role.split(",") if r.strip()]
    if not roles:
        roles = [role]

    headers = {
        "User-Agent": _UA,
        "Accept": "application/json",
        "Referer": "https://www.foundit.in/",
    }

    max_pages = 5
    active_combinations = [(c, r) for c in locations for r in roles]

    for page_idx in range(max_pages):
        if len(all_jobs) >= limit or not active_combinations:
            break

        start = (page_idx * 20) + 1
        next_active = []

        for c, r in active_combinations:
            if len(all_jobs) >= limit:
                break

            qs = _build_qs(r, c, job_freshness_days, min_experience, max_experience, start)
            url = f"https://www.foundit.in/middleware/jobsearch?{qs}"
            print(f"[Foundit] Fetching: {url}")

            try:
                resp = requests.get(url, headers=headers, timeout=20)
                if resp.status_code != 200:
                    print(f"[Foundit] HTTP {resp.status_code} on start={start} for role '{r}'; skipping role.")
                    continue

                res_data = resp.json()
                job_list = res_data.get("jobSearchResponse", {}).get("data", [])
                if not job_list:
                    print(f"[Foundit] No jobs found at start={start} for role '{r}'; stopping role.")
                    continue

                added_this_page = 0
                for job in job_list:
                    if len(all_jobs) >= limit:
                        break

                    # Resolve details
                    href = job.get("seoJdUrl") or job.get("jdUrl") or ""
                    if not href:
                        continue
                    if not href.startswith("http"):
                        link = "https://www.foundit.in" + href
                    else:
                        link = href

                    if link in seen_links:
                        continue

                    title_txt = job.get("title") or ""
                    if not title_txt:
                        continue

                    posted = _parse_last_updated(job.get("lastUpdated"))
                    easy_apply = bool(job.get("quickApplyJob") == 1)

                    location_str = job.get("locations") or ""
                    desc_str = job.get("companyProfile") or ""
                    loc_lower = location_str.lower() + " " + desc_str.lower()
                    if "hybrid" in loc_lower:
                        workplace = "Hybrid"
                    elif "remote" in loc_lower or "work from home" in loc_lower:
                        workplace = "Remote"
                    else:
                        workplace = "On-site"

                    seen_links.add(link)
                    all_jobs.append({
                        "Job Title": title_txt,
                        "Company": job.get("companyName") or "N/A",
                        "Location": location_str,
                        "Posted": posted,
                        "Link": link,
                        "Experience": job.get("exp") or "",
                        "Salary": job.get("salary") or "",
                        "Skills": job.get("skills") or "",
                        "Description": desc_str,
                        "Workplace": workplace,
                        "Easy Apply": easy_apply,
                        "Apply Type": "Foundit Apply" if easy_apply else "External Site",
                    })
                    added_this_page += 1

                print(f"[Foundit] Got {added_this_page} jobs from start={start} for city '{c}' role '{r}'")
                if added_this_page > 0:
                    next_active.append((c, r))

            except Exception as e:
                print(f"[Foundit] Error querying endpoint at start={start}: {e}")

        active_combinations = next_active
        time.sleep(0.5)

    def sort_key(j):
        try:
            return datetime.strptime(j["Posted"][:10], "%Y-%m-%d")
        except Exception:
            return datetime.min

    all_jobs.sort(key=sort_key, reverse=True)
    return all_jobs[:limit]
