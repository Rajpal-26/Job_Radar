# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

import urllib.parse
import re

RECRUITER_ROLES = [
    {
        "role_key": "tech_recruiter",
        "title": "Technical Recruiter",
        "category": "Talent Acquisition",
        "badge_color": "#0077b5",
        "icon": "👔",
        "keywords": "Technical Recruiter",
        "search_terms": '("Technical Recruiter" OR "Tech Recruiter" OR "Engineering Recruiter")',
        "description": "Screens engineering resumes and coordinates technical interview rounds."
    },
    {
        "role_key": "ta_manager",
        "title": "Talent Acquisition Lead / Manager",
        "category": "Hiring Leadership",
        "badge_color": "#0284c7",
        "icon": "🎯",
        "keywords": "Talent Acquisition Manager",
        "search_terms": '("Talent Acquisition Manager" OR "Lead Recruiter" OR "Head of Talent" OR "Staffing Lead")',
        "description": "Leads recruitment strategy and has direct oversight of hiring quotas."
    },
    {
        "role_key": "hr_manager",
        "title": "HR Manager / People Operations",
        "category": "Human Resources",
        "badge_color": "#0d9488",
        "icon": "📋",
        "keywords": "HR Manager",
        "search_terms": '("HR Manager" OR "Human Resources Specialist" OR "People Partner" OR "HRBP")',
        "description": "Manages candidate offers, compensation packages, and team allocations."
    },
    {
        "role_key": "em_lead",
        "title": "Engineering Manager & Tech Lead",
        "category": "Engineering Decision Maker",
        "badge_color": "#10b981",
        "icon": "👨‍💻",
        "keywords": "Engineering Manager",
        "search_terms": '("Engineering Manager" OR "Tech Lead" OR "Software Development Manager" OR "Engineering Lead")',
        "description": "Primary technical decision-maker with final authority over team hiring."
    },
    {
        "role_key": "vp_cto",
        "title": "VP of Engineering & Director",
        "category": "Executive Leadership",
        "badge_color": "#8b5cf6",
        "icon": "🚀",
        "keywords": "VP of Engineering",
        "search_terms": '("VP of Engineering" OR "Director of Engineering" OR "CTO" OR "Head of Engineering")',
        "description": "Key executive stakeholder for senior, staff, and leadership engineering roles."
    }
]


def search_company_decision_makers(company, target_keyword=None, location="India", user_skills=None, user_name="Applicant"):
    """
    Generate live, categorized decision-maker search channels and personalized outreach pitches.
    """
    comp_clean = (company or "Tech Company").strip()
    loc_clean = (location or "India").strip()
    skills_str = ", ".join(user_skills[:4]) if user_skills else "distributed systems, Python, APIs, and scalable architectures"

    comp_slug = re.sub(r'[^a-zA-Z0-9]+', '-', comp_clean.lower()).strip('-')

    results = []

    # If user provided a specific keyword (e.g. "Talent Acquisition Manager" or "HR Manager")
    custom_role = None
    if target_keyword and target_keyword.strip() and target_keyword.lower() not in ["all", "any"]:
        kw = target_keyword.strip()
        custom_role = {
            "role_key": "custom",
            "title": kw,
            "category": "Targeted Role",
            "badge_color": "#f59e0b",
            "icon": "🔍",
            "keywords": kw,
            "search_terms": f'"{kw}"',
            "description": f"Targeted search for {kw} at {comp_clean}."
        }

    roles_to_process = [custom_role] + RECRUITER_ROLES if custom_role else RECRUITER_ROLES

    for role_info in roles_to_process:
        kw = role_info["keywords"]
        search_terms = role_info["search_terms"]

        # 1. Direct LinkedIn People Search URL
        linkedin_query = f'{comp_clean} {search_terms}'
        linkedin_search_url = f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(linkedin_query)}"

        # 2. Company Page People Tab Deep Link
        company_people_url = f"https://www.linkedin.com/company/{comp_slug}/people/?keywords={urllib.parse.quote(kw)}"

        # 3. Google X-Ray Search URL (Bypasses LinkedIn commercial limits)
        google_xray_query = f'site:linkedin.com/in/ "{comp_clean}" {search_terms} "{loc_clean}"'
        google_xray_url = f"https://www.google.com/search?q={urllib.parse.quote(google_xray_query)}"

        # 4. Tailored Outreaches
        if role_info["role_key"] in ["em_lead", "vp_cto"]:
            pitch_title = "👨‍💻 Engineering Manager Pitch (High Impact)"
            pitch_subject = f"Question regarding engineering priorities & open roles @ {comp_clean}"
            pitch_body = (
                f"Hi [Hiring Manager],\n\n"
                f"I noticed {comp_clean} is building out high-impact engineering solutions and wanted to reach out directly.\n\n"
                f"I specialize in {skills_str}. In my recent projects, I focused on high throughput, robust system design, and fast feature delivery.\n\n"
                f"Would you be open to a 5-minute chat this week, or may I send across a 1-page summary of my technical background?\n\n"
                f"Best regards,\n{user_name}"
            )
        else:
            pitch_title = "👔 Recruiter / HR Direct Note"
            pitch_subject = f"Application follow-up & quick note: Engineering roles @ {comp_clean} — {user_name}"
            pitch_body = (
                f"Hi [Recruiter Name],\n\n"
                f"I recently applied for engineering positions at {comp_clean} and wanted to share a brief note.\n\n"
                f"My core toolkit covers {skills_str}. I’m eager to contribute to {comp_clean}’s growth and would love to see if my background matches your current hiring priorities.\n\n"
                f"I’d appreciate the chance to connect for a quick 5-minute screener or share my resume.\n\n"
                f"Thanks for your time!\n{user_name}"
            )

        gmail_url = (
            f"https://mail.google.com/mail/?view=cm&fs=1"
            f"&su={urllib.parse.quote(pitch_subject)}"
            f"&body={urllib.parse.quote(pitch_body)}"
        )

        results.append({
            "role_key": role_info["role_key"],
            "title": role_info["title"],
            "category": role_info["category"],
            "badge_color": role_info["badge_color"],
            "icon": role_info["icon"],
            "description": role_info["description"],
            "company": comp_clean,
            "location": loc_clean,
            "links": {
                "linkedin_search": linkedin_search_url,
                "company_people": company_people_url,
                "google_xray": google_xray_url
            },
            "pitch": {
                "title": pitch_title,
                "subject": pitch_subject,
                "body": pitch_body,
                "gmail_url": gmail_url
            }
        })

    return {
        "company": comp_clean,
        "location": loc_clean,
        "target_keyword": target_keyword or "All Hiring Roles",
        "decision_makers": results
    }
