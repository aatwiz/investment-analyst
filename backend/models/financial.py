"""
Financial modeling database models for Feature 4.
"""
from datetime import datetime

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from backend.config.database import Base


class FinancialModel(Base):
    """
    Financial models and projections.
    """
    __tablename__ = "financial_models"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Model identification
    model_name = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    model_type = Column(String(50), nullable=False)  # e.g., "dcf", "multiples", "venture"
    
    # Model configuration
    base_year = Column(Integer, nullable=False)
    projection_years = Column(Integer, default=5)
    
    # Assumptions (JSON)
    assumptions = Column(JSON, nullable=False)
    
    # Results summary
    valuation = Column(Float)
    currency = Column(String(10), default="USD")
    
    # Model details
    methodology = Column(Text)
    notes = Column(Text)
    
    # Confidence and quality
    confidence_score = Column(Float)
    sensitivity_analysis = Column(JSON)
    
    # Metadata
    created_by = Column(String(100))
    version = Column(Integer, default=1)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    projections = relationship("FinancialProjection", back_populates="model", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_model_name", "model_name"),
        Index("idx_model_company", "company_name"),
        Index("idx_model_type", "model_type"),
        Index("idx_model_year", "base_year"),
    )
    
    def __repr__(self):
        return f"<FinancialModel(id={self.id}, name='{self.model_name}', type='{self.model_type}')>"


class FinancialProjection(Base):
    """
    Individual financial projections within a model.
    """
    __tablename__ = "financial_projections"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("financial_models.id", ondelete="CASCADE"), nullable=False)
    
    # Projection details
    year = Column(Integer, nullable=False)
    quarter = Column(Integer)  # Optional for quarterly projections
    
    # Financial metrics
    revenue = Column(Float)
    cost_of_revenue = Column(Float)
    gross_profit = Column(Float)
    operating_expenses = Column(Float)
    ebitda = Column(Float)
    net_income = Column(Float)
    
    # Cash flow metrics
    operating_cash_flow = Column(Float)
    free_cash_flow = Column(Float)
    capital_expenditure = Column(Float)
    
    # Balance sheet metrics
    total_assets = Column(Float)
    total_liabilities = Column(Float)
    equity = Column(Float)
    
    # Additional metrics (JSON for flexibility)
    additional_metrics = Column(JSON)
    
    # Growth rates
    revenue_growth_rate = Column(Float)
    profit_margin = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    model = relationship("FinancialModel", back_populates="projections")
    
    __table_args__ = (
        Index("idx_projection_model", "model_id"),
        Index("idx_projection_year", "year"),
    )
    
    def __repr__(self):
        return f"<FinancialProjection(id={self.id}, model_id={self.model_id}, year={self.year})>"
