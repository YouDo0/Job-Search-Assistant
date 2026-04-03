import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import Config

def send_email(to: str, subject: str, html_body: str) -> bool:
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = Config.EMAIL_FROM
    msg['To'] = to

    part = MIMEText(html_body, 'html')
    msg.attach(part)

    try:
        with smtplib.SMTP(Config.EMAIL_HOST, Config.EMAIL_PORT) as server:
            server.starttls()
            server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Email send error: {e}")
        return False
