import os
import smtplib
from email.message import EmailMessage
from datetime import datetime

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
# Task: send formal enrollment email
# ----------------------------------------------------------------------

@app.task(name="send_course_enrollment_email")
def send_course_enrollment_email(course_name: str, user_id: int, email: str, user_name: str = None):
    # ── SMTP settings ────────────────────────────────────────────────
    host = os.getenv("SMTP_HOST", "mailhog")
    port = int(os.getenv("SMTP_PORT", 1025))
    user = os.getenv("SMTP_USER")
    pwd = os.getenv("SMTP_PASSWORD")
    use_tls = os.getenv("SMTP_USE_TLS", "false").lower() == "true"
    from_email = os.getenv("FROM_EMAIL", "noreply@example.com")
    company_name = os.getenv("COMPANY_NAME", "Poridhi")
    contact_no = os.getenv("CONTACT_NUMBER")
    
    greeting = f"Dear {user_name}," if user_name else "Dear Learner,"
    current_date = datetime.now().strftime("%B %d, %Y")

    # ── Build the message ────────────────────────────────────────────
    msg = EmailMessage()
    msg["Subject"] = f"🎉 Welcome to {course_name} - Enrollment Confirmed!"
    msg["From"] = f"{company_name} <{from_email}>"
    msg["To"] = email

    # Beautiful HTML version
    html = f"""\
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; background: #f8f9fa;">
    
    <!-- Header -->
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0;">
        <h1 style="margin: 0; font-size: 24px;">🎉 Enrollment Confirmed!</h1>
        <p style="margin: 10px 0 0; opacity: 0.9;">Welcome to {company_name}</p>
    </div>
    
    <!-- Content -->
    <div style="background: white; padding: 30px; border-radius: 0 0 8px 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <p style="font-size: 16px; margin-bottom: 20px;">{greeting}</p>
        
        <div style="background: #e8f5e8; border-left: 4px solid #28a745; padding: 15px; margin: 20px 0; border-radius: 4px;">
            <strong style="color: #155724;">✅ Payment Successful - You're now enrolled in "{course_name}"</strong>
        </div>
        
        <!-- Enrollment Details -->
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="color: #333; margin-top: 0;">📋 Your Details</h3>
            <p style="margin: 5px 0;"><strong>Learner ID:</strong> #{user_id}</p>
            <p style="margin: 5px 0;"><strong>Course:</strong> {course_name}</p>
            <p style="margin: 5px 0;"><strong>Date:</strong> {current_date}</p>
            <p style="margin: 5px 0;"><strong>Status:</strong> <span style="color: #28a745;">✅ Active</span></p>
        </div>
        
        <!-- Next Steps -->
        <h3 style="color: #333;">🚀 What's Next?</h3>
        <ol style="padding-left: 20px;">
            <li style="margin: 8px 0;">Join our course community and networks</li>
            <li style="margin: 8px 0;">Access your learning materials</li>
            <li style="margin: 8px 0;">Get administrative support when needed</li>
        </ol>
        
        <!-- Contact -->
        <div style="background: #4299e1; color: white; padding: 20px; border-radius: 8px; text-align: center; margin: 25px 0;">
            <h3 style="margin-top: 0;">💬 Need Help?</h3>
            <p style="margin: 10px 0;">Contact us on WhatsApp for instant support:</p>
            <a href="https://wa.me/{contact_no.lstrip('+')}" 
               style="background: rgba(255,255,255,0.2); color: white; padding: 12px 20px; text-decoration: none; border-radius: 6px; display: inline-block; margin-top: 10px;">
                📱 {contact_no}
            </a>
        </div>
        
        <p style="margin-top: 30px; color: #666; font-size: 14px; text-align: center;">
            Thank you for choosing {company_name}!<br>
            We're excited to be part of your learning journey.
        </p>
    </div>
    
</body>
</html>
"""

    msg.add_alternative(html, subtype="html")

    # ── Send ─────────────────────────────────────────────────────────
    try:
        smtp_cls = smtplib.SMTP_SSL if port == 465 else smtplib.SMTP
        with smtp_cls(host, port, timeout=10) as server:
            if use_tls and port != 465:
                server.starttls()
            if user and pwd:
                server.login(user, pwd)
            server.send_message(msg)
        
        return f"✅ Email sent to {email} for {course_name} (ID: {user_id})"
        
    except Exception as e:
        return f"❌ Failed to send email: {str(e)}"