"""
Company-related database models for Feature 1 (Deal Sourcing).
"""
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from config.database import Base


class Company(Base):
    """
    Company profiles for deal sourcing and tracking.
    """
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    legal_name = Column(String(255))
    website = Column(String(500))
    description = Column(Text)
    
    # Classification
    industry = Column(String(100))
    sector = Column(String(100))
    stage = Column(String(50))  # e.g., "seed", "series_a", "growth"
    
    # Location
    headquarters_country = Column(String(100))
    headquarters_city = Column(String(100))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    
    # Deal qualification
    qualification_score = Column(Float)  # 0.0 to 100.0
    is_qualified = Column(Boolean)
    qualification_reason = Column(Text)
    
    # Metadata
    source = Column(String(100))  # Where we found this company
    tags = Column(String(1000))  # Comma-separated
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scraped = Column(DateTime)
    
    # Relationships
    metrics = relationship("CompanyMetric", back_populates="company", cascade="all, delete-orphan")
    funding = relationship("CompanyFunding", back_populates="company", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_company_name", "name"),
        Index("idx_company_industry", "industry"),
        Index("idx_company_stage", "stage"),
        Index("idx_company_qualified", "is_qualified"),
    )
    
    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', stage='{self.stage}')>"


class CompanyMetric(Base):
    """
    Time-series metrics for companies.
    """
    __tablename__ = "company_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    # Metric information
    metric_name = Column(String(100), nullable=False)  # e.g., "revenue", "employees", "growth_rate"
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50))  # e.g., "USD", "percent", "count"
    
    # Time period
    period_date = Column(DateTime, nullable=False)
    period_type = Column(String(20))  # e.g., "annual", "quarterly", "monthly"
    
    # Source and confidence
    source = Column(String(100))
    confidence = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="metrics")
    
    __table_args__ = (
        Index("idx_metric_company", "company_id"),
        Index("idx_metric_name", "metric_name"),
        Index("idx_metric_date", "period_date"),
    )
    
    def __repr__(self):
        return f"<CompanyMetric(id={self.id}, company_id={self.company_id}, metric='{self.metric_name}')>"


class CompanyFunding(Base):
    """
    Funding rounds and investment information for companies.
    """
    __tablename__ = "company_funding"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    # Round information
    round_type = Column(String(50), nullable=False)  # e.g., "seed", "series_a", "series_b"
    round_date = Column(DateTime)
    amount_raised = Column(Float)  # in USD
    currency = Column(String(10), default="USD")
    
    # Valuation
    pre_money_valuation = Column(Float)
    post_money_valuation = Column(Float)
    
    # Investors (JSON array)
    lead_investors = Column(JSON)
    other_investors = Column(JSON)
    
    # Details
    announcement_url = Column(String(500))
    notes = Column(Text)
    
    # Source
    source = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="funding")
    
    __table_args__ = (
        Index("idx_funding_company", "company_id"),
        Index("idx_funding_round", "round_type"),
        Index("idx_funding_date", "round_date"),
    )
    
    def __repr__(self):
        return f"<CompanyFunding(id={self.id}, company_id={self.company_id}, round='{self.round_type}')>"
