"""
Mortgage Alert System

A Python-based alert system that monitors refinance mortgage rates
and sends notifications when rates drop below your target threshold.

Features:
- Multi-source rate aggregation
- Historical rate tracking
- Email and Telegram notifications
- GitHub Actions integration
- Rate trend analysis
"""

__version__ = "2.0.0"
__author__ = "Mortgage Alert Team"
__email__ = "mortgage.alert@example.com"

from .core.alert_system import AlertSystem
from .core.config import Config
from .scrapers.rate_scraper import EnhancedRateScraper
from .data.data_manager import RateDataManager
from .notifications.notification_service import NotificationService

# CLI entry point
def main():
    """CLI entry point for the mortgage alert system"""
    from .cli import main as cli_main
    return cli_main()

__all__ = [
    "AlertSystem",
    "Config", 
    "EnhancedRateScraper",
    "RateDataManager",
    "NotificationService",
    "main"
]
