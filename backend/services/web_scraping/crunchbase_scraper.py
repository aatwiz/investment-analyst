"""
Crunchbase scraper for deal sourcing.
https://www.crunchbase.com/

Note: Crunchbase requires authentication and has rate limits.
For production, you'll need a Crunchbase API key.
"""
from typing import Dict, List, Optional, Any
from loguru import logger
import os

from .base_scraper import BaseScraper


class CrunchbaseScraper(BaseScraper):
    """
    Scraper for Crunchbase.
    
    Crunchbase provides comprehensive startup data including:
    - Funding rounds
    - Investors
    - Company profiles
    - M&A activity
    
    API Documentation: https://data.crunchbase.com/docs
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Crunchbase scraper.
        
        Args:
            api_key: Crunchbase API key (or set CRUNCHBASE_API_KEY env var)
        """
        super().__init__(rate_limit=1.0)  # 1 request per second
        self.api_key = api_key or os.getenv('CRUNCHBASE_API_KEY')
        self.base_url = 'https://api.crunchbase.com/api/v4'
        
        if not self.api_key:
            logger.warning("Crunchbase API key not set. Scraping will be limited.")
    
    def get_platform_name(self) -> str:
        return "Crunchbase"
    
    async def scrape_deals(self, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Scrape recent funding rounds from Crunchbase.
        
        Args:
            filters: {
                'industries': ['fintech', 'saas'],
                'locations': ['United States', 'UAE'],
                'funding_types': ['seed', 'series_a'],
                'min_funding': 1000000,
                'max_funding': 50000000,
                'date_from': '2025-01-01'
            }
        
        Returns:
            List of deals
        """
        if not self.api_key:
            logger.error("Cannot scrape Crunchbase without API key")
            return []
        
        filters = filters or {}
        deals = []
        
        try:
            # Search for recent funding rounds
            search_url = f"{self.base_url}/searches/funding_rounds"
            
            # Build query parameters
            query = {
                'user_key': self.api_key,
                'field_ids': [
                    'identifier',
                    'announced_on',
                    'funded_organization_identifier',
                    'money_raised',
                    'investment_type',
                    'investor_identifiers',
                    'lead_investor_identifiers'
                ],
                'order': [{'field_id': 'announced_on', 'sort': 'desc'}],
                'limit': 100
            }
            
            # Apply filters
            query_filters = []
            
            if 'funding_types' in filters:
                query_filters.append({
                    'type': 'predicate',
                    'field_id': 'investment_type',
                    'operator_id': 'includes',
                    'values': filters['funding_types']
                })
            
            if 'min_funding' in filters:
                query_filters.append({
                    'type': 'predicate',
                    'field_id': 'money_raised',
                    'operator_id': 'gte',
                    'values': [{'value': filters['min_funding'], 'currency': 'USD'}]
                })
            
            if 'date_from' in filters:
                query_filters.append({
                    'type': 'predicate',
                    'field_id': 'announced_on',
                    'operator_id': 'gte',
                    'values': [filters['date_from']]
                })
            
            if query_filters:
                query['query'] = query_filters
            
            # Fetch funding rounds
            html = await self._fetch_page(
                search_url,
                method='POST',
                headers={'Content-Type': 'application/json'},
                data=query
            )
            
            if not html:
                return deals
            
            # Parse response
            import json
            response = json.loads(html)
            
            for item in response.get('entities', []):
                properties = item.get('properties', {})
                organization = properties.get('funded_organization_identifier', {})
                
                # Get company details
                company_uuid = organization.get('uuid')
                if company_uuid:
                    company_data = await self._fetch_company_details(company_uuid)
                    if company_data:
                        deal = self._parse_funding_round(properties, company_data)
                        deals.append(self._normalize_deal(deal))
            
            logger.info(f"Scraped {len(deals)} deals from Crunchbase")
            
        except Exception as e:
            logger.error(f"Error scraping Crunchbase: {e}")
        
        return deals
    
    async def _fetch_company_details(self, company_uuid: str) -> Optional[Dict]:
        """Fetch detailed company information."""
        try:
            url = f"{self.base_url}/entities/organizations/{company_uuid}"
            params = {
                'user_key': self.api_key,
                'field_ids': [
                    'identifier',
                    'description',
                    'website',
                    'categories',
                    'location_identifiers',
                    'founded_on',
                    'num_employees_enum',
                    'funding_total'
                ]
            }
            
            html = await self._fetch_page(url, params=params)
            if html:
                import json
                return json.loads(html).get('properties', {})
        except Exception as e:
            logger.error(f"Error fetching company {company_uuid}: {e}")
        
        return None
    
    def _parse_funding_round(
        self,
        funding: Dict,
        company: Dict
    ) -> Dict[str, Any]:
        """Parse funding round and company data into standard format."""
        
        # Extract investors
        investors = []
        for investor in funding.get('investor_identifiers', []):
            investors.append(investor.get('value', ''))
        
        # Get lead investors
        lead_investors = []
        for investor in funding.get('lead_investor_identifiers', []):
            lead_investors.append(investor.get('value', ''))
        
        # Extract categories/industries
        categories = []
        for cat in company.get('categories', []):
            categories.append(cat.get('value', ''))
        
        # Get location
        locations = company.get('location_identifiers', [])
        location = locations[0].get('value', '') if locations else ''
        
        return {
            'name': company.get('identifier', {}).get('value', ''),
            'description': company.get('description', ''),
            'website': company.get('website', {}).get('value', ''),
            'industry': ', '.join(categories),
            'stage': funding.get('investment_type', {}).get('value', ''),
            'location': location,
            'founded_year': company.get('founded_on', {}).get('value', '')[:4] if company.get('founded_on') else None,
            'funding_amount': funding.get('money_raised', {}).get('value'),
            'funding_date': funding.get('announced_on', {}).get('value'),
            'investors': investors,
            'lead_investors': lead_investors,
            'total_funding': company.get('funding_total', {}).get('value'),
            'employee_count': company.get('num_employees_enum', ''),
            'source_url': f"https://www.crunchbase.com/organization/{company.get('identifier', {}).get('permalink', '')}"
        }
    
    async def search_companies(
        self,
        query: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search for companies by name or keyword.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of companies
        """
        if not self.api_key:
            return []
        
        try:
            url = f"{self.base_url}/autocompletes"
            params = {
                'user_key': self.api_key,
                'query': query,
                'collection_ids': 'organizations',
                'limit': limit
            }
            
            html = await self._fetch_page(url, params=params)
            if html:
                import json
                results = json.loads(html).get('entities', [])
                
                companies = []
                for result in results:
                    company_uuid = result.get('identifier', {}).get('uuid')
                    if company_uuid:
                        company_data = await self._fetch_company_details(company_uuid)
                        if company_data:
                            companies.append(company_data)
                
                return companies
        
        except Exception as e:
            logger.error(f"Error searching Crunchbase: {e}")
        
        return []
