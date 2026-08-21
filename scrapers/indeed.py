# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

"""Indeed public job search scraper (no login required).

URL pattern reference (provided by user):
    https://in.indeed.com/jobs?q=DevOps+Engineer&l=Bengaluru%2C+Karnataka&fromage=1&radius=100&sort=date

Params:
    q       = role (spaces as +)
    l       = "City, State" (URL-encoded)
    fromage = posted within N days (1, 3, 7, 14)
    radius  = miles (hardcoded 100)
    sort    = date
    start   = pagination offset (multiples of 10)
"""

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
import time
import random
import re
from urllib.parse import quote_plus
from datetime import datetime, timedelta


# Indeed accepts free-text locations. We map our standard city chips to
# "City, State" so results match the user's reference URL.
INDEED_CITIES = {
    "Bengaluru":  "Bengaluru, Karnataka",
    "Hyderabad":  "Hyderabad, Telangana",
    "Mumbai":     "Mumbai, Maharashtra",
    "Pune":       "Pune, Maharashtra",
    "Chennai":    "Chennai, Tamil Nadu",
    "Delhi":      "Delhi, Delhi",
    "Noida":      "Noida, Uttar Pradesh",
    "Gurugram":   "Gurugram, Haryana",
    "Indore":     "Indore, Madhya Pradesh",
    "Ahmedabad":  "Ahmedabad, Gujarat",
    "Nagpur":     "Nagpur, Maharashtra",
    "Chandigarh": "Chandigarh, Chandigarh",
    "Mohali":     "Mohali, Punjab",
    "Kochi":      "Kochi, Kerala",
    "Kolkata":    "Kolkata, West Bengal",
    "Surat":      "Surat, Gujarat",
    "Jaipur":     "Jaipur, Rajasthan",
    "Coimbatore": "Coimbatore, Tamil Nadu",
}


def _parse_indeed_date(text):
    if not text:
        return datetime.today().strftime("%Y-%m-%d")
    text = text.lower().strip()
    today = datetime.today()
    if "just posted" in text or "today" in text or "active today" in text:
        return today.strftime("%Y-%m-%d")
    m = re.search(r"(\d+)\s*day", text)
    if m:
        return (today - timedelta(days=int(m.group(1)))).strftime("%Y-%m-%d")
    m = re.search(r"(\d+)\s*hour", text)
    if m:
        return today.strftime("%Y-%m-%d")
    m = re.search(r"(\d+)\+?\s*day", text)
    if m:
        return (today - timedelta(days=int(m.group(1)))).strftime("%Y-%m-%d")
    return today.strftime("%Y-%m-%d")


def _build_url(role, location, fromage_days, start=0, experience=None):
    url = (
        "https://in.indeed.com/jobs?"
        f"q={quote_plus(role)}"
        f"&l={quote_plus(location)}"
        f"&fromage={int(fromage_days)}"
        "&radius=100"
        "&sort=date"
        f"&start={int(start)}"
    )
    if experience:
        sc_val = None
        if experience in ("fresher", "0-1", "0-6m", "internship"):
            sc_val = "explvl(ENTRY_LEVEL)"
        elif experience in ("1-2", "1-3", "3-5"):
            sc_val = "explvl(MID_LEVEL)"
        elif experience in ("5-7", "7-10", "10+"):
            sc_val = "explvl(SENIOR_LEVEL)"
        if sc_val:
            url += f"&sc=0kf%3A{sc_val}%3B"
    return url


import os

_PROFILE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "_indeed_profile")


def _launch(p, headless):
    os.makedirs(_PROFILE_DIR, exist_ok=True)
    context = p.chromium.launch_persistent_context(
        _PROFILE_DIR,
        headless=False,
        viewport={"width": 1366, "height": 768},
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/132.0.0.0 Safari/537.36"
        ),
        locale="en-IN",
        timezone_id="Asia/Kolkata",
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--no-first-run",
            "--no-default-browser-check",
        ] + (["--headless=new"] if headless else []),
    )
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
        Object.defineProperty(navigator, 'languages', {get: () => ['en-IN', 'en']});
        window.chrome = {runtime: {}};
    """)
    return None, context


def _is_blocked(page):
    """Detect bot-check page (Cloudflare, hCaptcha, Indeed's own block)."""
    title = (page.title() or "").lower()
    if "just a moment" in title or "cloudflare" in title:
        return True
    try:
        body = (page.inner_text("body") or "").lower()
    except Exception:
        return False
    return (
        "verifying you are human" in body
        or "additional verification required" in body
        or "you've been blocked" in body
    )


def _scrape_with(p, role, fromage_days, internal_limit, locations,
                 apply_mode, headless, experience=None):
    """One scraping pass with the given headless mode. Returns (jobs, blocked_flag)."""
    all_jobs = []
    seen_links = set()
    blocked_any = False

    browser, context = _launch(p, headless=headless)
    page = context.pages[0] if context.pages else context.new_page()

    # Support multiple comma-separated job roles
    roles = [r.strip() for r in role.split(",") if r.strip()]
    if not roles:
        roles = [role]

    try:
        max_pages = 5  # Indeed page safety limit (10 jobs per page)
        active_combinations = [(city_key, r) for city_key in locations if city_key in INDEED_CITIES for r in roles]

        for page_idx in range(max_pages):
            if len(all_jobs) >= internal_limit or not active_combinations:
                break

            start = page_idx * 10
            next_active = []

            for city_key, r in active_combinations:
                if len(all_jobs) >= internal_limit:
                    break

                location_query = INDEED_CITIES[city_key]
                url = _build_url(r, location_query, fromage_days, start, experience)
                print(f"[Indeed] Fetching: {url}")

                # Bot-check retry
                cleared = False
                for attempt in range(2):
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=25000)
                    except Exception as e:
                        print(f"[Indeed] goto attempt {attempt+1} failed: {e}")
                        time.sleep(3)
                        continue

                    # Indeed bot check
                    deadline = time.time() + (20 if attempt == 0 else 12)
                    while time.time() < deadline:
                        if not _is_blocked(page):
                            cleared = True
                            break
                        time.sleep(1)

                    if cleared:
                        break
                    print(f"[Indeed] Bot check failed (attempt {attempt+1}/2)")
                    time.sleep(random.uniform(4.0, 7.0))

                if not cleared:
                    print(f"[Indeed] Hard blocked at start={start} for '{r}' in '{city_key}'")
                    blocked_any = True
                    continue  # skip to next combination

                try:
                    try:
                        page.wait_for_selector(".jobsearch-ResultsList", timeout=12000)
                    except Exception:
                        pass
                    time.sleep(random.uniform(2.0, 3.5))

                    cards = page.query_selector_all("div.job_seen_beacon")
                    if not cards:
                        cards = page.query_selector_all("td.resultContent")
                    if not cards:
                        print(f"[Indeed] No cards for {city_key} role {r} start={start}")
                        continue  # Exhausted

                    found_this_page = 0
                    for card in cards:
                        if len(all_jobs) >= internal_limit:
                            break
                        try:
                            # ── Title & Link ──
                            title_el = (
                                card.query_selector("h2.jobTitle a")
                                or card.query_selector("a[class*='JobTitle']")
                                or card.query_selector("h2 a")
                            )
                            title = title_el.inner_text().strip() if title_el else None
                            if not title:
                                continue

                            href = (title_el.get_attribute("href") or "").strip()
                            if href and not href.startswith("http"):
                                link = "https://www.indeed.com" + href
                            else:
                                link = href
                            link = link.split("?")[0].strip()

                            if "/rc/clk" not in link and "/company/" not in link and "/jobs/" not in link:
                                continue
                            if link in seen_links:
                                continue

                            # ── Company ──
                            comp_el = (
                                card.query_selector("span[data-testid='company-name']")
                                or card.query_selector("span.companyName")
                            )
                            company = comp_el.inner_text().strip() if comp_el else "N/A"

                            # ── Location ──
                            loc_el = (
                                card.query_selector("[data-testid='text-location']")
                                or card.query_selector("div.companyLocation")
                            )
                            loc_text = loc_el.inner_text().strip() if loc_el else location_query

                            # ── Date ──
                            date_el = (
                                card.query_selector("[data-testid='myJobsStateDate']")
                                or card.query_selector("span.date")
                                or card.query_selector("[class*='date']")
                            )
                            posted = _parse_indeed_date(date_el.inner_text() if date_el else "")

                            # ── Easy Apply ──
                            card_text = (card.inner_text() or "").lower()
                            easy_apply = ("easily apply" in card_text) or ("easy apply" in card_text)
                            apply_type = "Easy Apply" if easy_apply else "External"

                            if apply_mode == "only_external" and easy_apply:
                                continue
                            if apply_mode == "only_easy" and not easy_apply:
                                continue

                            # ── Salary ──
                            sal_el = (
                                card.query_selector("div.metadata.salary-snippet-container")
                                or card.query_selector("div.salary-snippet")
                                or card.query_selector("div.metadata-container")
                                or card.query_selector("[class*='salary']")
                            )
                            salary = sal_el.inner_text().strip() if sal_el else ""

                            # ── Workplace ──
                            workplace = ""
                            if "hybrid" in loc_text.lower():
                                workplace = "Hybrid"
                            elif "remote" in loc_text.lower():
                                workplace = "Remote"
                            elif "work from home" in loc_text.lower():
                                workplace = "Remote"
                            else:
                                workplace = "On-site"

                            # ── Description (Snippet) ──
                            snip_el = (
                                card.query_selector("div.job-snippet")
                                or card.query_selector("div.underSection")
                                or card.query_selector("table.jobCard_mainContent ul")
                            )
                            description = snip_el.inner_text().strip().replace("\n", " ") if snip_el else ""

                            # ── Experience ──
                            exp_match = re.search(r"(\d+-\d+|\d+\+?)\s*(years|yrs|year|yr)", card_text)
                            experience_text = exp_match.group(0).strip() if exp_match else ""

                            # ── Skills ──
                            skills = ""

                            seen_links.add(link)
                            all_jobs.append({
                                "Job Title": title,
                                "Company": company,
                                "Location": loc_text,
                                "Posted": posted,
                                "Link": link,
                                "Easy Apply": easy_apply,
                                "Apply Type": apply_type,
                                "Salary": salary,
                                "Workplace": workplace,
                                "Description": description,
                                "Experience": experience_text,
                                "Skills": skills,
                            })
                            found_this_page += 1
                        except Exception as e:
                            print(f"[Indeed] Card error: {e}")
                            continue

                    print(f"[Indeed] Got {found_this_page} jobs from {city_key} role '{r}' start={start}")
                    next_active.append((city_key, r))
                    time.sleep(random.uniform(2.0, 3.5))

                except PWTimeout:
                    print(f"[Indeed] Timeout for '{r}' in '{city_key}'")
                except Exception as e:
                    print(f"[Indeed] Error: {e}")

            active_combinations = next_active

    finally:
        try:
            context.close()
        except Exception:
            pass

    return all_jobs, blocked_any


def _filter_by_experience(jobs, exp_key):
    if not exp_key:
        return jobs
    exclude_patterns = []
    if exp_key in ("fresher", "0-1", "0-6m", "internship"):
        exclude_patterns = [
            r"\bsenior\b", r"\bsr\b", r"\bsr\.", r"\blead\b", r"\barchitect\b",
            r"\bmanager\b", r"\bdirector\b", r"\bvp\b", r"\bprincipal\b",
            r"\bstaff\b", r"\bii\b", r"\biii\b", r"\biv\b", r"\bhead\b", r"\bexpert\b"
        ]
    elif exp_key in ("1-2", "1-3", "3-5"):
        exclude_patterns = [
            r"\bintern\b", r"\bco-op\b", r"\bstudent\b", r"\btrainee\b", r"\bfresher\b",
            r"\bhead\b", r"\bdirector\b", r"\bvp\b", r"\bprincipal\b", r"\barchitect\b"
        ]
    elif exp_key in ("5-7", "7-10", "10+"):
        exclude_patterns = [
            r"\bintern\b", r"\bco-op\b", r"\bstudent\b", r"\btrainee\b", r"\bfresher\b",
            r"\bjunior\b", r"\bjr\b", r"\bjr\.", r"\bentry\b", r"\bassociate\b"
        ]
    filtered = []
    for job in jobs:
        title = (job.get("Job Title") or "").lower()
        matched_exclude = False
        for pattern in exclude_patterns:
            if re.search(pattern, title):
                matched_exclude = True
                break
        if not matched_exclude:
            filtered.append(job)
    return filtered


def scrape_indeed(role, fromage_days, limit, locations, apply_mode="include_easy", experience=None):
    """Scrape Indeed. Tries headless first; falls back to headed if blocked."""
    mode_multipliers = {"include_easy": 1.0, "only_easy": 2.5, "only_external": 2.5}
    internal_limit = max(limit, int(limit * mode_multipliers.get(apply_mode, 1.0)))

    with sync_playwright() as p:
        jobs, blocked = _scrape_with(
            p, role, fromage_days, internal_limit, locations, apply_mode,
            headless=True, experience=experience,
        )
        if not jobs and blocked:
            print("[Indeed] Headless blocked — retrying headed.")
            jobs, _ = _scrape_with(
                p, role, fromage_days, internal_limit, locations, apply_mode,
                headless=False, experience=experience,
            )

    if experience:
        jobs = _filter_by_experience(jobs, experience)

    def sort_key(j):
        try:
            return datetime.strptime(j["Posted"][:10], "%Y-%m-%d")
        except Exception:
            return datetime.min

    jobs.sort(key=sort_key, reverse=True)
    return jobs[:limit]
