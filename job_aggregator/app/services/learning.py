import json
from collections import defaultdict
from ..models import Job, Feedback, UserPreference
from .. import db

SKILL_KEYWORDS = [
    'python', 'sql', 'excel', 'tableau', 'power bi', 'data visualization',
    'statistics', 'machine learning', 'ml', 'ai', 'nlp', 'deep learning',
    'communication', 'presentation', 'reporting', 'analysis', 'analytics',
    'etl', 'database', 'spark', 'hadoop', 'aws', 'cloud'
]

INDUSTRY_KEYWORDS = [
    'banking', 'finance', 'fintech', 'consulting', 'technology', 'tech',
    'e-commerce', 'retail', 'manufacturing', 'oil', 'gas', 'energy',
    'telecommunications', 'telecom', 'media', 'healthcare', 'pharma'
]

def learn_from_feedback():
    applied_jobs = Job.query.join(Feedback).filter(Feedback.status == 'applied').all()
    not_interested_jobs = Job.query.join(Feedback).filter(Feedback.status == 'not_interested').all()

    if not applied_jobs:
        return {'status': 'no_data', 'message': 'Need at least 5 applied jobs to learn'}

    applied_titles = [j.title.lower() for j in applied_jobs]
    applied_companies = [j.company.lower() for j in applied_jobs if j.company]
    ni_companies = [j.company.lower() for j in not_interested_jobs if j.company]

    preferred_companies = set(applied_companies) - set(ni_companies)

    skill_counts = defaultdict(int)
    for job in applied_jobs:
        if job.description:
            desc_lower = job.description.lower()
            for skill in SKILL_KEYWORDS:
                if skill.lower() in desc_lower:
                    skill_counts[skill] += 1

    top_skills = [skill for skill, count in sorted(skill_counts.items(), key=lambda x: -x[1]) if count >= 2]

    industry_counts = defaultdict(int)
    for job in applied_jobs:
        text = (job.title + ' ' + (job.description or '') + ' ' + (job.company or '')).lower()
        for industry in INDUSTRY_KEYWORDS:
            if industry.lower() in text:
                industry_counts[industry] += 1

    top_industries = [ind for ind, count in sorted(industry_counts.items(), key=lambda x: -x[1]) if count >= 2]

    learned = {
        'preferred_companies': list(preferred_companies)[:20],
        'preferred_skills': top_skills[:15],
        'preferred_industries': top_industries[:10],
        'applied_count': len(applied_jobs),
        'not_interested_count': len(not_interested_jobs)
    }

    pref = UserPreference.query.filter_by(key='learned_preferences').first()
    if pref:
        pref.value = json.dumps(learned)
    else:
        pref = UserPreference(key='learned_preferences', value=json.dumps(learned))
        db.session.add(pref)

    db.session.commit()
    return learned

def score_job_for_user(job: Job, learned_prefs: dict) -> float:
    if not learned_prefs:
        return 0.5

    score = 0.5
    text = (job.title + ' ' + (job.description or '') + ' ' + (job.company or '')).lower()

    for company in learned_prefs.get('preferred_companies', []):
        if company.lower() in job.company.lower():
            score += 0.2
            break

    for skill in learned_prefs.get('preferred_skills', []):
        if skill.lower() in text:
            score += 0.1

    return min(score, 1.0)
