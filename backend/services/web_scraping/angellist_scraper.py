"""
AngelList (Wellfound) scraper for startup deal sourcing.
https://wellfound.com/ (formerly AngelList)

AngelList/Wellfound is a major platform for:
- Startup profiles
- Funding announcements
- Job postings
- Investor connections
"""
from typing import Dict, List, Optional, Any
from loguru import logger
import re
import json

from .base_scraper import BaseScraper


class AngelListScraper(BaseScraper):
    """
    Scraper for AngelList/Wellfound.
    
    Note: AngelList doesn't have a public API for free use.
    This scraper uses web scraping with careful rate limiting.
    """
    
    def __init__(self):
        super().__init__(rate_limit=3.0)  # 3 seconds between requests (be conservative)
        self.base_url = 'https://wellfound.com'
        self.api_url = 'https://wellfound.com/graphql'
    
    def get_platform_name(self) -> str:
        return "AngelList"
    
    async def scrape_deals(self, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Scrape startup funding data from AngelList/Wellfound.
        
        Args:
            filters: {
                'locations': ['San Francisco', 'New York'],
                'markets': ['fintech', 'health-tech'],
                'stage': ['seed', 'series-a'],
                'min_funding': 1000000
            }
        
        Returns:
            List of deals
        """
        filters = filters or {}
        deals = []
        
        try:
            # Build search URL
            search_url = self._build_search_url(filters)
            
            html = await self._fetch_page(search_url)
            if not html:
                return deals
            
            soup = self._parse_html(html)
            
            # Try to find JSON data embedded in page
            script_tags = soup.find_all('script', type='application/json')
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    # Look for startup data in the JSON
                    startups = self._extract_startups_from_json(data)
                    if startups:
                        for startup in startups:
                            deal = self._parse_angellist_startup(startup)
                            if deal and self._matches_filters(deal, filters):
                                deals.append(self._normalize_deal(deal))
                except:
                    continue
            
            # Fallback: Parse HTML directly
            if not deals:
                startup_cards = soup.find_all(['div', 'article'], attrs={'data-test': re.compile(r'startup', re.I)})
                if not startup_cards:
                    startup_cards = soup.find_all('div', class_=re.compile(r'startup.*card', re.I))
                
                for card in startup_cards[:20]:  # Limit to avoid rate limiting
                    try:
                        deal = self._parse_html_card(card)
                        if deal and self._matches_filters(deal, filters):
                            deals.append(self._normalize_deal(deal))
                    except Exception as e:
                        logger.warning(f"Error parsing AngelList card: {e}")
                        continue
            
            logger.info(f"Scraped {len(deals)} deals from AngelList")
            
        except Exception as e:
            logger.error(f"Error scraping AngelList: {e}")
        
        return deals
    
    def _build_search_url(self, filters: Dict) -> str:
        """Build AngelList search URL with filters."""
        url = f"{self.base_url}/companies"
        
        params = []
        
        if 'locations' in filters:
            for loc in filters['locations']:
                params.append(f"locations[]={loc.replace(' ', '%20')}")
        
        if 'markets' in filters:
            for market in filters['markets']:
                params.append(f"markets[]={market}")
        
        if 'stage' in filters:
            stage = filters['stage']
            if isinstance(stage, list):
                stage = stage[0]
            params.append(f"stage={stage}")
        
        if params:
            url += '?' + '&'.join(params)
        
        return url
    
    def _extract_startups_from_json(self, data: Any) -> List[Dict]:
        """Recursively extract startup data from JSON."""
        startups = []
        
        if isinstance(data, dict):
            # Check if this looks like startup data
            if 'name' in data and ('description' in data or 'company' in data or 'startup' in data):
                startups.append(data)
            
            # Recursively search nested objects
            for value in data.values():
                startups.extend(self._extract_startups_from_json(value))
        
        elif isinstance(data, list):
            for item in data:
                startups.extend(self._extract_startups_from_json(item))
        
        return startups
    
    def _parse_angellist_startup(self, data: Dict) -> Dict[str, Any]:
        """Parse startup data from JSON."""
        
        return {
            'name': data.get('name', ''),
            'description': data.get('description') or data.get('pitch', ''),
            'website': data.get('website_url') or data.get('website', ''),
            'location': self._parse_location(data),
            'industry': self._parse_markets(data),
            'stage': data.get('stage', ''),
            'total_funding': self._parse_funding(data.get('total_funding')),
            'employee_count': str(data.get('company_size', '')),
            'source_url': f"{self.base_url}/company/{data.get('slug', data.get('id', ''))}"
        }
    
    def _parse_html_card(self, card) -> Dict[str, Any]:
        """Parse startup data from HTML card."""
        
        # Extract company name
        name_elem = card.find(['h2', 'h3', 'a'], class_=re.compile(r'(name|title|company)', re.I))
        name = name_elem.get_text(strip=True) if name_elem else ''
        
        # Extract description
        desc_elem = card.find(['p', 'div'], class_=re.compile(r'(description|pitch|tagline)', re.I))
        description = desc_elem.get_text(strip=True) if desc_elem else ''
        
        # Extract location
        location_elem = card.find(['span', 'div'], attrs={'data-test': 'location'})
        if not location_elem:
            location_elem = card.find(['span', 'div'], class_=re.compile(r'location', re.I))
        location = location_elem.get_text(strip=True) if location_elem else ''
        
        # Extract markets/industry
        markets_elem = card.find_all(['span', 'a'], class_=re.compile(r'(market|tag)', re.I))
        markets = [m.get_text(strip=True) for m in markets_elem[:3]]
        industry = ', '.join(markets) if markets else ''
        
        # Get URL
        link_elem = card.find('a', href=True)
        source_url = link_elem['href'] if link_elem else ''
        if source_url and not source_url.startswith('http'):
            source_url = f"{self.base_url}{source_url}"
        
        return {
            'name': name,
            'description': description,
            'location': location,
            'industry': industry,
            'source_url': source_url
        }
    
    def _parse_location(self, data: Dict) -> str:
        """Parse location from various formats."""
        if 'location' in data:
            loc = data['location']
            if isinstance(loc, str):
                return loc
            elif isinstance(loc, dict):
                parts = []
                if 'city' in loc:
                    parts.append(loc['city'])
                if 'country' in loc:
                    parts.append(loc['country'])
                return ', '.join(parts)
        
        return ''
    
    def _parse_markets(self, data: Dict) -> str:
        """Parse markets/industries from data."""
        if 'markets' in data:
            markets = data['markets']
            if isinstance(markets, list):
                return ', '.join([m.get('name', m) if isinstance(m, dict) else str(m) for m in markets[:3]])
            elif isinstance(markets, str):
                return markets
        
        return ''
    
    def _parse_funding(self, funding_data: Any) -> Optional[float]:
        """Parse funding amount from various formats."""
        if not funding_data:
            return None
        
        if isinstance(funding_data, (int, float)):
            return float(funding_data)
        
        if isinstance(funding_data, str):
            # Remove currency symbols
            funding_data = funding_data.replace('$', '').replace(',', '').strip().upper()
            
            try:
                if 'M' in funding_data:
                    return float(funding_data.replace('M', '')) * 1_000_000
                elif 'K' in funding_data:
                    return float(funding_data.replace('K', '')) * 1_000
                elif 'B' in funding_data:
                    return float(funding_data.replace('B', '')) * 1_000_000_000
                else:
                    return float(funding_data)
            except:
                return None
        
        return None
    
    def _matches_filters(self, deal: Dict, filters: Dict) -> bool:
        """Check if deal matches filter criteria."""
        
        # Location filter
        if 'locations' in filters:
            location = deal.get('location', '').lower()
            if not any(loc.lower() in location for loc in filters['locations']):
                return False
        
        # Market/industry filter
        if 'markets' in filters:
            industry = deal.get('industry', '').lower()
            if not any(market.lower() in industry for market in filters['markets']):
                return False
        
        # Min funding filter
        if 'min_funding' in filters:
            funding = deal.get('total_funding')
            if not funding or funding < filters['min_funding']:
                return False
        
        return True
    
    async def get_startup_details(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed startup information from AngelList.
        
        Args:
            slug: Startup URL slug
            
        Returns:
            Startup details dictionary
        """
        try:
            url = f"{self.base_url}/company/{slug}"
            
            html = await self._fetch_page(url)
            if not html:
                return None
            
            soup = self._parse_html(html)
            
            # Try to extract JSON data first
            script_tags = soup.find_all('script', type='application/json')
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    startups = self._extract_startups_from_json(data)
                    if startups:
                        return self._parse_angellist_startup(startups[0])
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching AngelList startup {slug}: {e}")
            return None
