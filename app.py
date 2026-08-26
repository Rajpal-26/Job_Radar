# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

from flask import Flask, render_template, request, jsonify, send_file, abort, Response
from scrapers import (scrape_linkedin, scrape_glassdoor, scrape_indeed,
                      scrape_hirist, scrape_naukri, scrape_foundit,
                      scrape_apna, scrape_shine)
from scrapers.glassdoor import GLASSDOOR_CITIES
from scrapers.indeed import INDEED_CITIES
from scrapers.hirist import HIRIST_CATEGORIES, HIRIST_CITIES, HIRIST_EXPERIENCE
from scrapers.naukri import NAUKRI_CITIES
from scrapers.foundit import FOUNDIT_CITIES
from scrapers.apna import APNA_CITIES
from scrapers.shine import SHINE_CITIES, SHINE_EXPERIENCE
import pandas as pd
import os
from utils import search_engine, tracker_db

# Initialize Application Tracker SQLite DB
tracker_db.init_db()

app = Flask(__name__)

# Scrapers mapping for parallel aggregator
SCRAPERS_MAP = {
    "linkedin": scrape_linkedin,
    "glassdoor": scrape_glassdoor,
    "indeed": scrape_indeed,
    "hirist": scrape_hirist,
    "naukri": scrape_naukri,
    "foundit": scrape_foundit,
    "apna": scrape_apna,
    "shine": scrape_shine,
}

# Per-portal cache of the most recent search results
latest = {"linkedin": [], "glassdoor": [], "indeed": [],
          "hirist": [], "naukri": [], "foundit": [],
          "apna": [], "shine": [], "all": []}


def _parse_locations(req):
    """Extract location list from request form/json whether sent as 'locations' list, 'city', or 'location'."""
    locs = req.form.getlist("locations")
    if not locs:
        city_str = req.form.get("city") or req.form.get("location") or ""
        if city_str:
            locs = [c.strip() for c in city_str.split(",") if c.strip()]

    cleaned = []
    for l in locs:
        for part in str(l).split(","):
            part_clean = part.strip()
            if part_clean and part_clean not in cleaned:
                cleaned.append(part_clean)
    return cleaned


@app.route("/")
def home():
    return render_template("landing.html")


@app.route("/favicon.ico")
def favicon():
    return send_file(
        os.path.join(app.static_folder, "favicon.png"),
        mimetype="image/png",
    )


@app.route("/linkedin")
def linkedin_page():
    return render_template("linkedin.html")


@app.route("/glassdoor")
def glassdoor_page():
    return render_template("glassdoor.html", cities=list(GLASSDOOR_CITIES.keys()))


@app.route("/indeed")
def indeed_page():
    return render_template("indeed.html", cities=list(INDEED_CITIES.keys()))


@app.route("/hirist")
def hirist_page():
    return render_template(
        "hirist.html",
        categories=HIRIST_CATEGORIES,
        cities=list(HIRIST_CITIES.keys()),
        experiences=list(HIRIST_EXPERIENCE.keys()),
    )


@app.route("/naukri")
def naukri_page():
    return render_template("naukri.html", cities=list(NAUKRI_CITIES.keys()))


@app.route("/foundit")
def foundit_page():
    return render_template("foundit.html", cities=list(FOUNDIT_CITIES.keys()))


@app.route("/apna")
def apna_page():
    return render_template("apna.html", cities=list(APNA_CITIES.keys()))


@app.route("/shine")
def shine_page():
    return render_template(
        "shine.html",
        cities=list(SHINE_CITIES.keys()),
        experiences=SHINE_EXPERIENCE,
    )


@app.route("/search/linkedin", methods=["POST"])
def search_linkedin():
    try:
        role        = request.form.get("role", "").strip()
        time_filter = int(request.form.get("time_filter", 86400))
        limit       = int(request.form.get("limit", 10))
        apply_mode  = request.form.get("apply_mode", "include_easy").strip().lower()
        locations   = _parse_locations(request)
        experience  = request.form.get("experience", "").strip()

        if not role:
            return jsonify({"error": "Please enter a job role"}), 400
        if not locations:
            return jsonify({"error": "Select at least one location"}), 400
        if apply_mode not in {"include_easy", "only_easy", "only_external"}:
            return jsonify({"error": "Invalid apply filter selected"}), 400
        if experience:
            allowed_levels = {"1", "2", "3", "4", "5", "6"}
            for part in experience.split(","):
                if part.strip() not in allowed_levels:
                    return jsonify({"error": "Invalid experience level filter selected"}), 400

        jobs = scrape_linkedin(
            role=role,
            time_filter=time_filter,
            limit=limit,
            locations=locations,
            apply_mode=apply_mode,
            experience=experience,
        )
        latest["linkedin"] = jobs
        return jsonify({"jobs": jobs, "count": len(jobs), "requested": limit})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/search/glassdoor", methods=["POST"])
def search_glassdoor():
    try:
        role        = request.form.get("role", "").strip()
        from_age    = int(request.form.get("from_age", 1))
        limit       = int(request.form.get("limit", 10))
        apply_mode  = request.form.get("apply_mode", "include_easy").strip().lower()
        locations   = _parse_locations(request)
        experience  = request.form.get("experience", "").strip()

        if not role:
            return jsonify({"error": "Please enter a job role"}), 400
        if not locations:
            return jsonify({"error": "Select at least one location"}), 400
        if apply_mode not in {"include_easy", "only_easy", "only_external"}:
            return jsonify({"error": "Invalid apply filter selected"}), 400

        jobs = scrape_glassdoor(
            role=role,
            from_age_days=from_age,
            limit=limit,
            locations=locations,
            apply_mode=apply_mode,
            experience=experience or None,
        )
        latest["glassdoor"] = jobs
        return jsonify({"jobs": jobs, "count": len(jobs), "requested": limit})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/search/indeed", methods=["POST"])
def search_indeed():
    try:
        role        = request.form.get("role", "").strip()
        fromage     = int(request.form.get("fromage", 1))
        limit       = int(request.form.get("limit", 10))
        apply_mode  = request.form.get("apply_mode", "include_easy").strip().lower()
        locations   = _parse_locations(request)
        experience  = request.form.get("experience", "").strip()

        if not role:
            return jsonify({"error": "Please enter a job role"}), 400
        if not locations:
            return jsonify({"error": "Select at least one location"}), 400
        if apply_mode not in {"include_easy", "only_easy", "only_external"}:
            return jsonify({"error": "Invalid apply filter selected"}), 400

        jobs = scrape_indeed(
            role=role,
            fromage_days=fromage,
            limit=limit,
            locations=locations,
            apply_mode=apply_mode,
            experience=experience or None,
        )
        latest["indeed"] = jobs
        return jsonify({"jobs": jobs, "count": len(jobs), "requested": limit})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/search/hirist", methods=["POST"])
def search_hirist():
    try:
        role           = request.form.get("role", "").strip()  # category slug
        locations      = _parse_locations(request)
        experience_key = request.form.get("experience", "").strip()
        posting        = int(request.form.get("posting", 3))
        limit          = int(request.form.get("limit", 10))

        hirist_map = {
            "fresher": (0, 1),
            "0-1": (0, 1),
            "0-6m": (0, 0),
            "internship": (0, 0),
            "1-2": (1, 2),
            "1-3": (1, 3),
            "3-5": (3, 5),
            "5-7": (5, 7),
            "7-10": (7, 10),
            "10+": (10, 30),
        }
        min_exp, max_exp = hirist_map.get(experience_key, (0, 30))

        if not role:
            return jsonify({"error": "Please select a job category"}), 400
        if not locations:
            return jsonify({"error": "Please select at least one location"}), 400
        if role not in HIRIST_CATEGORIES:
            return jsonify({"error": "Unknown category"}), 400

        jobs = scrape_hirist(
            category=role,
            city=locations,
            min_exp=min_exp,
            max_exp=max_exp,
            posting_days=posting,
            limit=limit,
        )
        latest["hirist"] = jobs
        return jsonify({"jobs": jobs, "count": len(jobs), "requested": limit})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/search/naukri", methods=["POST"])
def search_naukri():
    try:
        role           = request.form.get("role", "").strip()
        locations      = _parse_locations(request)
        job_age        = int(request.form.get("job_age", 7))
        limit          = int(request.form.get("limit", 10))
        experience_key = request.form.get("experience", "").strip()

        naukri_map = {
            "fresher": 0,
            "0-1": 0,
            "0-6m": 0,
            "internship": 0,
            "1-2": 1,
            "1-3": 1,
            "3-5": 3,
            "5-7": 5,
            "7-10": 7,
            "10+": 10,
        }
        experience = naukri_map.get(experience_key, None)

        if not role:
            return jsonify({"error": "Please enter a job role"}), 400
        if not locations:
            return jsonify({"error": "Please select at least one location"}), 400

        jobs = scrape_naukri(
            role=role, city=locations, job_age_days=job_age,
            limit=limit, experience=experience,
        )
        latest["naukri"] = jobs
        return jsonify({"jobs": jobs, "count": len(jobs), "requested": limit})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/search/foundit", methods=["POST"])
def search_foundit():
    try:
        role           = request.form.get("role", "").strip()
        locations      = _parse_locations(request)
        freshness      = int(request.form.get("freshness", 7))
        limit          = int(request.form.get("limit", 10))
        experience_key = request.form.get("experience", "").strip()

        foundit_map = {
            "fresher": (0, 1),
            "0-1": (0, 1),
            "0-6m": (0, 0),
            "internship": (0, 0),
            "1-2": (1, 2),
            "1-3": (1, 3),
            "3-5": (3, 5),
            "5-7": (5, 7),
            "7-10": (7, 10),
            "10+": (10, 30),
        }
        min_exp, max_exp = foundit_map.get(experience_key, (None, None))

        if not role:
            return jsonify({"error": "Please enter a job role"}), 400
        if not locations:
            return jsonify({"error": "Please select at least one location"}), 400

        jobs = scrape_foundit(
            role=role, city=locations, job_freshness_days=freshness,
            limit=limit, min_experience=min_exp, max_experience=max_exp,
        )
        latest["foundit"] = jobs
        return jsonify({"jobs": jobs, "count": len(jobs), "requested": limit})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/search/apna", methods=["POST"])
def search_apna():
    try:
        role           = request.form.get("role", "").strip()
        locations      = _parse_locations(request)
        posted_in      = int(request.form.get("posted_in", 0))
        limit          = int(request.form.get("limit", 10))
        experience_key = request.form.get("experience", "").strip()

        apna_map = {
            "fresher": (0, 1),
            "0-1": (0, 1),
            "0-6m": (0, 0),
            "internship": (0, 0),
            "1-2": (1, 2),
            "1-3": (1, 3),
            "3-5": (3, 5),
            "5-7": (5, 7),
            "7-10": (7, 10),
            "10+": (10, 30),
        }
        min_exp, max_exp = apna_map.get(experience_key, (None, None))

        if not role:
            return jsonify({"error": "Please enter a job role"}), 400
        if not locations:
            return jsonify({"error": "Please select at least one location"}), 400

        jobs = scrape_apna(
            role=role, city=locations, posted_in_days=posted_in,
            limit=limit, min_experience=min_exp, max_experience=max_exp,
        )
        latest["apna"] = jobs
        return jsonify({"jobs": jobs, "count": len(jobs), "requested": limit})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/search/shine", methods=["POST"])
def search_shine():
    try:
        role           = request.form.get("role", "").strip()
        locations      = _parse_locations(request)
        posting_days   = int(request.form.get("posting_days", 0))
        limit          = int(request.form.get("limit", 10))
        experience_key = request.form.get("experience", "").strip()

        shine_map = {
            "fresher": ["1"],
            "0-1": ["1"],
            "0-6m": ["1"],
            "internship": ["1"],
            "1-2": ["1", "2"],
            "1-3": ["1", "2", "3"],
            "3-5": ["3", "4"],
            "5-7": ["4", "5"],
            "7-10": ["5", "6"],
            "10+": ["6", "7"],
        }
        fexp = shine_map.get(experience_key, [])

        if not role:
            return jsonify({"error": "Please enter a job role"}), 400
        if not locations:
            return jsonify({"error": "Please select at least one location"}), 400
        for v in fexp:
            if v not in SHINE_EXPERIENCE:
                return jsonify({"error": f"Unknown experience band: {v}"}), 400

        jobs = scrape_shine(
            role=role, city=locations, fexp=fexp,
            posting_days=posting_days, limit=limit,
        )
        latest["shine"] = jobs
        return jsonify({"jobs": jobs, "count": len(jobs), "requested": limit})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/export/<source>/<fmt>")
def export_results(source, fmt):
    source = source.lower()
    if source not in latest:
        abort(404)
    data = latest[source]
    if not data:
        return "No data. Run a search first.", 400

    import pandas as pd
    import os
    from datetime import datetime

    df = pd.DataFrame(data)
    source_name = {"linkedin": "LinkedIn", "glassdoor": "Glassdoor",
                   "indeed": "Indeed", "hirist": "Hirist",
                   "naukri": "Naukri", "foundit": "Foundit",
                   "apna": "Apna", "shine": "Shine"}.get(source, source.capitalize())
    df["Source"] = source_name

    df.rename(columns={"Company": "Company Name"}, inplace=True)
    column_order = ["Link", "Company Name", "Job Title", "Location", "Source",
                    "Posted", "Experience", "Workplace", "Seniority", "Rating",
                    "Salary", "Skills", "Industry", "Description", "Source ATS",
                    "Easy Apply", "Apply Type"]
    df = df[[c for c in column_order if c in df.columns]]

    fmt = fmt.lower()
    if fmt == "csv":
        csv_data = df.to_csv(index=False)
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename=jobs_{source}.csv"}
        )
    elif fmt == "xlsx":
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Jobs')
        output.seek(0)
        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=f"jobs_{source}.xlsx"
        )
    elif fmt == "pdf":
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from io import BytesIO

        output = BytesIO()
        doc = SimpleDocTemplate(
            output,
            pagesize=landscape(letter),
            rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            textColor=colors.HexColor('#0b111e'),
            spaceAfter=10
        )
        
        cell_style = ParagraphStyle(
            'CellStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#131826')
        )
        
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=11,
            textColor=colors.white
        )
        
        link_style = ParagraphStyle(
            'LinkStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=7,
            leading=9,
            textColor=colors.HexColor('#0a66c2')
        )

        story.append(Paragraph(f"Job Search Results — {source_name}", title_style))
        story.append(Paragraph(f"Generated on {datetime.today().strftime('%Y-%m-%d %H:%M:%S')} | Total: {len(df)} jobs", styles['Italic']))
        story.append(Spacer(1, 12))
        
        cols = ['Company Name', 'Job Title', 'Location', 'Posted', 'Link']
        table_data = []
        table_data.append([Paragraph(c, header_style) for c in cols])
        
        for _, row in df.iterrows():
            row_data = []
            for col in cols:
                val = str(row.get(col, '') or '')
                if col == 'Link':
                    short_url = val[:40] + '...' if len(val) > 40 else val
                    row_data.append(Paragraph(f'<a href="{val}" color="#0a66c2"><u>{short_url}</u></a>', link_style))
                else:
                    row_data.append(Paragraph(val, cell_style))
            table_data.append(row_data)
            
        col_widths = [120, 230, 120, 70, 192]
        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0b111e')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dde3ee')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f5f8')]),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ]))
        
        story.append(t)
        doc.build(story)
        output.seek(0)
        return send_file(
            output,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"jobs_{source}.pdf"
        )
    else:
        abort(400)


@app.route("/download/<source>")
def download(source):
    return export_results(source, 'xlsx')


# ==============================================================================
# UNIFIED AGGREGATOR & KANBAN TRACKER ROUTES
# ==============================================================================

@app.route("/unified")
def unified_page():
    return render_template("unified.html")


@app.route("/tracker")
def tracker_page():
    return render_template("tracker.html")


@app.route("/search/all", methods=["POST"])
def search_all():
    try:
        role             = request.form.get("role", "").strip()
        fromage          = int(request.form.get("fromage", 7))
        limit            = int(request.form.get("limit", 20))
        apply_mode       = request.form.get("apply_mode", "include_easy").strip().lower()
        locations        = _parse_locations(request)
        experience       = request.form.get("experience", "").strip()
        portals_str      = request.form.get("portals", "indeed,naukri,glassdoor,foundit,apna,shine,hirist,linkedin")
        
        include_keywords = request.form.get("include_keywords", "").strip()
        exclude_keywords = request.form.get("exclude_keywords", "").strip()
        min_salary       = request.form.get("min_salary", "0").strip()
        workplace_mode   = request.form.get("workplace_mode", "all").strip()
        resume_text      = request.form.get("resume_text", "").strip()

        if not role:
            return jsonify({"error": "Please enter a job role"}), 400
        if not locations:
            return jsonify({"error": "Select at least one location"}), 400

        selected_portals = [p.strip().lower() for p in portals_str.split(",") if p.strip()]

        raw_jobs = search_engine.execute_parallel_search(
            scrapers_map=SCRAPERS_MAP,
            role=role,
            fromage_days=fromage,
            limit=limit,
            locations=locations,
            apply_mode=apply_mode,
            experience=experience or None,
            selected_portals=selected_portals,
        )

        # Cross-platform deduplication
        deduped = search_engine.deduplicate_jobs(raw_jobs)

        # Advanced filtering & match scoring
        final_jobs = search_engine.filter_and_rank_jobs(
            jobs=deduped,
            include_kw=include_keywords,
            exclude_kw=exclude_keywords,
            min_salary=min_salary,
            workplace_mode=workplace_mode,
            resume_text=resume_text,
        )

        latest["all"] = final_jobs
        return jsonify({
            "jobs": final_jobs,
            "count": len(final_jobs),
            "raw_total": len(raw_jobs),
            "duplicates_removed": len(raw_jobs) - len(deduped),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/saved_jobs", methods=["GET", "POST"])
def saved_jobs_api():
    if request.method == "GET":
        jobs = tracker_db.get_all_saved_jobs()
        return jsonify(jobs)
    elif request.method == "POST":
        job_data = request.json or request.form.to_dict()
        if not job_data:
            return jsonify({"error": "No job data provided"}), 400
        job_id, is_new = tracker_db.save_job(job_data)
        msg = "Saved to Kanban Tracker!" if is_new else "Already in Kanban Tracker!"
        return jsonify({"success": True, "id": job_id, "is_new": is_new, "message": msg})


@app.route("/api/saved_jobs/<int:job_id>", methods=["PUT", "DELETE"])
def saved_job_detail_api(job_id):
    if request.method == "PUT":
        data = request.json or {}
        status = data.get("status")
        notes = data.get("notes")
        cover_letter = data.get("cover_letter")
        tracker_db.update_job_status(job_id, status=status, notes=notes, cover_letter=cover_letter)
        return jsonify({"success": True})
    elif request.method == "DELETE":
        tracker_db.delete_saved_job(job_id)
        return jsonify({"success": True})


@app.route("/api/generate_cover_letter", methods=["POST"])
def generate_cover_letter_api():
    try:
        data = request.json or {}
        job = data.get("job") or {}
        resume_text = data.get("resume_text", "")
        letter = search_engine.generate_cover_letter_text(job, resume_text)
        return jsonify({"success": True, "cover_letter": letter})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  JobRadar Codebase Watermarked for Rajpal Singh Tanwar")
    print("="*60 + "\n")
    app.run(debug=True, use_reloader=False)
