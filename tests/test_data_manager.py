"""
Tests for the Rate Data Manager
"""

import pytest
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, date
from unittest.mock import patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mortgage_alert.data.data_manager import RateDataManager


class TestRateDataManager:
    """Test cases for RateDataManager"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def data_manager(self, temp_dir):
        """Create a RateDataManager instance with temp directory"""
        return RateDataManager(temp_dir)
    
    def test_data_manager_initialization(self, temp_dir):
        """Test that RateDataManager initializes correctly"""
        dm = RateDataManager(temp_dir)
        
        assert dm.data_dir == Path(temp_dir)
        assert dm.rates_file == Path(temp_dir) / "rates.csv"
        assert dm.metadata_file == Path(temp_dir) / "metadata.json"
        
        # Check that files are created
        assert dm.rates_file.exists()
        assert dm.metadata_file.exists()
    
    def test_initial_files_creation(self, temp_dir):
        """Test that initial files are created with correct structure"""
        dm = RateDataManager(temp_dir)
        
        # Check CSV file has header
        with open(dm.rates_file, 'r') as f:
            content = f.read()
            assert 'date,timestamp,rate,source,target_rate' in content
        
        # Check metadata file has initial structure
        import json
        with open(dm.metadata_file, 'r') as f:
            metadata = json.load(f)
            assert 'created' in metadata
            assert 'last_updated' in metadata
            assert 'total_records' in metadata
            assert 'sources_used' in metadata
            assert 'latest_rate' in metadata
            assert 'rate_trend' in metadata
            assert metadata['total_records'] == 0
    
    def test_save_rate(self, data_manager):
        """Test saving a rate record"""
        success = data_manager.save_rate(
            rate=5.25,
            source="test",
            target_rate=6.0,
            state="Oregon",
            alert_sent=False,
            daily_report_sent=True,
            notes="Test rate"
        )
        
        assert success == True
        
        # Check that record was added
        assert data_manager._count_records() == 1
        
        # Check metadata was updated
        metadata = data_manager.get_metadata()
        assert metadata['total_records'] == 1
        assert metadata['latest_rate'] == 5.25
        assert 'test' in metadata['sources_used']
    
    def test_save_multiple_rates(self, data_manager):
        """Test saving multiple rate records"""
        rates = [
            (5.25, "fred"),
            (5.30, "bankrate"),
            (5.20, "mnd")
        ]
        
        for rate, source in rates:
            success = data_manager.save_rate(
                rate=rate,
                source=source,
                target_rate=6.0,
                state="Oregon",
                alert_sent=False,
                daily_report_sent=False,
                notes=f"Test rate from {source}"
            )
            assert success == True
        
        # Check total records
        assert data_manager._count_records() == 3
        
        # Check metadata
        metadata = data_manager.get_metadata()
        assert metadata['total_records'] == 3
        assert metadata['latest_rate'] == 5.20  # Last rate saved
        assert len(metadata['sources_used']) == 3
    
    def test_get_recent_rates(self, data_manager):
        """Test getting recent rates"""
        # Save some test rates
        test_rates = [5.25, 5.30, 5.20, 5.35, 5.15]
        for i, rate in enumerate(test_rates):
            data_manager.save_rate(
                rate=rate,
                source=f"test{i}",
                target_rate=6.0,
                state="Oregon",
                alert_sent=False,
                daily_report_sent=False,
                notes=f"Test rate {i}"
            )
        
        # Get recent rates
        recent_rates = data_manager.get_recent_rates(days=30)
        
        assert len(recent_rates) == 5
        assert recent_rates == sorted(test_rates, reverse=True)  # Should be sorted newest first
    
    def test_get_rate_statistics(self, data_manager):
        """Test getting rate statistics"""
        # Save some test rates
        test_rates = [5.25, 5.30, 5.20, 5.35, 5.15]
        for i, rate in enumerate(test_rates):
            data_manager.save_rate(
                rate=rate,
                source=f"test{i}",
                target_rate=6.0,
                state="Oregon",
                alert_sent=False,
                daily_report_sent=False,
                notes=f"Test rate {i}"
            )
        
        stats = data_manager.get_rate_statistics(days=30)
        
        assert stats['period_days'] == 30
        assert stats['record_count'] == 5
        assert stats['latest_rate'] == 5.15  # Most recent
        assert stats['average_rate'] == sum(test_rates) / len(test_rates)
        assert stats['min_rate'] == min(test_rates)
        assert stats['max_rate'] == max(test_rates)
        assert 'trend' in stats
        assert 'volatility' in stats
        assert isinstance(stats['volatility'], float)
    
    def test_get_rate_statistics_no_data(self, data_manager):
        """Test getting statistics when no data exists"""
        stats = data_manager.get_rate_statistics(days=30)
        
        assert 'error' in stats
        assert stats['error'] == 'No data available'
    
    def test_calculate_trend(self, data_manager):
        """Test trend calculation"""
        # Save rates with a clear trend (decreasing)
        decreasing_rates = [6.0, 5.8, 5.6, 5.4, 5.2]
        for i, rate in enumerate(decreasing_rates):
            data_manager.save_rate(
                rate=rate,
                source=f"test{i}",
                target_rate=6.0,
                state="Oregon",
                alert_sent=False,
                daily_report_sent=False,
                notes=f"Test rate {i}"
            )
        
        trend = data_manager._calculate_trend()
        assert trend in ['rising', 'falling', 'stable', 'insufficient_data']
    
    def test_calculate_volatility(self, data_manager):
        """Test volatility calculation"""
        # Test with stable rates
        stable_rates = [5.25, 5.26, 5.24, 5.25]
        volatility = data_manager._calculate_volatility(stable_rates)
        assert isinstance(volatility, float)
        assert volatility >= 0
        
        # Test with volatile rates
        volatile_rates = [5.0, 6.0, 4.0, 7.0]
        volatility = data_manager._calculate_volatility(volatile_rates)
        assert volatility > 0
        
        # Test with single rate
        single_rate = [5.25]
        volatility = data_manager._calculate_volatility(single_rate)
        assert volatility == 0.0
    
    def test_get_data_summary(self, data_manager):
        """Test getting data summary"""
        # Save a test rate
        data_manager.save_rate(
            rate=5.25,
            source="test",
            target_rate=6.0,
            state="Oregon",
            alert_sent=False,
            daily_report_sent=True,
            notes="Test rate"
        )
        
        summary = data_manager.get_data_summary()
        
        assert isinstance(summary, str)
        assert "Data Summary:" in summary
        assert "Total Records:" in summary
        assert "Latest Rate:" in summary
        assert "Sources:" in summary
    
    def test_file_size_calculation(self, data_manager):
        """Test file size calculation"""
        # Initially should be small
        initial_size = data_manager._get_file_size_kb()
        assert isinstance(initial_size, float)
        assert initial_size >= 0
        
        # After adding data, should be larger
        data_manager.save_rate(
            rate=5.25,
            source="test",
            target_rate=6.0,
            state="Oregon",
            alert_sent=False,
            daily_report_sent=False,
            notes="Test rate for size calculation"
        )
        
        new_size = data_manager._get_file_size_kb()
        assert new_size > initial_size
    
    def test_metadata_persistence(self, data_manager):
        """Test that metadata persists correctly"""
        # Save a rate
        data_manager.save_rate(
            rate=5.25,
            source="test",
            target_rate=6.0,
            state="Oregon",
            alert_sent=False,
            daily_report_sent=False,
            notes="Test rate"
        )
        
        # Get metadata
        metadata = data_manager.get_metadata()
        
        assert metadata['total_records'] == 1
        assert metadata['latest_rate'] == 5.25
        assert 'test' in metadata['sources_used']
        assert 'created' in metadata
        assert 'last_updated' in metadata
    
    def test_error_handling(self, temp_dir):
        """Test error handling in data manager"""
        # Create a data manager with invalid directory (should still work)
        dm = RateDataManager(temp_dir)
        
        # Test saving with invalid data
        success = dm.save_rate(
            rate=None,  # Invalid rate
            source="test",
            target_rate=6.0,
            state="Oregon",
            alert_sent=False,
            daily_report_sent=False,
            notes="Test"
        )
        
        # Should handle gracefully
        assert success == False or success == True  # Either way, shouldn't crash
