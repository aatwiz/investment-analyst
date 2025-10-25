"""
Companies/Deals API Routes - Feature 1: AI-Powered Deal Sourcing

Endpoints for managing companies and investment deals from various platforms.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from loguru import logger
from io import BytesIO

from config.database import get_db
from services.web_scraping.deal_sourcing_manager import DealSourcingManager
from services.deal_qualification.qualifier import DealQualifier
from services.deal_sourcing.discovery_engine import DealDiscoveryEngine, DealCriteria
from services.deal_sourcing.report_generator import DealReportGenerator

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


# ========== NEW: Deal Discovery & Report Generation ==========

class DiscoverDealsRequest(BaseModel):
    """Request to discover deals with criteria"""
    sectors: List[str] = Field(
        default=["Fintech", "ClimateTech", "Enterprise SaaS"],
        description="Target sectors"
    )
    stages: List[str] = Field(
        default=["Seed", "Series A", "Series B"],
        description="Target stages"
    )
    min_revenue: Optional[float] = Field(
        default=500_000,
        description="Minimum revenue ($)"
    )
    max_revenue: Optional[float] = Field(
        default=10_000_000,
        description="Maximum revenue ($)"
    )
    geographies: List[str] = Field(
        default=["North America", "Europe"],
        description="Target geographies"
    )
    max_deals: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of deals to return"
    )
    days_back: int = Field(
        default=30,
        ge=1,
        le=90,
        description="Look back N days for deals"
    )


class GenerateReportRequest(BaseModel):
    """Request to generate a daily deals report"""
    criteria: DiscoverDealsRequest
    format: str = Field(
        default="docx",
        description="Report format: docx, pdf, html, or text"
    )


@router.post("/discover")
async def discover_deals(
    request: DiscoverDealsRequest,
    db: Session = Depends(get_db)
):
    """
    Discover investment deals from multiple sources based on criteria
    
    This endpoint:
    1. Scrapes multiple sources (TechCrunch, AngelList, YC, etc.)
    2. Filters by sector, stage, revenue, geography
    3. Scores and ranks deals by relevance
    4. Returns top deals matching criteria
    
    Example:
    ```json
    {
        "sectors": ["Fintech", "ClimateTech"],
        "stages": ["Seed", "Series A"],
        "min_revenue": 500000,
        "max_revenue": 10000000,
        "geographies": ["North America", "Europe"],
        "max_deals": 20
    }
    ```
    """
    try:
        logger.info(f"Discovering deals with criteria: {request.dict()}")
        
        # Create criteria object
        criteria = DealCriteria(
            sectors=request.sectors,
            stages=request.stages,
            min_revenue=request.min_revenue,
            max_revenue=request.max_revenue,
            geographies=request.geographies,
            days_back=request.days_back
        )
        
        # Initialize discovery engine
        engine = DealDiscoveryEngine()
        
        # Discover deals
        deals = await engine.discover_deals(criteria, max_deals=request.max_deals)
        
        # Convert to dict for response
        deals_data = [
            {
                'company_name': deal.company_name,
                'sector': deal.sector,
                'stage': deal.stage,
                'description': deal.description,
                'funding_amount': deal.funding_amount,
                'funding_round': deal.funding_round,
                'lead_investor': deal.lead_investor,
                'revenue': deal.revenue,
                'location': deal.location,
                'country': deal.country,
                'website': deal.website,
                'key_signals': deal.key_signals,
                'potential_fit': deal.potential_fit,
                'risk_flags': deal.risk_flags,
                'sources': deal.sources,
                'confidence_score': deal.confidence_score,
                'discovered_at': deal.discovered_at.isoformat() if deal.discovered_at else None
            }
            for deal in deals
        ]
        
        return {
            'success': True,
            'deal_count': len(deals),
            'deals': deals_data,
            'criteria': request.dict()
        }
    
    except Exception as e:
        logger.error(f"Error discovering deals: {e}")
        raise HTTPException(status_code=500, detail=f"Error discovering deals: {str(e)}")


@router.post("/generate-report")
async def generate_daily_report(
    request: GenerateReportRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a daily potential deals report
    
    Returns structured report data that can be displayed in UI or exported
    
    Example:
    ```json
    {
        "criteria": {
            "sectors": ["Fintech", "ClimateTech"],
            "stages": ["Seed", "Series A"],
            "max_deals": 10
        },
        "format": "docx"
    }
    ```
    """
    try:
        logger.info("Generating daily deals report")
        
        # Create criteria
        criteria = DealCriteria(
            sectors=request.criteria.sectors,
            stages=request.criteria.stages,
            min_revenue=request.criteria.min_revenue,
            max_revenue=request.criteria.max_revenue,
            geographies=request.criteria.geographies,
            days_back=request.criteria.days_back
        )
        
        # Generate report
        engine = DealDiscoveryEngine()
        report_data = await engine.generate_daily_report(criteria, max_deals=request.criteria.max_deals)
        
        # Return structured data for frontend display
        return {
            'success': True,
            'report': report_data
        }
    
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


@router.post("/export-report")
async def export_report(
    request: GenerateReportRequest,
    db: Session = Depends(get_db)
):
    """
    Export daily deals report as DOCX, PDF, HTML, or text file
    
    Returns a downloadable file in the requested format
    
    Formats:
    - docx: Microsoft Word document (recommended)
    - html: HTML file for web/email
    - text: Plain text file
    """
    try:
        logger.info(f"Exporting report as {request.format}")
        
        # Create criteria
        criteria = DealCriteria(
            sectors=request.criteria.sectors,
            stages=request.criteria.stages,
            min_revenue=request.criteria.min_revenue,
            max_revenue=request.criteria.max_revenue,
            geographies=request.criteria.geographies,
            days_back=request.criteria.days_back
        )
        
        # Generate report data
        engine = DealDiscoveryEngine()
        report_data = await engine.generate_daily_report(criteria, max_deals=request.criteria.max_deals)
        
        # Initialize report generator
        generator = DealReportGenerator()
        
        # Generate file based on format
        if request.format.lower() == 'docx':
            # Generate DOCX
            buffer = generator.generate_docx(report_data)
            
            return StreamingResponse(
                buffer,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers={
                    "Content-Disposition": f"attachment; filename=Daily_Deals_Report_{report_data['date'].replace(' ', '_')}.docx"
                }
            )
        
        elif request.format.lower() == 'html':
            # Generate HTML
            html_content = generator.generate_html_report(report_data)
            
            return StreamingResponse(
                BytesIO(html_content.encode('utf-8')),
                media_type="text/html",
                headers={
                    "Content-Disposition": f"attachment; filename=Daily_Deals_Report_{report_data['date'].replace(' ', '_')}.html"
                }
            )
        
        elif request.format.lower() == 'text':
            # Generate text
            text_content = generator.generate_text_report(report_data)
            
            return StreamingResponse(
                BytesIO(text_content.encode('utf-8')),
                media_type="text/plain",
                headers={
                    "Content-Disposition": f"attachment; filename=Daily_Deals_Report_{report_data['date'].replace(' ', '_')}.txt"
                }
            )
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting report: {e}")
        raise HTTPException(status_code=500, detail=f"Error exporting report: {str(e)}")
