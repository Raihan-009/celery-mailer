import os
import time
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


class EmailTracking(Base):
    """Model for tracking email sending status."""
    
    __tablename__ = "email_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    subject = Column(String(500), nullable=False)
    course_name = Column(String(255), nullable=True)
    user_id = Column(String(255), nullable=True)
    user_name = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default="pending", index=True)
    sent_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class DatabaseManager:
    """Manager class for database operations."""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        self._tables_created = False
    
    def _wait_for_database(self, max_retries=30, delay=2):
        """Wait for database to be ready."""
        for attempt in range(max_retries):
            try:
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                return True
            except Exception:
                if attempt < max_retries - 1:
                    time.sleep(delay)
                else:
                    return False
        return False
    
    def create_tables(self):
        """Create all tables with retry logic."""
        if self._tables_created:
            return
        
        if not self._wait_for_database():
            return
        
        try:
            Base.metadata.create_all(bind=self.engine)
            self._tables_created = True
        except Exception:
            pass
    
    def ensure_tables_exist(self):
        """Ensure tables exist, creating them if necessary."""
        if not self._tables_created:
            self.create_tables()
    
    def get_session(self) -> Session:
        """Get a database session."""
        self.ensure_tables_exist()
        return self.SessionLocal()
    
    def log_email_attempt(self, 
                         task_id: str,
                         email: str,
                         subject: str,
                         course_name: Optional[str] = None,
                         user_id: Optional[int] = None,
                         user_name: Optional[str] = None,
                         status: str = "pending") -> EmailTracking:
        """Log an email sending attempt."""
        try:
            with self.get_session() as session:
                email_record = EmailTracking(
                    task_id=task_id,
                    email=email,
                    subject=subject,
                    course_name=course_name,
                    user_id=user_id,
                    user_name=user_name,
                    status=status
                )
                session.add(email_record)
                session.commit()
                session.refresh(email_record)
                return email_record
        except Exception:
            return None
    
    def update_email_status(self, 
                           task_id: str,
                           status: str,
                           error_message: Optional[str] = None,
                           sent_at: Optional[datetime] = None) -> bool:
        """Update email sending status."""
        try:
            with self.get_session() as session:
                email_record = session.query(EmailTracking).filter(
                    EmailTracking.task_id == task_id
                ).first()
                
                if email_record:
                    email_record.status = status
                    if error_message:
                        email_record.error_message = error_message
                    if sent_at:
                        email_record.sent_at = sent_at
                    
                    session.commit()
                    return True
                return False
        except Exception:
            return False
    
    def get_email_status(self, task_id: str) -> Optional[EmailTracking]:
        """Get email status by task ID."""
        try:
            with self.get_session() as session:
                return session.query(EmailTracking).filter(
                    EmailTracking.task_id == task_id
                ).first()
        except Exception:
            return None


# Create global database manager instance
db_manager = DatabaseManager()
