from celery import Celery
from .config import Config

celery_app = Celery(
    'job_aggregator',
    broker=Config.REDIS_URL,
    backend=Config.REDIS_URL,
    include=['app.tasks.scraper_tasks', 'app.tasks.email_tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Jakarta',
    enable_utc=True,
    beat_schedule={
        'scrape-every-6-hours': {
            'task': 'app.tasks.scraper_tasks.run_all_scrapers',
            'schedule': 6 * 60 * 60,
        },
    }
)
