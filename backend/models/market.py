"""
Market intelligence database models for Feature 3.
"""
from datetime import datetime

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
)

from backend.config.database import Base


class MarketData(Base):
    """
    Market intelligence and trends data.
    """
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Market identification
    market_name = Column(String(255), nullable=False)
    market_segment = Column(String(100))
    geography = Column(String(100))
    
    # Data type
    data_type = Column(String(50), nullable=False)  # e.g., "size", "growth", "trends"
    
    # Metrics
    metric_value = Column(Float)
    metric_unit = Column(String(50))
    
    # Time period
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    year = Column(Integer)
    
    # Structured data
    detailed_data = Column(JSON)
    
    # Source
    source = Column(String(255))
    source_url = Column(String(500))
    confidence = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_market_name", "market_name"),
        Index("idx_market_segment", "market_segment"),
        Index("idx_market_year", "year"),
    )
    
    def __repr__(self):
        return f"<MarketData(id={self.id}, market='{self.market_name}', type='{self.data_type}')>"


class CompetitorAnalysis(Base):
    """
    Competitive analysis and intelligence.
    """
    __tablename__ = "competitor_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Target company/market
    company_name = Column(String(255), nullable=False)
    market_segment = Column(String(100))
    
    # Competitor information
    competitor_name = Column(String(255), nullable=False)
    competitor_website = Column(String(500))
    
    # Analysis
    competitive_position = Column(String(50))  # e.g., "leader", "challenger", "follower"
    strengths = Column(JSON)  # Array of strengths
    weaknesses = Column(JSON)  # Array of weaknesses
    market_share = Column(Float)
    
    # Detailed analysis
    analysis_summary = Column(Text)
    detailed_analysis = Column(JSON)
    
    # Source
    source = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_competitor_company", "company_name"),
        Index("idx_competitor_name", "competitor_name"),
    )
    
    def __repr__(self):
        return f"<CompetitorAnalysis(id={self.id}, company='{self.company_name}', competitor='{self.competitor_name}')>"


class MarketTrend(Base):
    """
    Market trends and predictions.
    """
    __tablename__ = "market_trends"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Trend identification
    trend_name = Column(String(255), nullable=False)
    market_segment = Column(String(100))
    geography = Column(String(100))
    
    # Trend details
    trend_type = Column(String(50))  # e.g., "emerging", "declining", "stable"
    impact_level = Column(String(20))  # e.g., "high", "medium", "low"
    
    # Description
    description = Column(Text)
    key_drivers = Column(JSON)  # Array of trend drivers
    
    # Metrics
    growth_rate = Column(Float)  # Percentage
    adoption_rate = Column(Float)  # Percentage
    
    # Timeline
    identified_date = Column(DateTime, nullable=False)
    predicted_peak = Column(DateTime)
    
    # Related entities
    affected_companies = Column(JSON)  # Array of company names
    
    # Source
    source = Column(String(100))
    confidence = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_trend_name", "trend_name"),
        Index("idx_trend_segment", "market_segment"),
        Index("idx_trend_type", "trend_type"),
        Index("idx_trend_identified", "identified_date"),
    )
    
    def __repr__(self):
        return f"<MarketTrend(id={self.id}, trend='{self.trend_name}', type='{self.trend_type}')>"
