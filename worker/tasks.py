import os
import smtplib
from email.message import EmailMessage

from celery import Celery

# ----------------------------------------------------------------------
# Celery wiring
# ----------------------------------------------------------------------
app = Celery(
    "tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1"),
)

# ----------------------------------------------------------------------
# Task: send formal HTML enrolment e-mail
# ----------------------------------------------------------------------

@app.task(name="send_course_enrollment_email")
def send_course_enrollment_email(course_name: str, user_id: int, email: str):
    # ── SMTP settings ────────────────────────────────────────────────
    host        = os.getenv("SMTP_HOST", "mailhog")
    port        = int(os.getenv("SMTP_PORT", 1025))
    user        = os.getenv("SMTP_USER")
    pwd         = os.getenv("SMTP_PASSWORD")
    use_tls     = os.getenv("SMTP_USE_TLS", "false").lower() == "true"
    from_email  = os.getenv("FROM_EMAIL", "noreply@example.com")

    # ── WhatsApp / phone number pulled from ENV ──────────────────────
    contact_no  = os.getenv("CONTACT_NUMBER", "+0000000000")

    # ── Build the message ────────────────────────────────────────────
    msg = EmailMessage()
    msg["Subject"] = f"Payment Received – Enrollment Confirmed ({course_name})"
    msg["From"]    = from_email
    msg["To"]      = email

    # 1️⃣ Plain-text fall-back
    plain = f"""\
Hello Sir/Mam,

We hope you are doing well. We have successfully received your payment for "{course_name}" and you have been successfully enrolled.
We will assist you in addition to the necessary community and networks regarding the course. We will also guide you through the process of administrative assistance.
For this you are requested to contact us using the number below.

Contact us at: {contact_no} (WhatsApp)

Learner ID: {user_id}

Best regards,
The Course Team
"""

    # 2️⃣ HTML body
    html = f"""\
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"></head>
<body style="font-family:Arial,Helvetica,sans-serif;line-height:1.55;color:#333;">
  <p>Hello&nbsp;Sir/Mam,</p>

  <p>
    We hope you are doing well. We have <strong>successfully received your payment</strong> for
    “<span style="background:#f3f3f3;padding:2px 4px;border-radius:4px;">{course_name}</span>”
    and <strong>you have been successfully enrolled</strong>.
  </p>

  <p>
    We will assist you in joining the necessary community and networks for this course and guide you
    through any administrative processes.
  </p>

  <p>
    For assistance, please contact us via WhatsApp:&nbsp;
    <a href="https://wa.me/{contact_no.lstrip('+')}"
       style="color:#1a73e8;text-decoration:none;">{contact_no}</a>
  </p>

  <p style="margin-top:2em;">
    Learner&nbsp;ID:&nbsp;{user_id}
  </p>

  <p style="margin-top:2.5em;">
    Best regards,<br>
    The&nbsp;Course&nbsp;Team
  </p>
</body>
</html>
"""
    msg.set_content(plain)
    msg.add_alternative(html, subtype="html")

    # ── Send ─────────────────────────────────────────────────────────
    smtp_cls = smtplib.SMTP_SSL if port == 465 else smtplib.SMTP
    with smtp_cls(host, port, timeout=10) as server:
        if use_tls and port != 465:
            server.starttls()
        if user and pwd:
            server.login(user, pwd)
        server.send_message(msg)

    return f"E-mail dispatched to {email} for course “{course_name}” (user_id={user_id})"
