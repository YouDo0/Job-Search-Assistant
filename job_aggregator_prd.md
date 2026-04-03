# Job Aggregator & Notifier — Product Requirements Document

**Status:** Draft
**Owner:** You
**Version:** 0.1
**Last updated:** March 2026

---

## Overview

A personal job aggregator that runs 24/7 on a VPS, pulling listings from public job portals (LinkedIn, JobStreet, Indeed) and monitoring career pages of individual companies. It filters jobs by user preferences, learns from application history, and sends a daily email digest with clickable apply links.

---

## Problem & Goals

### Problem

Manually checking multiple job portals and individual company career pages is time-consuming. Opportunities from companies with their own portals (e.g. BCA, Mandiri, Deloitte) are easy to miss. There is no single place that surfaces all relevant openings based on personal fit.

### Goals

1. Aggregate jobs from public portals and company-owned career pages in one system.
2. Filter results based on configurable personal preferences.
3. Learn from application history to improve relevance over time.
4. Deliver a single daily email digest with apply links.

---

## Data Sources

### Track A

Public job portals — LinkedIn, JobStreet, Indeed, Glints, Kalibrr

*Scraped or via official API where available*

### Track B

Company-owned career pages — BCA, Bank Mandiri, Bank BRI, PwC, Deloitte, KPMG, Barito Pacific, and others discovered automatically

*Monitored separately; discovered when their name appears in Track A listings*

---

## User Preferences (Configurable)

| Preference | Current Value | Notes |
|------------|---------------|-------|
| Job titles / keywords | e.g. Data Analyst, Business Analyst, Finance | Match against title and description |
| Seniority level | Entry level / Fresh graduate | Filter out mid/senior roles |
| Location | All locations (no restriction) | Can be narrowed later |
| Salary band | No restriction | Can be narrowed later |
| Excluded companies | None yet | Blacklist to stop repeated noise |

All preferences editable via a simple settings UI or config file at any time.

---

## Smart Learning System

### Input

User marks each job in the digest as: ✅ Applied, ❌ Not Interested, or leaves it unmarked (undecided)

### Output

System builds a profile of preferred job titles, required skills, company types, and industries from marked history

### Effect

Future digests surface more jobs similar to "Applied" ones and fewer matching "Not Interested" patterns — even if not explicitly in the preference settings

### Approach

Start with rule-based filtering (keyword matching, preferred companies, seniority) — ML can be added later once enough feedback history is collected.

### Discovery

When a company appears in a public portal listing, system auto-checks if they have a dedicated career page and adds it to Track B monitoring

---

## Notification & Delivery

### Channel

Email

### Schedule

Twice daily at 11:00 AM and 2:30 PM (local timezone) — times configurable

### Format

Consolidated digest — job title, company name, source portal, brief description snippet, direct apply link, and three feedback buttons (Applied / Not Interested / Skip) — each button is a clickable URL that opens the web app to record your response

---

## Infrastructure

### Hosting

Personal VPS — runs 24/7, no dependency on local machine being online

### Settings UI

Simple web-based settings panel or CLI to update preferences, schedule, email, and company watchlist at any time

---

## Feature Backlog

| Feature | Priority | Notes |
|---------|----------|-------|
| Public portal scraping (LinkedIn, JobStreet, Indeed) | **High** | Core MVP |
| Company career page monitoring (Track B) | **High** | Core MVP |
| Preference filtering (title, level, location, salary) | **High** | Core MVP |
| Daily email digest with apply links | **High** | Core MVP |
| Feedback buttons (Applied / Not Interested / Skip) | **High** | Needed for learning to work |
| Auto-discovery of company career pages | **Medium** | Smart expansion of Track B |
| Learning from application history | **Medium** | Improves relevance over time |
| Settings panel / config UI | **Medium** | Web UI or CLI |
| Duplicate job detection | **Low** | Same job appearing on multiple portals |
| Multi-channel notifications (WhatsApp, Telegram) | **Low** | Future enhancement |

---

## Open Questions

1. Which job portals have official APIs vs require scraping?
2. How to handle anti-scraping measures on public portals?
3. What tech stack — Python (BeautifulSoup / Playwright) for scraping, Celery or cron for scheduling?
4. Where to store job history and user feedback — SQLite, PostgreSQL?
5. How to structure the email template for feedback buttons to work simply?

---

*All fields above are editable in the source HTML version.*
