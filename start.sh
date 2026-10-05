#!/usr/bin/env bash
# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# Job Radar & Recruiter Radar — Render Production Start Script
# ==============================================================================

# Bind to Render's dynamic PORT variable or fallback to 10000
TARGET_PORT=${PORT:-10000}

echo "==> Starting Gunicorn on 0.0.0.0:${TARGET_PORT}..."
exec gunicorn --bind 0.0.0.0:${TARGET_PORT} --workers 1 --threads 4 --timeout 180 --worker-class gthread app:app
