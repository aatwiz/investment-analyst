"""
Market Research & Competitive Analysis API Routes
Feature 3: Market & Competitive Intelligence

Endpoints for generating market overviews, competitive analysis,
and industry trend reports.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from loguru import logger

from services.market_intelligence.research_agent import (
    MarketResearchAgent,
    CompanyInfo,
    MarketAnalysisReport
)

router = APIRouter(tags=["market-research"])


# Request/Response Models
class MarketAnalysisRequest(BaseModel):
    """Request to analyze a company/market"""
    company_name: str = Field(..., description="Company name to analyze")
    industry: str = Field(..., description="Industry/sector")
    description: Optional[str] = Field(None, description="Company description")
    website: Optional[str] = Field(None, description="Company website")
    include_competitors: bool = Field(default=True, description="Include competitive analysis")
    include_trends: bool = Field(default=True, description="Include industry trends")
    include_regulatory: bool = Field(default=True, description="Include regulatory analysis")


class MarketMetricsResponse(BaseModel):
    """Market metrics summary"""
    market_size: float
    growth_rate: float
    market_position: int
    yoy_growth: float
    market_shares: Dict[str, float]


class MarketAnalysisResponse(BaseModel):
    """Complete market analysis response"""
    success: bool
    company_name: str
    industry: str
    metrics: MarketMetricsResponse
    market_overview: str
    trends: List[str]
    competitors: List[str]
    competitive_position: str
    opportunities: List[str]
    threats: List[str]
    key_drivers: List[str]
    regulatory_environment: str
    timestamp: str
    report_text: Optional[str] = None


class IndustryTrendsRequest(BaseModel):
    """Request for industry trends"""
    industry: str = Field(..., description="Industry/sector to analyze")
    count: int = Field(default=5, ge=1, le=20, description="Number of trends to return")


class IndustryTrendsResponse(BaseModel):
    """Industry trends response"""
    success: bool
    industry: str
    trends: List[str]
    timestamp: str


class CompetitorAnalysisRequest(BaseModel):
    """Request for competitor analysis"""
    company_name: str = Field(..., description="Target company")
    industry: str = Field(..., description="Industry/sector")


class CompetitorAnalysisResponse(BaseModel):
    """Competitor analysis response"""
    success: bool
    company_name: str
    competitors: Dict[str, float]  # competitor name -> market share
    competitive_position: str
    timestamp: str


@router.post("/analyze", response_model=MarketAnalysisResponse)
async def analyze_market(request: MarketAnalysisRequest):
    """
    Generate comprehensive market and competitive analysis for a company.
    
    This endpoint:
    1. Researches market size, growth, and trends
    2. Identifies key competitors and market shares
    3. Analyzes competitive positioning
    4. Identifies opportunities and threats
    5. Assesses regulatory environment
    
    Example:
    ```json
    {
        "company_name": "Anthropic",
        "industry": "AI & Machine Learning",
        "description": "AI safety and research company",
        "include_competitors": true,
        "include_trends": true
    }
    ```
    """
    try:
        logger.info(f"Starting market analysis for {request.company_name}")
        
        # Initialize agent
        agent = MarketResearchAgent()
        
        # Create company info
        company_info = CompanyInfo(
            name=request.company_name,
            industry=request.industry,
            description=request.description or "",
            website=request.website
        )
        
        # Run analysis
        report = await agent.run_full_analysis(company_info)
        
        # Format response
        response = MarketAnalysisResponse(
            success=True,
            company_name=report.company_name,
            industry=report.industry,
            metrics=MarketMetricsResponse(
                market_size=report.market_size,
                growth_rate=report.growth_rate,
                market_position=report.market_position,
                yoy_growth=report.yoy_growth,
                market_shares=report.market_shares
            ),
            market_overview=report.market_overview,
            trends=report.trends,
            competitors=report.competitors,
            competitive_position=report.competitive_position,
            opportunities=report.opportunities,
            threats=report.threats,
            key_drivers=report.key_drivers,
            regulatory_environment=report.regulatory_environment,
            timestamp=report.timestamp,
            report_text=agent.format_report(report)
        )
        
        logger.info(f"Market analysis completed for {request.company_name}")
        return response
    
    except Exception as e:
        logger.error(f"Error in market analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to complete market analysis: {str(e)}"
        )


@router.post("/trends", response_model=IndustryTrendsResponse)
async def get_industry_trends(request: IndustryTrendsRequest):
    """
    Get current trends for a specific industry.
    
    Returns the top trends affecting the industry including:
    - Technology adoption
    - Market shifts
    - Consumer behavior changes
    - Regulatory changes
    - Competitive dynamics
    
    Example:
    ```json
    {
        "industry": "Fintech",
        "count": 5
    }
    ```
    """
    try:
        logger.info(f"Fetching trends for {request.industry}")
        
        agent = MarketResearchAgent()
        trends = await agent.news_agent.get_industry_trends(request.industry, request.count)
        
        from datetime import datetime
        response = IndustryTrendsResponse(
            success=True,
            industry=request.industry,
            trends=trends,
            timestamp=datetime.utcnow().isoformat()
        )
        
        logger.info(f"Retrieved {len(trends)} trends for {request.industry}")
        return response
    
    except Exception as e:
        logger.error(f"Error fetching industry trends: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch industry trends: {str(e)}"
        )


@router.post("/competitors", response_model=CompetitorAnalysisResponse)
async def analyze_competitors(request: CompetitorAnalysisRequest):
    """
    Identify and analyze key competitors for a company.
    
    Returns:
    - List of main competitors
    - Estimated market shares
    - Competitive positioning analysis
    
    Example:
    ```json
    {
        "company_name": "Stripe",
        "industry": "Payments & Fintech"
    }
    ```
    """
    try:
        logger.info(f"Analyzing competitors for {request.company_name}")
        
        agent = MarketResearchAgent()
        
        # Get competitors and market shares
        market_shares = await agent.competitive_agent.identify_competitors(
            request.company_name,
            request.industry
        )
        
        # Get competitive position
        competitors = list(market_shares.keys())
        competitive_position = await agent.competitive_agent.analyze_competitive_position(
            request.company_name,
            competitors,
            f"Analysis of {request.company_name} in the {request.industry} industry"
        )
        
        from datetime import datetime
        response = CompetitorAnalysisResponse(
            success=True,
            company_name=request.company_name,
            competitors=market_shares,
            competitive_position=competitive_position,
            timestamp=datetime.utcnow().isoformat()
        )
        
        logger.info(f"Competitor analysis completed for {request.company_name}")
        return response
    
    except Exception as e:
        logger.error(f"Error analyzing competitors: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze competitors: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Market Research & Competitive Analysis"
    }
