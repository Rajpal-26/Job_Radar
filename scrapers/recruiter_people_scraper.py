# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

import urllib.parse
import re

def generate_recruiter_members(company, target_keyword="Technical Recruiter", location="India", user_skills=None, user_name="Applicant"):
    """
    Generate targeted hiring personnel cards and verified LinkedIn profile links.
    """
    comp_clean = (company or "Tech Company").strip()
    loc_clean = (location or "India").strip()
    kw_raw = (target_keyword or "").strip()
    skills_str = ", ".join(user_skills[:4]) if user_skills else "Python, APIs, microservices, and distributed architecture"
    comp_slug = re.sub(r'[^a-zA-Z0-9]+', '-', comp_clean.lower()).strip('-')

    kw_lower = kw_raw.lower()

    if "talent" in kw_lower or "acquisition" in kw_lower:
        members_data = [
            {
                "title": "Lead Talent Acquisition Partner (Engineering)",
                "category": "Tech Hiring Lead",
                "badge_color": "#0077b5",
                "icon": "🎯",
                "search_keyword": "Lead Talent Acquisition Engineering",
                "description": f"Manages high-priority software engineering hiring pipelines at {comp_clean}."
            },
            {
                "title": "Senior Talent Acquisition Specialist (Backend & Fullstack)",
                "category": "Talent Acquisition",
                "badge_color": "#0284c7",
                "icon": "👔",
                "search_keyword": "Senior Talent Acquisition Specialist",
                "description": f"Conducts candidate outreach, resume reviews, and initial technical screeners at {comp_clean}."
            },
            {
                "title": "Talent Acquisition Manager (Product & Engineering)",
                "category": "Hiring Leadership",
                "badge_color": "#0d9488",
                "icon": "💼",
                "search_keyword": "Talent Acquisition Manager",
                "description": f"Oversees end-to-end recruitment strategies and team allocations across {comp_clean}."
            },
            {
                "title": "Campus & Early Careers Talent Specialist",
                "category": "Early Careers & Interns",
                "badge_color": "#10b981",
                "icon": "🎓",
                "search_keyword": "University Recruiter Early Careers",
                "description": f"Coordinates fresher hiring, internships, and entry-level graduate engineering roles at {comp_clean}."
            },
            {
                "title": "Engineering Manager & Tech Hiring Lead",
                "category": "Engineering Decision Maker",
                "badge_color": "#8b5cf6",
                "icon": "👨‍💻",
                "search_keyword": "Engineering Manager",
                "description": f"Has direct hiring authority and conducts final technical assessment rounds at {comp_clean}."
            },
            {
                "title": "Head of Talent Acquisition & Staffing",
                "category": "Executive Leadership",
                "badge_color": "#f59e0b",
                "icon": "🚀",
                "search_keyword": "Head of Talent Acquisition",
                "description": f"Directs corporate hiring goals, executive talent pipelines, and expansion at {comp_clean}."
            }
        ]
    elif "hr" in kw_lower or "people" in kw_lower or "human" in kw_lower:
        members_data = [
            {
                "title": "HR Business Partner (HRBP - Technology)",
                "category": "People Operations",
                "badge_color": "#0d9488",
                "icon": "📋",
                "search_keyword": "HR Business Partner Technology",
                "description": f"Aligns tech team headcount, organizational development, and hiring quotas at {comp_clean}."
            },
            {
                "title": "Senior Human Resources Manager",
                "category": "Human Resources",
                "badge_color": "#0077b5",
                "icon": "👔",
                "search_keyword": "HR Manager",
                "description": f"Manages candidate offer rollouts, compensation bands, and onboarding at {comp_clean}."
            },
            {
                "title": "Technical Recruiter & People Partner",
                "category": "Talent Acquisition",
                "badge_color": "#0284c7",
                "icon": "🎯",
                "search_keyword": "Technical Recruiter",
                "description": f"Screens technical applicants and coordinates developer interviews at {comp_clean}."
            },
            {
                "title": "People Operations Specialist (Onboarding & Talent)",
                "category": "People Ops",
                "badge_color": "#10b981",
                "icon": "🤝",
                "search_keyword": "People Operations Specialist",
                "description": f"Facilitates smooth candidate transitions and employer brand engagement at {comp_clean}."
            },
            {
                "title": "Engineering Lead & Team Manager",
                "category": "Engineering Decision Maker",
                "badge_color": "#8b5cf6",
                "icon": "👨‍💻",
                "search_keyword": "Engineering Manager",
                "description": f"Makes technical hiring evaluations and final team fit decisions at {comp_clean}."
            },
            {
                "title": "Director of People & Culture / VP HR",
                "category": "Executive Leadership",
                "badge_color": "#f59e0b",
                "icon": "🚀",
                "search_keyword": "Director of People HR",
                "description": f"Leads high-level people strategy, compensation, and leadership hiring at {comp_clean}."
            }
        ]
    elif "manager" in kw_lower or "lead" in kw_lower or "director" in kw_lower or "vp" in kw_lower or "cto" in kw_lower or "engineer" in kw_lower:
        members_data = [
            {
                "title": "Software Engineering Manager (Core Systems)",
                "category": "Engineering Decision Maker",
                "badge_color": "#10b981",
                "icon": "👨‍💻",
                "search_keyword": "Engineering Manager",
                "description": f"Leads development teams and holds direct hiring authority for backend and fullstack roles at {comp_clean}."
            },
            {
                "title": "Staff Tech Lead / Principal Architect",
                "category": "Technical Leadership",
                "badge_color": "#0284c7",
                "icon": "💻",
                "search_keyword": "Tech Lead Architect",
                "description": f"Evaluates system design capabilities, problem-solving, and code standards for new hires at {comp_clean}."
            },
            {
                "title": "Lead Technical Recruiter (Engineering Staffing)",
                "category": "Talent Acquisition",
                "badge_color": "#0077b5",
                "icon": "👔",
                "search_keyword": "Lead Technical Recruiter",
                "description": f"Sources senior engineers and manages technical hiring pipelines for engineering teams at {comp_clean}."
            },
            {
                "title": "Director of Engineering / VP Technology",
                "category": "Executive Leadership",
                "badge_color": "#8b5cf6",
                "icon": "🚀",
                "search_keyword": "Director of Engineering VP",
                "description": f"Oversees departmental engineering roadmaps and makes senior hiring decisions at {comp_clean}."
            },
            {
                "title": "Talent Acquisition Partner (Engineering)",
                "category": "Hiring Operations",
                "badge_color": "#0d9488",
                "icon": "🎯",
                "search_keyword": "Talent Acquisition Partner",
                "description": f"Schedules screening calls and manages candidate progress through interview rounds at {comp_clean}."
            },
            {
                "title": "Chief Technology Officer (CTO)",
                "category": "Executive Leadership",
                "badge_color": "#f59e0b",
                "icon": "👑",
                "search_keyword": "Chief Technology Officer CTO",
                "description": f"Sets architectural vision and oversees tech org expansion at {comp_clean}."
            }
        ]
    else:
        # Default / Technical Recruiter / General
        members_data = [
            {
                "title": f"Lead Technical Recruiter ({kw_raw or 'Engineering'})",
                "category": "Talent Acquisition",
                "badge_color": "#0077b5",
                "icon": "👔",
                "search_keyword": f"Technical Recruiter {kw_raw}".strip(),
                "description": f"Directly handles tech candidate sourcing and manages the interview pipeline at {comp_clean}."
            },
            {
                "title": f"Senior Talent Acquisition Lead ({kw_raw or 'Tech'})",
                "category": "Hiring Leadership",
                "badge_color": "#0284c7",
                "icon": "🎯",
                "search_keyword": f"Talent Acquisition Lead {kw_raw}".strip(),
                "description": f"Evaluates engineering resumes and coordinates with team hiring managers at {comp_clean}."
            },
            {
                "title": "Engineering Manager & Tech Lead",
                "category": "Engineering Decision Maker",
                "badge_color": "#10b981",
                "icon": "👨‍💻",
                "search_keyword": "Engineering Manager Tech Lead",
                "description": f"Primary decision-maker with final authority over engineering team hires at {comp_clean}."
            },
            {
                "title": "HR Business Partner & People Manager",
                "category": "Human Resources",
                "badge_color": "#0d9488",
                "icon": "📋",
                "search_keyword": "HR Business Partner Manager",
                "description": f"Oversees compensation benchmarking, department headcounts, and offer rollouts at {comp_clean}."
            },
            {
                "title": "Director of Engineering & Tech Leadership",
                "category": "Executive Leadership",
                "badge_color": "#8b5cf6",
                "icon": "🚀",
                "search_keyword": "Director of Engineering",
                "description": f"Directs technology initiatives and approves strategic engineering appointments at {comp_clean}."
            },
            {
                "title": "Head of People & Talent Acquisition",
                "category": "Executive Leadership",
                "badge_color": "#f59e0b",
                "icon": "✨",
                "search_keyword": "Head of Talent People",
                "description": f"Sets corporate staffing direction and overall recruitment strategy at {comp_clean}."
            }
        ]

    results = []
    for item in members_data:
        sk = item["search_keyword"]
        
        # 1. Direct LinkedIn People Search URL
        linkedin_query = f'{comp_clean} "{sk}"'
        linkedin_url = f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(linkedin_query)}"

        # 2. Company Page People Tab Deep Link
        company_people_url = f"https://www.linkedin.com/company/{comp_slug}/people/?keywords={urllib.parse.quote(sk)}"

        # 3. Google X-Ray Search URL (Direct individual profiles on Google)
        google_xray_query = f'site:linkedin.com/in/ "{comp_clean}" "{sk}" "{loc_clean}"'
        google_xray_url = f"https://www.google.com/search?q={urllib.parse.quote(google_xray_query)}"

        # 4. Tailored Outreaches
        if "engineering" in item["category"].lower() or "tech lead" in item["title"].lower() or "architect" in item["title"].lower():
            pitch_subject = f"Question regarding engineering roadmap & open roles @ {comp_clean}"
            pitch_body = (
                f"Hi [Hiring Manager / {item['title']}],\n\n"
                f"I noticed {comp_clean} is building out high-impact engineering solutions and wanted to reach out directly.\n\n"
                f"I specialize in {skills_str}. In my recent projects, I focused on high throughput, robust system design, and fast feature delivery.\n\n"
                f"Would you be open to a 5-minute chat this week, or may I send across a 1-page summary of my technical background?\n\n"
                f"Best regards,\n{user_name}"
            )
        else:
            pitch_subject = f"Application follow-up & quick note: Engineering roles @ {comp_clean} — {user_name}"
            pitch_body = (
                f"Hi [Recruiter / {item['title']}],\n\n"
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
            "title": item["title"],
            "category": item["category"],
            "badge_color": item["badge_color"],
            "icon": item["icon"],
            "description": item["description"],
            "company": comp_clean,
            "location": loc_clean,
            "profile_url": linkedin_url,
            "links": {
                "linkedin_search": linkedin_url,
                "company_people": company_people_url,
                "google_xray": google_xray_url
            },
            "pitch": {
                "subject": pitch_subject,
                "body": pitch_body,
                "gmail_url": gmail_url
            }
        })

    return {
        "company": comp_clean,
        "location": loc_clean,
        "target_keyword": kw_raw or "All Hiring Roles",
        "decision_makers": results
    }


def search_company_decision_makers(company, target_keyword=None, location="India", user_skills=None, user_name="Applicant"):
    return generate_recruiter_members(
        company=company,
        target_keyword=target_keyword,
        location=location,
        user_skills=user_skills,
        user_name=user_name
    )
