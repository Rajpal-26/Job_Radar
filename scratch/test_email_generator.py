import sys, os
sys.path.insert(0, os.path.abspath("."))
from services.email_alert_service import generate_digest_html, send_job_digest_email
from services.daily_job_cron import TARGET_ROLES, TARGET_EXPERIENCE, TARGET_LOCATIONS

sample_jobs = [
    {
        "title": "Python Developer (Fresher / 0-1 Yr)",
        "company": "TCS Interactive",
        "location": "Indore, India",
        "experience": "0-1 Year",
        "posted": "Today",
        "link": "https://in.linkedin.com/jobs/view/123456",
        "portal": "LinkedIn"
    },
    {
        "title": "Associate Software Engineer - Python / Django",
        "company": "Infosys Ltd",
        "location": "Bengaluru, India",
        "experience": "0-6 Months",
        "posted": "3 hours ago",
        "link": "https://in.indeed.com/viewjob?jk=789101",
        "portal": "Indeed"
    },
    {
        "title": "AI/LLM Engineer (Junior / Entry Level)",
        "company": "Cognizant AI Labs",
        "location": "Pune / Remote",
        "experience": "Fresher",
        "posted": "Just posted",
        "link": "https://in.linkedin.com/jobs/view/555666",
        "portal": "LinkedIn"
    },
    {
        "title": "Software Engineer - Backend (Python / FastAPI)",
        "company": "Razorpay Tech",
        "location": "Bengaluru, India",
        "experience": "0-1 Year",
        "posted": "1 day ago",
        "link": "https://in.indeed.com/viewjob?jk=222333",
        "portal": "Indeed"
    },
    {
        "title": "AI Engineer (GenAI & LangChain)",
        "company": "ThoughtWin Solutions",
        "location": "Indore, India",
        "experience": "0-1 Year",
        "posted": "Today",
        "link": "https://in.linkedin.com/jobs/view/777888",
        "portal": "LinkedIn"
    }
]

res = send_job_digest_email(
    jobs=sample_jobs,
    target_roles=TARGET_ROLES,
    target_exp=TARGET_EXPERIENCE,
    target_locations=TARGET_LOCATIONS,
    recipient_email="rajpaltanwar2608@gmail.com"
)

print("Result:", res)
