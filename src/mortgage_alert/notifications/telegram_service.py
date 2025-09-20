"""
Telegram notification service
"""

import requests
import logging
from typing import Dict, Any
from datetime import datetime

from .notification_service import NotificationService


class TelegramNotificationService(NotificationService):
    """Telegram notification service using bot API"""
    
    def __init__(self, config: Dict[str, Any]):
        self.bot_token = config.get("bot_token")
        self.chat_id = config.get("chat_id")
        self.logger = logging.getLogger(__name__)
        
        if not all([self.bot_token, self.chat_id]):
            raise ValueError("Telegram configuration incomplete. Please check bot_token and chat_id.")
    
    def send_alert(self, current_rate: float, target_rate: float, state: str, 
                   source_data: Dict[str, Any] = None, notification_type: str = "alert") -> bool:
        """Send Telegram alert"""
        try:
            # Create message content
            content = self._create_message_content(current_rate, target_rate, state, source_data, notification_type)
            message = self._create_telegram_message(content)
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            
            self.logger.info(f"Telegram {notification_type} sent successfully to chat {self.chat_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send Telegram {notification_type}: {e}")
            return False
    
    def _create_telegram_message(self, content: Dict[str, Any]) -> str:
        """Create Telegram message"""
        is_alert = content['is_alert']
        emoji = "🚨" if is_alert else "📊"
        
        message = f"""
{emoji} <b>{content['title']}</b>

{content['subtitle']}

📊 <b>Rate Information:</b>
• Current Rate: <b>{content['current_rate']}</b>
• Target Rate: {content['target_rate']}
• Date: {content['date']}
{f'• Potential Savings: <b>{content["savings"]}</b>' if content['savings'] else ''}
{f'• {content["source_info"]}' if content['source_info'] else ''}

{self._get_telegram_action_section(content)}

⏰ Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        """
        
        return message.strip()
    
    def _get_telegram_action_section(self, content: Dict[str, Any]) -> str:
        """Get action section for Telegram message"""
        is_alert = content['is_alert']
        
        if is_alert:
            return """
💡 <b>What This Means:</b>
• This could be a good time to consider refinancing
• Contact your mortgage lender to discuss options
• Compare rates from multiple lenders

📋 <b>Next Steps:</b>
1. Contact multiple lenders for quotes
2. Compare closing costs and fees
3. Calculate your break-even point
4. Consider your long-term financial goals
"""
        else:
            return """
📈 <b>Rate Analysis:</b>
• Current market conditions and trends
• Historical rate comparison
• Refinancing considerations
"""
