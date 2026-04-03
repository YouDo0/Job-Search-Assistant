from datetime import datetime
import json
from .. import db
from ..models import Job, ScrapingLog, UserPreference, CompanyCareerPage
from .celery_app import celery_app
from ..scrapers import (
    LinkedInScraper, JobStreetScraper, IndeedScraper,
    GlintsScraper, KalibrrScraper, CareerPageScraper
)

def get_preferences():
    prefs = UserPreference.query.all()
    result = {}
    for p in prefs:
        try:
            result[p.key] = json.loads(p.value)
        except:
            result[p.key] = p.value
    return result

@celery_app.task
def run_all_scrapers():
    prefs = get_preferences()
    keywords = prefs.get('job_titles', ['Data Analyst', 'Business Analyst'])
    location = prefs.get('location', '')

    scrapers = {
        'linkedin': LinkedInScraper(prefs),
        'jobstreet': JobStreetScraper(prefs),
        'indeed': IndeedScraper(prefs),
        'glints': GlintsScraper(prefs),
        'kalibrr': KalibrrScraper(prefs),
    }

    track_b_urls = {c.company_name: c.career_url for c in CompanyCareerPage.query.filter_by(is_active=True).all()}
    scrapers['career_pages'] = CareerPageScraper(prefs, track_b_urls)

    total_new_jobs = 0
    total_found = 0

    for source_name, scraper in scrapers.items():
        log = ScrapingLog(source=source_name, status='running', started_at=datetime.utcnow())
        db.session.add(log)
        db.session.commit()

        try:
            jobs_data = scraper.search(keywords, location)
            total_found += len(jobs_data)
            new_count = 0

            for job_data in jobs_data:
                existing = Job.query.filter_by(external_id=job_data['external_id']).first()
                if not existing:
                    job = Job(**job_data)
                    db.session.add(job)
                    new_count += 1

            log.status = 'success'
            log.jobs_found = len(jobs_data)
            log.completed_at = datetime.utcnow()
            total_new_jobs += new_count

        except Exception as e:
            log.status = 'failed'
            log.error_message = str(e)
            log.completed_at = datetime.utcnow()

        db.session.commit()

    return {'total_found': total_found, 'new_jobs': total_new_jobs}

@celery_app.task
def scrape_single_source(source: str):
    prefs = get_preferences()
    keywords = prefs.get('job_titles', ['Data Analyst', 'Business Analyst'])
    location = prefs.get('location', '')

    scraper_map = {
        'linkedin': LinkedInScraper(prefs),
        'jobstreet': JobStreetScraper(prefs),
        'indeed': IndeedScraper(prefs),
        'glints': GlintsScraper(prefs),
        'kalibrr': KalibrrScraper(prefs),
    }

    scraper = scraper_map.get(source)
    if not scraper:
        return {'error': f'Unknown source: {source}'}

    jobs_data = scraper.search(keywords, location)
    new_count = 0

    for job_data in jobs_data:
        existing = Job.query.filter_by(external_id=job_data['external_id']).first()
        if not existing:
            job = Job(**job_data)
            db.session.add(job)
            new_count += 1

    db.session.commit()
    return {'found': len(jobs_data), 'new': new_count}
