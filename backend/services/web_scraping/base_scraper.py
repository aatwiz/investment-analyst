"""
Base web scraper class for deal sourcing.
Provides common functionality for all platform scrapers.
"""
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
from loguru import logger
import random


class BaseScraper(ABC):
    """
    Abstract base class for all web scrapers.
    
    Provides common functionality:
    - HTTP request handling with retries
    - Rate limiting
    - User agent rotation
    - Error handling
    - Data normalization
    """
    
    def __init__(self, rate_limit: float = 1.0):
        """
        Initialize scraper.
        
        Args:
            rate_limit: Minimum seconds between requests (default: 1.0)
        """
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Rotate user agents to avoid detection
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        ]
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Return the name of the platform being scraped."""
        pass
    
    @abstractmethod
    async def scrape_deals(self, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Scrape deals from the platform.
        
        Args:
            filters: Optional filters (industry, stage, location, etc.)
            
        Returns:
            List of deal dictionaries with standardized fields
        """
        pass
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _fetch_page(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        max_retries: int = 3
    ) -> Optional[str]:
        """
        Fetch a page with rate limiting and retries.
        
        Args:
            url: URL to fetch
            method: HTTP method
            headers: Additional headers
            params: Query parameters
            data: POST data
            max_retries: Maximum retry attempts
            
        Returns:
            Page HTML content or None if failed
        """
        # Rate limiting
        await self._respect_rate_limit()
        
        # Prepare headers with random user agent
        request_headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        if headers:
            request_headers.update(headers)
        
        session = await self._get_session()
        
        for attempt in range(max_retries):
            try:
                async with session.request(
                    method,
                    url,
                    headers=request_headers,
                    params=params,
                    data=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        content = await response.text()
                        logger.debug(f"Fetched {url} (attempt {attempt + 1})")
                        return content
                    elif response.status == 429:
                        # Rate limited - wait longer
                        wait_time = (attempt + 1) * 5
                        logger.warning(f"Rate limited on {url}, waiting {wait_time}s")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
                        
            except asyncio.TimeoutError:
                logger.warning(f"Timeout fetching {url} (attempt {attempt + 1})")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                await asyncio.sleep(2 ** attempt)
        
        logger.error(f"Failed to fetch {url} after {max_retries} attempts")
        return None
    
    async def _respect_rate_limit(self):
        """Ensure rate limit is respected between requests."""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit:
            wait_time = self.rate_limit - time_since_last
            await asyncio.sleep(wait_time)
        
        self.last_request_time = asyncio.get_event_loop().time()
    
    def _parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content with BeautifulSoup."""
        return BeautifulSoup(html, 'html.parser')
    
    def _normalize_deal(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize deal data to standard format.
        
        Standard fields:
        - name: Company name
        - description: Brief description
        - website: Company website
        - industry: Industry/sector
        - stage: Funding stage (Seed, Series A, etc.)
        - location: Location/geography
        - founded_year: Year founded
        - funding_amount: Latest funding amount
        - funding_date: Latest funding date
        - investors: List of investors
        - total_funding: Total funding raised
        - employee_count: Number of employees
        - source: Platform source
        - source_url: URL where found
        - source_article_title: Original article title (if from news source)
        - scraped_at: Timestamp
        """
        return {
            'name': raw_data.get('name', '').strip(),
            'description': raw_data.get('description', '').strip(),
            'website': raw_data.get('website', '').strip(),
            'industry': raw_data.get('industry', '').strip(),
            'stage': raw_data.get('stage', '').strip(),
            'location': raw_data.get('location', '').strip(),
            'founded_year': raw_data.get('founded_year'),
            'funding_amount': raw_data.get('funding_amount'),
            'funding_date': raw_data.get('funding_date'),
            'investors': raw_data.get('investors', []),
            'total_funding': raw_data.get('total_funding'),
            'employee_count': raw_data.get('employee_count'),
            'source': self.get_platform_name(),
            'source_url': raw_data.get('source_url', ''),
            'source_article_title': raw_data.get('source_article_title', ''),
            'scraped_at': datetime.utcnow().isoformat(),
            'raw_data': raw_data  # Keep original for reference
        }
    
    async def close(self):
        """Close the scraper session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
