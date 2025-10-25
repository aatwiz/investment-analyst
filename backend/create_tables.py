"""
Script to create all database tables.
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from config.database import Base, get_engine

# Import all models to register them with Base.metadata
from models.document import Document, DocumentChunk, DocumentEmbedding
from models.analysis import Analysis, AnalysisResult
from models.company import Company, CompanyMetric, CompanyFunding
from models.market import MarketData, CompetitorAnalysis, MarketTrend
from models.financial import FinancialModel, FinancialProjection
from models.memo import Memo, MemoSection
from models.ai_model import AIModel


async def create_all_tables():
    """Create all database tables."""
    engine = get_engine()
    
    print(f"Creating {len(Base.metadata.tables)} tables...")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("\n✅ All tables created successfully!")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_all_tables())
