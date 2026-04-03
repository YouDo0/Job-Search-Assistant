from datetime import datetime
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import Config
from ..models import Job, UserPreference, Feedback
from .celery_app import celery_app

def should_send_digest():
    schedule_json = Config.DIGEST_SCHEDULE
    try:
        schedule = json.loads(schedule_json)
    except:
        return False

    now = datetime.now()
    current_time_str = now.strftime('%H:%M')

    for target_time, timezone in schedule.items():
        if current_time_str == target_time:
            return True
    return False

def get_filtered_jobs_for_digest():
    prefs = {}
    for p in UserPreference.query.all():
        try:
            prefs[p.key] = json.loads(p.value)
        except:
            prefs[p.key] = p.value

    yesterday = datetime.utcnow()

    query = Job.query.filter(Job.is_active == True, Job.scraped_at >= yesterday)

    jobs = []
    for job in query.all():
        if job.feedback:
            if job.feedback[0].status == 'applied':
                jobs.append(job)
        else:
            jobs.append(job)

    return jobs

def build_digest_email(jobs: list, base_url: str = 'http://localhost:5000') -> str:
    html = """
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
        <h1 style="color: #2c3e50;">Job Digest</h1>
        <p style="color: #666;">Here's your curated list of jobs scraped in the last 24 hours.</p>
    """

    for job in jobs:
        applied_url = f"{base_url}/feedback/record?job_id={job.id}&status=applied"
        not_interested_url = f"{base_url}/feedback/record?job_id={job.id}&status=not_interested"
        skip_url = f"{base_url}/feedback/record?job_id={job.id}&status=skip"

        feedback_status = ""
        if job.feedback:
            status = job.feedback[0].status
            feedback_status = f'<span style="color: #888; font-size: 12px;">Your feedback: {status}</span>'

        html += f"""
        <div style="background: #f9f9f9; border-left: 4px solid #3498db; padding: 15px; margin: 15px 0; border-radius: 4px;">
            <h3 style="margin: 0 0 5px 0;">{job.title}</h3>
            <p style="margin: 0; color: #555;"><strong>{job.company}</strong> &middot; {job.location or 'Location N/A'}</p>
            <p style="color: #777; font-size: 14px; margin: 5px 0;">Source: {job.source} {feedback_status}</p>
            <p style="margin: 10px 0;">{job.description[:200]}...</p>
            <div style="margin-top: 10px;">
                <a href="{job.source_url}" style="background: #27ae60; color: white; padding: 8px 15px; text-decoration: none; border-radius: 4px; font-size: 14px; margin-right: 5px;">Apply Now</a>
                <a href="{applied_url}" style="background: #27ae60; color: white; padding: 8px 15px; text-decoration: none; border-radius: 4px; font-size: 14px; margin-right: 5px;">Applied</a>
                <a href="{not_interested_url}" style="background: #e74c3c; color: white; padding: 8px 15px; text-decoration: none; border-radius: 4px; font-size: 14px; margin-right: 5px;">Not Interested</a>
                <a href="{skip_url}" style="background: #95a5a6; color: white; padding: 8px 15px; text-decoration: none; border-radius: 4px; font-size: 14px;">Skip</a>
            </div>
        </div>
        """

    if not jobs:
        html += "<p style='color: #888;'>No new jobs found in the last 24 hours.</p>"

    html += """
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        <p style="color: #aaa; font-size: 12px;">
            This email was sent by your Job Aggregator & Notifier system.<br>
            Feedback buttons above open the web app to record your response.
        </p>
    </body>
    </html>
    """
    return html

@celery_app.task
def send_digest():
    if not should_send_digest():
        return {'skipped': True, 'reason': 'Not scheduled time'}

    jobs = get_filtered_jobs_for_digest()

    if not jobs:
        return {'skipped': True, 'reason': 'No new jobs'}

    email_body = build_digest_email(jobs)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'Job Digest - {datetime.now().strftime("%Y-%m-%d")} ({len(jobs)} jobs)'
    msg['From'] = Config.EMAIL_FROM
    msg['To'] = Config.EMAIL_USER

    part = MIMEText(email_body, 'html')
    msg.attach(part)

    try:
        with smtplib.SMTP(Config.EMAIL_HOST, Config.EMAIL_PORT) as server:
            server.starttls()
            server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
            server.send_message(msg)

        return {'success': True, 'jobs_count': len(jobs)}
    except Exception as e:
        return {'error': str(e)}
