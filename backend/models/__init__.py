"""
Database models for Investment AI.
Inspired by open-notebook's schema, adapted for PostgreSQL with pgvector.
"""
from backend.config.database import Base
from backend.models.document import Document, DocumentChunk, DocumentEmbedding
from backend.models.analysis import Analysis, AnalysisResult
from backend.models.company import Company, CompanyMetric, CompanyFunding
from backend.models.market import MarketData, CompetitorAnalysis, MarketTrend
from backend.models.financial import FinancialModel, FinancialProjection
from backend.models.memo import Memo, MemoSection
from backend.models.ai_model import AIModel

__all__ = [
    "Base",
    # Documents
    "Document",
    "DocumentChunk",
    "DocumentEmbedding",
    # Analysis
    "Analysis",
    "AnalysisResult",
    # Companies
    "Company",
    "CompanyMetric",
    "CompanyFunding",
    # Market Intelligence
    "MarketData",
    "CompetitorAnalysis",
    "MarketTrend",
    # Financial Models
    "FinancialModel",
    "FinancialProjection",
    # Memos
    "Memo",
    "MemoSection",
    # AI Configuration
    "AIModel",
]
