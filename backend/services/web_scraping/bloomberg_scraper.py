"""
Bloomberg scraper for funding news and deals.
https://www.bloomberg.com/

Bloomberg is a premium financial news platform with extensive
startup and venture capital coverage.

Note: Bloomberg has paywalls and restrictions. This scraper focuses on
publicly accessible content and RSS feeds where possible.
"""
from typing import Dict, List, Optional, Any
from loguru import logger
import re
from datetime import datetime, timedelta

from .base_scraper import BaseScraper


class BloombergScraper(BaseScraper):
    """
    Scraper for Bloomberg funding news.
    
    Focuses on:
    - Publicly accessible articles
    - RSS feeds
    - Technology/startup sections
    
    Note: Premium content behind paywall may not be accessible.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(rate_limit=3.0)  # Conservative rate limit
        self.base_url = 'https://www.bloomberg.com'
        self.api_key = api_key  # For Bloomberg Terminal API if available
    
    def get_platform_name(self) -> str:
        return "Bloomberg"
    
    async def scrape_deals(self, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Scrape funding news from Bloomberg.
        
        Args:
            filters: {
                'keywords': ['funding', 'raises', 'series'],
                'days_back': 7,
                'min_funding': 10000000
            }
        
        Returns:
            List of deals
        """
        filters = filters or {}
        deals = []
        
        try:
            # Bloomberg Technology section
            tech_url = f"{self.base_url}/technology"
            
            html = await self._fetch_page(tech_url)
            if not html:
                logger.warning("Could not fetch Bloomberg page")
                return deals
            
            soup = self._parse_html(html)
            
            # Find article links
            articles = soup.find_all('article')
            if not articles:
                articles = soup.find_all('div', class_=re.compile(r'story|article', re.I))
            
            for article in articles[:30]:  # Limit to avoid rate limiting
                try:
                    deal = self._parse_bloomberg_article(article)
                    
                    if deal and self._is_funding_news(deal) and self._matches_filters(deal, filters):
                        deals.append(self._normalize_deal(deal))
                
                except Exception as e:
                    logger.warning(f"Error parsing Bloomberg article: {e}")
                    continue
            
            logger.info(f"Scraped {len(deals)} deals from Bloomberg")
            
        except Exception as e:
            logger.error(f"Error scraping Bloomberg: {e}")
        
        return deals
    
    def _parse_bloomberg_article(self, article) -> Optional[Dict[str, Any]]:
        """Parse Bloomberg article for funding information."""
        
        # Extract headline
        headline_elem = article.find(['h1', 'h2', 'h3', 'a'], class_=re.compile(r'(headline|title)', re.I))
        if not headline_elem:
            return None
        
        headline = headline_elem.get_text(strip=True)
        
        # Extract summary/description
        summary_elem = article.find(['p', 'div'], class_=re.compile(r'(summary|abstract|description)', re.I))
        summary = summary_elem.get_text(strip=True) if summary_elem else headline
        
        # Get article URL
        link_elem = article.find('a', href=True)
        article_url = link_elem['href'] if link_elem else ''
        if article_url and not article_url.startswith('http'):
            article_url = f"{self.base_url}{article_url}"
        
        # Extract date
        date_elem = article.find('time')
        if not date_elem:
            date_elem = article.find(['span', 'div'], class_=re.compile(r'date|time', re.I))
        
        published_date = ''
        if date_elem:
            published_date = date_elem.get('datetime', date_elem.get_text(strip=True))
        
        # Try to extract key information from headline and summary
        company_name = self._extract_company_name(headline)
        funding_amount = self._extract_funding_amount(headline, summary)
        stage = self._extract_stage(headline, summary)
        
        return {
            'name': company_name,
            'description': summary,
            'funding_amount': funding_amount,
            'stage': stage,
            'funding_date': published_date,
            'source_url': article_url
        }
    
    def _is_funding_news(self, deal: Dict) -> bool:
        """Check if article is about funding/investment."""
        text = f"{deal.get('name', '')} {deal.get('description', '')}".lower()
        
        funding_keywords = [
            'raises', 'raised', 'funding', 'investment', 'series',
            'seed', 'round', 'venture', 'capital', 'investors',
            'valuation', 'closes', 'secures', 'million', 'billion'
        ]
        
        return any(keyword in text for keyword in funding_keywords)
    
    def _extract_company_name(self, text: str) -> str:
        """Extract company name from headline."""
        # Common patterns: "Company Raises $X" or "Company Gets $X Investment"
        patterns = [
            r'^([^,]+?)(?:\s+raises|\s+gets|\s+secures|\s+closes)',
            r'^([A-Z][a-zA-Z0-9\s&]+?)(?:\s+raises|\s+gets)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback: take first capitalized words
        words = []
        for word in text.split():
            if word[0].isupper() and len(word) > 1:
                words.append(word)
                if len(words) >= 3:
                    break
            elif words:  # Stop after first non-capitalized word
                break
        
        return ' '.join(words) if words else text[:50]
    
    def _extract_funding_amount(self, headline: str, summary: str) -> Optional[float]:
        """Extract funding amount from text."""
        text = f"{headline} {summary}"
        
        # Patterns for funding amounts
        patterns = [
            r'\$(\d+(?:\.\d+)?)\s*billion',
            r'\$(\d+(?:\.\d+)?)\s*million',
            r'\$(\d+(?:\.\d+)?)\s*([BMK])',
            r'(\d+(?:\.\d+)?)\s*billion',
            r'(\d+(?:\.\d+)?)\s*million',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = float(match.group(1))
                
                if 'billion' in pattern or 'B' in pattern:
                    return amount * 1_000_000_000
                elif 'million' in pattern or 'M' in pattern:
                    return amount * 1_000_000
                elif 'K' in pattern:
                    return amount * 1_000
        
        return None
    
    def _extract_stage(self, headline: str, summary: str) -> str:
        """Extract funding stage from text."""
        text = f"{headline} {summary}".lower()
        
        stages = {
            'series e': 'Series E',
            'series d': 'Series D',
            'series c': 'Series C',
            'series b': 'Series B',
            'series a': 'Series A',
            'seed round': 'Seed',
            'seed funding': 'Seed',
            'pre-seed': 'Pre-Seed',
        }
        
        for pattern, stage in stages.items():
            if pattern in text:
                return stage
        
        return ''
    
    def _matches_filters(self, deal: Dict, filters: Dict) -> bool:
        """Check if deal matches filter criteria."""
        
        # Keywords filter
        if 'keywords' in filters:
            text = f"{deal.get('name', '')} {deal.get('description', '')}".lower()
            if not any(keyword.lower() in text for keyword in filters['keywords']):
                return False
        
        # Min funding filter
        if 'min_funding' in filters:
            funding = deal.get('funding_amount')
            if not funding or funding < filters['min_funding']:
                return False
        
        # Days back filter
        if 'days_back' in filters:
            funding_date = deal.get('funding_date', '')
            if funding_date:
                try:
                    # Try to parse date
                    if isinstance(funding_date, str):
                        # Simple check - if date looks recent
                        cutoff = datetime.now() - timedelta(days=filters['days_back'])
                        # This is a simple heuristic - may need more sophisticated date parsing
                        pass
                except:
                    pass
        
        return True
    
    async def search_news(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Search Bloomberg news for specific query.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of news articles
        """
        try:
            # Bloomberg search URL
            search_url = f"{self.base_url}/search"
            params = {'query': query}
            
            html = await self._fetch_page(search_url, params=params)
            if not html:
                return []
            
            soup = self._parse_html(html)
            articles = []
            
            results = soup.find_all('article')[:max_results]
            for result in results:
                article = self._parse_bloomberg_article(result)
                if article:
                    articles.append(article)
            
            return articles
            
        except Exception as e:
            logger.error(f"Error searching Bloomberg: {e}")
            return []
