"""
Tests for the AlertSystem class
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mortgage_alert.core.alert_system import AlertSystem
from mortgage_alert.core.config import config


class TestAlertSystem:
    """Test cases for AlertSystem"""
    
    def test_alert_system_initialization(self):
        """Test that AlertSystem initializes correctly"""
        alert_system = AlertSystem()
        assert alert_system is not None
        assert alert_system.rate_scraper is not None
        assert alert_system.data_manager is not None
    
    def test_should_send_alert_daily_report(self):
        """Test alert logic when daily report is enabled"""
        # Mock daily report enabled
        original_daily_report = config.daily_report
        config.daily_report = True
        
        alert_system = AlertSystem()
        
        # Should always send when daily report is enabled
        assert alert_system.should_send_alert(7.0) == True  # Above target
        assert alert_system.should_send_alert(5.0) == True  # Below target
        
        # Restore original value
        config.daily_report = original_daily_report
    
    def test_should_send_alert_threshold_only(self):
        """Test alert logic when only threshold alerts are enabled"""
        # Mock daily report disabled
        original_daily_report = config.daily_report
        config.daily_report = False
        
        alert_system = AlertSystem()
        
        # Should only send when below target
        assert alert_system.should_send_alert(7.0) == False  # Above target
        assert alert_system.should_send_alert(5.0) == True   # Below target
        
        # Restore original value
        config.daily_report = original_daily_report
    
    def test_get_current_rate(self):
        """Test getting current rate without contacting external services."""
        alert_system = AlertSystem()
        expected_source_data = {
            'aggregated_rate': 5.25,
            'successful_sources': ['fred'],
        }

        with patch.object(
            alert_system.rate_scraper,
            'get_aggregated_rate',
            return_value=(5.25, expected_source_data),
        ):
            rate, source_data = alert_system.get_current_rate()

        assert rate == 5.25
        assert source_data == expected_source_data
