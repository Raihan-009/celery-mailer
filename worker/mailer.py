import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from typing import Optional
from pathlib import Path
from database import db_manager


class EmailService:
    """Email service for sending course enrollment and other emails."""
    
    def __init__(self):
        # SMTP configuration from environment variables
        self.host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.port = int(os.getenv("SMTP_PORT", 587))
        self.user = os.getenv("SMTP_USER")
        self.password = os.getenv("SMTP_PASSWORD")
        self.use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        self.from_email = os.getenv("FROM_EMAIL", self.user or "noreply@example.com")
        
        # Company details
        self.company_name = os.getenv("COMPANY_NAME", "Poridhi")
        self.contact_number = os.getenv("CONTACT_NUMBER", "+0000000000")
    
    def _create_smtp_connection(self):
        """Create and configure SMTP connection."""
        smtp_cls = smtplib.SMTP_SSL if self.port == 465 else smtplib.SMTP
        server = smtp_cls(self.host, self.port, timeout=10)
        
        if self.use_tls and self.port != 465:
            server.starttls()
        
        if self.user and self.password:
            server.login(self.user, self.password)
        
        return server
    
    def send_course_enrollment_email(self, 
                                   course_name: str,
                                   user_id: int,
                                   email: str,
                                   user_name: Optional[str] = None,
                                   task_id: Optional[str] = None) -> str:
        """
        Send course enrollment confirmation email.
        
        Args:
            course_name: Name of the course
            user_id: User's ID
            email: Recipient email address
            user_name: Optional user name for personalization
            task_id: Celery task ID for tracking
            
        Returns:
            Success or error message
        """
        subject = f"🎉 Welcome to {course_name} – Enrollment Confirmed!"
        
        # Log email attempt to database
        if task_id:
            try:
                db_manager.log_email_attempt(
                    task_id=task_id,
                    email=email,
                    subject=subject,
                    course_name=course_name,
                    user_id=user_id,
                    user_name=user_name,
                    status="pending"
                )
            except Exception:
                pass
        
        try:
            msg = self._create_enrollment_email(course_name, user_id, email, user_name)
            
            with self._create_smtp_connection() as server:
                server.send_message(msg)
            
            # Update database with success status
            if task_id:
                try:
                    db_manager.update_email_status(
                        task_id=task_id,
                        status="sent",
                        sent_at=datetime.now()
                    )
                except Exception:
                    pass
            
            return f"✅ E-mail sent to {email} (course: {course_name}, ID: {user_id})"
        
        except Exception as err:
            error_msg = str(err)
            
            # Update database with failure status
            if task_id:
                try:
                    db_manager.update_email_status(
                        task_id=task_id,
                        status="failed",
                        error_message=error_msg
                    )
                except Exception:
                    pass
            
            return f"❌ Failed to send e-mail → {error_msg}"
    
    def _create_enrollment_email(self, 
                               course_name: str,
                               user_id: int,
                               email: str,
                               user_name: Optional[str] = None) -> EmailMessage:
        """Create enrollment email message with both plain text and HTML versions."""
        
        greeting = f"Dear {user_name}," if user_name else "Dear Learner,"
        today = datetime.now().strftime("%B %d, %Y")
        
        # Create message
        msg = EmailMessage()
        msg["Subject"] = f"🎉 Welcome to {course_name} – Enrollment Confirmed!"
        msg["From"] = f"{self.company_name} <{self.from_email}>"
        msg["To"] = email
        
        # Plain text content
        plain_content = self._create_plain_text_content(
            greeting, course_name, user_id, today
        )
        msg.set_content(plain_content)
        
        # HTML content
        html_content = self._create_html_content(
            greeting, course_name, user_id, today
        )
        msg.add_alternative(html_content, subtype="html")
        
        return msg
    
    def _create_plain_text_content(self, 
                                 greeting: str,
                                 course_name: str,
                                 user_id: int,
                                 today: str) -> str:
        """Create plain text email content."""
        template_path = Path(__file__).parent / "templates" / "plain_text_enrollment.txt"
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        return template.format(
            greeting=greeting,
            course_name=course_name,
            user_id=user_id,
            today=today,
            contact_number=self.contact_number,
            company_name=self.company_name
        )
    
    def _create_html_content(self, 
                           greeting: str,
                           course_name: str,
                           user_id: int,
                           today: str) -> str:
        """Create HTML email content."""
        template_path = Path(__file__).parent / "templates" / "html_enrollment.html"
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        return template.format(
            greeting=greeting,
            course_name=course_name,
            user_id=user_id,
            today=today,
            contact_number=self.contact_number,
            contact_number_clean=self.contact_number.lstrip('+'),
            company_name=self.company_name
        )
    
    def send_custom_email(self, 
                         to_email: str,
                         subject: str,
                         plain_content: str,
                         html_content: Optional[str] = None,
                         task_id: Optional[str] = None) -> str:
        """
        Send a custom email with plain text and optional HTML content.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            plain_content: Plain text content
            html_content: Optional HTML content
            task_id: Celery task ID for tracking
            
        Returns:
            Success or error message
        """
        # Log email attempt to database
        if task_id:
            try:
                db_manager.log_email_attempt(
                    task_id=task_id,
                    email=to_email,
                    subject=subject,
                    status="pending"
                )
            except Exception:
                pass
        
        try:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = f"{self.company_name} <{self.from_email}>"
            msg["To"] = to_email
            
            msg.set_content(plain_content)
            
            if html_content:
                msg.add_alternative(html_content, subtype="html")
            
            with self._create_smtp_connection() as server:
                server.send_message(msg)
            
            # Update database with success status
            if task_id:
                try:
                    db_manager.update_email_status(
                        task_id=task_id,
                        status="sent",
                        sent_at=datetime.now()
                    )
                except Exception:
                    pass
            
            return f"✅ Custom email sent to {to_email}"
        
        except Exception as err:
            error_msg = str(err)
            
            # Update database with failure status
            if task_id:
                try:
                    db_manager.update_email_status(
                        task_id=task_id,
                        status="failed",
                        error_message=error_msg
                    )
                except Exception:
                    pass
            
            return f"❌ Failed to send custom email → {error_msg}"


# Create a global instance for easy importing
email_service = EmailService()