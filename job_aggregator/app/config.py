import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///jobtracker.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USER = os.getenv('EMAIL_USER', '')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
    EMAIL_FROM = os.getenv('EMAIL_FROM', '')

    SCRAPE_INTERVAL_HOURS = int(os.getenv('SCRAPE_INTERVAL_HOURS', 6))
    DIGEST_SCHEDULE = os.getenv('DIGEST_SCHEDULE', '{"11:00": "Asia/Jakarta", "14:30": "Asia/Jakarta"}')
