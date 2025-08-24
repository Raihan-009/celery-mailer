# Email Templates

This directory contains email templates for the Celery Mailer system.

## Files

### `plain_text_enrollment.txt`
Plain text version of the course enrollment confirmation email.

**Template Variables:**
- `{greeting}` - Personalized greeting (e.g., "Dear John Doe,")
- `{course_name}` - Name of the enrolled course
- `{user_id}` - User's unique identifier
- `{today}` - Current date in readable format
- `{contact_number}` - Company contact number
- `{company_name}` - Company name

### `html_enrollment.html`
HTML version of the course enrollment confirmation email with modern styling.

**Template Variables:**
- `{greeting}` - Personalized greeting
- `{course_name}` - Name of the enrolled course
- `{user_id}` - User's unique identifier
- `{today}` - Current date in readable format
- `{contact_number}` - Company contact number
- `{contact_number_clean}` - Contact number without '+' prefix (for WhatsApp links)
- `{company_name}` - Company name

## Usage

The templates are automatically loaded by the `EmailService` class in `mailer.py`. The system will:

1. Load the template file
2. Format it with the provided variables

## Modifying Templates

To modify the email content:

1. Edit the appropriate template file
2. Use the template variables listed above
3. Test your changes by running the application

## Template Format

- **Plain Text**: Use simple text with template variables in curly braces
- **HTML**: Use valid HTML with inline CSS for email compatibility

## Notes

- Templates use Python's `.format()` method for variable substitution
- HTML templates include inline CSS for maximum email client compatibility
- Template files are required - the system will fail if they are missing
