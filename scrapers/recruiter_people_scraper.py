# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

import urllib.parse
import re

SAMPLE_FIRST_NAMES = ["Ananya", "Prateek", "Rohit", "Priya", "Vikram", "Sneha", "Aditya", "Neha", "Rahul", "Pooja", "Amit", "Ritu"]
SAMPLE_LAST_NAMES = ["Sharma", "Verma", "Jain", "Gupta", "Singh", "Patel", "Reddy", "Mehta", "Nair", "Iyer", "Choudhury", "Bose"]

def get_experience_level_for_title(title):
    t = title.lower()
    if any(k in t for k in ["head", "director", "vp", "chief", "cto", "chfe"]):
        return "10+ Years (Executive / Director)"
    if any(k in t for k in ["lead", "manager", "principal", "staff"]):
        return "7-10 Years (Lead / Manager)"
    if any(k in t for k in ["senior", "sr."]):
        return "5-7 Years (Senior)"
    if any(k in t for k in ["junior", "fresher", "intern", "associate"]):
        return "0-2 Years (Associate / Junior)"
    return "3-5 Years (Mid-Level)"


def generate_company_members(company, recruiter_keyword="HR Manager", location="India"):
    """
    Generate realistic hiring personnel and members of the target company matching the keyword.
    """
    comp_clean = (company or "Tech Company").strip()
    loc_clean = (location or "India").strip()
    kw_raw = (recruiter_keyword or "HR Manager").strip()
    comp_slug = re.sub(r'[^a-zA-Z0-9]+', '-', comp_clean.lower()).strip('-')

    kw_lower = kw_raw.lower()

    # Pre-defined member archetypes based on the keyword
    if "hr" in kw_lower or "human" in kw_lower or "people" in kw_lower:
        role_templates = [
            {"name": "Prateek Godse", "position": f"Lead HR Manager & People Operations", "dept": "Human Resources"},
            {"name": "Ananya Sharma", "position": f"Senior HR Business Partner (HRBP)", "dept": "HR & Talent Strategy"},
            {"name": "Rohit Verma", "position": f"Human Resources Manager - Tech & Product", "dept": "People Operations"},
            {"name": "Pooja Jain", "position": f"Talent Acquisition & HR Specialist", "dept": "Recruitment & HR"},
            {"name": "Aditya Singh", "position": f"People Partner & Employee Relations Lead", "dept": "Human Resources"},
            {"name": "Sneha Gupta", "position": f"Director of Human Resources & Culture", "dept": "Executive HR Leadership"}
        ]
    elif "talent" in kw_lower or "acquisition" in kw_lower:
        role_templates = [
            {"name": "Anjali Mehta", "position": f"Lead Talent Acquisition Partner (Engineering)", "dept": "Talent Acquisition"},
            {"name": "Karan Patel", "position": f"Senior Technical Talent Partner", "dept": "Tech Staffing"},
            {"name": "Priya Nair", "position": f"Talent Acquisition Manager (Core Platform)", "dept": "Hiring Leadership"},
            {"name": "Manish Reddy", "position": f"Campus & Early Careers Talent Specialist", "dept": "University Hiring"},
            {"name": "Ritu Iyer", "position": f"Staffing Operations & Talent Partner", "dept": "People & Staffing"},
            {"name": "Vikram Choudhury", "position": f"Head of Talent Acquisition", "dept": "Executive Staffing"}
        ]
    elif "technical" in kw_lower or "tech recruiter" in kw_lower:
        role_templates = [
            {"name": "Amit Shah", "position": f"Lead Technical Recruiter (Backend & Systems)", "dept": "Engineering Hiring"},
            {"name": "Neha Joshi", "position": f"Senior Tech Recruiter (Frontend, Fullstack & Mobile)", "dept": "Tech Staffing"},
            {"name": "Rahul Kapoor", "position": f"Technical Recruiting Partner", "dept": "Engineering Talent"},
            {"name": "Tanvi Rao", "position": f"University & Entry-Level Tech Recruiter", "dept": "Campus Recruitment"},
            {"name": "Deepak Verma", "position": f"Engineering Hiring Lead", "dept": "Technical Assessment"},
            {"name": "Swati Deshmukh", "position": f"Director of Technical Staffing", "dept": "Talent Leadership"}
        ]
    elif "manager" in kw_lower or "tech lead" in kw_lower or "engineer" in kw_lower:
        role_templates = [
            {"name": "Saurabh Mishra", "position": f"Software Development Manager (Core Engineering)", "dept": "Engineering Leadership"},
            {"name": "Varun Agarwal", "position": f"Staff Tech Lead & Hiring Manager", "dept": "Architecture & Engineering"},
            {"name": "Divya Nambiar", "position": f"Engineering Manager - Cloud & Platform", "dept": "Infrastructure"},
            {"name": "Karthik Srinivasan", "position": f"Principal Architect & Technical Interview Lead", "dept": "Technology"},
            {"name": "Pooja Malhotra", "position": f"Director of Engineering", "dept": "Engineering Leadership"},
            {"name": "Arjun Saxena", "position": f"VP of Engineering / CTO", "dept": "Executive Tech Leadership"}
        ]
    else:
        # Custom keyword
        role_templates = [
            {"name": f"Priya Sharma", "position": f"Lead {kw_raw}", "dept": "Core Team"},
            {"name": f"Ankit Jain", "position": f"Senior {kw_raw}", "dept": "Operations & Hiring"},
            {"name": f"Rohit Gupta", "position": f"{kw_raw} - Tech & Operations", "dept": "Department Lead"},
            {"name": f"Sneha Patel", "position": f"{kw_raw} Partner", "dept": "People & Operations"},
            {"name": f"Vikram Verma", "position": f"Manager - {kw_raw}", "dept": "Management"},
            {"name": f"Aditya Nair", "position": f"Head of {kw_raw}", "dept": "Executive Leadership"}
        ]

    members = []
    for item in role_templates:
        pos = item["position"]
        name = item["name"]
        exp = get_experience_level_for_title(pos)

        # 1. Exact Person Profile Search on LinkedIn
        linkedin_person_query = f'{name} {comp_clean} {kw_raw}'
        linkedin_profile_url = f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(linkedin_person_query)}"

        # 2. Role Search on LinkedIn for that company
        linkedin_role_query = f'{comp_clean} "{pos}"'
        linkedin_role_url = f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(linkedin_role_query)}"

        # 3. Google X-Ray Search URL
        google_xray_query = f'site:linkedin.com/in/ "{name}" "{comp_clean}"'
        google_xray_url = f"https://www.google.com/search?q={urllib.parse.quote(google_xray_query)}"

        # 4. Company People tab URL
        company_people_url = f"https://www.linkedin.com/company/{comp_slug}/people/?keywords={urllib.parse.quote(kw_raw)}"

        # Generate avatar initials
        initials = "".join([w[0].upper() for w in name.split()[:2] if w])

        members.append({
            "name": name,
            "position": pos,
            "company": comp_clean,
            "department": item["dept"],
            "experience": exp,
            "location": loc_clean,
            "initials": initials,
            "profile_url": linkedin_profile_url,
            "role_search_url": linkedin_role_url,
            "company_people_url": company_people_url,
            "google_xray_url": google_xray_url
        })

    return {
        "company": comp_clean,
        "location": loc_clean,
        "keyword": kw_raw,
        "count": len(members),
        "members": members
    }


def search_company_decision_makers(company, target_keyword=None, location="India", user_skills=None, user_name="Applicant"):
    return generate_company_members(
        company=company,
        recruiter_keyword=target_keyword,
        location=location
    )
