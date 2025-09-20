"""
Enhanced Rate Scraper Module
Fetches current refinance mortgage rates from multiple sources with improved reliability
"""

import requests
from bs4 import BeautifulSoup
import logging
import statistics
from typing import Optional, Dict, Any, List, Tuple
import time
import random
import os
import re

logger = logging.getLogger(__name__)


class EnhancedRateScraper:
    """Enhanced rate scraper with multiple sources and validation"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.rate_sources = {
            'fred': self._get_fred_rate,
            'bankrate': self._get_bankrate_rate,
            'mortgage_news_daily': self._get_mnd_rate,
            'freddiemac': self._get_freddiemac_rate,
            'zillow': self._get_zillow_rate,
            'nerdwallet': self._get_nerdwallet_rate
        }
    
    def get_aggregated_rate(self, preferred_sources: List[str] = None) -> Tuple[Optional[float], Dict[str, Any]]:
        """
        Get aggregated rate from multiple sources
        
        Returns:
            Tuple of (aggregated_rate, source_data)
        """
        if preferred_sources is None:
            preferred_sources = ['fred', 'bankrate', 'mortgage_news_daily', 'freddiemac']
        
        source_rates = {}
        successful_sources = []
        
        logger.info(f"Fetching rates from sources: {preferred_sources}")
        
        # Fetch from all sources
        for source in preferred_sources:
            if source in self.rate_sources:
                try:
                    rate = self.rate_sources[source]()
                    if rate and self._validate_rate(rate):
                        source_rates[source] = rate
                        successful_sources.append(source)
                        logger.info(f"[OK] {source}: {rate}%")
                    else:
                        logger.warning(f"[FAIL] {source}: Invalid rate {rate}")
                except Exception as e:
                    logger.error(f"[ERROR] {source}: Error - {e}")
                    source_rates[source] = None
            else:
                logger.warning(f"Unknown source: {source}")
        
        # Calculate aggregated rate
        valid_rates = [rate for rate in source_rates.values() if rate is not None]
        
        if not valid_rates:
            logger.error("No valid rates found from any source")
            return None, {'error': 'No valid rates found', 'sources': source_rates}
        
        # Use median for more robust aggregation
        aggregated_rate = round(statistics.median(valid_rates), 3)
        
        # Calculate additional statistics
        source_data = {
            'aggregated_rate': aggregated_rate,
            'source_rates': source_rates,
            'successful_sources': successful_sources,
            'rate_count': len(valid_rates),
            'min_rate': min(valid_rates),
            'max_rate': max(valid_rates),
            'average_rate': round(statistics.mean(valid_rates), 3),
            'rate_spread': round(max(valid_rates) - min(valid_rates), 3),
            'confidence': self._calculate_confidence(valid_rates, successful_sources)
        }
        
        logger.info(f"Aggregated rate: {aggregated_rate}% (from {len(valid_rates)} sources)")
        logger.info(f"Rate range: {source_data['min_rate']}% - {source_data['max_rate']}%")
        
        return aggregated_rate, source_data
    
    def _validate_rate(self, rate: float) -> bool:
        """Validate that a rate is realistic"""
        if not isinstance(rate, (int, float)):
            return False
        
        # Reasonable mortgage rate range: 2% to 15%
        if not (2.0 <= rate <= 15.0):
            return False
        
        # Check for suspicious values
        if rate == 0 or rate > 20:
            return False
        
        return True
    
    def _calculate_confidence(self, rates: List[float], sources: List[str]) -> str:
        """Calculate confidence level based on rate consistency and source count"""
        if len(rates) < 2:
            return 'low'
        
        # Calculate coefficient of variation (standard deviation / mean)
        mean_rate = statistics.mean(rates)
        std_dev = statistics.stdev(rates)
        cv = std_dev / mean_rate if mean_rate > 0 else 1
        
        # High confidence: multiple sources with low variance
        if len(sources) >= 3 and cv < 0.05:
            return 'high'
        # Medium confidence: multiple sources with moderate variance
        elif len(sources) >= 2 and cv < 0.1:
            return 'medium'
        # Low confidence: few sources or high variance
        else:
            return 'low'
    
    def _make_request(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Make HTTP request with error handling and retries"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Add random delay to be respectful
                time.sleep(random.uniform(1, 3))
                response = self.session.get(url, timeout=30, **kwargs)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed for {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"All {max_retries} attempts failed for {url}")
        return None
    
    def _extract_rate_from_text(self, text: str) -> Optional[float]:
        """Extract rate percentage from text with improved patterns"""
        if not text:
            return None
        
        # Clean the text
        text = text.strip()
        
        # Look for various rate patterns
        patterns = [
            r'(\d+\.\d+)%',  # 5.25%
            r'(\d+\.\d+)\s*percent',  # 5.25 percent
            r'rate[:\s]*(\d+\.\d+)',  # rate: 5.25
            r'(\d+\.\d+)\s*APR',  # 5.25 APR
            r'(\d+\.\d+)\s*interest',  # 5.25 interest
            r'(\d+\.\d+)\s*fixed',  # 5.25 fixed
            r'(\d+\.\d+)\s*refinance',  # 5.25 refinance
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    rate = float(match.group(1))
                    if self._validate_rate(rate):
                        return rate
                except ValueError:
                    continue
        
        return None
    
    def _find_rate_in_text(self, text: str) -> Optional[float]:
        """Find any reasonable rate percentage in text"""
        # Look for any percentage pattern
        matches = re.findall(r'(\d+\.\d+)%', text)
        for match in matches:
            try:
                rate = float(match)
                if self._validate_rate(rate):
                    return rate
            except ValueError:
                continue
        return None
    
    # Source-specific scrapers
    def _get_fred_rate(self) -> Optional[float]:
        """Get rate from FRED (Federal Reserve Economic Data)"""
        try:
            series_id = "MORTGAGE30US"
            api_key = os.getenv('FRED_API_KEY', '')
            
            if api_key:
                url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json&limit=1&sort_order=desc"
                response = self._make_request(url)
                
                if response:
                    data = response.json()
                    if 'observations' in data and len(data['observations']) > 0:
                        rate_str = data['observations'][0]['value']
                        if rate_str != '.' and rate_str:
                            return float(rate_str)
            else:
                # Use public CSV endpoint
                url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&cosd=2024-01-01"
                response = self._make_request(url)
                
                if response:
                    lines = response.text.strip().split('\n')
                    if len(lines) > 1:
                        for line in reversed(lines[1:]):
                            parts = line.split(',')
                            if len(parts) >= 2:
                                try:
                                    rate_str = parts[1].strip().strip('"')
                                    if rate_str and rate_str != '.':
                                        return float(rate_str)
                                except (ValueError, IndexError):
                                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting FRED rate: {e}")
            return None
    
    def _get_bankrate_rate(self) -> Optional[float]:
        """Get rate from Bankrate with updated URLs and selectors"""
        try:
            # Updated Bankrate URLs
            urls = [
                "https://www.bankrate.com/mortgages/refinance-rates/",
                "https://www.bankrate.com/mortgages/mortgage-rates/",
                "https://www.bankrate.com/mortgages/",
                "https://www.bankrate.com/mortgage-rates/"
            ]
            
            for url in urls:
                response = self._make_request(url)
                if response:
                    soup = BeautifulSoup(response.content, 'html5lib')
                    
                    # Updated selectors for current Bankrate layout
                    rate_selectors = [
                        '.rate-value',
                        '.current-rate',
                        '.mortgage-rate',
                        '.refinance-rate',
                        '.rate',
                        '.apr',
                        '.interest-rate',
                        '[data-testid*="rate"]',
                        '[class*="rate"]',
                        '[class*="apr"]',
                        '.rate-display',
                        '.rate-number',
                        '.primary-rate',
                        '.main-rate'
                    ]
                    
                    for selector in rate_selectors:
                        rate_elements = soup.select(selector)
                        for element in rate_elements:
                            rate_text = element.get_text().strip()
                            rate = self._extract_rate_from_text(rate_text)
                            if rate:
                                return rate
                    
                    # Fallback: look for any percentage pattern
                    rate = self._find_rate_in_text(soup.get_text())
                    if rate:
                        return rate
            
            return None
            
        except Exception as e:
            logger.error(f"Error scraping Bankrate: {e}")
            return None
    
    def _get_mnd_rate(self) -> Optional[float]:
        """Get rate from Mortgage News Daily"""
        try:
            url = "https://www.mortgagenewsdaily.com/mortgage-rates"
            response = self._make_request(url)
            
            if response:
                soup = BeautifulSoup(response.content, 'html5lib')
                
                # Look for rate information
                rate_selectors = [
                    '.rate-value',
                    '.current-rate',
                    '.mortgage-rate',
                    '[data-rate]',
                    '.mnd-rate',
                    '.today-rate'
                ]
                
                for selector in rate_selectors:
                    rate_elements = soup.select(selector)
                    for element in rate_elements:
                        rate_text = element.get_text().strip()
                        rate = self._extract_rate_from_text(rate_text)
                        if rate:
                            return rate
                
                # Fallback: look for any percentage pattern
                rate = self._find_rate_in_text(soup.get_text())
                if rate:
                    return rate
            
            return None
            
        except Exception as e:
            logger.error(f"Error scraping Mortgage News Daily: {e}")
            return None
    
    def _get_freddiemac_rate(self) -> Optional[float]:
        """Get rate from Freddie Mac PMMS"""
        try:
            url = "https://www.freddiemac.com/pmms/"
            response = self._make_request(url)
            
            if response:
                soup = BeautifulSoup(response.content, 'html5lib')
                
                # Look for the 30-year fixed rate
                rate_selectors = [
                    '.rate-value',
                    '.current-rate',
                    '.mortgage-rate',
                    '.pmms-rate',
                    '.rate',
                    '.apr',
                    '[class*="rate"]',
                    '[class*="apr"]',
                    '.rate-display',
                    '.rate-number',
                    '.primary-mortgage-market-survey',
                    '.survey-rate',
                    '.pmm-rate'
                ]
                
                for selector in rate_selectors:
                    rate_elements = soup.select(selector)
                    for element in rate_elements:
                        rate_text = element.get_text().strip()
                        rate = self._extract_rate_from_text(rate_text)
                        if rate:
                            return rate
                
                # Fallback: look for any percentage pattern
                rate = self._find_rate_in_text(soup.get_text())
                if rate:
                    return rate
            
            return None
            
        except Exception as e:
            logger.error(f"Error scraping Freddie Mac: {e}")
            return None
    
    def _get_zillow_rate(self) -> Optional[float]:
        """Get rate from Zillow (if available)"""
        try:
            # Zillow rate URLs (may change)
            urls = [
                "https://www.zillow.com/mortgage-rates/",
                "https://www.zillow.com/mortgages/rates/"
            ]
            
            for url in urls:
                response = self._make_request(url)
                if response:
                    soup = BeautifulSoup(response.content, 'html5lib')
                    
                    # Look for rate information
                    rate_selectors = [
                        '.rate-value',
                        '.current-rate',
                        '.mortgage-rate',
                        '.zillow-rate',
                        '[data-testid*="rate"]'
                    ]
                    
                    for selector in rate_selectors:
                        rate_elements = soup.select(selector)
                        for element in rate_elements:
                            rate_text = element.get_text().strip()
                            rate = self._extract_rate_from_text(rate_text)
                            if rate:
                                return rate
            
            return None
            
        except Exception as e:
            logger.error(f"Error scraping Zillow: {e}")
            return None
    
    def _get_nerdwallet_rate(self) -> Optional[float]:
        """Get rate from NerdWallet (if available)"""
        try:
            url = "https://www.nerdwallet.com/mortgages/mortgage-rates"
            response = self._make_request(url)
            
            if response:
                soup = BeautifulSoup(response.content, 'html5lib')
                
                # Look for rate information
                rate_selectors = [
                    '.rate-value',
                    '.current-rate',
                    '.mortgage-rate',
                    '.nerdwallet-rate',
                    '[data-testid*="rate"]'
                ]
                
                for selector in rate_selectors:
                    rate_elements = soup.select(selector)
                    for element in rate_elements:
                        rate_text = element.get_text().strip()
                        rate = self._extract_rate_from_text(rate_text)
                        if rate:
                            return rate
            
            return None
            
        except Exception as e:
            logger.error(f"Error scraping NerdWallet: {e}")
            return None


# Factory function for backward compatibility
def get_enhanced_rate_scraper() -> EnhancedRateScraper:
    """Get enhanced rate scraper instance"""
    return EnhancedRateScraper()


# Mock rate for testing when all sources fail
def get_mock_rate() -> float:
    """Return a mock rate for testing purposes"""
    import random
    # Return a random rate between 4.5% and 6.5% for testing
    return round(random.uniform(4.5, 6.5), 2)
