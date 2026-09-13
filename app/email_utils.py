"""SMTP email sending, used by the Email Tool."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import settings


def send_email(to_email: str, subject: str, body: str) -> tuple[bool, str]:
    """
    Send a plain-text email. Returns (success, message).
    Never raises — booking flow must succeed even if email delivery fails.
    """
    if not settings.EMAIL_ENABLED:
        return False, "Email sending is disabled (EMAIL_ENABLED=false)."

    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        return False, "SMTP credentials are not configured."

    try:
        msg = MIMEMultipart()
        msg["From"] = settings.EMAIL_FROM or settings.SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(msg["From"], [to_email], msg.as_string())

        return True, "Email sent."
    except Exception as exc:
        return False, f"Email delivery failed: {exc}"
