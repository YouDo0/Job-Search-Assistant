# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a **Job Aggregator & Notifier** system that runs on a VPS. It scrapes job listings from public portals and company career pages, filters based on user preferences, learns from feedback, and sends daily email digests.

## Repository Structure

```
job_aggregator/           # Main project directory
├── app/
│   ├── __init__.py       # Flask app factory with SQLAlchemy
│   ├── models.py         # Database models (Job, UserPreference, Feedback, etc.)
│   ├── routes/           # Flask blueprints
│   │   ├── jobs.py       # Job listing dashboard
│   │   ├── feedback.py   # Feedback recording endpoints
│   │   └── settings.py   # User preferences API
│   ├── scrapers/         # Track A & B scrapers
│   │   ├── base.py       # BaseScraper class
│   │   ├── linkedin.py
│   │   ├── jobstreet.py
│   │   ├── indeed.py
│   │   ├── glints.py
│   │   ├── kalibrr.py
│   │   └── career_pages.py  # Track B scraper
│   ├── services/
│   │   ├── filter.py     # Rule-based job filtering
│   │   ├── learning.py   # Feedback-based learning (rule-based → ML later)
│   │   └── email_service.py
│   ├── tasks/            # Celery tasks
│   │   ├── celery_app.py
│   │   ├── scraper_tasks.py
│   │   └── email_tasks.py
│   └── templates/         # HTML templates
│       ├── base.html
│       ├── index.html    # Dashboard
│       └── settings.html
├── config.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── run.py
```

## Current State

The system is implemented with:

- **Track A scrapers**: LinkedIn, JobStreet, Indeed, Glints, Kalibbr
- **Track B scraper**: Generic career page scraper for BCA, Mandiri, BRI, PwC, Deloitte, KPMG, Barito Pacific
- **Learning system**: Rule-based filtering (ML to be added later after feedback history accumulates)
- **Email digest**: Twice daily at 11:00 AM and 2:30 PM with clickable feedback buttons (URL-based)
- **Infrastructure**: PostgreSQL + Redis/Celery + Flask + Docker

## Tech Stack

- **Web**: Flask 3.0 with Flask-SQLAlchemy
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Task Queue**: Celery with Redis broker
- **Scraping**: BeautifulSoup4 + requests
- **Deployment**: Docker + Docker Compose

## Getting Started

1. Copy `.env.example` to `.env` and fill in credentials
2. Run `docker-compose up` to start all services
3. Access web UI at `http://localhost:5000`
4. Configure preferences at `/settings/`
5. Celery worker handles periodic scraping and email digests

## Key Design Decisions

- Feedback buttons in emails are **clickable URLs** to the web app (not mailto links)
- Rule-based filtering runs before ML-based learning
- Scraping runs every 6 hours; digest checks schedule config at runtime
- No authentication (single user, local access only)
