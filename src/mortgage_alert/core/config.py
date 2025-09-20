"""
Configuration management for the Mortgage Alert System
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the mortgage alert system"""
    
    def __init__(self):
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment variables"""
        # Rate Alert Configuration
        self.target_rate = float(self._get_env("TARGET_RATE", 6.0, float))
        self.state = self._get_env("STATE", "Oregon")
        
        # Notification Configuration
        self.notification_method = self._get_env("NOTIFICATION_METHOD", "email").lower()
        
        # Daily Report Configuration
        self.daily_report = self._get_env("DAILY_REPORT", "false").lower() == "true"
        
        # Email Configuration
        self.email_config = {
            "smtp_server": self._get_env("SMTP_SERVER", "smtp.gmail.com"),
            "smtp_port": int(self._get_env("SMTP_PORT", 587)),
            "sender_email": self._get_env("SENDER_EMAIL", ""),
            "sender_password": self._get_env("SENDER_PASSWORD", ""),
            "recipient_email": self._get_env("RECIPIENT_EMAIL", ""),
        }
        
        # Telegram Configuration
        self.telegram_config = {
            "bot_token": self._get_env("TELEGRAM_BOT_TOKEN", ""),
            "chat_id": self._get_env("TELEGRAM_CHAT_ID", ""),
        }
        
        # Rate Source Configuration
        self.rate_source = self._get_env("RATE_SOURCE", "fred")
        
        # FRED API Configuration
        self.fred_api_key = self._get_env("FRED_API_KEY", "")
        
        # Logging Configuration
        self.log_level = self._get_env("LOG_LEVEL", "INFO")
        self.log_file = self._get_env("LOG_FILE", "alert.log")
        
        # Data Configuration
        self.data_dir = self._get_env("DATA_DIR", "data")
        
        # Preferred rate sources for aggregation
        self.preferred_sources = [
            "fred",
            "bankrate", 
            "mortgage_news_daily",
            "freddiemac"
        ]
    
    def _get_env(self, key: str, default: Any = None, cast_type: type = str) -> Any:
        """Get environment variable with type casting"""
        value = os.getenv(key, default)
        if cast_type == str:
            return value
        elif cast_type == bool:
            return str(value).lower() == "true"
        elif cast_type == int:
            try:
                return int(value)
            except (ValueError, TypeError):
                return default
        elif cast_type == float:
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        else:
            return value
    
    def validate(self) -> Dict[str, bool]:
        """Validate configuration and return validation results"""
        validation = {}
        
        # Validate email configuration
        if self.notification_method == "email":
            email_valid = all([
                self.email_config.get("sender_email"),
                self.email_config.get("sender_password"),
                self.email_config.get("recipient_email")
            ])
            validation["email"] = email_valid
        else:
            validation["email"] = True  # Not using email
        
        # Validate telegram configuration
        if self.notification_method == "telegram":
            telegram_valid = all([
                self.telegram_config.get("bot_token"),
                self.telegram_config.get("chat_id")
            ])
            validation["telegram"] = telegram_valid
        else:
            validation["telegram"] = True  # Not using telegram
        
        # Validate rate configuration
        validation["target_rate"] = 0 < self.target_rate < 20
        validation["state"] = bool(self.state and len(self.state.strip()) > 0)
        
        # Overall validation
        validation["valid"] = all(validation.values())
        
        return validation
    
    def get_summary(self) -> Dict[str, Any]:
        """Get configuration summary for logging"""
        return {
            "target_rate": self.target_rate,
            "state": self.state,
            "rate_source": self.rate_source,
            "notification_method": self.notification_method,
            "daily_report": self.daily_report,
            "log_level": self.log_level,
            "preferred_sources": self.preferred_sources,
            "validation": self.validate()
        }
    
    def __repr__(self):
        return f"Config(target_rate={self.target_rate}%, state={self.state}, method={self.notification_method})"


# Global config instance
config = Config()
