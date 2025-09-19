import os
from celery import Celery
from mailer import email_service

# ── Celery wiring ─────────────────────────────────────────────
app = Celery(
    "tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1"),
)

# ── Task definition ───────────────────────────────────────────
@app.task(name="send_course_enrollment_email", bind=True)
def send_course_enrollment_email(self, course_name: str,
                                 user_id: str,
                                 email: str,
                                 user_name: str | None = None):
    """
    Celery task to send course enrollment confirmation email.
    
    Args:
        course_name: Name of the course
        user_id: User's ID
        email: Recipient email address
        user_name: Optional user name for personalization
        
    Returns:
        Success or error message
    """
    return email_service.send_course_enrollment_email(
        course_name=course_name,
        user_id=user_id,
        email=email,
        user_name=user_name,
        task_id=self.request.id
    )

# ── Additional email tasks ────────────────────────────────────
@app.task(name="send_custom_email", bind=True)
def send_custom_email(self, to_email: str,
                     subject: str,
                     plain_content: str,
                     html_content: str | None = None):
    """
    Celery task to send custom emails.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        plain_content: Plain text content
        html_content: Optional HTML content
        
    Returns:
        Success or error message
    """
    return email_service.send_custom_email(
        to_email=to_email,
        subject=subject,
        plain_content=plain_content,
        html_content=html_content,
        task_id=self.request.id
    )