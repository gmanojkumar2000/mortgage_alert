#!/usr/bin/env python3
"""
Test script for the Refinance Rate Alert System
"""

import logging
import sys
from rate_scraper import get_rate_scraper, get_mock_rate
from notifications import get_notification_service
import config

# Setup basic logging for testing
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_rate_scraping():
    """Test rate scraping functionality"""
    logger.info("Testing rate scraping...")
    
    try:
        # Test mock rate
        mock_rate = get_mock_rate()
        logger.info(f"Mock rate: {mock_rate}%")
        
        # Test actual scraper
        scraper = get_rate_scraper(config.RATE_SOURCE)
        rate = scraper.get_rate()
        
        if rate:
            logger.info(f"Scraped rate from {config.RATE_SOURCE}: {rate}%")
        else:
            logger.warning(f"Could not scrape rate from {config.RATE_SOURCE}")
        
        return True
        
    except Exception as e:
        logger.error(f"Rate scraping test failed: {e}")
        return False


def test_notification_service():
    """Test notification service setup"""
    logger.info("Testing notification service setup...")
    
    try:
        if config.NOTIFICATION_METHOD == "email":
            service = get_notification_service("email", config.EMAIL_CONFIG)
            logger.info("Email notification service created successfully")
        elif config.NOTIFICATION_METHOD == "telegram":
            service = get_notification_service("telegram", config.TELEGRAM_CONFIG)
            logger.info("Telegram notification service created successfully")
        else:
            logger.error(f"Unknown notification method: {config.NOTIFICATION_METHOD}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Notification service test failed: {e}")
        return False


def test_configuration():
    """Test configuration loading"""
    logger.info("Testing configuration...")
    
    logger.info(f"Target rate: {config.TARGET_RATE}%")
    logger.info(f"State: {config.STATE}")
    logger.info(f"Rate source: {config.RATE_SOURCE}")
    logger.info(f"Notification method: {config.NOTIFICATION_METHOD}")
    
    # Check if credentials are configured
    if config.NOTIFICATION_METHOD == "email":
        email_configured = all([
            config.EMAIL_CONFIG.get("sender_email"),
            config.EMAIL_CONFIG.get("sender_password"),
            config.EMAIL_CONFIG.get("recipient_email")
        ])
        if email_configured:
            recipient_emails = config.EMAIL_CONFIG.get("recipient_email", "").split(',')
            recipient_emails = [email.strip() for email in recipient_emails if email.strip()]
            logger.info(f"Email configuration is complete - {len(recipient_emails)} recipient(s): {', '.join(recipient_emails)}")
        else:
            logger.warning("Email configuration is incomplete")
    
    elif config.NOTIFICATION_METHOD == "telegram":
        telegram_configured = all([
            config.TELEGRAM_CONFIG.get("bot_token"),
            config.TELEGRAM_CONFIG.get("chat_id")
        ])
        if telegram_configured:
            logger.info("Telegram configuration is complete")
        else:
            logger.warning("Telegram configuration is incomplete")
    
    return True


def test_alert_logic():
    """Test alert logic"""
    logger.info("Testing alert logic...")
    
    # Test with rate below threshold
    test_rate_low = 5.0
    should_alert = test_rate_low < config.TARGET_RATE
    logger.info(f"Rate {test_rate_low}% < {config.TARGET_RATE}%: Should alert = {should_alert}")
    
    # Test with rate above threshold
    test_rate_high = 6.0
    should_alert = test_rate_high < config.TARGET_RATE
    logger.info(f"Rate {test_rate_high}% < {config.TARGET_RATE}%: Should alert = {should_alert}")
    
    return True


def main():
    """Run all tests"""
    logger.info("Starting Refinance Rate Alert System Tests")
    
    tests = [
        ("Configuration", test_configuration),
        ("Rate Scraping", test_rate_scraping),
        ("Notification Service", test_notification_service),
        ("Alert Logic", test_alert_logic),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} Test ---")
        try:
            if test_func():
                logger.info(f"✅ {test_name} test passed")
                passed += 1
            else:
                logger.error(f"❌ {test_name} test failed")
        except Exception as e:
            logger.error(f"❌ {test_name} test failed with exception: {e}")
    
    logger.info(f"\n--- Test Results ---")
    logger.info(f"Passed: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 All tests passed!")
        return True
    else:
        logger.error("❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 