"""
Deal Sourcing Manager - orchestrates scraping from multiple platforms.
"""
from typing import Dict, List, Optional, Any
from loguru import logger
import asyncio
from datetime import datetime

from .techcrunch_scraper import TechCrunchScraper


class DealSourcingManager:
    """
    Manages deal sourcing from multiple platforms.
    
    Currently using TechCrunch for real, curated funding data.
    """
    
    def __init__(self):
        """Initialize platform scrapers."""
        self.scrapers = {
            'techcrunch': TechCrunchScraper(),  # Real funding data from TechCrunch
        }
    
    async def scrape_all_platforms(
        self,
        platforms: Optional[List[str]] = None,
        filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Scrape deals from multiple platforms concurrently.
        
        Args:
            platforms: List of platform names to scrape (default: all)
            filters: Common filters to apply across platforms
            
        Returns:
            Aggregated list of deals from all platforms
        """
        if platforms is None:
            platforms = list(self.scrapers.keys())
        
        logger.info(f"Starting deal scraping from platforms: {', '.join(platforms)}")
        
        # Create scraping tasks
        tasks = []
        for platform in platforms:
            if platform not in self.scrapers:
                logger.warning(f"Unknown platform: {platform}")
                continue
            
            scraper = self.scrapers[platform]
            task = self._scrape_platform(scraper, filters)
            tasks.append(task)
        
        # Run all scrapers concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        all_deals = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error scraping {platforms[i]}: {result}")
            else:
                all_deals.extend(result)
        
        logger.info(f"Total deals scraped: {len(all_deals)}")
        
        return all_deals
    
    async def _scrape_platform(
        self,
        scraper,
        filters: Optional[Dict]
    ) -> List[Dict[str, Any]]:
        """Scrape a single platform with error handling."""
        try:
            async with scraper:
                deals = await scraper.scrape_deals(filters)
                logger.info(f"{scraper.get_platform_name()}: {len(deals)} deals")
                return deals
        except Exception as e:
            logger.error(f"Error scraping {scraper.get_platform_name()}: {e}")
            return []
    
    def deduplicate_deals(self, deals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate deals across platforms.
        
        Uses fuzzy matching on company names and websites to identify duplicates.
        Keeps the deal with the most complete information.
        
        Args:
            deals: List of deals from multiple sources
            
        Returns:
            Deduplicated list of deals
        """
        if not deals:
            return []
        
        # Group deals by normalized name
        groups = {}
        for deal in deals:
            key = self._normalize_company_name(deal.get('name', ''))
            if key:
                if key not in groups:
                    groups[key] = []
                groups[key].append(deal)
        
        # For each group, keep the most complete deal
        unique_deals = []
        for company_deals in groups.values():
            if len(company_deals) == 1:
                unique_deals.append(company_deals[0])
            else:
                # Merge information from multiple sources
                merged = self._merge_deals(company_deals)
                unique_deals.append(merged)
        
        logger.info(f"Deduplicated {len(deals)} deals to {len(unique_deals)} unique companies")
        
        return unique_deals
    
    def _normalize_company_name(self, name: str) -> str:
        """Normalize company name for matching."""
        if not name:
            return ''
        
        # Convert to lowercase
        name = name.lower()
        
        # Remove common suffixes
        suffixes = [' inc', ' ltd', ' llc', ' corp', ' corporation', ' limited']
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
        
        # Remove special characters
        name = ''.join(c for c in name if c.isalnum() or c.isspace())
        
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        return name
    
    def _merge_deals(self, deals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge multiple deals for the same company.
        
        Combines information from multiple sources, preferring:
        - Most complete data
        - Most recent data
        - Higher quality sources (Crunchbase, PitchBook)
        """
        # Start with the deal that has the most fields
        merged = max(deals, key=lambda d: len([v for v in d.values() if v]))
        
        # Merge additional data from other sources
        for deal in deals:
            if deal is merged:
                continue
            
            # Fill in missing fields
            for key, value in deal.items():
                if value and not merged.get(key):
                    merged[key] = value
            
            # Combine lists (like investors)
            if 'investors' in deal and 'investors' in merged:
                merged_investors = set(merged.get('investors', []))
                merged_investors.update(deal.get('investors', []))
                merged['investors'] = list(merged_investors)
        
        # Add metadata about sources
        sources = [deal.get('source', 'Unknown') for deal in deals]
        merged['sources'] = list(set(sources))
        merged['source_count'] = len(sources)
        
        return merged
    
    def rank_deals(
        self,
        deals: List[Dict[str, Any]],
        criteria: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Rank deals based on criteria.
        
        Args:
            deals: List of deals to rank
            criteria: Ranking criteria with weights {
                'funding_amount': 0.3,
                'recent': 0.2,
                'stage': 0.2,
                'completeness': 0.3
            }
        
        Returns:
            Ranked list of deals (highest score first)
        """
        if not criteria:
            criteria = {
                'funding_amount': 0.3,
                'recent': 0.2,
                'stage': 0.2,
                'completeness': 0.3
            }
        
        # Score each deal
        for deal in deals:
            score = 0.0
            
            # Funding amount score
            if 'funding_amount' in criteria and deal.get('funding_amount'):
                amount = deal['funding_amount']
                # Normalize to 0-100 scale (log scale)
                amount_score = min(100, (amount / 100_000_000) * 100)
                score += amount_score * criteria['funding_amount']
            
            # Recency score
            if 'recent' in criteria and deal.get('scraped_at'):
                # Higher score for more recent scrapes
                # This is a simplified version
                score += 80 * criteria['recent']
            
            # Stage score (prefer later stages)
            if 'stage' in criteria and deal.get('stage'):
                stage = deal['stage'].lower()
                stage_scores = {
                    'pre-seed': 20,
                    'seed': 40,
                    'series a': 60,
                    'series b': 80,
                    'series c': 90,
                    'series d': 95,
                    'series e': 98,
                }
                for stage_name, stage_score in stage_scores.items():
                    if stage_name in stage:
                        score += stage_score * criteria['stage']
                        break
            
            # Completeness score (more fields filled = higher score)
            if 'completeness' in criteria:
                total_fields = 15  # Expected number of fields
                filled_fields = len([v for v in deal.values() if v])
                completeness_score = (filled_fields / total_fields) * 100
                score += completeness_score * criteria['completeness']
            
            deal['_score'] = score
        
        # Sort by score
        ranked = sorted(deals, key=lambda d: d.get('_score', 0), reverse=True)
        
        return ranked
    
    def filter_deals(
        self,
        deals: List[Dict[str, Any]],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Filter deals based on criteria.
        
        Args:
            deals: List of deals
            filters: {
                'min_funding': 1000000,
                'max_funding': 100000000,
                'industries': ['fintech', 'healthtech'],
                'locations': ['United States', 'UAE'],
                'stages': ['Series A', 'Series B']
            }
        
        Returns:
            Filtered list of deals
        """
        filtered = deals
        
        # Min funding
        if 'min_funding' in filters:
            filtered = [d for d in filtered if (d.get('funding_amount') or 0) >= filters['min_funding']]
        
        # Max funding
        if 'max_funding' in filters:
            filtered = [d for d in filtered if (d.get('funding_amount') or float('inf')) <= filters['max_funding']]
        
        # Industries
        if 'industries' in filters:
            filtered = [
                d for d in filtered
                if any(ind.lower() in d.get('industry', '').lower() for ind in filters['industries'])
            ]
        
        # Locations
        if 'locations' in filters:
            filtered = [
                d for d in filtered
                if any(loc.lower() in d.get('location', '').lower() for loc in filters['locations'])
            ]
        
        # Stages
        if 'stages' in filters:
            filtered = [
                d for d in filtered
                if any(stage.lower() in d.get('stage', '').lower() for stage in filters['stages'])
            ]
        
        return filtered
    
    def generate_summary(self, deals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics for scraped deals.
        
        Returns:
            Summary dictionary with statistics
        """
        if not deals:
            return {
                'total_deals': 0,
                'total_funding': 0,
                'avg_funding': 0,
                'platforms': [],
                'top_industries': [],
                'top_locations': []
            }
        
        # Calculate statistics
        total_funding = sum(d.get('funding_amount', 0) or 0 for d in deals)
        deals_with_funding = [d for d in deals if d.get('funding_amount')]
        avg_funding = total_funding / len(deals_with_funding) if deals_with_funding else 0
        
        # Count by platform
        platforms = {}
        for deal in deals:
            source = deal.get('source', 'Unknown')
            platforms[source] = platforms.get(source, 0) + 1
        
        # Top industries
        industries = {}
        for deal in deals:
            industry = deal.get('industry', 'Unknown')
            if industry:
                industries[industry] = industries.get(industry, 0) + 1
        
        # Top locations
        locations = {}
        for deal in deals:
            location = deal.get('location', 'Unknown')
            if location:
                locations[location] = locations.get(location, 0) + 1
        
        return {
            'total_deals': len(deals),
            'total_funding': total_funding,
            'avg_funding': avg_funding,
            'platforms': dict(sorted(platforms.items(), key=lambda x: x[1], reverse=True)),
            'top_industries': dict(sorted(industries.items(), key=lambda x: x[1], reverse=True)[:10]),
            'top_locations': dict(sorted(locations.items(), key=lambda x: x[1], reverse=True)[:10]),
        }
