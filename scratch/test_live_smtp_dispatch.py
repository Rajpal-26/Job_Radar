import sys, os
sys.path.insert(0, os.path.abspath("."))

from services.email_alert_service import send_job_digest_email, get_smtp_config
from services.daily_job_cron import TARGET_ROLES, TARGET_EXPERIENCE, TARGET_LOCATIONS

cfg = get_smtp_config()
print("Loaded Config:")
print(f"  Host: {cfg['host']}:{cfg['port']}")
print(f"  User: {cfg['user']}")
print(f"  Recipient: {cfg['recipient']}")
print(f"  Has Password: {bool(cfg['password'])}")

sample_jobs = [
    {
        "title": "Python Developer (0-1 Year / Entry Level)",
        "company": "TCS Interactive",
        "location": "Indore, Madhya Pradesh",
        "experience": "0-1 Year",
        "posted": "Today",
        "link": "https://in.linkedin.com/jobs/view/4100000001",
        "portal": "LinkedIn"
    },
    {
        "title": "Associate Software Engineer - Python / Django",
        "company": "Infosys Ltd",
        "location": "Bengaluru, Karnataka",
        "experience": "0-6 Months",
        "posted": "Just posted",
        "link": "https://in.indeed.com/viewjob?jk=indeed100002",
        "portal": "Indeed"
    },
    {
        "title": "AI/LLM Engineer (GenAI / LangChain)",
        "company": "Cognizant AI Labs",
        "location": "Pune / Remote",
        "experience": "Fresher",
        "posted": "1 day ago",
        "link": "https://in.linkedin.com/jobs/view/4100000003",
        "portal": "LinkedIn"
    },
    {
        "title": "Software Engineer - Backend (Python / FastAPI)",
        "company": "Razorpay Payments",
        "location": "Bengaluru, Karnataka",
        "experience": "0-1 Year",
        "posted": "2 days ago",
        "link": "https://in.indeed.com/viewjob?jk=indeed100004",
        "portal": "Indeed"
    },
    {
        "title": "AI Engineer (Computer Vision & NLP)",
        "company": "ThoughtWin Solutions",
        "location": "Indore, Madhya Pradesh",
        "experience": "0-1 Year",
        "posted": "Today",
        "link": "https://in.linkedin.com/jobs/view/4100000005",
        "portal": "LinkedIn"
    }
]

print("\n--- Dispatching Live Test Email via SMTP ---")
result = send_job_digest_email(
    jobs=sample_jobs,
    target_roles=TARGET_ROLES,
    target_exp=TARGET_EXPERIENCE,
    target_locations=TARGET_LOCATIONS,
    recipient_email=cfg['recipient']
)

print("\nDispatch Result:")
print(result)
