import os, smtplib
from email.message import EmailMessage
from datetime import datetime
from celery import Celery

# ── Celery wiring ─────────────────────────────────────────────
app = Celery(
    "tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1"),
)

# ── Task definition ───────────────────────────────────────────
@app.task(name="send_course_enrollment_email")
def send_course_enrollment_email(course_name: str,
                                 user_id: int,
                                 email: str,
                                 user_name: str | None = None):
    # 1️⃣ SMTP / company settings (••• all overridable via .env •••)
    host        = os.getenv("SMTP_HOST", "smtp.gmail.com")
    port        = int(os.getenv("SMTP_PORT", 587))         # 587 = STARTTLS
    user        = os.getenv("SMTP_USER")                   # gmail address
    pwd         = os.getenv("SMTP_PASSWORD")               # 16-digit App PW
    use_tls     = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    from_email  = os.getenv("FROM_EMAIL", user or "noreply@example.com")
    company     = os.getenv("COMPANY_NAME", "Poridhi")
    contact_no  = os.getenv("CONTACT_NUMBER", "+0000000000")

    # 2️⃣ Dynamic bits
    greeting    = f"Dear {user_name}," if user_name else "Dear Learner,"
    today       = datetime.now().strftime("%B %d, %Y")

    # 3️⃣ Message skeleton
    msg             = EmailMessage()
    msg["Subject"]  = f"🎉 Welcome to {course_name} – Enrollment Confirmed!"
    msg["From"]     = f"{company} <{from_email}>"
    msg["To"]       = email

    # ••• Plain-text part (always include) •••
    plain = f"""{greeting}

Congratulations! Your payment has been processed and you’re now enrolled in “{course_name}”.

Enrollment details
──────────────────
• Learner ID : {user_id}
• Course     : {course_name}
• Date       : {today}

Need help? WhatsApp {contact_no}

Best regards,
The {company} Team
"""
    msg.set_content(plain)

    # ••• HTML alternative •••
    html = f"""\
<!doctype html><html><head><meta charset="utf-8"></head>
<body style="font-family:Arial,Helvetica,sans-serif;line-height:1.6;color:#333;">
  <div style="max-width:600px;margin:auto;background:#f8f9fa;border-radius:8px;">
    <div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;
                padding:30px;border-radius:8px 8px 0 0;text-align:center;">
      <h1 style="margin:0;font-size:24px;">🎉 Enrollment Confirmed!</h1>
      <p style="opacity:.9;margin-top:10px;">Welcome to {company}</p>
    </div>
    <div style="background:#fff;padding:30px;border-radius:0 0 8px 8px;
                box-shadow:0 2px 10px rgba(0,0,0,.1);">
      <p>{greeting}</p>
      <div style="background:#e8f5e8;border-left:4px solid #28a745;padding:15px;
                  border-radius:4px;margin:20px 0;">
        <strong style="color:#155724;">✅ Payment successful – you’re enrolled in “{course_name}”</strong>
      </div>
      <h3>📋 Your details</h3>
      <ul style="padding-left:0;list-style:none;">
        <li><strong>Learner ID:</strong> #{user_id}</li>
        <li><strong>Course:</strong> {course_name}</li>
        <li><strong>Date:</strong> {today}</li>
        <li><strong>Status:</strong> <span style="color:#28a745">✅ Active</span></li>
      </ul>
      <h3>🚀 What’s next?</h3>
      <ol>
        <li>Join our course community & networks.</li>
        <li>Access your learning materials.</li>
        <li>Get administrative support whenever needed.</li>
      </ol>
      <div style="background:#4299e1;color:#fff;text-align:center;padding:20px;border-radius:8px;">
        <h3 style="margin-top:0;">💬 Need help?</h3>
        <p>WhatsApp us for instant support:</p>
        <a href="https://wa.me/{contact_no.lstrip('+')}"
           style="display:inline-block;margin-top:10px;padding:12px 20px;
                  background:rgba(255,255,255,.2);color:#fff;text-decoration:none;
                  border-radius:6px;">📱 {contact_no}</a>
      </div>
      <p style="margin-top:30px;text-align:center;font-size:14px;color:#666;">
        Thank you for choosing {company}!<br>
        We’re excited to be part of your learning journey.
      </p>
    </div>
  </div>
</body></html>
"""
    msg.add_alternative(html, subtype="html")

    # 4️⃣  Send
    smtp_cls = smtplib.SMTP_SSL if port == 465 else smtplib.SMTP
    try:
        with smtp_cls(host, port, timeout=10) as server:
            if use_tls and port != 465:
                server.starttls()
            if user and pwd:
                server.login(user, pwd)
            server.send_message(msg)
        return f"✅ E-mail sent to {email} (course: {course_name}, ID: {user_id})"
    except Exception as err:
        return f"❌ Failed to send e-mail → {err}"
