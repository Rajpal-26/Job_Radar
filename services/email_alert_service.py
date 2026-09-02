# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

"""Email Alert Service for JobRadar daily job digests via SMTP."""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import json

def load_env_vars():
    """Reads .env file dynamically."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip()
                    os.environ[k.strip()] = v.strip()
    return env_vars

load_env_vars()

# Dynamic getters for configuration
def get_smtp_config():
    env = load_env_vars()
    return {
        "host": os.getenv("SMTP_HOST") or env.get("SMTP_HOST", "smtp.gmail.com"),
        "port": int(os.getenv("SMTP_PORT") or env.get("SMTP_PORT", 587)),
        "user": os.getenv("SMTP_USER") or env.get("SMTP_USER", ""),
        "password": os.getenv("SMTP_PASSWORD") or env.get("SMTP_PASSWORD", ""),
        "recipient": os.getenv("ALERT_RECIPIENT_EMAIL") or env.get("ALERT_RECIPIENT_EMAIL", "rajpaltanwar2608@gmail.com")
    }

DEFAULT_RECIPIENT = get_smtp_config()["recipient"]


def generate_digest_html(jobs, target_roles, target_exp, target_locations, recipient_email=DEFAULT_RECIPIENT):
    """Generates a modern, responsive HTML email template for daily job alerts."""
    today_str = datetime.now().strftime("%B %d, %Y")
    total_jobs = len(jobs)
    
    linkedin_count = sum(1 for j in jobs if j.get("portal", "").lower() == "linkedin" or "linkedin" in j.get("link", "").lower())
    indeed_count = sum(1 for j in jobs if j.get("portal", "").lower() == "indeed" or "indeed" in j.get("link", "").lower())
    ats_count = sum(1 for j in jobs if "ats" in j.get("portal", "").lower() or "greenhouse" in j.get("link", "").lower() or "lever.co" in j.get("link", "").lower() or "ashby" in j.get("link", "").lower())
    
    # Format Job Rows
    rows_html = ""
    for idx, job in enumerate(jobs, 1):
        title = job.get("title", "Software Engineer")
        company = job.get("company", "Tech Company")
        location = job.get("location", "India / Remote")
        exp = job.get("experience", "Fresher / 0-1 Yr")
        posted = job.get("posted", "Recent")
        link = job.get("link", "#")
        portal = job.get("portal", "LinkedIn").upper()
        salary = job.get("salary", "")
        skills = job.get("skills", [])
        
        if "ATS" in portal or "CAREER" in portal:
            portal_badge_bg = "#059669"
            portal_label = "✅ DIRECT ATS"
        elif "LINKEDIN" in portal:
            portal_badge_bg = "#0a66c2"
            portal_label = "LINKEDIN"
        else:
            portal_badge_bg = "#2164f3"
            portal_label = "INDEED"
            
        salary_html = f'<span style="background: #fef3c7; color: #b45309; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 4px; display: inline-block; margin-right: 4px;">💰 {salary}</span>' if salary else ""
        skills_html = "".join([f'<span style="background: #ede9fe; color: #6d28d9; font-size: 10px; font-weight: 600; padding: 2px 6px; border-radius: 4px; display: inline-block; margin-right: 3px;">{s}</span>' for s in skills[:3]]) if skills else ""
        
        rows_html += f"""
        <tr style="border-bottom: 1px solid #e2e8f0; font-size: 14px;">
            <td style="padding: 16px 12px; vertical-align: top;">
                <span style="font-weight: 800; color: #64748b; font-size: 12px;">#{idx}</span>
            </td>
            <td style="padding: 16px 12px; vertical-align: top;">
                <div style="font-weight: 700; color: #0f172a; font-size: 15px; margin-bottom: 4px;">
                    {title}
                </div>
                <div style="color: #475569; font-weight: 600; font-size: 13px; margin-bottom: 6px;">
                    🏢 {company}
                </div>
                <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-top: 6px;">
                    <span style="background: #f1f5f9; color: #334155; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 4px; display: inline-block; margin-right: 4px;">📍 {location}</span>
                    <span style="background: #ecfdf5; color: #059669; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 4px; display: inline-block; margin-right: 4px;">⏳ {exp}</span>
                    {salary_html}
                    <span style="background: #f8fafc; color: #64748b; font-size: 11px; padding: 2px 8px; border-radius: 4px; display: inline-block;">🕒 {posted}</span>
                </div>
                {f'<div style="margin-top: 6px;">{skills_html}</div>' if skills_html else ''}
            </td>
            <td style="padding: 16px 12px; text-align: right; vertical-align: middle; white-space: nowrap;">
                <div style="margin-bottom: 8px;">
                    <span style="background: {portal_badge_bg}; color: #ffffff; font-size: 11px; font-weight: 800; padding: 3px 8px; border-radius: 4px; text-transform: uppercase;">
                        {portal_label}
                    </span>
                </div>
                <a href="{link}" target="_blank" style="background: linear-gradient(135deg, #0ea5e9, #0284c7); color: #ffffff; text-decoration: none; font-weight: 700; font-size: 12px; padding: 7px 14px; border-radius: 6px; display: inline-block; box-shadow: 0 2px 6px rgba(14,165,233,0.3);">
                    ⚡ Apply Now &rarr;
                </a>
            </td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JobRadar Daily Job Alert - {today_str}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b;">
    <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f8fafc; padding: 24px 12px;">
        <tr>
            <td align="center">
                <!-- Main Container -->
                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 680px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.06); border: 1px solid #e2e8f0;">
                    
                    <!-- Header Banner -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 32px 28px; text-align: left; border-bottom: 3px solid #0ea5e9;">
                            <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                <tr>
                                    <td>
                                        <div style="font-size: 24px; font-weight: 900; letter-spacing: -0.5px; color: #ffffff; margin-bottom: 4px;">
                                            Job<span style="color: #38bdf8;">Radar</span> <span style="font-size: 13px; font-weight: 700; background: rgba(56, 189, 248, 0.2); color: #38bdf8; padding: 3px 8px; border-radius: 4px; border: 1px solid rgba(56, 189, 248, 0.4); vertical-align: middle; margin-left: 8px;">DAILY DIGEST</span>
                                        </div>
                                        <div style="font-size: 13px; color: #94a3b8; font-weight: 500;">
                                            Automated Job Alert &bull; {today_str}
                                        </div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Summary Stats Bar -->
                    <tr>
                        <td style="background-color: #f1f5f9; padding: 16px 28px; border-bottom: 1px solid #e2e8f0;">
                            <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                <tr>
                                    <td style="font-size: 13px; color: #475569;">
                                        🎯 <strong>{total_jobs} Fresh Matching Jobs</strong> Scraped Today
                                    </td>
                                    <td align="right" style="font-size: 12px; color: #64748b;">
                                        <span style="color: #0a66c2; font-weight: 700;">LinkedIn: {linkedin_count}</span> &bull; 
                                        <span style="color: #2164f3; font-weight: 700;">Indeed: {indeed_count}</span>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Filter Criteria Box -->
                    <tr>
                        <td style="padding: 20px 28px 12px 28px;">
                            <div style="background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 8px; padding: 12px 16px; font-size: 12px; color: #64748b; line-height: 1.6;">
                                <strong>🎯 Targeted Roles:</strong> {', '.join(target_roles)}<br>
                                <strong>⏳ Experience Band:</strong> {', '.join(target_exp)}<br>
                                <strong>📍 Locations:</strong> {', '.join(target_locations[:5])}{f" (+{len(target_locations)-5} more)" if len(target_locations) > 5 else ""}
                            </div>
                        </td>
                    </tr>

                    <!-- Jobs Table -->
                    <tr>
                        <td style="padding: 10px 28px 28px 28px;">
                            <table width="100%" border="0" cellspacing="0" cellpadding="0" style="border-collapse: collapse;">
                                <thead>
                                    <tr style="border-bottom: 2px solid #cbd5e1; font-size: 12px; font-weight: 800; color: #64748b; text-transform: uppercase;">
                                        <th align="left" style="padding: 10px 12px; width: 30px;">#</th>
                                        <th align="left" style="padding: 10px 12px;">Job Opportunity</th>
                                        <th align="right" style="padding: 10px 12px; width: 120px;">Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {rows_html if rows_html else '<tr><td colspan="3" style="text-align: center; padding: 30px; color: #64748b;">No new jobs matched the criteria for today.</td></tr>'}
                                </tbody>
                            </table>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #0f172a; padding: 24px 28px; text-align: center; color: #64748b; font-size: 12px; border-top: 1px solid #1e293b;">
                            <div style="color: #94a3b8; font-size: 13px; font-weight: 600; margin-bottom: 6px;">
                                JobRadar automated by <a href="https://mail.google.com/mail/?view=cm&fs=1&to=rajpaltanwar2608@gmail.com" style="color: #38bdf8; text-decoration: none;">Rajpal Singh Tanwar</a>
                            </div>
                            <div>
                                This alert was automatically compiled and sent to <span style="color: #cbd5e1;">{recipient_email}</span>.
                            </div>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
    return html


def send_job_digest_email(jobs, target_roles, target_exp, target_locations, recipient_email=None, smtp_config=None):
    """
    Sends the HTML job digest email via SMTP.
    If SMTP credentials are not configured, saves a local HTML preview and returns status.
    """
    cfg = get_smtp_config()
    recipient = recipient_email or cfg["recipient"]
    smtp_host = (smtp_config or {}).get("host") or cfg["host"]
    smtp_port = int((smtp_config or {}).get("port") or cfg["port"])
    smtp_user = (smtp_config or {}).get("user") or cfg["user"]
    smtp_pass = (smtp_config or {}).get("password") or cfg["password"]
    
    html_content = generate_digest_html(
        jobs=jobs,
        target_roles=target_roles,
        target_exp=target_exp,
        target_locations=target_locations,
        recipient_email=recipient
    )
    
    # Save copy to local data directory for inspection & preview
    os.makedirs("data", exist_ok=True)
    preview_path = os.path.join("data", "latest_email_digest.html")
    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    # Check if SMTP credentials are provided
    if not smtp_user or not smtp_pass:
        print(f"[Email Service] SMTP credentials not set. Email digest with {len(jobs)} jobs saved to: {preview_path}")
        return {
            "success": True,
            "mode": "preview_saved",
            "message": f"Digest generated with {len(jobs)} jobs. Saved local preview to {preview_path} (Configure SMTP_USER & SMTP_PASSWORD to send live email).",
            "preview_path": preview_path,
            "jobs_count": len(jobs),
            "recipient": recipient
        }
        
    # Live SMTP Dispatch
    try:
        today_formatted = datetime.now().strftime("%A, %d %b %Y")
        linkedin_count = sum(1 for j in jobs if j.get("portal", "").lower() == "linkedin" or "linkedin" in j.get("link", "").lower())
        indeed_count = sum(1 for j in jobs if j.get("portal", "").lower() == "indeed" or "indeed" in j.get("link", "").lower())
        ats_count = sum(1 for j in jobs if "ats" in j.get("portal", "").lower() or "greenhouse" in j.get("link", "").lower() or "lever.co" in j.get("link", "").lower() or "ashby" in j.get("link", "").lower())
        
        breakdown_str = f"LinkedIn: {linkedin_count}, Indeed: {indeed_count}"
        if ats_count > 0:
            breakdown_str += f", ATS: {ats_count}"
            
        subject = f"🎯 JobRadar Daily Alert: {len(jobs)} Jobs ({breakdown_str}) - {today_formatted}"
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"JobRadar Alert <{smtp_user}>"
        msg["To"] = recipient
        
        # Attach HTML body
        msg.attach(MIMEText(html_content, "html", "utf-8"))
        
        print(f"[Email Service] Connecting to SMTP server {smtp_host}:{smtp_port}...")
        with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [recipient], msg.as_string())
            
        print(f"[Email Service] Successfully sent daily job digest with {len(jobs)} jobs to {recipient}!")
        return {
            "success": True,
            "mode": "sent",
            "message": f"Successfully sent daily digest with {len(jobs)} jobs to {recipient}",
            "recipient": recipient,
            "jobs_count": len(jobs),
            "preview_path": preview_path
        }
    except Exception as e:
        print(f"[Email Service ERROR] Failed to dispatch email: {e}")
        return {
            "success": False,
            "mode": "error",
            "error": str(e),
            "message": f"Failed to send email via SMTP ({e}). Local preview saved to {preview_path}",
            "preview_path": preview_path,
            "jobs_count": len(jobs),
            "recipient": recipient
        }
