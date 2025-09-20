"""
Data Manager Module - GitHub Artifacts Version
Handles persistence of rate data using GitHub Artifacts (100% FREE)
"""

import csv
import json
import os
import logging
from datetime import datetime, date
from typing import List, Dict, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class RateDataManager:
    """Manages rate data persistence using GitHub Artifacts"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.rates_file = self.data_dir / "rates.csv"
        self.metadata_file = self.data_dir / "metadata.json"
        
        # Create data directory if it doesn't exist
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize data files if they don't exist"""
        # Initialize rates CSV
        if not self.rates_file.exists():
            with open(self.rates_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'date', 'timestamp', 'rate', 'source', 'target_rate', 
                    'state', 'alert_sent', 'daily_report_sent', 'notes'
                ])
            logger.info(f"Created new rates file: {self.rates_file}")
        
        # Initialize metadata JSON
        if not self.metadata_file.exists():
            metadata = {
                'created': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'total_records': 0,
                'sources_used': [],
                'latest_rate': None,
                'rate_trend': 'unknown',
                'data_size_kb': 0
            }
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"Created new metadata file: {self.metadata_file}")
    
    def save_rate(self, rate: float, source: str, target_rate: float, 
                  state: str, alert_sent: bool = False, 
                  daily_report_sent: bool = False, notes: str = "") -> bool:
        """Save a new rate record"""
        try:
            current_time = datetime.now()
            current_date = current_time.date()
            
            # Always append new record (simple and reliable)
            with open(self.rates_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    current_date.isoformat(),
                    current_time.isoformat(),
                    rate,
                    source,
                    target_rate,
                    state,
                    alert_sent,
                    daily_report_sent,
                    notes
                ])
            logger.info(f"Saved rate record: {rate}% from {source}")
            
            # Update metadata
            self._update_metadata(rate, source)
            return True
            
        except Exception as e:
            logger.error(f"Failed to save rate data: {e}")
            return False
    
    def _update_metadata(self, rate: float, source: str):
        """Update metadata file"""
        try:
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Update metadata
            metadata['last_updated'] = datetime.now().isoformat()
            metadata['latest_rate'] = rate
            metadata['total_records'] = self._count_records()
            metadata['data_size_kb'] = self._get_file_size_kb()
            
            if source not in metadata['sources_used']:
                metadata['sources_used'].append(source)
            
            # Calculate trend
            metadata['rate_trend'] = self._calculate_trend()
            
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to update metadata: {e}")
    
    def _count_records(self) -> int:
        """Count total number of rate records"""
        try:
            with open(self.rates_file, 'r', newline='') as f:
                reader = csv.reader(f)
                return sum(1 for row in reader) - 1  # Subtract header
        except Exception:
            return 0
    
    def _get_file_size_kb(self) -> float:
        """Get file size in KB"""
        try:
            size_bytes = os.path.getsize(self.rates_file)
            return round(size_bytes / 1024, 2)
        except Exception:
            return 0
    
    def _calculate_trend(self) -> str:
        """Calculate rate trend over last 7 days"""
        try:
            recent_rates = self.get_recent_rates(days=7)
            if len(recent_rates) < 2:
                return 'insufficient_data'
            
            # Simple trend calculation
            first_half = recent_rates[:len(recent_rates)//2]
            second_half = recent_rates[len(recent_rates)//2:]
            
            if not first_half or not second_half:
                return 'insufficient_data'
            
            avg_first = sum(first_half) / len(first_half)
            avg_second = sum(second_half) / len(second_half)
            
            if avg_second > avg_first + 0.1:
                return 'rising'
            elif avg_second < avg_first - 0.1:
                return 'falling'
            else:
                return 'stable'
                
        except Exception as e:
            logger.error(f"Error calculating trend: {e}")
            return 'unknown'
    
    def get_recent_rates(self, days: int = 30) -> List[float]:
        """Get recent rates for trend analysis"""
        try:
            rates = []
            cutoff_date = datetime.now().date().replace(day=max(1, datetime.now().day - days))
            
            with open(self.rates_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        record_date = datetime.fromisoformat(row['date']).date()
                        if record_date >= cutoff_date:
                            rates.append(float(row['rate']))
                    except (ValueError, KeyError):
                        continue
            
            return sorted(rates, reverse=True)  # Most recent first
            
        except Exception as e:
            logger.error(f"Error getting recent rates: {e}")
            return []
    
    def get_rate_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get rate statistics for the specified period"""
        try:
            rates = self.get_recent_rates(days)
            if not rates:
                return {'error': 'No data available'}
            
            return {
                'period_days': days,
                'record_count': len(rates),
                'latest_rate': rates[0] if rates else None,
                'average_rate': round(sum(rates) / len(rates), 3),
                'min_rate': min(rates),
                'max_rate': max(rates),
                'trend': self._calculate_trend(),
                'volatility': round(self._calculate_volatility(rates), 3),
                'data_size_kb': self._get_file_size_kb()
            }
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {'error': str(e)}
    
    def _calculate_volatility(self, rates: List[float]) -> float:
        """Calculate rate volatility (standard deviation)"""
        if len(rates) < 2:
            return 0.0
        
        mean = sum(rates) / len(rates)
        variance = sum((rate - mean) ** 2 for rate in rates) / len(rates)
        return variance ** 0.5
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get current metadata"""
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading metadata: {e}")
            return {}
    
    def get_data_summary(self) -> str:
        """Get a summary of stored data for logging"""
        metadata = self.get_metadata()
        stats = self.get_rate_statistics(30)
        
        return f"""Data Summary:
- Total Records: {metadata.get('total_records', 0)}
- Latest Rate: {metadata.get('latest_rate', 'N/A')}%
- Trend: {metadata.get('rate_trend', 'unknown')}
- Data Size: {metadata.get('data_size_kb', 0)} KB
- Sources: {', '.join(metadata.get('sources_used', []))}
- Last 30 Days: {stats.get('record_count', 0)} records, Avg: {stats.get('average_rate', 'N/A')}%"""


# Global data manager instance
data_manager = RateDataManager()