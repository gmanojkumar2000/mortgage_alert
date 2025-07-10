"""
Rate Scraper Module
Fetches current refinance mortgage rates from public sources
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import Optional, Dict, Any
import time
import random
import os

logger = logging.getLogger(__name__)


class RateScraper:
    """Base class for rate scraping"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_rate(self) -> Optional[float]:
        """Get current refinance rate"""
        raise NotImplementedError
    
    def _make_request(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Make HTTP request with error handling"""
        try:
            # Add random delay to be respectful
            time.sleep(random.uniform(1, 3))
            response = self.session.get(url, timeout=30, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return None


class BankrateScraper(RateScraper):
    """Scraper for Bankrate.com"""
    
    def get_rate(self) -> Optional[float]:
        """Get current refinance rate from Bankrate"""
        try:
            # Try multiple Bankrate URLs for better success rate
            urls = [
                "https://www.bankrate.com/mortgages/refinance-rates/",
                "https://www.bankrate.com/mortgages/",
                "https://www.bankrate.com/mortgages/refinance-rates/oregon/",
                "https://www.bankrate.com/mortgage-rates/"
            ]
            
            for url in urls:
                logger.info(f"Trying Bankrate URL: {url}")
                response = self._make_request(url)
                
                if response:
                    soup = BeautifulSoup(response.content, 'html5lib')
                    
                    # Look for rate information in various possible locations
                    rate_selectors = [
                        '.rate-value',
                        '.current-rate',
                        '[data-testid="rate-value"]',
                        '.mortgage-rate',
                        '.refinance-rate',
                        '.rate',
                        '.apr',
                        '.interest-rate',
                        '[class*="rate"]',
                        '[class*="apr"]',
                        '.rate-display',
                        '.rate-number'
                    ]
                    
                    for selector in rate_selectors:
                        rate_elements = soup.select(selector)
                        for element in rate_elements:
                            rate_text = element.get_text().strip()
                            # Extract numeric rate from text
                            rate = self._extract_rate_from_text(rate_text)
                            if rate:
                                logger.info(f"Found rate from Bankrate ({url}): {rate}%")
                                return rate
                    
                    # Fallback: look for any percentage pattern in the page
                    rate = self._find_rate_in_text(soup.get_text())
                    if rate:
                        logger.info(f"Found rate from Bankrate fallback ({url}): {rate}%")
                        return rate
                else:
                    logger.warning(f"Failed to fetch {url}")
            
            logger.warning("No rate found on any Bankrate page")
            return None
            
        except Exception as e:
            logger.error(f"Error scraping Bankrate: {e}")
            return None
    
    def _extract_rate_from_text(self, text: str) -> Optional[float]:
        """Extract rate percentage from text"""
        import re
        # Look for patterns like "5.25%", "5.25", "5.25 percent"
        patterns = [
            r'(\d+\.\d+)%',
            r'(\d+\.\d+)\s*percent',
            r'rate[:\s]*(\d+\.\d+)',
            r'(\d+\.\d+)\s*APR'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    rate = float(match.group(1))
                    # Validate reasonable rate range (2% to 15%)
                    if 2.0 <= rate <= 15.0:
                        return rate
                except ValueError:
                    continue
        return None
    
    def _find_rate_in_text(self, text: str) -> Optional[float]:
        """Find any reasonable rate percentage in text"""
        import re
        # Look for any percentage pattern
        matches = re.findall(r'(\d+\.\d+)%', text)
        for match in matches:
            try:
                rate = float(match)
                if 2.0 <= rate <= 15.0:
                    return rate
            except ValueError:
                continue
        return None


class MortgageNewsDailyScraper(RateScraper):
    """Scraper for Mortgage News Daily"""
    
    def get_rate(self) -> Optional[float]:
        """Get current refinance rate from Mortgage News Daily"""
        try:
            # MND rates page
            url = "https://www.mortgagenewsdaily.com/mortgage-rates"
            response = self._make_request(url)
            
            if not response:
                return None
            
            soup = BeautifulSoup(response.content, 'html5lib')
            
            # Look for rate information
            rate_selectors = [
                '.rate-value',
                '.current-rate',
                '.mortgage-rate',
                '[data-rate]'
            ]
            
            for selector in rate_selectors:
                rate_elements = soup.select(selector)
                for element in rate_elements:
                    rate_text = element.get_text().strip()
                    rate = self._extract_rate_from_text(rate_text)
                    if rate:
                        logger.info(f"Found rate from MND: {rate}%")
                        return rate
            
            # Fallback: look for any percentage pattern
            rate = self._find_rate_in_text(soup.get_text())
            if rate:
                logger.info(f"Found rate from MND (fallback): {rate}%")
                return rate
                
            logger.warning("No rate found on MND page")
            return None
            
        except Exception as e:
            logger.error(f"Error scraping Mortgage News Daily: {e}")
            return None
    
    def _extract_rate_from_text(self, text: str) -> Optional[float]:
        """Extract rate percentage from text"""
        import re
        patterns = [
            r'(\d+\.\d+)%',
            r'(\d+\.\d+)\s*percent',
            r'rate[:\s]*(\d+\.\d+)',
            r'(\d+\.\d+)\s*APR'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    rate = float(match.group(1))
                    if 2.0 <= rate <= 15.0:
                        return rate
                except ValueError:
                    continue
        return None
    
    def _find_rate_in_text(self, text: str) -> Optional[float]:
        """Find any reasonable rate percentage in text"""
        import re
        matches = re.findall(r'(\d+\.\d+)%', text)
        for match in matches:
            try:
                rate = float(match)
                if 2.0 <= rate <= 15.0:
                    return rate
            except ValueError:
                continue
        return None


class FreddieMacScraper(RateScraper):
    """Scraper for Freddie Mac rates (more reliable)"""
    
    def get_rate(self) -> Optional[float]:
        """Get current refinance rate from Freddie Mac"""
        try:
            # Freddie Mac rates page
            url = "https://www.freddiemac.com/pmms/"
            response = self._make_request(url)
            
            if not response:
                return None
            
            soup = BeautifulSoup(response.content, 'html5lib')
            
            # Look for rate information in various possible locations
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
                '.survey-rate'
            ]
            
            for selector in rate_selectors:
                rate_elements = soup.select(selector)
                for element in rate_elements:
                    rate_text = element.get_text().strip()
                    rate = self._extract_rate_from_text(rate_text)
                    if rate:
                        logger.info(f"Found rate from Freddie Mac: {rate}%")
                        return rate
            
            # Fallback: look for any percentage pattern
            rate = self._find_rate_in_text(soup.get_text())
            if rate:
                logger.info(f"Found rate from Freddie Mac (fallback): {rate}%")
                return rate
                
            logger.warning("No rate found on Freddie Mac page")
            return None
            
        except Exception as e:
            logger.error(f"Error scraping Freddie Mac: {e}")
            return None
    
    def _extract_rate_from_text(self, text: str) -> Optional[float]:
        """Extract rate percentage from text"""
        import re
        patterns = [
            r'(\d+\.\d+)%',
            r'(\d+\.\d+)\s*percent',
            r'rate[:\s]*(\d+\.\d+)',
            r'(\d+\.\d+)\s*APR'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    rate = float(match.group(1))
                    if 2.0 <= rate <= 15.0:
                        return rate
                except ValueError:
                    continue
        return None
    
    def _find_rate_in_text(self, text: str) -> Optional[float]:
        """Find any reasonable rate percentage in text"""
        import re
        matches = re.findall(r'(\d+\.\d+)%', text)
        for match in matches:
            try:
                rate = float(match)
                if 2.0 <= rate <= 15.0:
                    return rate
            except ValueError:
                continue
        return None


class FREDScraper(RateScraper):
    """Scraper for Federal Reserve Economic Data (FRED) - Most accurate source"""
    
    def __init__(self):
        super().__init__()
        # FRED API key (free to get from https://fred.stlouisfed.org/docs/api/api_key.html)
        self.api_key = os.getenv('FRED_API_KEY', '')
        if not self.api_key:
            logger.warning("FRED_API_KEY not found in environment variables. Using public endpoint.")
    
    def get_rate(self) -> Optional[float]:
        """Get current 30-year fixed mortgage rate from FRED"""
        try:
            # FRED series ID for 30-Year Fixed Rate Mortgage Average in the United States
            series_id = "MORTGAGE30US"
            
            if self.api_key:
                # Use FRED API if key is available
                url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={self.api_key}&file_type=json&limit=1&sort_order=desc"
            else:
                # Use public endpoint (limited but works)
                url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=1318&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id={series_id}&scale=left&cosd=2020-01-01&coed=2025-12-31&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Weekly%2C%20Ending%20Wednesday&fam=avg&fgst=lin&fgsnd=2020-02-01&line_index=1&transformation=lin&vintage_date=&revision_date=&nd=1971-04-02"
            
            response = self._make_request(url)
            
            if not response:
                return None
            
            # Parse the response
            if self.api_key:
                # JSON response from API
                data = response.json()
                if 'observations' in data and len(data['observations']) > 0:
                    rate_str = data['observations'][0]['value']
                    if rate_str != '.' and rate_str:  # FRED uses '.' for missing data
                        rate = float(rate_str)
                        logger.info(f"Found rate from FRED API: {rate}%")
                        return rate
            else:
                # CSV response from public endpoint
                lines = response.text.strip().split('\n')
                if len(lines) > 1:
                    # Skip header line, get the most recent data
                    for line in reversed(lines[1:]):  # Start from most recent
                        parts = line.split(',')
                        if len(parts) >= 2:
                            try:
                                rate_str = parts[1].strip().strip('"')
                                if rate_str and rate_str != '.':
                                    rate = float(rate_str)
                                    logger.info(f"Found rate from FRED public data: {rate}%")
                                    return rate
                            except (ValueError, IndexError):
                                continue
            
            logger.warning("No valid rate found in FRED data")
            return None
            
        except Exception as e:
            logger.error(f"Error getting rate from FRED: {e}")
            return None


class FreddieMacPMMSScraper(RateScraper):
    """Scraper for Freddie Mac Primary Mortgage Market Survey - Official source"""
    
    def get_rate(self) -> Optional[float]:
        """Get current rate from Freddie Mac PMMS"""
        try:
            # Freddie Mac PMMS page
            url = "https://www.freddiemac.com/pmms/"
            response = self._make_request(url)
            
            if not response:
                return None
            
            soup = BeautifulSoup(response.content, 'html5lib')
            
            # Look for the 30-year fixed rate specifically
            rate_selectors = [
                '[data-rate="30-year"]',
                '.rate-30-year',
                '.pmm-30-year',
                '.mortgage-rate-30',
                '[class*="30-year"]',
                '.rate-value',
                '.current-rate'
            ]
            
            for selector in rate_selectors:
                rate_elements = soup.select(selector)
                for element in rate_elements:
                    rate_text = element.get_text().strip()
                    rate = self._extract_rate_from_text(rate_text)
                    if rate:
                        logger.info(f"Found 30-year rate from Freddie Mac PMMS: {rate}%")
                        return rate
            
            # Fallback: look for any percentage pattern
            rate = self._find_rate_in_text(soup.get_text())
            if rate:
                logger.info(f"Found rate from Freddie Mac PMMS (fallback): {rate}%")
                return rate
                
            logger.warning("No rate found on Freddie Mac PMMS page")
            return None
            
        except Exception as e:
            logger.error(f"Error scraping Freddie Mac PMMS: {e}")
            return None
    
    def _extract_rate_from_text(self, text: str) -> Optional[float]:
        """Extract rate percentage from text"""
        import re
        patterns = [
            r'(\d+\.\d+)%',
            r'(\d+\.\d+)\s*percent',
            r'rate[:\s]*(\d+\.\d+)',
            r'(\d+\.\d+)\s*APR'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    rate = float(match.group(1))
                    if 2.0 <= rate <= 15.0:
                        return rate
                except ValueError:
                    continue
        return None
    
    def _find_rate_in_text(self, text: str) -> Optional[float]:
        """Find any reasonable rate percentage in text"""
        import re
        matches = re.findall(r'(\d+\.\d+)%', text)
        for match in matches:
            try:
                rate = float(match)
                if 2.0 <= rate <= 15.0:
                    return rate
            except ValueError:
                continue
        return None


def get_rate_scraper(source: str) -> RateScraper:
    """Factory function to get appropriate rate scraper"""
    scrapers = {
        "bankrate": BankrateScraper,
        "mortgage_news_daily": MortgageNewsDailyScraper,
        "freddiemac": FreddieMacScraper,
        "fred": FREDScraper,
        "pmm": FreddieMacPMMSScraper
    }
    
    scraper_class = scrapers.get(source.lower())
    if not scraper_class:
        raise ValueError(f"Unknown rate source: {source}")
    
    return scraper_class()


# Mock rate for testing when scraping fails
def get_mock_rate() -> float:
    """Return a mock rate for testing purposes"""
    import random
    # Return a random rate between 4.5% and 6.5% for testing
    return round(random.uniform(4.5, 6.5), 2) 