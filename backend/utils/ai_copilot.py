# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

import re
from utils.resume_parser import TECH_SKILLS

def analyze_skill_gaps(jobs, user_skills):
    """
    Compare user skills against all scraped job descriptions.
    Annotates each job with 'missing_skills' and returns overall market demand.
    """
    user_skills_set = set([s.lower() for s in user_skills])
    skill_market_counts = {}

    annotated_jobs = []
    for job in jobs:
        desc = (job.get("Description") or "") + " " + (job.get("Job Title") or "")
        job_skills = set()
        for skill in TECH_SKILLS:
            if re.search(r'\b' + re.escape(skill) + r'\b', desc, re.IGNORECASE):
                job_skills.add(skill)
                skill_market_counts[skill] = skill_market_counts.get(skill, 0) + 1

        missing = [s for s in job_skills if s.lower() not in user_skills_set]
        j_copy = dict(job)
        j_copy["Required_Skills"] = sorted(list(job_skills))
        j_copy["Missing_Skills"] = missing[:5]
        annotated_jobs.append(j_copy)

    # Sort market demand
    sorted_market_demand = sorted(
        [{"skill": k, "count": v} for k, v in skill_market_counts.items()],
        key=lambda x: x["count"],
        reverse=True
    )

    return annotated_jobs, sorted_market_demand

def generate_recruiter_dm(job_title, company, user_skills=None, user_name="Applicant"):
    """
    Generate a high-converting, personalized 2-sentence LinkedIn/Email recruiter outreach DM.
    """
    skills_str = ", ".join(user_skills[:4]) if user_skills else "software engineering and modern tech stacks"
    
    dm = (
        f"Hi [Hiring Manager], I saw your opening for {job_title} at {company} and wanted to reach out. "
        f"With a strong background in {skills_str}, I’ve built scalable solutions that match what {company} is growing. "
        f"I’d love to connect for 5 minutes or share my resume. Best, {user_name}."
    )
    return dm


def generate_recruiter_intelligence(company, job_title="Software Engineer", user_skills=None, user_name="Applicant", location="India"):
    """
    Generate deep search queries and multi-channel outreach templates for decision makers (Recruiters, EMs, Tech Leads).
    """
    import urllib.parse
    
    comp_clean = (company or "Tech Company").strip()
    role_clean = (job_title or "Software Engineer").strip()
    skills_str = ", ".join(user_skills[:4]) if user_skills else "distributed systems, scalable APIs, and problem solving"
    
    # 1. Direct Search URLs
    recruiter_kw = f'{comp_clean} ("Technical Recruiter" OR "Talent Acquisition" OR "Recruiter" OR "HR Manager")'
    em_kw = f'{comp_clean} ("Engineering Manager" OR "Tech Lead" OR "Software Development Manager" OR "Engineering Lead")'
    exec_kw = f'{comp_clean} ("VP of Engineering" OR "Head of Engineering" OR "CTO" OR "Director of Engineering")'
    team_kw = f'{comp_clean} "{role_clean}"'
    
    linkedin_recruiters = f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(recruiter_kw)}"
    linkedin_ems = f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(em_kw)}"
    linkedin_execs = f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(exec_kw)}"
    linkedin_team = f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(team_kw)}"
    
    # Google X-Ray Search (bypasses LinkedIn commercial search limits)
    google_xray_query = f'site:linkedin.com/in/ "{comp_clean}" ("Engineering Manager" OR "Tech Lead" OR "Technical Recruiter") {location}'
    google_xray_url = f"https://www.google.com/search?q={urllib.parse.quote(google_xray_query)}"

    # 2. Outreach Templates
    em_subject = f"Quick question regarding {role_clean} on your team at {comp_clean}"
    em_pitch = (
        f"Hi [Engineering Manager],\n\n"
        f"I noticed {comp_clean} is expanding the engineering team and recently opened the {role_clean} position.\n\n"
        f"I specialize in {skills_str}, with hands-on experience building high-throughput services and reliable infrastructure. "
        f"I’ve followed {comp_clean}’s work in tech and would love to bring this experience to your sprint priorities.\n\n"
        f"Would you be open to a 5-minute chat this week, or may I send across a 1-page summary of my technical background?\n\n"
        f"Best regards,\n{user_name}"
    )

    recruiter_subject = f"Application & Quick Note: {role_clean} @ {comp_clean} — {user_name}"
    recruiter_pitch = (
        f"Hi [Recruiter Name],\n\n"
        f"I recently applied for the {role_clean} opening at {comp_clean} and wanted to reach out directly to express my strong interest.\n\n"
        f"My core toolkit covers {skills_str}. In my recent projects, I focused on high performance, clean architecture, and rapid feature delivery.\n\n"
        f"I’d love to connect and see if my background aligns with what the hiring team is prioritizing for this role.\n\n"
        f"Thanks for your time!\n{user_name}"
    )

    referral_subject = f"Connecting with fellow engineer @ {comp_clean} / Quick referral question"
    referral_pitch = (
        f"Hi [Engineer Name],\n\n"
        f"Hope you’re having a great week! I came across your profile while researching engineering at {comp_clean}.\n\n"
        f"I’m applying for the {role_clean} role and really admire the technical challenges the team is tackling. "
        f"Given my background in {skills_str}, I believe I’d be a strong contributor.\n\n"
        f"If you feel there’s good alignment, would you be open to putting in a quick internal referral for me? Happy to share my resume and portfolio first.\n\n"
        f"Thanks a lot,\n{user_name}"
    )

    gmail_compose_em = (
        f"https://mail.google.com/mail/?view=cm&fs=1"
        f"&su={urllib.parse.quote(em_subject)}"
        f"&body={urllib.parse.quote(em_pitch)}"
    )

    return {
        "company": comp_clean,
        "role": role_clean,
        "links": {
            "recruiters": linkedin_recruiters,
            "engineering_managers": linkedin_ems,
            "executives": linkedin_execs,
            "team_members": linkedin_team,
            "google_xray": google_xray_url
        },
        "templates": {
            "em": {
                "title": "👨‍💻 Engineering Manager Pitch (Highest Response Rate)",
                "subject": em_subject,
                "body": em_pitch,
                "gmail_url": gmail_compose_em
            },
            "recruiter": {
                "title": "👔 Technical Recruiter Direct Note",
                "subject": recruiter_subject,
                "body": recruiter_pitch
            },
            "referral": {
                "title": "🤝 Peer Engineer Referral Request",
                "subject": referral_subject,
                "body": referral_pitch
            }
        }
    }
