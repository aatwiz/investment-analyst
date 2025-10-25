"""
Base scraper class for all web scraping implementations.

Provides common functionality:
- Rate limiting
- Error handling
- Retry logic
- Data validation
- Logging
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for all scrapers"""
    
    def __init__(
        self,
        rate_limit: float = 1.0,
        max_retries: int = 3,
        timeout: int = 30
    ):
        """
        Initialize base scraper
        
        Args:
            rate_limit: Seconds between requests
            max_retries: Maximum retry attempts
            timeout: Request timeout in seconds
        """
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self.timeout = timeout
        self.last_request_time = 0.0
        
    @abstractmethod
    async def scrape(self) -> List[Dict]:
        """
        Main scraping method to be implemented by subclasses
        
        Returns:
            List of scraped data dictionaries
        """
        pass
    
    async def _rate_limit_wait(self):
        """Enforce rate limiting between requests"""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit:
            wait_time = self.rate_limit - time_since_last
            await asyncio.sleep(wait_time)
        
        self.last_request_time = asyncio.get_event_loop().time()
    
    def _validate_data(self, data: Dict) -> bool:
        """
        Validate scraped data
        
        Args:
            data: Data dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['name', 'url', 'scraped_at']
        return all(field in data for field in required_fields)
    
    def _normalize_data(self, data: Dict) -> Dict:
        """
        Normalize scraped data to standard format
        
        Args:
            data: Raw scraped data
            
        Returns:
            Normalized data dictionary
        """
        normalized = {
            'name': data.get('name', '').strip(),
            'url': data.get('url', '').strip(),
            'description': data.get('description', '').strip(),
            'scraped_at': datetime.now().isoformat(),
            'source': self.__class__.__name__,
            'raw_data': data
        }
        
        return normalized


# TODO: Implement specific scrapers
# - YCombinatorScraper
# - TechStarsScraper
# - CrunchbaseScraper
# - AngelListScraper
# - NewsAggregator
