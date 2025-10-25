"""
Wamda scraper for Middle East/North Africa deal sourcing.
https://www.wamda.com/

Wamda is a platform for the MENA startup ecosystem, covering:
- Startup funding news
- Ecosystem insights
- Investment trends
"""
from typing import Dict, List, Optional, Any
from loguru import logger
import re
from datetime import datetime

from .base_scraper import BaseScraper


class WamdaScraper(BaseScraper):
    """
    Scraper for Wamda (MENA region focus).
    
    Wamda provides:
    - Funding announcements
    - Startup profiles
    - Ecosystem news
    """
    
    def __init__(self):
        super().__init__(rate_limit=2.0)  # 2 seconds between requests
        self.base_url = 'https://www.wamda.com'
    
    def get_platform_name(self) -> str:
        return "Wamda"
    
    async def scrape_deals(self, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Scrape recent funding deals from Wamda.
        
        Args:
            filters: {
                'countries': ['UAE', 'Saudi Arabia', 'Egypt'],
                'industries': ['fintech', 'healthtech'],
                'min_funding': 500000,
                'days_back': 30  # How many days to look back
            }
        
        Returns:
            List of deals
        """
        filters = filters or {}
        deals = []
        
        # TEMPORARY: Return mock data - Wamda site structure changed
        # TODO: Update scraping logic after inspecting current site
        logger.warning("Using mock data - Wamda site structure needs update")
        
        mock_deals = [
            {
                'name': 'FoodTech MENA',
                'description': 'Cloud kitchen and food delivery platform',
                'funding_amount': 1800000,
                'stage': 'Seed',
                'location': 'Dubai, UAE',
                'funding_date': '2025-10-15',
                'source_url': f'{self.base_url}/article/foodtech-mena-raises-1-8m'
            },
            {
                'name': 'EduConnect Arabia',
                'description': 'Online learning platform for K-12',
                'funding_amount': 2200000,
                'stage': 'Series A',
                'location': 'Amman, Jordan',
                'funding_date': '2025-10-10',
                'source_url': f'{self.base_url}/article/educonnect-raises-series-a'
            }
        ]
        
        # Apply filters
        for deal in mock_deals:
            if self._matches_filters(deal, filters):
                deals.append(self._normalize_deal(deal))
        
        logger.info(f"Scraped {len(deals)} deals from Wamda (mock data)")
        return deals
    
    def _parse_wamda_article(self, article) -> Optional[Dict[str, Any]]:
        """Parse a Wamda funding article."""
        
        # Extract title (usually contains company name and funding info)
        title_elem = article.find(['h1', 'h2', 'h3', 'a'], class_=re.compile(r'(title|headline)', re.I))
        if not title_elem:
            return None
        
        title = title_elem.get_text(strip=True)
        
        # Check if it's actually a funding announcement
        if not any(keyword in title.lower() for keyword in ['raises', 'funding', 'investment', 'round', 'seed', 'series']):
            return None
        
        # Extract company name (usually first part of title)
        company_name = self._extract_company_name(title)
        
        # Extract funding amount from title
        funding_amount = self._extract_funding_amount(title)
        
        # Extract stage from title
        stage = self._extract_stage(title)
        
        # Extract article content/description
        content_elem = article.find(['p', 'div'], class_=re.compile(r'(excerpt|summary|description)', re.I))
        description = content_elem.get_text(strip=True) if content_elem else title
        
        # Get article URL
        link_elem = article.find('a', href=True)
        source_url = link_elem['href'] if link_elem else ''
        if source_url and not source_url.startswith('http'):
            source_url = f"{self.base_url}{source_url}"
        
        # Extract date
        date_elem = article.find(['time', 'span'], class_=re.compile(r'date', re.I))
        funding_date = date_elem.get('datetime', date_elem.get_text(strip=True)) if date_elem else ''
        
        return {
            'name': company_name,
            'description': description,
            'funding_amount': funding_amount,
            'stage': stage,
            'funding_date': funding_date,
            'source_url': source_url,
            'location': self._extract_location(title, description)
        }
    
    def _extract_company_name(self, text: str) -> str:
        """Extract company name from title like 'Company raises $5M in Series A'."""
        # Usually company name comes before 'raises', 'secures', 'closes'
        patterns = [
            r'^([^,]+?)(?:\s+raises|\s+secures|\s+closes|\s+gets)',
            r'^([^,]+?)(?:\s+in\s+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback: take first few words
        words = text.split()
        if len(words) >= 2:
            return ' '.join(words[:2])
        
        return text[:50]
    
    def _extract_funding_amount(self, text: str) -> Optional[float]:
        """Extract funding amount from text."""
        # Look for patterns like $5M, $1.5 million, $500K
        patterns = [
            r'\$(\d+(?:\.\d+)?)\s*([MBK])',  # $5M, $1.5B
            r'\$(\d+(?:\.\d+)?)\s*million',   # $5 million
            r'\$(\d+(?:\.\d+)?)\s*billion',   # $1 billion
            r'(\d+(?:\.\d+)?)\s*million',     # 5 million (without $)
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = float(match.group(1))
                
                # Get multiplier
                if len(match.groups()) > 1:
                    multiplier = match.group(2).upper()
                    if multiplier == 'M' or 'million' in pattern.lower():
                        return amount * 1_000_000
                    elif multiplier == 'B' or 'billion' in pattern.lower():
                        return amount * 1_000_000_000
                    elif multiplier == 'K':
                        return amount * 1_000
                else:
                    return amount * 1_000_000  # Default to millions
        
        return None
    
    def _extract_stage(self, text: str) -> str:
        """Extract funding stage from text."""
        stages = ['pre-seed', 'seed', 'series a', 'series b', 'series c', 'series d', 'bridge', 'growth']
        
        text_lower = text.lower()
        for stage in stages:
            if stage in text_lower:
                return stage.title()
        
        return ''
    
    def _extract_location(self, title: str, description: str) -> str:
        """Extract location/country from text."""
        # Common MENA countries
        countries = [
            'UAE', 'Saudi Arabia', 'Egypt', 'Jordan', 'Lebanon', 'Kuwait',
            'Bahrain', 'Qatar', 'Oman', 'Morocco', 'Tunisia', 'Algeria',
            'Dubai', 'Riyadh', 'Cairo', 'Amman', 'Beirut'
        ]
        
        text = f"{title} {description}"
        for country in countries:
            if country.lower() in text.lower():
                return country
        
        return ''
    
    def _matches_filters(self, deal: Dict, filters: Dict) -> bool:
        """Check if deal matches filter criteria."""
        
        # Country filter
        if 'countries' in filters:
            location = deal.get('location', '').lower()
            if not any(country.lower() in location for country in filters['countries']):
                return False
        
        # Industry filter (check in description)
        if 'industries' in filters:
            text = f"{deal.get('description', '')} {deal.get('name', '')}".lower()
            if not any(industry.lower() in text for industry in filters['industries']):
                return False
        
        # Min funding filter
        if 'min_funding' in filters:
            funding = deal.get('funding_amount')
            if not funding or funding < filters['min_funding']:
                return False
        
        return True
    
    async def scrape_startup_profile(self, startup_slug: str) -> Optional[Dict[str, Any]]:
        """
        Scrape detailed startup profile from Wamda.
        
        Args:
            startup_slug: Startup URL slug or ID
            
        Returns:
            Startup profile dictionary
        """
        try:
            url = f"{self.base_url}/startups/{startup_slug}"
            
            html = await self._fetch_page(url)
            if not html:
                return None
            
            soup = self._parse_html(html)
            
            profile = {
                'name': '',
                'description': '',
                'website': '',
                'industry': '',
                'location': '',
                'founded_year': None,
                'source_url': url
            }
            
            # Parse profile details
            # Note: This is a template - actual structure may vary
            name_elem = soup.find('h1', class_=re.compile(r'(name|title)', re.I))
            if name_elem:
                profile['name'] = name_elem.get_text(strip=True)
            
            desc_elem = soup.find('div', class_=re.compile(r'(description|about)', re.I))
            if desc_elem:
                profile['description'] = desc_elem.get_text(strip=True)
            
            return profile
            
        except Exception as e:
            logger.error(f"Error scraping Wamda profile {startup_slug}: {e}")
            return None
