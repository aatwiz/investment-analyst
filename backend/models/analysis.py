"""
Analysis-related database models.
Stores LLM analysis results for documents.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from backend.config.database import Base


class Analysis(Base):
    """
    Stores LLM analysis metadata and results for documents.
    """
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    
    # Analysis type and configuration
    analysis_type = Column(
        Enum(
            "financial_analysis",
            "market_analysis",
            "risk_assessment",
            "valuation",
            "sentiment_analysis",
            "competitive_analysis",
            "investment_thesis",
            "full_analysis",
            name="analysis_type_enum"
        ),
        nullable=False
    )
    
    # LLM configuration
    llm_model = Column(String(100), nullable=False)  # e.g., "gpt-4o-mini"
    llm_provider = Column(String(50), default="openai")
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=3000)
    
    # Status
    status = Column(
        Enum("pending", "processing", "completed", "failed", name="analysis_status_enum"),
        default="pending",
        nullable=False
    )
    
    # Results (store full JSON response)
    result_data = Column(JSON)  # Full structured analysis result
    summary = Column(Text)  # Brief summary for quick access
    
    # Quality metrics
    confidence_score = Column(Float)  # 0.0 to 1.0
    completeness_score = Column(Float)  # How complete is the analysis
    
    # Error handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Processing metadata
    processing_time_seconds = Column(Float)
    token_usage = Column(Integer)
    cost_usd = Column(Float)
    
    # Relationships
    document = relationship("Document", back_populates="analyses")
    results = relationship("AnalysisResult", back_populates="analysis", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_analysis_document", "document_id"),
        Index("idx_analysis_type", "analysis_type"),
        Index("idx_analysis_status", "status"),
        Index("idx_analysis_created", "created_at"),
    )
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, type='{self.analysis_type}', status='{self.status}')>"


class AnalysisResult(Base):
    """
    Stores individual results/insights from analyses.
    Allows for granular storage and retrieval of analysis components.
    """
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False)
    
    # Result identification
    result_key = Column(String(100), nullable=False)  # e.g., "revenue_analysis", "risk_factors"
    result_type = Column(String(50))  # e.g., "metric", "insight", "recommendation"
    
    # Content
    title = Column(String(500))
    content = Column(Text, nullable=False)
    structured_data = Column(JSON)  # For numeric data, lists, etc.
    
    # Categorization
    category = Column(String(100))  # e.g., "financial", "operational", "market"
    severity = Column(Enum("critical", "high", "medium", "low", "info", name="severity_enum"))
    
    # Metrics
    confidence = Column(Float)
    importance_score = Column(Float)  # How important is this result
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    analysis = relationship("Analysis", back_populates="results")
    
    # Indexes
    __table_args__ = (
        Index("idx_result_analysis", "analysis_id"),
        Index("idx_result_key", "result_key"),
        Index("idx_result_type", "result_type"),
    )
    
    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, key='{self.result_key}', type='{self.result_type}')>"
