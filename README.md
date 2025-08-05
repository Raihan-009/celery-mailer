# Celery Mailer

A Celery-based email sending system with Redis as the message broker.

## Quick Start

1. **Copy environment template:**
   ```bash
   cp env.template .env
   ```

2. **Configure your email settings in `.env`:**
   - For **Gmail**: Use your 16-digit app password
   - For **Private Email**: Use your email provider's SMTP settings

3. **Start the services:**
   ```bash
   docker-compose up -d
   ```

## Email Configuration

### For Gmail Users
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-gmail@gmail.com
SMTP_PASSWORD=your-16-digit-app-password
SMTP_USE_TLS=true
```

### For Private Email Services
```env
SMTP_HOST=smtp.your-provider.com
SMTP_PORT=587                    # or 465 for SSL, 25 for plain
SMTP_USER=your-email@your-domain.com
SMTP_PASSWORD=your-password-or-api-key
SMTP_USE_TLS=true               # false for port 465
```

## Common Private Email Providers

| Provider | SMTP Host | Port | TLS |
|----------|-----------|------|-----|
| Outlook/Hotmail | smtp-mail.outlook.com | 587 | true |
| Yahoo | smtp.mail.yahoo.com | 587 | true |
| ProtonMail | smtp.protonmail.ch | 587 | true |
| Zoho | smtp.zoho.com | 587 | true |
| Fastmail | smtp.fastmail.com | 587 | true |
| Custom Domain | smtp.your-domain.com | 587 | true |

## Usage

1. **Send a test email:**
   ```bash
   docker-compose exec producer python producer.py
   ```

2. **Monitor tasks:**
   ```bash
   docker-compose logs -f worker
   ```

## Troubleshooting

### Authentication Issues
- Verify your email credentials
- Check if your email provider requires app-specific passwords
- Ensure SMTP settings match your provider's requirements

### Connection Issues
- Check firewall settings
- Verify SMTP host and port are correct
- Try different ports (587, 465, 25)

### TLS/SSL Issues
- Set `SMTP_USE_TLS=false` for port 465 (SSL)
- Set `SMTP_USE_TLS=true` for port 587 (STARTTLS)
