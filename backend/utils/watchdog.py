# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from models.database import db
from models.watchdog import Watchdog
from models.saved_job import SavedJob
from utils.search_engine import execute_parallel_search

scheduler = None

def run_single_watchdog(watchdog_id, app=None):
    """Execute search for a single watchdog and save high-match jobs to DB."""
    def _execute():
        watchdog = Watchdog.query.get(watchdog_id)
        if not watchdog or not watchdog.active:
            return 0

        portals_list = [p.strip() for p in watchdog.portals.split(",") if p.strip()]
        locations_list = [l.strip() for l in watchdog.locations.split(",") if l.strip()]

        jobs, _ = execute_parallel_search(
            role=watchdog.role,
            locations=locations_list,
            fromage=3,
            limit_per_portal=15,
            portals=portals_list
        )

        saved_count = 0
        for j in jobs:
            score = j.get("Match_Score", 75)
            if score >= watchdog.min_match_score:
                link = j.get("Link") or f"https://jobradar.local/{hash(j.get('Job Title')+j.get('Company'))}"
                existing = SavedJob.query.filter_by(link=link).first()
                if not existing:
                    new_job = SavedJob(
                        job_title=j.get("Job Title", "Unknown Role"),
                        company=j.get("Company", "Unknown Company"),
                        location=j.get("Location", ""),
                        link=link,
                        platform=j.get("Platform", "JobRadar"),
                        salary=j.get("Salary", ""),
                        status="Watchdog Alert",
                        match_score=score,
                        notes=f"Auto-saved by Watchdog: {watchdog.name}"
                    )
                    db.session.add(new_job)
                    saved_count += 1

        watchdog.last_run = datetime.utcnow()
        db.session.commit()
        return saved_count

    if app:
        with app.app_context():
            return _execute()
    else:
        return _execute()

def init_scheduler(app):
    """Initialize APScheduler background scheduler for active watchdogs."""
    global scheduler
    if scheduler and scheduler.running:
        return

    scheduler = BackgroundScheduler(daemon=True)
    
    def check_and_run_all():
        with app.app_context():
            active_watchdogs = Watchdog.query.filter_by(active=True).all()
            for w in active_watchdogs:
                try:
                    run_single_watchdog(w.id, app)
                except Exception as e:
                    print(f"[Watchdog Error] Failed to run watchdog {w.id}: {e}")

    # Schedule watchdog checks every 6 hours
    scheduler.add_job(check_and_run_all, 'interval', hours=6, id='job_watchdog_cron')
    
    # Schedule Daily Indeed & LinkedIn Digest at 08:00 AM daily
    def run_daily_email_job():
        try:
            from services.daily_job_cron import run_daily_scraper_pipeline
            print(f"[Daily Alert Cron] Executing scheduled daily job digest for Indeed & LinkedIn...")
            with app.app_context():
                run_daily_scraper_pipeline(limit=50)
        except Exception as e:
            print(f"[Daily Alert Cron Error] {e}")
            
    import os
    digest_time_str = os.getenv("DAILY_DIGEST_TIME", "08:00")
    try:
        hr, mn = [int(x) for x in digest_time_str.split(":")]
    except Exception:
        hr, mn = 8, 0
        
    scheduler.add_job(run_daily_email_job, 'cron', hour=hr, minute=mn, id='daily_job_alert_digest')
    scheduler.start()
    print(f"[Watchdog Scheduler] Started successfully. Daily Email Digest scheduled at {hr:02d}:{mn:02d} daily.")
