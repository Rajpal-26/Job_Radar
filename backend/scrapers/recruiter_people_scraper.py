# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

"""
Recruiter People Scraper Wrapper for Backend.
"""

from services.recruiter_service import (
    scrape_recruiters_async,
    scrape_recruiters_sync,
    resolve_company_slug
)

async def scrape_live_linkedin_people(company, keyword="HR", location="India", limit=15):
    res = await scrape_recruiters_async(company, [keyword] if isinstance(keyword, str) else keyword, location, limit)
    return res.get("members", [])

def search_company_decision_makers(company, target_keyword=None, location="India", user_skills=None, user_name="Applicant", limit=25):
    kws = [target_keyword] if isinstance(target_keyword, str) and target_keyword else (target_keyword or ["HR", "Talent Acquisition"])
    return scrape_recruiters_sync(company, kws, location, limit)
