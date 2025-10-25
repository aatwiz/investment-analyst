"""
Database models for Investment AI.
Inspired by open-notebook's schema, adapted for PostgreSQL with pgvector.
"""
from config.database import Base
from models.document import Document, DocumentChunk, DocumentEmbedding
from models.analysis import Analysis, AnalysisResult
from models.company import Company, CompanyMetric, CompanyFunding
from models.market import MarketData, CompetitorAnalysis, MarketTrend
from models.financial import FinancialModel, FinancialProjection
from models.memo import Memo, MemoSection
from models.ai_model import AIModel

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
