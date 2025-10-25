"""
Magnitt scraper for Middle East deal sourcing.
https://magnitt.com/

Magnitt is a leading platform for MENA region startups and funding data.
"""
from typing import Dict, List, Optional, Any
from loguru import logger
import re

from .base_scraper import BaseScraper


class MagnittScraper(BaseScraper):
    """
    Scraper for Magnitt (MENA region focus).
    
    Magnitt provides data on:
    - MENA startups
    - Funding rounds
    - Investors
    - Accelerators
    """
    
    def __init__(self):
        super().__init__(rate_limit=2.0)  # 2 seconds between requests
        self.base_url = 'https://magnitt.com'
    
    def get_platform_name(self) -> str:
        return "Magnitt"
    
    async def scrape_deals(self, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Scrape recent funding deals from Magnitt.
        
        Args:
            filters: {
                'countries': ['UAE', 'Saudi Arabia', 'Egypt'],
                'industries': ['fintech', 'ecommerce'],
                'stages': ['seed', 'series-a'],
                'min_funding': 100000
            }
        
        Returns:
            List of deals
        """
        filters = filters or {}
        deals = []
        
        # TEMPORARY: Return mock data for testing UI
        # TODO: Implement real scraping after inspecting actual HTML structure
        logger.warning("Using mock data - real scraping not yet implemented")
        
        mock_deals = [
            {
                'name': 'TechStart MENA',
                'description': 'E-commerce platform connecting regional merchants',
                'industry': 'E-commerce',
                'stage': 'Series A',
                'location': 'Dubai, UAE',
                'funding_amount': 2500000,
                'source_url': f'{self.base_url}/companies/techstart-mena'
            },
            {
                'name': 'FinFlow Arabia',
                'description': 'Digital payments and financial services',
                'industry': 'Fintech',
                'stage': 'Seed',
                'location': 'Riyadh, Saudi Arabia',
                'funding_amount': 1200000,
                'source_url': f'{self.base_url}/companies/finflow-arabia'
            },
            {
                'name': 'HealthHub Egypt',
                'description': 'Telemedicine platform for MENA region',
                'industry': 'Healthcare',
                'stage': 'Series A',
                'location': 'Cairo, Egypt',
                'funding_amount': 3500000,
                'source_url': f'{self.base_url}/companies/healthhub-egypt'
            }
        ]
        
        # Apply filters to mock data
        for deal in mock_deals:
            if self._matches_filters(deal, filters):
                deals.append(self._normalize_deal(deal))
        
        logger.info(f"Scraped {len(deals)} deals from Magnitt (mock data)")
        return deals
    
    def _parse_magnitt_card(self, card) -> Dict[str, Any]:
        """Parse a Magnitt funding card."""
        
        # Extract company name
        name_elem = card.find(['h2', 'h3', 'h4'], class_=re.compile(r'(title|name|company)', re.I))
        name = name_elem.get_text(strip=True) if name_elem else ''
        
        # Extract description
        desc_elem = card.find('p', class_=re.compile(r'description', re.I))
        description = desc_elem.get_text(strip=True) if desc_elem else ''
        
        # Extract funding amount
        amount_elem = card.find(['span', 'div'], class_=re.compile(r'(amount|funding|raised)', re.I))
        funding_amount = self._parse_funding_amount(amount_elem.get_text(strip=True)) if amount_elem else None
        
        # Extract stage
        stage_elem = card.find(['span', 'div'], class_=re.compile(r'(stage|round)', re.I))
        stage = stage_elem.get_text(strip=True) if stage_elem else ''
        
        # Extract location
        location_elem = card.find(['span', 'div'], class_=re.compile(r'(location|country|city)', re.I))
        location = location_elem.get_text(strip=True) if location_elem else ''
        
        # Extract industry
        industry_elem = card.find(['span', 'div'], class_=re.compile(r'(industry|sector|category)', re.I))
        industry = industry_elem.get_text(strip=True) if industry_elem else ''
        
        # Get URL
        link_elem = card.find('a', href=True)
        source_url = f"{self.base_url}{link_elem['href']}" if link_elem and not link_elem['href'].startswith('http') else (link_elem['href'] if link_elem else '')
        
        return {
            'name': name,
            'description': description,
            'industry': industry,
            'stage': stage,
            'location': location,
            'funding_amount': funding_amount,
            'source_url': source_url
        }
    
    def _parse_funding_amount(self, text: str) -> Optional[float]:
        """Parse funding amount from text like '$1.5M' or '$500K'."""
        try:
            # Remove currency symbols and spaces
            text = text.replace('$', '').replace(',', '').strip().upper()
            
            # Handle millions
            if 'M' in text:
                amount = float(text.replace('M', '')) * 1_000_000
                return amount
            
            # Handle thousands
            if 'K' in text:
                amount = float(text.replace('K', '')) * 1_000
                return amount
            
            # Handle billions
            if 'B' in text:
                amount = float(text.replace('B', '')) * 1_000_000_000
                return amount
            
            # Try direct conversion
            return float(text)
        
        except:
            return None
    
    def _matches_filters(self, deal: Dict, filters: Dict) -> bool:
        """Check if deal matches filter criteria."""
        
        # Country filter
        if 'countries' in filters:
            if not any(country.lower() in deal.get('location', '').lower() for country in filters['countries']):
                return False
        
        # Industry filter
        if 'industries' in filters:
            if not any(industry.lower() in deal.get('industry', '').lower() for industry in filters['industries']):
                return False
        
        # Stage filter
        if 'stages' in filters:
            if not any(stage.lower() in deal.get('stage', '').lower() for stage in filters['stages']):
                return False
        
        # Min funding filter
        if 'min_funding' in filters:
            funding = deal.get('funding_amount')
            if not funding or funding < filters['min_funding']:
                return False
        
        return True
    
    async def get_company_profile(self, company_slug: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed company profile from Magnitt.
        
        Args:
            company_slug: Company URL slug
            
        Returns:
            Company data dictionary
        """
        try:
            url = f"{self.base_url}/companies/{company_slug}"
            
            html = await self._fetch_page(url)
            if not html:
                return None
            
            soup = self._parse_html(html)
            
            # Extract company details
            # Note: This is a template - actual structure may vary
            company = {
                'name': '',
                'description': '',
                'website': '',
                'industry': '',
                'location': '',
                'founded_year': None,
                'employee_count': '',
                'total_funding': None,
                'investors': [],
                'source_url': url
            }
            
            # Parse company name
            name_elem = soup.find('h1')
            if name_elem:
                company['name'] = name_elem.get_text(strip=True)
            
            # Parse description
            desc_elem = soup.find('div', class_=re.compile(r'description', re.I))
            if desc_elem:
                company['description'] = desc_elem.get_text(strip=True)
            
            # Parse website
            website_elem = soup.find('a', text=re.compile(r'website|visit', re.I))
            if website_elem and website_elem.get('href'):
                company['website'] = website_elem['href']
            
            return company
            
        except Exception as e:
            logger.error(f"Error fetching Magnitt profile {company_slug}: {e}")
            return None
