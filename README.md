# Celery Mailer with PostgreSQL Tracking

A robust email sending system built with Celery, Redis, and PostgreSQL for comprehensive email tracking.

## Features

- **Asynchronous Email Processing**: Uses Celery for background email processing
- **Email Tracking**: PostgreSQL database tracks all email sending attempts
- **Status Monitoring**: Track successful, failed, and pending emails
- **Docker Support**: Full containerization with Docker Compose

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Producer   │───▶│    Redis    │───▶│   Worker   │
│             │    │  (Broker)   │    │            │
└─────────────┘    └─────────────┘    └─────────────┘
                           │                   │
                           │                   ▼
                           │            ┌─────────────┐
                           │            │ PostgreSQL │
                           │            │ (Tracking) │
                           │            └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ PostgreSQL  │
                    │ (Results)   │
                    └─────────────┘
```

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd celery-mailer
cp env.template .env
# Edit .env with your SMTP credentials
```

### 2. Start Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database for email tracking
- Redis for Celery broker/backend
- Celery worker for processing emails
- Producer container for sending email tasks

### 3. Send Test Email

```bash
# Exec into producer container
docker-compose exec producer bash

# Send a test email
python producer.py "Python Programming" 123 "user@example.com"
```

## Configuration

### Environment Variables

Copy `env.template` to `.env` and configure:

```bash
# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com

# Database Configuration (auto-configured)
DATABASE_URL=postgresql://mailer_user:mailer_password@postgres:5432/celery_mailer

# Company Details
COMPANY_NAME=Your Company
CONTACT_NUMBER=+1234567890
```

### Database Schema

The system automatically creates these tables:

- **email_tracking**: Main table for tracking email status
  - `task_id`: Unique Celery task identifier
  - `email`: Recipient email address
  - `subject`: Email subject
  - `status`: Current status (pending/sent/failed)
  - `sent_at`: Timestamp when email was sent
  - `error_message`: Error details if failed
  - `retry_count`: Number of retry attempts

## Usage

### Sending Emails

#### Course Enrollment Emails

```python
from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/0')

# Send course enrollment email
result = app.send_task('send_course_enrollment_email', 
                      args=['Python Course', 123, 'user@example.com', 'John Doe'])
```

#### Custom Emails

```python
# Send custom email
result = app.send_task('send_custom_email',
                      args=['user@example.com', 'Welcome!', 'Plain text content', '<h1>HTML content</h1>'])
```

## Database Operations

### Direct Database Access

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U mailer_user -d celery_mailer

# View email tracking data
SELECT * FROM email_tracking ORDER BY created_at DESC LIMIT 10;

# Check failed emails
SELECT email, subject, error_message, retry_count 
FROM email_tracking 
WHERE status = 'failed' 
ORDER BY updated_at DESC;
```

### Database Backup

```bash
# Backup database
docker-compose exec postgres pg_dump -U mailer_user celery_mailer > backup.sql

# Restore database
docker-compose exec -T postgres psql -U mailer_user -d celery_mailer < backup.sql
```

## Project Structure

```
celery-mailer/
├── docker-compose.yml          # Service orchestration
├── init-db.sql                # Database initialization
├── producer/                   # Email task producer
│   ├── Dockerfile
│   └── producer.py
├── worker/                     # Celery worker and email processing
│   ├── Dockerfile
│   ├── requirements.txt        # Python dependencies
│   ├── tasks.py               # Celery task definitions
│   ├── mailer.py              # Email service
│   ├── database.py            # Database models and manager
│   ├── start_worker.sh        # Worker startup script
│   └── templates/             # Email templates
│       ├── html_enrollment.html
│       └── plain_text_enrollment.txt
└── README.md
```

### Adding New Email Types

1. **Create Task**: Add new task in `worker/tasks.py`
2. **Update Mailer**: Add corresponding method in `worker/mailer.py`
3. **Database Tracking**: Ensure database logging is implemented
4. **Templates**: Add email templates if needed

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Ensure PostgreSQL container is running
   - Check database credentials in `.env`
   - Verify network connectivity between containers

2. **SMTP Authentication Failed**
   - Verify SMTP credentials in `.env`
   - Check if using app passwords for Gmail
   - Ensure SMTP server allows connections

3. **Emails Not Being Sent**
   - Check Celery worker logs: `docker-compose logs worker`
   - Verify Redis connection
   - Check database for email tracking records

### Logs

```bash
# View all service logs
docker-compose logs

# View specific service logs
docker-compose logs worker
docker-compose logs postgres
docker-compose logs redis

# Follow logs in real-time
docker-compose logs -f worker
```

## Performance and Scaling

### Optimization Tips

- **Connection Pooling**: Configure database connection pooling for high volume
- **Batch Processing**: Group multiple emails into single tasks
- **Rate Limiting**: Implement SMTP rate limiting to avoid being blocked

### Scaling

- **Multiple Workers**: Scale worker containers for higher throughput
- **Database Replication**: Use PostgreSQL read replicas for monitoring queries
- **Redis Clustering**: Implement Redis cluster for high availability

## License

[Your License Here]

## Contributing

[Your Contributing Guidelines Here]
