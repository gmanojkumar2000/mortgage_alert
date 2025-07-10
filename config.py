"""
Configuration loader for the Refinance Rate Alert System
Loads all config from environment variables using python-dotenv
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Helper to get env with type casting and default
getenv = lambda key, default=None, cast=str: cast(os.getenv(key, default))

# Rate Alert Configuration
TARGET_RATE = float(getenv("TARGET_RATE", 6))
STATE = getenv("STATE", "Oregon")

# Notification Configuration
NOTIFICATION_METHOD = getenv("NOTIFICATION_METHOD", "email").lower()  # "email" or "telegram"

# Daily Report Configuration
DAILY_REPORT = getenv("DAILY_REPORT", "false").lower() == "true"  # Send daily report regardless of threshold

# Email Configuration
EMAIL_CONFIG = {
    "smtp_server": getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(getenv("SMTP_PORT", 587)),
    "sender_email": getenv("SENDER_EMAIL", ""),
    "sender_password": getenv("SENDER_PASSWORD", ""),
    "recipient_email": getenv("RECIPIENT_EMAIL", ""),
}

# Telegram Configuration
TELEGRAM_CONFIG = {
    "bot_token": getenv("TELEGRAM_BOT_TOKEN", ""),
    "chat_id": getenv("TELEGRAM_CHAT_ID", ""),
}

# Rate Source Configuration
RATE_SOURCE = getenv("RATE_SOURCE", "fred")  # "fred", "pmm", "bankrate", "mortgage_news_daily", or "freddiemac"

# FRED API Configuration
FRED_API_KEY = getenv("FRED_API_KEY", "")  # Optional: for more reliable FRED data

# Logging Configuration
LOG_LEVEL = getenv("LOG_LEVEL", "INFO")
LOG_FILE = getenv("LOG_FILE", "alert.log") 