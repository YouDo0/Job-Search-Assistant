from datetime import datetime
from . import db

class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(255), unique=True)
    source = db.Column(db.String(50))
    source_url = db.Column(db.Text)
    title = db.Column(db.String(255))
    company = db.Column(db.String(255))
    location = db.Column(db.String(255))
    description = db.Column(db.Text)
    seniority = db.Column(db.String(50))
    salary_min = db.Column(db.Integer, nullable=True)
    salary_max = db.Column(db.Integer, nullable=True)
    posted_date = db.Column(db.Date, nullable=True)
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    feedback = db.relationship('Feedback', backref='job', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'external_id': self.external_id,
            'source': self.source,
            'source_url': self.source_url,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'description': self.description[:200] + '...' if self.description and len(self.description) > 200 else self.description,
            'seniority': self.seniority,
            'salary': f"{self.salary_min}-{self.salary_max}" if self.salary_min and self.salary_max else None,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'feedback_status': self.feedback[0].status if self.feedback else None
        }


class UserPreference(db.Model):
    __tablename__ = 'user_preferences'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True)
    value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get(key, default=None):
        pref = UserPreference.query.filter_by(key=key).first()
        return pref.value if pref else default

    @staticmethod
    def set(key, value):
        import json
        pref = UserPreference.query.filter_by(key=key).first()
        if pref:
            pref.value = json.dumps(value) if not isinstance(value, str) else value
        else:
            pref = UserPreference(key=key, value=json.dumps(value) if not isinstance(value, str) else value)
            db.session.add(pref)
        db.session.commit()


class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    status = db.Column(db.String(20))
    feedback_at = db.Column(db.DateTime, default=datetime.utcnow)


class CompanyCareerPage(db.Model):
    __tablename__ = 'company_career_pages'

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255))
    career_url = db.Column(db.Text)
    discovered_from = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    last_scraped = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ScrapingLog(db.Model):
    __tablename__ = 'scraping_log'

    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(50))
    status = db.Column(db.String(20))
    jobs_found = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text, nullable=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
