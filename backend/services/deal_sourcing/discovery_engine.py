"""
Daily Deal Discovery Engine
Multi-source deal aggregation and filtering system

Discovers investment opportunities from multiple sources:
- Crunchbase (recent funding rounds)
- AngelList (startup profiles)
- Y Combinator (batch companies)
- TechCrunch (funding announcements)
- Accelerator websites (IndieBio, a16z, etc.)
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from loguru import logger
import asyncio
from enum import Enum

from services.web_scraping.techcrunch_scraper import TechCrunchScraper
from services.web_scraping.base_scraper import BaseScraper


class DealStage(str, Enum):
    """Investment stages"""
    PRE_SEED = "Pre-Seed"
    SEED = "Seed"
    SERIES_A = "Series A"
    SERIES_B = "Series B"
    SERIES_C = "Series C"
    GROWTH = "Growth"


class DealSector(str, Enum):
    """Industry sectors"""
    FINTECH = "Fintech"
    CLIMATETECH = "ClimateTech"
    ENTERPRISE_SAAS = "Enterprise SaaS"
    HEALTHCARE = "Healthcare"
    AGRITECH = "AgriTech"
    AI_ML = "AI & Machine Learning"
    CYBERSECURITY = "Cybersecurity"
    ECOMMERCE = "E-commerce"
    EDTECH = "EdTech"
    PROPTECH = "PropTech"


@dataclass
class DealCriteria:
    """Filtering criteria for deal discovery"""
    sectors: List[str] = None  # e.g., ["Fintech", "ClimateTech"]
    stages: List[str] = None  # e.g., ["Seed", "Series A", "Series B"]
    min_revenue: Optional[float] = 500_000  # $500K
    max_revenue: Optional[float] = 10_000_000  # $10M
    geographies: List[str] = None  # e.g., ["North America", "Europe"]
    min_funding: Optional[float] = None  # Minimum funding amount
    max_funding: Optional[float] = None  # Maximum funding amount
    signal_sources: List[str] = None  # e.g., ["accelerator", "recent_funding", "ip"]
    days_back: int = 30  # Look back N days for recent deals
    
    def __post_init__(self):
        """Set defaults"""
        if self.sectors is None:
            self.sectors = ["Fintech", "ClimateTech", "Enterprise SaaS"]
        if self.stages is None:
            self.stages = ["Seed", "Series A", "Series B"]
        if self.geographies is None:
            self.geographies = ["North America", "Europe"]
        if self.signal_sources is None:
            self.signal_sources = ["accelerator", "recent_funding", "traction", "ip"]


@dataclass
class DealSignal:
    """Investment signal for a deal"""
    type: str  # "accelerator", "recent_funding", "traction", "ip", "team"
    description: str
    strength: float  # 0-1 confidence score
    source: str


@dataclass
class DiscoveredDeal:
    """A discovered investment opportunity"""
    company_name: str
    sector: str
    stage: str
    description: str
    funding_amount: Optional[float] = None
    funding_round: Optional[str] = None
    lead_investor: Optional[str] = None
    revenue: Optional[float] = None  # ARR or trailing 12 months
    location: str = None
    country: str = None
    founded_year: Optional[int] = None
    team_size: Optional[int] = None
    website: Optional[str] = None
    
    # Signals
    key_signals: List[str] = None
    potential_fit: str = None
    risk_flags: List[str] = None
    
    # Metadata
    sources: List[str] = None  # Where we found this deal
    discovered_at: datetime = None
    last_updated: datetime = None
    confidence_score: float = 0.0  # 0-1 overall confidence
    
    def __post_init__(self):
        if self.key_signals is None:
            self.key_signals = []
        if self.risk_flags is None:
            self.risk_flags = []
        if self.sources is None:
            self.sources = []
        if self.discovered_at is None:
            self.discovered_at = datetime.utcnow()
        if self.last_updated is None:
            self.last_updated = datetime.utcnow()


class DealDiscoveryEngine:
    """
    Multi-source deal discovery engine
    
    Aggregates deals from multiple sources and filters by criteria
    """
    
    def __init__(self):
        self.sources = {
            'techcrunch': TechCrunchScraper(),
            # Add more scrapers as they're built
        }
        logger.info("DealDiscoveryEngine initialized")
    
    async def discover_deals(
        self,
        criteria: DealCriteria,
        max_deals: int = 50
    ) -> List[DiscoveredDeal]:
        """
        Discover deals matching criteria from all sources
        
        Args:
            criteria: Filtering criteria
            max_deals: Maximum number of deals to return
            
        Returns:
            List of discovered deals sorted by relevance
        """
        logger.info(f"Starting deal discovery with criteria: {criteria}")
        
        # Collect deals from all sources
        all_deals = []
        
        # Scrape TechCrunch
        try:
            tc_deals = await self._scrape_techcrunch(criteria)
            all_deals.extend(tc_deals)
            logger.info(f"Found {len(tc_deals)} deals from TechCrunch")
        except Exception as e:
            logger.error(f"Error scraping TechCrunch: {e}")
        
        # Scrape AngelList (placeholder - to be implemented)
        try:
            al_deals = await self._scrape_angellist(criteria)
            all_deals.extend(al_deals)
            logger.info(f"Found {len(al_deals)} deals from AngelList")
        except Exception as e:
            logger.error(f"Error scraping AngelList: {e}")
        
        # Scrape Y Combinator (placeholder - to be implemented)
        try:
            yc_deals = await self._scrape_yc(criteria)
            all_deals.extend(yc_deals)
            logger.info(f"Found {len(yc_deals)} deals from YC")
        except Exception as e:
            logger.error(f"Error scraping YC: {e}")
        
        # Filter deals by criteria
        filtered_deals = self._filter_deals(all_deals, criteria)
        logger.info(f"Filtered to {len(filtered_deals)} deals matching criteria")
        
        # Score and rank deals
        scored_deals = self._score_deals(filtered_deals, criteria)
        
        # Sort by confidence score
        scored_deals.sort(key=lambda d: d.confidence_score, reverse=True)
        
        # Return top N deals
        result = scored_deals[:max_deals]
        logger.info(f"Returning {len(result)} top deals")
        
        return result
    
    async def _scrape_techcrunch(self, criteria: DealCriteria) -> List[DiscoveredDeal]:
        """Scrape deals from TechCrunch"""
        scraper = self.sources['techcrunch']
        
        # Scrape recent funding announcements
        raw_deals = await scraper.scrape_deals(filters={})
        
        # Convert to DiscoveredDeal format
        discovered_deals = []
        for raw_deal in raw_deals:
            deal = self._normalize_techcrunch_deal(raw_deal)
            if deal:
                discovered_deals.append(deal)
        
        return discovered_deals
    
    def _normalize_techcrunch_deal(self, raw_deal: Dict) -> Optional[DiscoveredDeal]:
        """Convert TechCrunch raw deal to DiscoveredDeal"""
        try:
            # Map TechCrunch field names to our format
            company_name = raw_deal.get('name') or raw_deal.get('company_name', 'Unknown')
            
            # Extract investors (can be list or single)
            investors = raw_deal.get('investors', [])
            lead_investor = investors[0] if isinstance(investors, list) and investors else str(investors) if investors else None
            
            # Extract key signals
            key_signals = []
            funding_amount = raw_deal.get('funding_amount', 0)
            if funding_amount > 1_000_000:
                key_signals.append(f"Recent funding round ${funding_amount/1_000_000:.1f}M")
            if lead_investor:
                key_signals.append(f"Led by {lead_investor}")
            if raw_deal.get('source_article_title'):
                key_signals.append(f"Featured in TechCrunch")
            
            # Determine potential fit
            potential_fit = self._assess_fit(raw_deal)
            
            # Identify risk flags
            risk_flags = self._identify_risks(raw_deal)
            
            # Parse funding date
            funding_date = raw_deal.get('funding_date')
            discovered_at = datetime.utcnow()
            if funding_date:
                try:
                    discovered_at = datetime.strptime(funding_date, '%Y-%m-%d')
                except:
                    pass
            
            deal = DiscoveredDeal(
                company_name=company_name,
                sector=raw_deal.get('industry', 'Unknown'),
                stage=raw_deal.get('stage', raw_deal.get('funding_stage', 'Unknown')),
                description=raw_deal.get('description', ''),
                funding_amount=funding_amount,
                funding_round=raw_deal.get('stage', raw_deal.get('funding_round')),
                lead_investor=lead_investor,
                revenue=raw_deal.get('revenue'),
                location=raw_deal.get('location'),
                country=raw_deal.get('country'),
                website=raw_deal.get('website') or raw_deal.get('source_url'),
                key_signals=key_signals,
                potential_fit=potential_fit,
                risk_flags=risk_flags,
                sources=['TechCrunch'],
                discovered_at=discovered_at
            )
            
            return deal
        
        except Exception as e:
            logger.error(f"Error normalizing TechCrunch deal: {e}")
            return None
    
    async def _scrape_angellist(self, criteria: DealCriteria) -> List[DiscoveredDeal]:
        """
        Scrape deals from AngelList
        
        TODO: Implement AngelList scraper
        - Use AngelList API if available
        - Or scrape angellist.com/companies
        - Filter by stage, sector, location
        """
        logger.warning("AngelList scraping not yet implemented")
        return []
    
    async def _scrape_yc(self, criteria: DealCriteria) -> List[DiscoveredDeal]:
        """
        Scrape deals from Y Combinator
        
        TODO: Implement YC scraper
        - Scrape current batch from ycombinator.com/companies
        - Filter by sector/stage
        - Extract Demo Day information
        """
        logger.warning("YC scraping not yet implemented")
        return []
    
    def _filter_deals(
        self,
        deals: List[DiscoveredDeal],
        criteria: DealCriteria
    ) -> List[DiscoveredDeal]:
        """Filter deals by criteria"""
        filtered = []
        
        for deal in deals:
            
            # Check sector
            if criteria.sectors and deal.sector not in criteria.sectors:
                # Fuzzy matching for sectors - match if any word overlaps
                sector_match = False
                deal_sector_lower = deal.sector.lower()
                for criteria_sector in criteria.sectors:
                    # Split both into words and check for overlaps (remove punctuation)
                    import string
                    translator = str.maketrans('', '', string.punctuation)
                    
                    criteria_clean = criteria_sector.lower().translate(translator)
                    deal_clean = deal_sector_lower.translate(translator)
                    
                    criteria_words = set(criteria_clean.split())
                    deal_words = set(deal_clean.split())
                    
                    # If any significant words match (excluding common words)
                    common_words = {'and', 'the', 'or', 'in', 'of', 'to', 'a'}
                    criteria_words_clean = criteria_words - common_words
                    deal_words_clean = deal_words - common_words
                    
                    if criteria_words_clean & deal_words_clean:  # If intersection exists
                        sector_match = True
                        break
                    
                    # Also check simple substring match
                    if criteria_clean in deal_clean or deal_clean in criteria_clean:
                        sector_match = True
                        break
                
                if not sector_match:
                    continue
                else:
                    logger.info(f"  ✅ Sector match: '{deal.sector}'")
            
            # Check stage
            if criteria.stages and deal.stage not in criteria.stages:
                if not any(s.lower() in deal.stage.lower() for s in criteria.stages):
                    continue
            
            # Check revenue range
            if deal.revenue:
                if criteria.min_revenue and deal.revenue < criteria.min_revenue:
                    continue
                if criteria.max_revenue and deal.revenue > criteria.max_revenue:
                    continue
            
            # Check funding range
            if deal.funding_amount:
                if criteria.min_funding and deal.funding_amount < criteria.min_funding:
                    continue
                if criteria.max_funding and deal.funding_amount > criteria.max_funding:
                    continue
            
            # Check geography (fuzzy matching with smarter location detection)
            if criteria.geographies and deal.location:
                geo_match = False
                
                # Smart geography mapping
                north_america_indicators = ['usa', 'us', 'united states', 'canada', 'mexico', 'ca', 'ny', 'tx', 'fl', 'il', 
                                            'san francisco', 'new york', 'los angeles', 'boston', 'austin', 'seattle',
                                            'toronto', 'vancouver', 'montreal']
                europe_indicators = ['uk', 'united kingdom', 'germany', 'france', 'spain', 'italy', 'netherlands', 'sweden',
                                    'london', 'berlin', 'paris', 'amsterdam', 'stockholm', 'madrid', 'dublin']
                
                location_lower = deal.location.lower()
                
                for geo in criteria.geographies:
                    geo_lower = geo.lower()
                    
                    # Direct match
                    if geo_lower in location_lower:
                        geo_match = True
                        break
                    
                    # Smart matching for North America
                    if 'north america' in geo_lower or 'america' in geo_lower:
                        if any(indicator in location_lower for indicator in north_america_indicators):
                            geo_match = True
                            break
                    
                    # Smart matching for Europe
                    if 'europe' in geo_lower:
                        if any(indicator in location_lower for indicator in europe_indicators):
                            geo_match = True
                            break
                
                if not geo_match:
                    continue
            
            # All criteria passed
            filtered.append(deal)
        
        logger.info(f"Filtered {len(deals)} deals to {len(filtered)} matching criteria")
        return filtered
    
    def _score_deals(
        self,
        deals: List[DiscoveredDeal],
        criteria: DealCriteria
    ) -> List[DiscoveredDeal]:
        """Score deals based on fit and signals"""
        for deal in deals:
            score = 0.0
            
            # Score based on signals
            if deal.key_signals:
                score += len(deal.key_signals) * 0.1
            
            # Score based on funding amount (bigger = more notable)
            if deal.funding_amount:
                if deal.funding_amount > 10_000_000:
                    score += 0.3
                elif deal.funding_amount > 5_000_000:
                    score += 0.2
                elif deal.funding_amount > 1_000_000:
                    score += 0.1
            
            # Score based on stage match
            if criteria.stages and deal.stage in criteria.stages:
                score += 0.2
            
            # Score based on sector match
            if criteria.sectors and deal.sector in criteria.sectors:
                score += 0.2
            
            # Penalty for risk flags
            if deal.risk_flags:
                score -= len(deal.risk_flags) * 0.05
            
            # Score based on data completeness
            completeness = sum([
                bool(deal.funding_amount),
                bool(deal.revenue),
                bool(deal.lead_investor),
                bool(deal.website),
                bool(deal.description),
                bool(deal.location)
            ]) / 6.0
            score += completeness * 0.2
            
            # Normalize to 0-1
            deal.confidence_score = max(0.0, min(1.0, score))
        
        return deals
    
    def _assess_fit(self, raw_deal: Dict) -> str:
        """Assess potential investment fit"""
        factors = []
        
        # Check stage
        stage = raw_deal.get('funding_stage', '')
        if any(s in stage for s in ['Seed', 'Series A', 'Series B']):
            factors.append("appropriate stage")
        
        # Check industry
        industry = raw_deal.get('industry', '')
        if any(i in industry for i in ['Fintech', 'Climate', 'SaaS', 'Enterprise']):
            factors.append("target sector")
        
        # Check team
        if raw_deal.get('founders'):
            factors.append("experienced team")
        
        # Check traction
        if raw_deal.get('revenue', 0) > 1_000_000:
            factors.append("revenue traction")
        
        if factors:
            return f"{', '.join(factors)}"
        else:
            return "Requires further evaluation"
    
    def _identify_risks(self, raw_deal: Dict) -> List[str]:
        """Identify potential risk flags"""
        risks = []
        
        # Early stage risks
        stage = raw_deal.get('funding_stage', '')
        if 'Pre-Seed' in stage or 'Seed' in stage:
            if not raw_deal.get('revenue'):
                risks.append("Pre-revenue / early validation needed")
        
        # Market risks
        if raw_deal.get('competitors', 0) > 10:
            risks.append("Highly competitive market")
        
        # Team risks
        if raw_deal.get('team_size', 0) < 5:
            risks.append("Small team")
        
        # Tech risks
        industry = raw_deal.get('industry', '')
        if any(term in industry.lower() for term in ['pilot', 'prototype', 'development']):
            risks.append("Technology still in development phase")
        
        return risks
    
    async def generate_daily_report(
        self,
        criteria: DealCriteria,
        max_deals: int = 20
    ) -> Dict[str, Any]:
        """
        Generate a daily potential deals report
        
        Returns structured data for report generation
        """
        logger.info("Generating daily deals report")
        
        # Discover deals
        deals = await self.discover_deals(criteria, max_deals)
        
        # Build report
        report = {
            'date': datetime.utcnow().strftime('%B %d, %Y'),
            'generated_by': 'AI Investment Copilot',
            'criteria': {
                'sectors': criteria.sectors,
                'stages': criteria.stages,
                'revenue_range': f"${criteria.min_revenue:,.0f} - ${criteria.max_revenue:,.0f}" if criteria.min_revenue and criteria.max_revenue else "Any",
                'geographies': criteria.geographies,
                'signal_sources': criteria.signal_sources
            },
            'deal_count': len(deals),
            'deals': deals
        }
        
        logger.info(f"Report generated with {len(deals)} deals")
        return report
