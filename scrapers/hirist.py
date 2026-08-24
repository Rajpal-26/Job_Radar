# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

"""Hirist Tech public job search scraper (no login required).

URL pattern reference (provided by user):
    https://www.hirist.tech/c/devops-sre-jobs?ref=topnavigation&minexp=0&maxexp=30&loc=Bangalore&posting=3

Categories live in the path slug (e.g. devops-sre-jobs, backend-development-jobs).
Params:
    minexp / maxexp = years of experience range (0..30)
    loc             = free-text city (Bangalore, Mumbai, etc.)
    posting         = posted within N days (1, 3, 7, 14, 30)
    page            = pagination (1, 2, 3 ...)

Hirist embeds the page's job list as JSON-LD (`@type=ItemList`) with name+url
for each job. We pair that with the rendered DOM cards (data-testid='job-list-*')
to get experience / location / posted date / skill tags / link in one shot.
Hirist is a centralized apply portal — no Easy Apply vs External distinction.
"""

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
import time
import random
import re
import json
from urllib.parse import quote_plus
from datetime import datetime, timedelta


# Category slug -> display label (Software Development sub-categories)
HIRIST_CATEGORIES = {
    "devops-sre-jobs":                       "DevOps / SRE",
    "backend-development-jobs":              "Backend Development",
    "frontend-development-jobs":             "Frontend Development",
    "full-stack-jobs":                       "Full Stack",
    "mobile-applications-jobs":              "Mobile Applications",
    "emerging-technologies-jobs":            "Emerging Technologies",
    "cybersecurity-jobs":                    "CyberSecurity",
    "quality-assurance-jobs":                "Quality Assurance",
    "platform-engineering-sap-oracle-jobs":  "Platform Engineering / SAP-Oracle",
}

# Display name -> Hirist's loc spelling (Hirist uses "Bangalore" not "Bengaluru")
HIRIST_CITIES = {
    "Bengaluru":  "Bangalore",
    "Hyderabad":  "Hyderabad",
    "Mumbai":     "Mumbai",
    "Pune":       "Pune",
    "Chennai":    "Chennai",
    "Delhi":      "Delhi",
    "Noida":      "Noida",
    "Gurugram":   "Gurgaon",
    "Indore":     "Indore",
    "Ahmedabad":  "Ahmedabad",
    "Nagpur":     "Nagpur",
    "Chandigarh": "Chandigarh",
    "Mohali":     "Mohali",
    "Kochi":      "Kochi",
    "Kolkata":    "Kolkata",
    "Surat":      "Surat",
    "Jaipur":     "Jaipur",
    "Coimbatore": "Coimbatore",
}

# Experience range options surfaced in the UI
HIRIST_EXPERIENCE = {
    "any":   (0, 30),
    "0-1":   (0, 1),
    "2-3":   (2, 3),
    "4-6":   (4, 6),
    "7-10":  (7, 10),
    "10+":   (10, 30),
}


def _parse_hirist_date(text):
    if not text:
        return datetime.today().strftime("%Y-%m-%d")
    text = text.lower().strip()
    today = datetime.today()
    if "today" in text or "just" in text:
        return today.strftime("%Y-%m-%d")
    if "yesterday" in text:
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")
    m = re.search(r"(\d+)\s*day", text)
    if m:
        return (today - timedelta(days=int(m.group(1)))).strftime("%Y-%m-%d")
    m = re.search(r"(\d+)\s*hour", text)
    if m:
        return today.strftime("%Y-%m-%d")
    m = re.search(r"(\d+)\s*week", text)
    if m:
        return (today - timedelta(weeks=int(m.group(1)))).strftime("%Y-%m-%d")
    m = re.search(r"(\d+)\s*month", text)
    if m:
        return (today - timedelta(days=int(m.group(1)) * 30)).strftime("%Y-%m-%d")
    return today.strftime("%Y-%m-%d")


def _build_url(category_slug, city, minexp, maxexp, posting, page=1):
    return (
        f"https://www.hirist.tech/c/{category_slug}"
        f"?ref=topnavigation"
        f"&minexp={int(minexp)}"
        f"&maxexp={int(maxexp)}"
        f"&loc={quote_plus(city)}"
        f"&posting={int(posting)}"
        + (f"&page={int(page)}" if page > 1 else "")
    )


def _extract_company_from_html(html):
    """Pull a company name from a detail page using whichever source survives.
    Tries in order:
      1. JSON-LD JobPosting.hiringOrganization.name (preferred)
      2. Any JSON-LD object's hiringOrganization.name (Hirist sometimes nests it)
      3. og:site_name meta (ignored if it just says 'Hirist')
    Returns None if nothing usable was found.
    """
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL):
        try:
            data = json.loads(block)
        except Exception:
            continue
        candidates = data if isinstance(data, list) else [data]
        for entry in candidates:
            if not isinstance(entry, dict):
                continue
            org = entry.get("hiringOrganization")
            if isinstance(org, dict):
                name = (org.get("name") or "").strip()
                if name:
                    return name
    m = re.search(
        r'<meta[^>]+property=["\']og:site_name["\'][^>]+content=["\']([^"\']+)["\']',
        html, re.IGNORECASE,
    )
    if m:
        name = m.group(1).strip()
        if name and name.lower() not in ("hirist", "hirist.tech", "hirist tech"):
            return name
    return None


def _extract_url_map(html):
    """Parse the ItemList JSON-LD on the listing page. Returns:
        by_id:           {job_id: url}      — keyed by trailing -{number} in the URL
        ordered:         [url, url, ...]    — same order as JSON-LD positions
        company_by_id:   {job_id: company}  — when ItemList items carry hiringOrganization
        company_by_url:  {url:    company}  — same data, keyed by url as backup
    Hirist's DOM gives every card the same data-testid='job-list-1', so we
    can't rely on position from the DOM — we key by the job_id embedded in
    each card's logo `itemid` attribute. We also harvest hiringOrganization
    from the listing JSON-LD when present so we don't have to re-fetch the
    detail page just to get a company name.
    """
    by_id = {}
    ordered = []
    company_by_id = {}
    company_by_url = {}
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL):
        try:
            data = json.loads(block)
        except Exception:
            continue
        if data.get("@type") != "ItemList":
            continue
        for item in sorted(data.get("itemListElement", []), key=lambda x: x.get("position", 0)):
            url = item.get("url")
            inner = item.get("item") if isinstance(item.get("item"), dict) else None
            if not url and inner:
                url = inner.get("url")
            if not url:
                continue
            ordered.append(url)
            m = re.search(r"-(\d+)/?$", url)
            jid = m.group(1) if m else None
            if jid:
                by_id[jid] = url
            org = (inner or {}).get("hiringOrganization") or item.get("hiringOrganization")
            if isinstance(org, dict):
                name = (org.get("name") or "").strip()
                if name:
                    if jid:
                        company_by_id[jid] = name
                    company_by_url[url] = name
    return by_id, ordered, company_by_id, company_by_url


# Words that look like job-title prefixes — used to reject false-positive
# "Company - Role" splits where the head is actually part of the title.
_TITLE_HEAD_BLACKLIST = {
    "senior", "junior", "sr", "jr", "lead", "principal", "staff",
    "associate", "manager", "engineer", "developer", "architect",
    "consultant", "specialist", "analyst", "remote", "hybrid",
    "head", "director", "vp", "chief", "executive", "intern",
    "fullstack", "full-stack", "frontend", "backend", "devops",
    "cloud", "data", "ml", "ai", "qa", "test", "site",
}


def _strip_company_prefix_from_title(job_title, company):
    """If `job_title` starts with `company` separated by ' - ', return the
    tail. Otherwise return the title unchanged. Handles minor mismatches
    (company is a prefix of the head, or vice versa)."""
    if not company or " - " not in job_title:
        return job_title
    head, tail = job_title.split(" - ", 1)
    head_l = head.strip().lower()
    comp_l = company.strip().lower()
    if not head_l:
        return job_title
    if (head_l == comp_l
            or comp_l.startswith(head_l + " ")
            or head_l.startswith(comp_l + " ")):
        return tail.strip()
    return job_title


def _company_from_title(job_title):
    """Heuristic fallback: if the title looks like 'Company Name - Job Role',
    return (company, role); otherwise (None, job_title). Rejects heads whose
    first word is a known job-title token."""
    if " - " not in job_title:
        return None, job_title
    head, tail = job_title.split(" - ", 1)
    head = head.strip()
    if not (1 < len(head) < 60):
        return None, job_title
    first_word = head.split()[0].lower() if head.split() else ""
    if first_word in _TITLE_HEAD_BLACKLIST:
        return None, job_title
    return head, tail.strip()


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


def scrape_hirist(category, city="Bengaluru", exp_key=None, posting_days=3, limit=10, min_exp=None, max_exp=None):
    """
    category:    one of HIRIST_CATEGORIES keys (slug)
    city:        display city name, list of cities, or comma-separated string
    exp_key:     optional key of HIRIST_EXPERIENCE ('any', '0-1', etc.)
    posting_days: int (1, 3, 7, 14, 30)
    limit:       max results
    min_exp:     optional int min experience years
    max_exp:     optional int max experience years
    """
    if category not in HIRIST_CATEGORIES:
        raise ValueError(f"Unknown category: {category}")

    locations = _normalize_locations(city, HIRIST_CITIES)

    if min_exp is None or max_exp is None:
        if exp_key and exp_key in HIRIST_EXPERIENCE:
            minexp, maxexp = HIRIST_EXPERIENCE[exp_key]
        else:
            minexp, maxexp = 0, 30
    else:
        minexp, maxexp = min_exp, max_exp

    all_jobs = []
    seen_links = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
            ],
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 900},
            locale="en-IN",
            timezone_id="Asia/Kolkata",
        )
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-IN', 'en']});
            window.chrome = {runtime: {}};
        """)
        page = context.new_page()

        max_pages = 5
        active_combinations = [(c, category) for c in locations]

        for page_idx in range(max_pages):
            if len(all_jobs) >= limit or not active_combinations:
                break

            page_num = page_idx + 1
            next_active = []

            for c, cat in active_combinations:
                if len(all_jobs) >= limit:
                    break

                loc_query = HIRIST_CITIES[c]
                url = _build_url(cat, loc_query, minexp, maxexp, posting_days, page_num)
                print(f"[Hirist] Fetching: {url}")

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)

                try:
                    page.wait_for_selector("div[data-testid^='job-list-']", timeout=20000)
                except Exception:
                    pass
                time.sleep(random.uniform(2.0, 3.0))

                page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
                time.sleep(1.0)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1.5)

                by_id, ordered_urls, company_by_id, company_by_url = _extract_url_map(page.content())

                cards = page.query_selector_all("div[data-testid^='job-list-']")
                if not cards:
                    print(f"[Hirist] No cards on page {page_num}")
                    break

                found_this_page = 0
                for idx, card in enumerate(cards):
                    if len(all_jobs) >= limit:
                        break
                    try:
                        title_el = card.query_selector("[data-testid='job_title']")
                        title = title_el.inner_text().strip() if title_el else None
                        if not title:
                            continue

                        company = "N/A"
                        company_source = None
                        job_title = title

                        exp_el = card.query_selector("[data-testid='job_experience']")
                        experience = exp_el.inner_text().strip() if exp_el else ""

                        loc_el = card.query_selector("[data-testid='job_location']")
                        loc_text = loc_el.inner_text().strip() if loc_el else loc_query

                        date_el = card.query_selector("[data-testid='job_posting_date']")
                        posted = _parse_hirist_date(date_el.inner_text() if date_el else "")

                        sal_el = card.query_selector("[data-testid='job_salary']")
                        salary = sal_el.inner_text().strip() if sal_el else ""

                        tags = [t.inner_text().strip() for t in card.query_selector_all("[data-testid^='job_tag_']")]

                        # Link resolution: Hirist marks every card with the same
                        # data-testid (job-list-1), so we identify each job by the
                        # `itemid` attribute on its logo image, then look up the
                        # canonical URL from the JSON-LD ItemList we parsed above.
                        link = ""
                        logo = card.query_selector("img[itemid]")
                        jid = logo.get_attribute("itemid") if logo else None
                        if jid and jid in by_id:
                            link = by_id[jid]
                        elif idx < len(ordered_urls):
                            link = ordered_urls[idx]

                        if not link or link in seen_links:
                            continue
                        seen_links.add(link)

                        # Resolve company name from multiple sources in order
                        # of confidence. First hit wins.

                        # 1. Listing-page JSON-LD ItemList (no extra fetch).
                        if jid and jid in company_by_id:
                            company = company_by_id[jid]
                            company_source = "listing-jsonld"
                        elif link in company_by_url:
                            company = company_by_url[link]
                            company_source = "listing-jsonld"

                        # 2. Card DOM — try a few selectors Hirist might use.
                        if company == "N/A":
                            for sel in (
                                "[data-testid='job_company']",
                                "[data-testid='company_name']",
                                "[data-testid='employer_name']",
                                "[data-testid='job_company_name']",
                            ):
                                el = card.query_selector(sel)
                                if el:
                                    txt = (el.inner_text() or "").strip()
                                    if txt:
                                        company = txt
                                        company_source = "card-dom"
                                        break

                        # 2b. Logo image alt text — job boards routinely set
                        # <img alt="Company Name"> on the employer logo.
                        if company == "N/A" and logo is not None:
                            alt = (logo.get_attribute("alt") or "").strip()
                            if alt and alt.lower() not in (
                                "logo", "company logo", "hirist", "company"
                            ):
                                company = alt
                                company_source = "logo-alt"

                        # 3. Raw HTTP detail page (JSON-LD / og:site_name).
                        if company == "N/A":
                            try:
                                resp = context.request.get(link, timeout=2500)
                                if resp.ok:
                                    detail_name = _extract_company_from_html(resp.text())
                                    if detail_name:
                                        company = detail_name
                                        company_source = "detail-http"
                            except Exception as e:
                                print(f"[Hirist] Detail fetch failed for {link}: {e}")

                        # 4. Title-prefix heuristic — "Company Name - Role".
                        if company == "N/A":
                            head, tail = _company_from_title(job_title)
                            if head:
                                company = head
                                job_title = tail
                                company_source = "title-prefix"

                        # If company is still N/A, fallback to title-prefix or default
                        if company == "N/A":
                            head, tail = _company_from_title(job_title)
                            if head:
                                company = head
                                job_title = tail
                                company_source = "title-prefix"

                        # If a high-confidence source found the company, also
                        # strip its name from the title when present as prefix.
                        if company_source in (
                            "listing-jsonld", "card-dom", "logo-alt",
                            "detail-http", "detail-render",
                        ):
                            job_title = _strip_company_prefix_from_title(job_title, company)

                        title_lower = job_title.lower()
                        if "remote" in title_lower or "work from home" in title_lower:
                            workplace = "Remote"
                        elif "hybrid" in title_lower:
                            workplace = "Hybrid"
                        else:
                            workplace = "On-site"

                        all_jobs.append({
                            "Job Title": job_title,
                            "Company": company,
                            "Location": loc_text,
                            "Posted": posted,
                            "Link": link,
                            "Experience": experience,
                            "Salary": salary,
                            "Skills": ", ".join(tags),
                            "Description": "",
                            "Workplace": workplace,
                            # No Easy/External distinction on Hirist — every job
                            # goes through Hirist's apply flow.
                            "Easy Apply": False,
                            "Apply Type": "Hirist Apply",
                            "_company_source": company_source,
                        })
                        found_this_page += 1
                    except Exception as e:
                        print(f"[Hirist] Card error: {e}")
                        continue

                source_counts = {}
                for j in all_jobs[-found_this_page:]:
                    src = j.get("_company_source") or "none"
                    source_counts[src] = source_counts.get(src, 0) + 1
                print(f"[Hirist] Got {found_this_page} jobs from page {page_num} for city '{c}' "
                      f"(company sources: {source_counts})")
                if found_this_page > 0:
                    next_active.append((c, cat))

            except PWTimeout:
                print(f"[Hirist] Timeout on page {page_num} for city '{c}'")
            except Exception as e:
                print(f"[Hirist] Error fetching city '{c}': {e}")

        active_combinations = next_active

        browser.close()

    def sort_key(j):
        try:
            return datetime.strptime(j["Posted"][:10], "%Y-%m-%d")
        except Exception:
            return datetime.min

    all_jobs.sort(key=sort_key, reverse=True)
    for j in all_jobs:
        j.pop("_company_source", None)
    return all_jobs[:limit]
