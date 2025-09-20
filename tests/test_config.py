"""
Tests for the Config class
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mortgage_alert.core.config import Config


class TestConfig:
    """Test cases for Config class"""
    
    def test_config_initialization(self):
        """Test that Config initializes with default values"""
        config = Config()
        assert config.target_rate == 6.0
        assert config.state == "Oregon"
        assert config.notification_method == "email"
        assert config.daily_report == False
        assert config.log_level == "INFO"
        assert config.log_file == "alert.log"
        assert config.data_dir == "data"
    
    def test_config_environment_variables(self):
        """Test that Config reads environment variables correctly"""
        with patch.dict(os.environ, {
            'TARGET_RATE': '5.5',
            'STATE': 'California',
            'NOTIFICATION_METHOD': 'telegram',
            'DAILY_REPORT': 'true',
            'LOG_LEVEL': 'DEBUG'
        }):
            config = Config()
            assert config.target_rate == 5.5
            assert config.state == "California"
            assert config.notification_method == "telegram"
            assert config.daily_report == True
            assert config.log_level == "DEBUG"
    
    def test_config_type_casting(self):
        """Test that Config properly casts environment variable types"""
        with patch.dict(os.environ, {
            'TARGET_RATE': '7.25',
            'SMTP_PORT': '465',
            'DAILY_REPORT': 'true',
            'SMTP_PORT': '587'
        }):
            config = Config()
            assert isinstance(config.target_rate, float)
            assert config.target_rate == 7.25
            assert isinstance(config.email_config['smtp_port'], int)
            assert config.email_config['smtp_port'] == 587
            assert isinstance(config.daily_report, bool)
            assert config.daily_report == True
    
    def test_config_validation(self):
        """Test configuration validation"""
        config = Config()
        validation = config.validate()
        
        # Should have validation keys
        assert 'email' in validation
        assert 'telegram' in validation
        assert 'target_rate' in validation
        assert 'state' in validation
        assert 'valid' in validation
        
        # Target rate should be valid (between 0 and 20)
        assert validation['target_rate'] == True
        
        # State should be valid (non-empty)
        assert validation['state'] == True
    
    def test_config_validation_invalid_target_rate(self):
        """Test validation with invalid target rate"""
        with patch.dict(os.environ, {'TARGET_RATE': '25'}):
            config = Config()
            validation = config.validate()
            assert validation['target_rate'] == False
            assert validation['valid'] == False
    
    def test_config_validation_invalid_state(self):
        """Test validation with invalid state"""
        with patch.dict(os.environ, {'STATE': ''}):
            config = Config()
            validation = config.validate()
            assert validation['state'] == False
            assert validation['valid'] == False
    
    def test_config_email_validation(self):
        """Test email configuration validation"""
        # Test with complete email config
        with patch.dict(os.environ, {
            'SENDER_EMAIL': 'test@example.com',
            'SENDER_PASSWORD': 'password',
            'RECIPIENT_EMAIL': 'recipient@example.com',
            'NOTIFICATION_METHOD': 'email'
        }):
            config = Config()
            validation = config.validate()
            assert validation['email'] == True
        
        # Test with incomplete email config
        with patch.dict(os.environ, {
            'NOTIFICATION_METHOD': 'email'
            # Missing email credentials
        }):
            config = Config()
            validation = config.validate()
            assert validation['email'] == False
    
    def test_config_telegram_validation(self):
        """Test telegram configuration validation"""
        # Test with complete telegram config
        with patch.dict(os.environ, {
            'TELEGRAM_BOT_TOKEN': 'bot_token',
            'TELEGRAM_CHAT_ID': 'chat_id',
            'NOTIFICATION_METHOD': 'telegram'
        }):
            config = Config()
            validation = config.validate()
            assert validation['telegram'] == True
        
        # Test with incomplete telegram config
        with patch.dict(os.environ, {
            'NOTIFICATION_METHOD': 'telegram'
            # Missing telegram credentials
        }):
            config = Config()
            validation = config.validate()
            assert validation['telegram'] == False
    
    def test_config_get_summary(self):
        """Test configuration summary generation"""
        config = Config()
        summary = config.get_summary()
        
        assert 'target_rate' in summary
        assert 'state' in summary
        assert 'rate_source' in summary
        assert 'notification_method' in summary
        assert 'daily_report' in summary
        assert 'log_level' in summary
        assert 'preferred_sources' in summary
        assert 'validation' in summary
        
        # Check that preferred sources is a list
        assert isinstance(summary['preferred_sources'], list)
        assert len(summary['preferred_sources']) > 0
    
    def test_config_repr(self):
        """Test string representation of config"""
        config = Config()
        repr_str = repr(config)
        assert 'Config(' in repr_str
        assert 'target_rate=' in repr_str
        assert 'state=' in repr_str
        assert 'method=' in repr_str
