"""
Companies/Deals API Routes - Feature 1: AI-Powered Deal Sourcing

Endpoints for managing companies and investment deals from various platforms.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from loguru import logger

from config.database import get_db
from services.web_scraping.deal_sourcing_manager import DealSourcingManager
from services.deal_qualification.qualifier import DealQualifier

router = APIRouter(prefix="/companies", tags=["companies"])


# Pydantic models for request/response
class ScrapeRequest(BaseModel):
    """Request to scrape deals from platforms."""
    platforms: List[str] = Field(
        default=['crunchbase', 'angellist', 'bloomberg', 'magnitt', 'wamda'],
        description="List of platforms to scrape"
    )
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Filters to apply: industries, locations, stages, min_funding, etc."
    )
    qualify: bool = Field(
        default=True,
        description="Whether to qualify deals after scraping"
    )
    min_score: float = Field(
        default=50.0,
        description="Minimum qualification score (0-100)"
    )


class QualifyRequest(BaseModel):
    """Request to qualify existing deals."""
    deal_ids: Optional[List[int]] = None
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Investment context: target_industries, target_stages, etc."
    )
    min_score: float = Field(default=50.0)


class DealFilter(BaseModel):
    """Filters for listing deals."""
    platforms: Optional[List[str]] = None
    industries: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    stages: Optional[List[str]] = None
    min_funding: Optional[float] = None
    max_funding: Optional[float] = None
    min_score: Optional[float] = None
    recommendations: Optional[List[str]] = None
    limit: int = Field(default=50, le=200)
    offset: int = Field(default=0, ge=0)


@router.post("/scrape", response_model=Dict[str, Any])
async def scrape_deals(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger scraping from selected platforms.
    
    This endpoint:
    1. Scrapes deals from specified platforms
    2. Deduplicates across sources
    3. Optionally qualifies deals using AI
    4. Stores in database
    5. Returns summary
    
    Example:
    ```
    POST /companies/scrape
    {
        "platforms": ["crunchbase", "magnitt"],
        "filters": {
            "industries": ["fintech", "healthtech"],
            "locations": ["UAE", "Saudi Arabia"],
            "min_funding": 1000000
        },
        "qualify": true,
        "min_score": 60.0
    }
    ```
    """
    try:
        logger.info(f"Starting deal scraping from platforms: {request.platforms}")
        
        # Initialize managers
        sourcing_manager = DealSourcingManager()
        
        # Scrape deals from platforms
        deals = await sourcing_manager.scrape_all_platforms(
            platforms=request.platforms,
            filters=request.filters
        )
        
        logger.info(f"Scraped {len(deals)} total deals")
        
        # Deduplicate
        unique_deals = sourcing_manager.deduplicate_deals(deals)
        logger.info(f"Deduplicated to {len(unique_deals)} unique companies")
        
        # Apply additional filters if provided
        if request.filters:
            unique_deals = sourcing_manager.filter_deals(unique_deals, request.filters)
            logger.info(f"Filtered to {len(unique_deals)} deals matching criteria")
        
        # Qualify deals if requested
        qualified_deals = []
        if request.qualify and unique_deals:
            qualifier = DealQualifier()
            qualified_results = await qualifier.qualify_batch(unique_deals)
            
            # Filter by minimum score
            qualified_deals = qualifier.filter_by_threshold(
                qualified_results,
                min_score=request.min_score
            )
            
            logger.info(f"Qualified {len(qualified_deals)} deals above score {request.min_score}")
        
        # TODO: Store in database (implement when Company model is ready)
        # For now, return the data
        
        # Generate summary
        summary = sourcing_manager.generate_summary(unique_deals)
        
        return {
            'success': True,
            'summary': {
                'total_scraped': len(deals),
                'unique_companies': len(unique_deals),
                'qualified_deals': len(qualified_deals) if qualified_deals else 0,
                **summary
            },
            'deals': qualified_deals[:20] if qualified_deals else unique_deals[:20],  # Return top 20
            'message': f"Successfully scraped {len(unique_deals)} unique deals"
        }
        
    except Exception as e:
        logger.error(f"Error scraping deals: {e}")
        raise HTTPException(status_code=500, detail=f"Error scraping deals: {str(e)}")


@router.get("/deals", response_model=Dict[str, Any])
async def list_deals(
    platforms: Optional[str] = None,
    industries: Optional[str] = None,
    locations: Optional[str] = None,
    stages: Optional[str] = None,
    min_funding: Optional[float] = None,
    max_funding: Optional[float] = None,
    min_score: Optional[float] = None,
    recommendations: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List deals with optional filtering.
    
    Query parameters:
    - platforms: Comma-separated platform names
    - industries: Comma-separated industries
    - locations: Comma-separated locations
    - stages: Comma-separated funding stages
    - min_funding: Minimum funding amount
    - max_funding: Maximum funding amount
    - min_score: Minimum qualification score
    - recommendations: Comma-separated recommendations (Strong Pass, Pass, etc.)
    - limit: Max results (default 50, max 200)
    - offset: Pagination offset
    
    Example:
    ```
    GET /companies/deals?industries=fintech,healthtech&min_score=70&limit=20
    ```
    """
    try:
        # TODO: Query from database when Company model is ready
        # For now, return sample response structure
        
        # Parse comma-separated parameters
        filters = {}
        if platforms:
            filters['platforms'] = [p.strip() for p in platforms.split(',')]
        if industries:
            filters['industries'] = [i.strip() for i in industries.split(',')]
        if locations:
            filters['locations'] = [l.strip() for l in locations.split(',')]
        if stages:
            filters['stages'] = [s.strip() for s in stages.split(',')]
        if min_funding:
            filters['min_funding'] = min_funding
        if max_funding:
            filters['max_funding'] = max_funding
        if min_score:
            filters['min_score'] = min_score
        if recommendations:
            filters['recommendations'] = [r.strip() for r in recommendations.split(',')]
        
        # TODO: Implement actual database query
        # deals = db.query(Company).filter(...).offset(offset).limit(limit).all()
        
        return {
            'success': True,
            'count': 0,
            'total': 0,
            'offset': offset,
            'limit': limit,
            'filters': filters,
            'deals': [],
            'message': 'Database integration pending - implement Company model storage'
        }
        
    except Exception as e:
        logger.error(f"Error listing deals: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing deals: {str(e)}")


@router.get("/deals/{deal_id}", response_model=Dict[str, Any])
async def get_deal(deal_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information for a specific deal.
    
    Returns:
    - Company information
    - Qualification scores and analysis
    - Source links
    - Historical data
    """
    try:
        # TODO: Query from database
        # deal = db.query(Company).filter(Company.id == deal_id).first()
        # if not deal:
        #     raise HTTPException(status_code=404, detail="Deal not found")
        
        return {
            'success': True,
            'deal': None,
            'message': 'Database integration pending'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching deal {deal_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching deal: {str(e)}")


@router.post("/qualify", response_model=Dict[str, Any])
async def qualify_deals(request: QualifyRequest, db: Session = Depends(get_db)):
    """
    Qualify/re-qualify deals using AI analysis.
    
    If deal_ids provided, qualifies those specific deals.
    Otherwise, qualifies all unqualified deals.
    
    Example:
    ```
    POST /companies/qualify
    {
        "deal_ids": [1, 2, 3],
        "context": {
            "target_industries": ["fintech", "healthtech"],
            "target_stages": ["Series A", "Series B"],
            "geographic_focus": ["MENA", "North America"]
        },
        "min_score": 60.0
    }
    ```
    """
    try:
        # TODO: Query deals from database
        # if request.deal_ids:
        #     deals = db.query(Company).filter(Company.id.in_(request.deal_ids)).all()
        # else:
        #     deals = db.query(Company).filter(Company.qualification_score.is_(None)).all()
        
        # Placeholder
        deals = []
        
        if not deals:
            return {
                'success': True,
                'qualified_count': 0,
                'message': 'No deals to qualify'
            }
        
        # Qualify deals
        qualifier = DealQualifier()
        results = await qualifier.qualify_batch(deals, context=request.context)
        
        # Filter by min_score
        qualified = qualifier.filter_by_threshold(results, min_score=request.min_score)
        
        # TODO: Update database with qualification results
        
        return {
            'success': True,
            'qualified_count': len(qualified),
            'results': qualified[:20],  # Return top 20
            'message': f'Qualified {len(qualified)} deals above score {request.min_score}'
        }
        
    except Exception as e:
        logger.error(f"Error qualifying deals: {e}")
        raise HTTPException(status_code=500, detail=f"Error qualifying deals: {str(e)}")


@router.get("/stats", response_model=Dict[str, Any])
async def get_stats(db: Session = Depends(get_db)):
    """
    Get overall statistics for deal pipeline.
    
    Returns:
    - Total deals by platform
    - Deals by stage
    - Top industries
    - Top locations
    - Qualification distribution
    - Recent activity
    """
    try:
        # TODO: Query aggregated stats from database
        
        return {
            'success': True,
            'stats': {
                'total_deals': 0,
                'by_platform': {},
                'by_stage': {},
                'by_industry': {},
                'by_location': {},
                'by_recommendation': {},
                'avg_score': 0,
                'last_updated': None
            },
            'message': 'Database integration pending'
        }
        
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")


@router.delete("/deals/{deal_id}")
async def delete_deal(deal_id: int, db: Session = Depends(get_db)):
    """Delete a deal from the database."""
    try:
        # TODO: Implement deletion
        # deal = db.query(Company).filter(Company.id == deal_id).first()
        # if not deal:
        #     raise HTTPException(status_code=404, detail="Deal not found")
        # db.delete(deal)
        # db.commit()
        
        return {
            'success': True,
            'message': 'Database integration pending'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting deal {deal_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting deal: {str(e)}")
