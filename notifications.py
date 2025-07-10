"""
Notifications Module
Handles email and Telegram notifications for rate alerts
"""

import smtplib
import requests
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class NotificationService:
    """Base class for notification services"""
    
    def send_alert(self, current_rate: float, target_rate: float, state: str) -> bool:
        """Send rate alert notification"""
        raise NotImplementedError


class EmailNotificationService(NotificationService):
    """Email notification service using SMTP"""
    
    def __init__(self, config: Dict[str, Any]):
        self.smtp_server = config.get("smtp_server", "smtp.gmail.com")
        self.smtp_port = config.get("smtp_port", 587)
        self.sender_email = config.get("sender_email", "")
        self.sender_password = config.get("sender_password", "")
        self.recipient_emails = config.get("recipient_email", "").split(',')
        
        # Clean up email addresses (remove whitespace)
        self.recipient_emails = [email.strip() for email in self.recipient_emails if email.strip()]
        
        if not all([self.sender_email, self.sender_password]) or not self.recipient_emails:
            raise ValueError("Email configuration incomplete. Please check sender_email, sender_password, and recipient_email.")
    
    def send_alert(self, current_rate: float, target_rate: float, state: str) -> bool:
        """Send email alert to all recipients"""
        logger = logging.getLogger(__name__)
        
        try:
            # Create message
            subject = f"🚨 Refinance Rate Alert - {state}"
            body = self._create_email_body(current_rate, target_rate, state)
            
            # Create MIME message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(self.recipient_emails)  # Join all recipients
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"Email alert sent successfully to {len(self.recipient_emails)} recipients: {', '.join(self.recipient_emails)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False
    
    def _create_email_body(self, current_rate: float, target_rate: float, state: str) -> str:
        """Create HTML email body"""
        savings = target_rate - current_rate
        current_date = datetime.now().strftime('%B %d, %Y')
        
        # Determine if this is an alert or daily report
        is_alert = current_rate < target_rate
        title = "🚨 Refinance Rate Alert" if is_alert else "📊 Daily Refinance Rate Report"
        subtitle = "Great News! Rates have dropped below your target." if is_alert else "Here's today's refinance rate update."
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid {'#28a745' if is_alert else '#007bff'};">
                <h2 style="color: {'#28a745' if is_alert else '#007bff'}; margin-top: 0;">{title} - {state}</h2>
                <p style="color: #666; margin-bottom: 20px;">{subtitle}</p>
                
                <div style="background-color: white; padding: 15px; border-radius: 8px; margin: 15px 0;">
                    <h3 style="margin-top: 0; color: #333;">Current Rate: <span style="color: {'#28a745' if is_alert else '#007bff'}; font-weight: bold;">{current_rate}%</span></h3>
                    <p style="margin: 5px 0; color: #666;">Target Rate: {target_rate}%</p>
                    <p style="margin: 5px 0; color: #666;">State: {state}</p>
                    <p style="margin: 5px 0; color: #666;">Date: {current_date}</p>
                    {f'<p style="margin: 5px 0; color: #666;">Potential Savings: <strong>{savings:.2f}%</strong></p>' if is_alert else ''}
                </div>
                
                {f'''
                <div style="background-color: #e8f5e8; padding: 15px; border-radius: 8px; margin: 15px 0;">
                    <h4 style="margin-top: 0; color: #155724;">What This Means:</h4>
                    <ul style="color: #155724;">
                        <li>Current refinance rates are below your target threshold</li>
                        <li>This could be a good time to consider refinancing</li>
                        <li>Contact your mortgage lender to discuss options</li>
                    </ul>
                </div>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; margin: 15px 0;">
                    <h4 style="margin-top: 0; color: #856404;">Next Steps:</h4>
                    <ol style="color: #856404;">
                        <li>Contact multiple lenders for quotes</li>
                        <li>Compare closing costs and fees</li>
                        <li>Calculate your break-even point</li>
                        <li>Consider your long-term financial goals</li>
                    </ol>
                </div>
                ''' if is_alert else '''
                <div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0;">
                    <h4 style="margin-top: 0; color: #0d47a1;">Rate Analysis:</h4>
                    <ul style="color: #0d47a1;">
                        <li>Current market conditions and trends</li>
                        <li>Historical rate comparison</li>
                        <li>Refinancing considerations</li>
                    </ul>
                </div>
                '''}
                
                <p style="color: #666; font-size: 12px; margin-top: 20px;">
                    Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
                </p>
            </div>
        </body>
        </html>
        """
        
        return html_body


class TelegramNotificationService(NotificationService):
    """Telegram notification service using bot API"""
    
    def __init__(self, config: Dict[str, Any]):
        self.bot_token = config.get("bot_token")
        self.chat_id = config.get("chat_id")
        
        if not all([self.bot_token, self.chat_id]):
            raise ValueError("Telegram configuration incomplete. Please check bot_token and chat_id.")
    
    def send_alert(self, current_rate: float, target_rate: float, state: str) -> bool:
        """Send Telegram alert"""
        try:
            message = self._create_telegram_message(current_rate, target_rate, state)
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Telegram alert sent successfully to chat {self.chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return False
    
    def _create_telegram_message(self, current_rate: float, target_rate: float, state: str) -> str:
        """Create Telegram message"""
        savings = target_rate - current_rate
        current_date = datetime.now().strftime('%B %d, %Y')
        
        # Determine if this is an alert or daily report
        is_alert = current_rate < target_rate
        title = "🚨 Refinance Rate Alert" if is_alert else "📊 Daily Refinance Rate Report"
        subtitle = "Great News! Current refinance rates have dropped below your target threshold." if is_alert else "Here's today's refinance rate update."
        
        message = f"""
{title} - {state}

{subtitle}

📊 <b>Rate Information:</b>
• Current Rate: <b>{current_rate}%</b>
• Target Rate: {target_rate}%
• Date: {current_date}
{f'• Potential Savings: <b>{savings:.2f}%</b>' if is_alert else ''}

{f'''
💡 <b>What This Means:</b>
• This could be a good time to consider refinancing
• Contact your mortgage lender to discuss options
• Compare rates from multiple lenders

📋 <b>Next Steps:</b>
1. Contact multiple lenders for quotes
2. Compare closing costs and fees
3. Calculate your break-even point
4. Consider your long-term financial goals
''' if is_alert else '''
📈 <b>Rate Analysis:</b>
• Current market conditions and trends
• Historical rate comparison
• Refinancing considerations
'''}

⏰ Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        """
        
        return message.strip()


def get_notification_service(method: str, config: Dict[str, Any]) -> NotificationService:
    """Factory function to get appropriate notification service"""
    services = {
        "email": EmailNotificationService,
        "telegram": TelegramNotificationService
    }
    
    service_class = services.get(method.lower())
    if not service_class:
        raise ValueError(f"Unknown notification method: {method}")
    
    return service_class(config) 