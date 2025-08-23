import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from typing import Optional


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
                                   user_name: Optional[str] = None) -> str:
        """
        Send course enrollment confirmation email.
        
        Args:
            course_name: Name of the course
            user_id: User's ID
            email: Recipient email address
            user_name: Optional user name for personalization
            
        Returns:
            Success or error message
        """
        try:
            msg = self._create_enrollment_email(course_name, user_id, email, user_name)
            
            with self._create_smtp_connection() as server:
                server.send_message(msg)
            
            return f"✅ E-mail sent to {email} (course: {course_name}, ID: {user_id})"
        
        except Exception as err:
            return f"❌ Failed to send e-mail → {err}"
    
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
        return f"""{greeting}

Congratulations! Your payment has been processed and you're now enrolled in "{course_name}".

Enrollment details
──────────────────
• Learner ID : {user_id}
• Course     : {course_name}
• Date       : {today}

Need help? WhatsApp {self.contact_number}

Best regards,
The {self.company_name} Team
"""
    
    def _create_html_content(self, 
                           greeting: str,
                           course_name: str,
                           user_id: int,
                           today: str) -> str:
        """Create HTML email content."""
        return f"""\
<!doctype html><html><head><meta charset="utf-8"></head>
<body style="font-family:Arial,Helvetica,sans-serif;line-height:1.6;color:#333;">
  <div style="max-width:600px;margin:auto;background:#f8f9fa;border-radius:8px;">
    <div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;
                padding:30px;border-radius:8px 8px 0 0;text-align:center;">
      <h1 style="margin:0;font-size:24px;">🎉 Enrollment Confirmed!</h1>
      <p style="opacity:.9;margin-top:10px;">Welcome to {self.company_name}</p>
    </div>
    <div style="background:#fff;padding:30px;border-radius:0 0 8px 8px;
                box-shadow:0 2px 10px rgba(0,0,0,.1);">
      <p>{greeting}</p>
      <div style="background:#e8f5e8;border-left:4px solid #28a745;padding:15px;
                  border-radius:4px;margin:20px 0;">
        <strong style="color:#155724;">✅ Payment successful – you're enrolled in "{course_name}"</strong>
      </div>
      <h3>📋 Your details</h3>
      <ul style="padding-left:0;list-style:none;">
        <li><strong>Learner ID:</strong> #{user_id}</li>
        <li><strong>Course:</strong> {course_name}</li>
        <li><strong>Date:</strong> {today}</li>
        <li><strong>Status:</strong> <span style="color:#28a745">✅ Active</span></li>
      </ul>
      <h3>🚀 What's next?</h3>
      <ol>
        <li>Join our course community & networks.</li>
        <li>Access your learning materials.</li>
        <li>Get administrative support whenever needed.</li>
      </ol>
      <div style="background:#4299e1;color:#fff;text-align:center;padding:20px;border-radius:8px;">
        <h3 style="margin-top:0;">💬 Need help?</h3>
        <p>WhatsApp us for instant support:</p>
        <a href="https://wa.me/{self.contact_number.lstrip('+')}"
           style="display:inline-block;margin-top:10px;padding:12px 20px;
                  background:rgba(255,255,255,.2);color:#fff;text-decoration:none;
                  border-radius:6px;">📱 {self.contact_number}</a>
      </div>
      <p style="margin-top:30px;text-align:center;font-size:14px;color:#666;">
        Thank you for choosing {self.company_name}!<br>
        We're excited to be part of your learning journey.
      </p>
    </div>
  </div>
</body></html>
"""
    
    def send_custom_email(self, 
                         to_email: str,
                         subject: str,
                         plain_content: str,
                         html_content: Optional[str] = None) -> str:
        """
        Send a custom email with plain text and optional HTML content.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            plain_content: Plain text content
            html_content: Optional HTML content
            
        Returns:
            Success or error message
        """
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
            
            return f"✅ Custom email sent to {to_email}"
        
        except Exception as err:
            return f"❌ Failed to send custom email → {err}"


# Create a global instance for easy importing
email_service = EmailService()