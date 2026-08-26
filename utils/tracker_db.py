# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tracker.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the SQLite database for saved jobs & application tracking."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            link TEXT UNIQUE,
            platform TEXT,
            salary TEXT,
            status TEXT DEFAULT 'Bookmarked',
            match_score INTEGER DEFAULT 75,
            notes TEXT DEFAULT '',
            cover_letter TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

def get_all_saved_jobs():
    """Retrieve all saved jobs grouped by status or flat list."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM saved_jobs ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()

    jobs = [dict(row) for row in rows]
    return jobs

def save_job(job_data):
    """Save a job to the tracker. Returns (inserted_id, is_new)."""
    conn = get_db()
    cursor = conn.cursor()
    
    title = job_data.get("Job Title") or job_data.get("title") or "Unknown Role"
    company = job_data.get("Company") or job_data.get("company") or "Unknown Company"
    location = job_data.get("Location") or job_data.get("location") or ""
    link = job_data.get("Link") or job_data.get("link") or f"https://jobradar.local/{hash(title+company)}"
    platform = job_data.get("Platform") or job_data.get("platform") or "JobRadar"
    salary = job_data.get("Salary") or job_data.get("salary") or ""
    match_score = int(job_data.get("Match_Score") or job_data.get("match_score") or 75)
    status = job_data.get("status") or "Bookmarked"
    notes = job_data.get("notes") or ""
    cover_letter = job_data.get("cover_letter") or ""

    try:
        cursor.execute("""
            INSERT INTO saved_jobs (job_title, company, location, link, platform, salary, status, match_score, notes, cover_letter)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, company, location, link, platform, salary, status, match_score, notes, cover_letter))
        conn.commit()
        inserted_id = cursor.lastrowid
        conn.close()
        return inserted_id, True
    except sqlite3.IntegrityError:
        # Job with same link already exists
        cursor.execute("SELECT id FROM saved_jobs WHERE link = ?", (link,))
        row = cursor.fetchone()
        conn.close()
        existing_id = row["id"] if row else None
        return existing_id, False

def update_job_status(job_id, status=None, notes=None, cover_letter=None):
    """Update status, notes, or cover letter of a saved job."""
    conn = get_db()
    cursor = conn.cursor()

    updates = []
    params = []
    if status is not None:
        updates.append("status = ?")
        params.append(status)
    if notes is not None:
        updates.append("notes = ?")
        params.append(notes)
    if cover_letter is not None:
        updates.append("cover_letter = ?")
        params.append(cover_letter)

    if not updates:
        conn.close()
        return False

    params.append(job_id)
    query = f"UPDATE saved_jobs SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(query, params)
    conn.commit()
    conn.close()
    return True

def delete_saved_job(job_id):
    """Delete a saved job by ID."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM saved_jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()
    return True
