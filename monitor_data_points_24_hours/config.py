import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Database configuration - all variables are required
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

# Validate all required database configurations
if not all([DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
    missing = [var for var, val in {'DB_HOST': DB_HOST, 'DB_USER': DB_USER, 
                                   'DB_PASSWORD': DB_PASSWORD, 'DB_NAME': DB_NAME}.items() if not val]
    raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')

# Handle SMTP port with proper error handling
try:
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
except ValueError:
    raise ValueError("SMTP_PORT must be a valid integer")

# Email authentication
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

# Validate email credentials
if not all([SMTP_USERNAME, SMTP_PASSWORD]):
    missing = [var for var, val in {'SMTP_USERNAME': SMTP_USERNAME, 
                                   'SMTP_PASSWORD': SMTP_PASSWORD}.items() if not val]
    raise ValueError(f"Missing required email credentials: {', '.join(missing)}")

# Recipients configuration
recipients_str = os.getenv('RECIPIENT_EMAILS')
if not recipients_str:
    raise ValueError("RECIPIENT_EMAILS environment variable is required")

# Parse recipient emails
RECIPIENT_EMAILS = [email.strip() for email in recipients_str.split(',')]
if not RECIPIENT_EMAILS:
    raise ValueError("RECIPIENT_EMAILS must contain at least one valid email address")
