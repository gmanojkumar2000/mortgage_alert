"""
Main Alert System class that orchestrates the mortgage rate monitoring
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

from ..scrapers.rate_scraper import EnhancedRateScraper
from ..data.data_manager import RateDataManager
from ..notifications.notification_service import NotificationService
from .config import config


class AlertSystem:
    """Main alert system that coordinates rate monitoring and notifications"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rate_scraper = EnhancedRateScraper()
        self.data_manager = RateDataManager(config.data_dir)
        self.notification_service = self._get_notification_service()
        
    def _get_notification_service(self) -> Optional[NotificationService]:
        """Get the appropriate notification service based on configuration"""
        try:
            if config.notification_method == "email":
                from ..notifications.email_service import EmailNotificationService
                return EmailNotificationService(config.email_config)
            elif config.notification_method == "telegram":
                from ..notifications.telegram_service import TelegramNotificationService
                return TelegramNotificationService(config.telegram_config)
            else:
                self.logger.error(f"Unknown notification method: {config.notification_method}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to initialize notification service: {e}")
            return None
    
    def get_current_rate(self) -> Tuple[Optional[float], Dict[str, Any]]:
        """Get current rate with multi-source aggregation"""
        self.logger.info("Fetching current refinance rate...")
        
        try:
            # Get aggregated rate from multiple sources
            rate, source_data = self.rate_scraper.get_aggregated_rate(config.preferred_sources)
            
            if rate is not None:
                self.logger.info(f"Successfully retrieved aggregated rate: {rate}%")
                self.logger.info(f"Rate confidence: {source_data.get('confidence', 'unknown')}")
                self.logger.info(f"Sources used: {', '.join(source_data.get('successful_sources', []))}")
                return rate, source_data
            else:
                self.logger.warning("No rate retrieved from any source")
                return None, {'error': 'No rate found'}
                
        except Exception as e:
            self.logger.error(f"Error getting current rate: {e}")
            return None, {'error': str(e)}
    
    def should_send_alert(self, current_rate: float) -> bool:
        """Check if alert should be sent based on current rate"""
        # If daily report is enabled, always send
        if config.daily_report:
            return True
        
        # Otherwise, only send if rate is below target
        return current_rate < config.target_rate
    
    def send_notification(self, current_rate: float, source_data: Dict[str, Any]) -> bool:
        """Send notification with enhanced data"""
        if not self.notification_service:
            self.logger.error("No notification service available")
            return False
        
        try:
            # Determine notification type
            is_alert = current_rate < config.target_rate
            notification_type = "alert" if is_alert else "daily_report"
            
            # Send notification
            success = self.notification_service.send_alert(
                current_rate=current_rate,
                target_rate=config.target_rate,
                state=config.state,
                source_data=source_data,
                notification_type=notification_type
            )
            
            if success:
                self.logger.info(f"{notification_type.capitalize()} sent successfully")
            else:
                self.logger.error(f"Failed to send {notification_type}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")
            return False
    
    def save_rate_data(self, current_rate: float, source_data: Dict[str, Any], 
                      alert_sent: bool = False, daily_report_sent: bool = False) -> bool:
        """Save rate data to persistence layer"""
        try:
            notes = f"Sources: {', '.join(source_data.get('successful_sources', []))}, Confidence: {source_data.get('confidence', 'unknown')}"
            
            success = self.data_manager.save_rate(
                rate=current_rate,
                source=','.join(source_data.get('successful_sources', ['unknown'])),
                target_rate=config.target_rate,
                state=config.state,
                alert_sent=alert_sent,
                daily_report_sent=daily_report_sent,
                notes=notes
            )
            
            if success:
                self.logger.info("Rate data saved successfully")
            else:
                self.logger.error("Failed to save rate data")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error saving rate data: {e}")
            return False
    
    def run_alert_check(self) -> bool:
        """Run the complete alert check process"""
        self.logger.info("Starting mortgage rate alert check")
        
        try:
            # Log configuration summary
            config_summary = config.get_summary()
            self.logger.info(f"Configuration: {config_summary}")
            
            # Validate configuration
            validation = config.validate()
            if not validation.get("valid", False):
                self.logger.error(f"Configuration validation failed: {validation}")
                return False
            
            # Get current rate
            current_rate, source_data = self.get_current_rate()
            
            if current_rate is None:
                self.logger.error("Could not retrieve current rate")
                return False
            
            # Determine if notification should be sent
            should_alert = self.should_send_alert(current_rate)
            alert_sent = False
            daily_report_sent = False
            
            # Send notification if needed
            if should_alert:
                if config.daily_report:
                    self.logger.info(f"Daily rate report: {current_rate}% - sending report")
                    daily_report_sent = True
                else:
                    self.logger.info(f"Rate {current_rate}% is below target {config.target_rate}% - sending alert")
                    alert_sent = True
                
                # Send notification
                notification_success = self.send_notification(current_rate, source_data)
                if not notification_success:
                    self.logger.error("Failed to send notification")
            else:
                self.logger.info(f"Rate {current_rate}% is above target {config.target_rate}% - no alert needed")
            
            # Save rate data
            self.save_rate_data(current_rate, source_data, alert_sent, daily_report_sent)
            
            # Log data summary
            self.logger.info("Data Summary:")
            self.logger.info(self.data_manager.get_data_summary())
            
            self.logger.info("Alert check completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in alert check: {e}")
            return False
    
    def get_rate_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get rate statistics for the specified period"""
        return self.data_manager.get_rate_statistics(days)
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get current metadata"""
        return self.data_manager.get_metadata()
