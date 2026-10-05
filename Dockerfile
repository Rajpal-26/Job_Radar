# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# Job Radar & Recruiter Radar — Production Container Dockerfile
# ==============================================================================

# Use official Microsoft Playwright Python base image (pre-installed system browser deps)
FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

# Set working directory
WORKDIR /app

# Prevent Python from writing .pyc files & enable unbuffered stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# Install system utilities if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifest first for layer caching
COPY requirements.txt /app/

# Install python dependencies
RUN pip install --no-cache-dir -U pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Ensure Playwright Chromium browser binary is downloaded
RUN playwright install chromium

# Copy full application codebase (backend, frontend, configs)
COPY . /app

# Create persistent storage directories
RUN mkdir -p /app/data

# Expose web server port
EXPOSE 5000

# Run with high-concurrency Gunicorn WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "120", "app:app"]
