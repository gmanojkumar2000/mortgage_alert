"""
Tests for the Enhanced Rate Scraper
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mortgage_alert.scrapers.rate_scraper import EnhancedRateScraper, get_enhanced_rate_scraper, get_mock_rate


class TestEnhancedRateScraper:
    """Test cases for EnhancedRateScraper"""
    
    def test_enhanced_rate_scraper_initialization(self):
        """Test that EnhancedRateScraper initializes correctly"""
        scraper = EnhancedRateScraper()
        assert scraper is not None
        assert hasattr(scraper, 'rate_sources')
        assert isinstance(scraper.rate_sources, dict)
        assert len(scraper.rate_sources) > 0
    
    def test_rate_validation(self):
        """Test rate validation functionality"""
        scraper = EnhancedRateScraper()
        
        # Test valid rates
        valid_rates = [4.5, 5.25, 6.0, 7.5, 8.0]
        for rate in valid_rates:
            assert scraper._validate_rate(rate) == True, f"Rate {rate} should be valid"
        
        # Test invalid rates
        invalid_rates = [0, 1.5, 16.0, 25.0, -1.0, 0.0]
        for rate in invalid_rates:
            assert scraper._validate_rate(rate) == False, f"Rate {rate} should be invalid"
        
        # Test edge cases
        assert scraper._validate_rate(2.0) == True  # Minimum valid
        assert scraper._validate_rate(15.0) == True  # Maximum valid
        assert scraper._validate_rate(1.99) == False  # Just below minimum
        assert scraper._validate_rate(15.01) == False  # Just above maximum
    
    def test_rate_extraction_from_text(self):
        """Test rate extraction from various text formats"""
        scraper = EnhancedRateScraper()
        
        test_cases = [
            ("5.25%", 5.25),
            ("5.25 percent", 5.25),
            ("rate: 5.25", 5.25),
            ("5.25 APR", 5.25),
            ("5.25 interest", 5.25),
            ("5.25 fixed", 5.25),
            ("5.25 refinance", 5.25),
            ("Current rate is 5.25%", 5.25),
            ("The mortgage rate is 6.75% today", 6.75),
        ]
        
        for text, expected_rate in test_cases:
            result = scraper._extract_rate_from_text(text)
            assert result == expected_rate, f"Failed to extract {expected_rate} from '{text}'"
    
    def test_rate_extraction_invalid_text(self):
        """Test rate extraction with invalid text"""
        scraper = EnhancedRateScraper()
        
        invalid_texts = [
            "",
            "No rate here",
            "25.5%",  # Too high
            "1.5%",   # Too low
            "rate: 0%",  # Zero rate
            "invalid text",
            "5.25.5%",  # Invalid format
        ]
        
        for text in invalid_texts:
            result = scraper._extract_rate_from_text(text)
            assert result is None, f"Should not extract rate from '{text}'"
    
    def test_confidence_calculation(self):
        """Test confidence calculation"""
        scraper = EnhancedRateScraper()
        
        # High confidence: multiple sources with low variance
        rates_high = [5.25, 5.30, 5.20]
        sources_high = ['fred', 'bankrate', 'mnd']
        confidence = scraper._calculate_confidence(rates_high, sources_high)
        assert confidence == 'high'
        
        # Medium confidence: multiple sources with moderate variance
        rates_medium = [5.25, 5.50]
        sources_medium = ['fred', 'bankrate']
        confidence = scraper._calculate_confidence(rates_medium, sources_medium)
        assert confidence == 'medium'
        
        # Low confidence: few sources or high variance
        rates_low = [5.25, 6.50]
        sources_low = ['fred', 'bankrate']
        confidence = scraper._calculate_confidence(rates_low, sources_low)
        assert confidence == 'low'
        
        # Single source should be low confidence
        rates_single = [5.25]
        sources_single = ['fred']
        confidence = scraper._calculate_confidence(rates_single, sources_single)
        assert confidence == 'low'
    
    @patch('mortgage_alert.scrapers.rate_scraper.requests.Session.get')
    def test_fred_rate_scraping(self, mock_get):
        """Test FRED rate scraping with mocked response"""
        scraper = EnhancedRateScraper()
        
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            'observations': [
                {'value': '5.25'}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Mock environment variable for API key
        with patch.dict('os.environ', {'FRED_API_KEY': 'test_key'}):
            rate = scraper._get_fred_rate()
            assert rate == 5.25
    
    @patch('mortgage_alert.scrapers.rate_scraper.requests.Session.get')
    def test_bankrate_scraping(self, mock_get):
        """Test Bankrate scraping with mocked response"""
        scraper = EnhancedRateScraper()
        
        # Mock successful response with HTML content
        mock_response = Mock()
        mock_response.content = b'<html><body><div class="rate-value">5.25%</div></body></html>'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        rate = scraper._get_bankrate_rate()
        assert rate == 5.25
    
    def test_get_aggregated_rate_mock(self):
        """Test aggregated rate calculation with mocked sources"""
        scraper = EnhancedRateScraper()
        
        # Mock individual source methods
        with patch.object(scraper, '_get_fred_rate', return_value=5.25), \
             patch.object(scraper, '_get_bankrate_rate', return_value=5.30), \
             patch.object(scraper, '_get_mnd_rate', return_value=5.20):
            
            rate, source_data = scraper.get_aggregated_rate(['fred', 'bankrate', 'mortgage_news_daily'])
            
            assert rate is not None
            assert 5.20 <= rate <= 5.30  # Should be median (5.25)
            assert 'aggregated_rate' in source_data
            assert 'source_rates' in source_data
            assert 'successful_sources' in source_data
            assert 'confidence' in source_data
            assert len(source_data['successful_sources']) == 3
    
    def test_get_aggregated_rate_no_sources(self):
        """Test aggregated rate when no sources work"""
        scraper = EnhancedRateScraper()
        
        # Mock all sources to return None
        with patch.object(scraper, '_get_fred_rate', return_value=None), \
             patch.object(scraper, '_get_bankrate_rate', return_value=None):
            
            rate, source_data = scraper.get_aggregated_rate(['fred', 'bankrate'])
            
            assert rate is None
            assert 'error' in source_data
            assert source_data['error'] == 'No valid rates found'
    
    def test_get_aggregated_rate_mixed_results(self):
        """Test aggregated rate with some sources working"""
        scraper = EnhancedRateScraper()
        
        # Mock mixed results
        with patch.object(scraper, '_get_fred_rate', return_value=5.25), \
             patch.object(scraper, '_get_bankrate_rate', return_value=None), \
             patch.object(scraper, '_get_mnd_rate', return_value=5.30):
            
            rate, source_data = scraper.get_aggregated_rate(['fred', 'bankrate', 'mortgage_news_daily'])
            
            assert rate is not None
            assert rate == 5.275  # Average of 5.25 and 5.30
            assert len(source_data['successful_sources']) == 2
            assert 'fred' in source_data['successful_sources']
            assert 'mortgage_news_daily' in source_data['successful_sources']


class TestRateScraperFactory:
    """Test factory functions"""
    
    def test_get_enhanced_rate_scraper(self):
        """Test factory function"""
        scraper = get_enhanced_rate_scraper()
        assert isinstance(scraper, EnhancedRateScraper)
    
    def test_get_mock_rate(self):
        """Test mock rate generation"""
        rate = get_mock_rate()
        assert isinstance(rate, float)
        assert 4.5 <= rate <= 6.5  # Should be in the mock range
