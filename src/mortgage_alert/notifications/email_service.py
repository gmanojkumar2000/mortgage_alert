"""
Email notification service
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
from datetime import datetime

from .notification_service import NotificationService


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
        
        self.logger = logging.getLogger(__name__)
        
        if not all([self.sender_email, self.sender_password]) or not self.recipient_emails:
            raise ValueError("Email configuration incomplete. Please check sender_email, sender_password, and recipient_email.")
    
    def send_alert(self, current_rate: float, target_rate: float, state: str, 
                   source_data: Dict[str, Any] = None, notification_type: str = "alert") -> bool:
        """Send email alert to all recipients"""
        try:
            # Create message content
            content = self._create_message_content(current_rate, target_rate, state, source_data, notification_type)
            
            # Create message
            subject = content['title']
            body = self._create_email_body(content)
            
            # Create MIME message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(self.recipient_emails)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            self.logger.info(f"Email {notification_type} sent successfully to {len(self.recipient_emails)} recipients")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email {notification_type}: {e}")
            return False
    
    def _create_email_body(self, content: Dict[str, Any]) -> str:
        """Create HTML email body"""
        is_alert = content['is_alert']
        color = '#28a745' if is_alert else '#007bff'
        bg_color = '#e8f5e8' if is_alert else '#e3f2fd'
        text_color = '#155724' if is_alert else '#0d47a1'
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid {color};">
                <h2 style="color: {color}; margin-top: 0;">{content['title']}</h2>
                <p style="color: #666; margin-bottom: 20px;">{content['subtitle']}</p>
                
                <div style="background-color: white; padding: 15px; border-radius: 8px; margin: 15px 0;">
                    <h3 style="margin-top: 0; color: #333;">Current Rate: <span style="color: {color}; font-weight: bold;">{content['current_rate']}</span></h3>
                    <p style="margin: 5px 0; color: #666;">Target Rate: {content['target_rate']}</p>
                    <p style="margin: 5px 0; color: #666;">State: {content['state']}</p>
                    <p style="margin: 5px 0; color: #666;">Date: {content['date']}</p>
                    {f'<p style="margin: 5px 0; color: #666;">Potential Savings: <strong>{content["savings"]}</strong></p>' if content['savings'] else ''}
                    {f'<p style="margin: 5px 0; color: #666; font-size: 12px;">{content["source_info"]}</p>' if content['source_info'] else ''}
                </div>
                
                {self._get_action_section(content)}
                
                <p style="color: #666; font-size: 12px; margin-top: 20px;">
                    Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
                </p>
            </div>
        </body>
        </html>
        """
        
        return html_body
    
    def _get_action_section(self, content: Dict[str, Any]) -> str:
        """Get action section based on notification type"""
        is_alert = content['is_alert']
        
        if is_alert:
            return f"""
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
            """
        else:
            return f"""
            <div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0;">
                <h4 style="margin-top: 0; color: #0d47a1;">Rate Analysis:</h4>
                <ul style="color: #0d47a1;">
                    <li>Current market conditions and trends</li>
                    <li>Historical rate comparison</li>
                    <li>Refinancing considerations</li>
                </ul>
            </div>
            """
