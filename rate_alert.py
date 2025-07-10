#!/usr/bin/env python3
"""
Refinance Rate Alert System
Main script that checks current refinance rates and sends alerts when they drop below threshold
"""

import os
import sys
import logging
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# Import our modules
from rate_scraper import get_rate_scraper, get_mock_rate
from notifications import get_notification_service
import config

# Load environment variables
load_dotenv()

# Configure logging
def setup_logging():
    """Setup logging configuration to always log to alert.log"""
    log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('alert.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def load_credentials_from_env():
    """Load credentials from environment variables"""
    # Update email config with environment variables
    sender_email = os.getenv('SENDER_EMAIL')
    if sender_email:
        config.EMAIL_CONFIG['sender_email'] = sender_email
    sender_password = os.getenv('SENDER_PASSWORD')
    if sender_password:
        config.EMAIL_CONFIG['sender_password'] = sender_password
    recipient_email = os.getenv('RECIPIENT_EMAIL')
    if recipient_email:
        config.EMAIL_CONFIG['recipient_email'] = recipient_email
    
    # Update telegram config with environment variables
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if bot_token:
        config.TELEGRAM_CONFIG['bot_token'] = bot_token
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if chat_id:
        config.TELEGRAM_CONFIG['chat_id'] = chat_id


def get_current_rate() -> Optional[float]:
    """Get current refinance rate from configured source"""
    logger = logging.getLogger(__name__)
    
    try:
        # Get the appropriate scraper
        scraper = get_rate_scraper(config.RATE_SOURCE)
        logger.info(f"Fetching rate from {config.RATE_SOURCE}")
        
        # Try to get the rate
        rate = scraper.get_rate()
        
        if rate is not None:
            logger.info(f"Successfully retrieved rate: {rate}%")
            return rate
        else:
            logger.warning(f"Failed to get rate from {config.RATE_SOURCE}, using mock rate for testing")
            # Use mock rate for testing when scraping fails
            mock_rate = get_mock_rate()
            logger.info(f"Using mock rate: {mock_rate}%")
            return mock_rate
            
    except Exception as e:
        logger.error(f"Error getting current rate: {e}")
        # Fallback to mock rate
        mock_rate = get_mock_rate()
        logger.info(f"Using mock rate due to error: {mock_rate}%")
        return mock_rate


def should_send_alert(current_rate: float) -> bool:
    """Check if alert should be sent based on current rate"""
    # If daily report is enabled, always send
    if config.DAILY_REPORT:
        return True
    # Otherwise, only send if rate is below target
    return current_rate < config.TARGET_RATE


def send_alert(current_rate: float) -> bool:
    """Send rate alert notification"""
    logger = logging.getLogger(__name__)
    
    try:
        # Get the appropriate notification service
        if config.NOTIFICATION_METHOD == "email":
            service = get_notification_service("email", config.EMAIL_CONFIG)
        elif config.NOTIFICATION_METHOD == "telegram":
            service = get_notification_service("telegram", config.TELEGRAM_CONFIG)
        else:
            logger.error(f"Unknown notification method: {config.NOTIFICATION_METHOD}")
            return False
        
        # Send the alert
        success = service.send_alert(current_rate, config.TARGET_RATE, config.STATE)
        
        if success:
            if config.DAILY_REPORT:
                logger.info(f"Daily rate report sent successfully via {config.NOTIFICATION_METHOD}")
            else:
                logger.info(f"Alert sent successfully via {config.NOTIFICATION_METHOD}")
        else:
            logger.error(f"Failed to send alert via {config.NOTIFICATION_METHOD}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error sending alert: {e}")
        return False


def main():
    """Main function to run the rate alert system"""
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Refinance Rate Alert System")
    logger.info(f"Target rate: {config.TARGET_RATE}%")
    logger.info(f"State: {config.STATE}")
    logger.info(f"Rate source: {config.RATE_SOURCE}")
    logger.info(f"Notification method: {config.NOTIFICATION_METHOD}")
    logger.info(f"Daily report mode: {config.DAILY_REPORT}")
    
    # Load credentials from environment
    load_credentials_from_env()
    
    # Get current rate
    current_rate = get_current_rate()
    
    if current_rate is None:
        logger.error("Could not retrieve current rate")
        return False
    
    logger.info(f"Current refinance rate: {current_rate}%")
    
    # Check if alert should be sent
    if should_send_alert(current_rate):
        if config.DAILY_REPORT:
            logger.info(f"Daily rate report: {current_rate}% - sending report")
        else:
            logger.info(f"Rate {current_rate}% is below target {config.TARGET_RATE}% - sending alert")
        return send_alert(current_rate)
    else:
        logger.info(f"Rate {current_rate}% is above target {config.TARGET_RATE}% - no alert needed")
        return True


if __name__ == "__main__":
    setup_logging()
    success = main()
    sys.exit(0 if success else 1) 