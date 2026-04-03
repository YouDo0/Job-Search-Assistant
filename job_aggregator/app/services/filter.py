import json
from ..models import UserPreference

def get_preferences():
    prefs = {}
    for p in UserPreference.query.all():
        try:
            prefs[p.key] = json.loads(p.value)
        except:
            prefs[p.key] = p.value
    return prefs

def should_include_job(job, prefs: dict) -> tuple:
    seniority = prefs.get('seniority', '')
    if seniority:
        job_seniority = job.seniority or 'mid'
        if seniority == 'entry' and job_seniority not in ['entry', 'mid']:
            return False, f"Seniority mismatch: wanted {seniority}, got {job_seniority}"
        elif seniority == 'mid' and job_seniority == 'senior':
            return False, f"Seniority mismatch: wanted {seniority}, got {job_seniority}"

    location = prefs.get('location', '')
    if location and job.location:
        if location.lower() not in job.location.lower():
            return False, f"Location mismatch: wanted {location}, got {job.location}"

    excluded = prefs.get('excluded_companies', [])
    if excluded and job.company:
        if any(exc.lower() in job.company.lower() for exc in excluded):
            return False, f"Company excluded: {job.company}"

    return True, "Passed filters"

def filter_jobs(jobs, prefs: dict = None) -> tuple:
    if prefs is None:
        prefs = get_preferences()

    included = []
    excluded = []

    for job in jobs:
        include, reason = should_include_job(job, prefs)
        if include:
            included.append(job)
        else:
            excluded.append((job, reason))

    return included, excluded
