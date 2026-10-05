#!/usr/bin/env bash
# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# Job Radar & Recruiter Radar — Render Native Python Build Script
# ==============================================================================

# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "==> [1/3] Upgrading pip, setuptools, wheel..."
pip install --upgrade pip setuptools wheel

echo "==> [2/3] Installing application dependencies from requirements.txt..."
pip install -r requirements.txt

echo "==> [3/3] Installing Playwright Chromium browser and system dependencies..."
playwright install --with-deps chromium

echo "==> Build complete successfully!"
