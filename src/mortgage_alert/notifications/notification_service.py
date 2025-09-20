"""
Base notification service class
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class NotificationService(ABC):
    """Base class for notification services"""
    
    @abstractmethod
    def send_alert(self, current_rate: float, target_rate: float, state: str, 
                   source_data: Dict[str, Any] = None, notification_type: str = "alert") -> bool:
        """Send rate alert notification"""
        pass
    
    def _create_message_content(self, current_rate: float, target_rate: float, state: str,
                               source_data: Dict[str, Any] = None, notification_type: str = "alert") -> Dict[str, str]:
        """Create message content for notifications"""
        is_alert = notification_type == "alert"
        savings = target_rate - current_rate
        current_date = self._get_current_date()
        
        # Determine title and subtitle
        if is_alert:
            title = "🚨 Refinance Rate Alert"
            subtitle = "Great News! Rates have dropped below your target."
        else:
            title = "📊 Daily Refinance Rate Report"
            subtitle = "Here's today's refinance rate update."
        
        # Add source information if available
        source_info = ""
        if source_data:
            sources = source_data.get('successful_sources', [])
            confidence = source_data.get('confidence', 'unknown')
            if sources:
                source_info = f"Sources: {', '.join(sources)} | Confidence: {confidence}"
        
        return {
            'title': f"{title} - {state}",
            'subtitle': subtitle,
            'current_rate': f"{current_rate}%",
            'target_rate': f"{target_rate}%",
            'state': state,
            'date': current_date,
            'savings': f"{savings:.2f}%" if is_alert else "",
            'is_alert': is_alert,
            'source_info': source_info
        }
    
    def _get_current_date(self) -> str:
        """Get current date formatted for display"""
        from datetime import datetime
        return datetime.now().strftime('%B %d, %Y')
