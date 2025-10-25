"""
Test script to verify database integration
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from config.database import get_engine, get_db_session
from models.document import Document
from models.analysis import Analysis
from services.embeddings.embedding_service import generate_embedding, vector_search
from sqlalchemy import select


async def test_database_integration():
    """Test the full database integration flow"""
    print("🧪 Testing Database Integration\n")
    print("=" * 60)
    
    engine = get_engine()
    
    try:
        # Test 1: Create a test document
        print("\n✅ Test 1: Creating test document...")
        async with get_db_session() as db:
            test_doc = Document(
                filename="test_document.pdf",
                original_filename="test_document.pdf",
                file_path="/tmp/test.pdf",
                file_type="pdf",
                file_size=1024,
                document_type="financial_statement",
                full_text="This is a test document about investment strategies and market analysis.",
                is_vectorized=False
            )
            
            db.add(test_doc)
            await db.commit()
            await db.refresh(test_doc)
            print(f"   Created document ID: {test_doc.id}")
        
        # Test 2: Generate embedding
        print("\n✅ Test 2: Generating embedding...")
        embedding = await generate_embedding("This is a test query about investments")
        print(f"   Generated embedding vector of dimension: {len(embedding)}")
        
        # Test 3: Create analysis record
        print("\n✅ Test 3: Creating analysis record...")
        async with get_db_session() as db:
            analysis = Analysis(
                document_id=test_doc.id,
                analysis_type="financial_analysis",
                llm_model="gpt-4o-mini",
                result_data={"test": "data"},
                summary="Test analysis summary",
                token_usage=100,
                cost_usd=0.001,
                status="completed"
            )
            
            db.add(analysis)
            await db.commit()
            await db.refresh(analysis)
            print(f"   Created analysis ID: {analysis.id}")
        
        # Test 4: Retrieve documents
        print("\n✅ Test 4: Retrieving documents...")
        async with get_db_session() as db:
            result = await db.execute(select(Document))
            docs = result.scalars().all()
            print(f"   Found {len(docs)} documents in database")
        
        # Test 5: Retrieve analyses
        print("\n✅ Test 5: Retrieving analyses...")
        async with get_db_session() as db:
            result = await db.execute(select(Analysis))
            analyses = result.scalars().all()
            print(f"   Found {len(analyses)} analyses in database")
        
        print("\n" + "=" * 60)
        print("✅ All tests passed! Database integration is working!")
        print("=" * 60)
        
        # Cleanup
        print("\n🧹 Cleaning up test data...")
        async with get_db_session() as db:
            await db.delete(test_doc)
            await db.commit()
        print("   Cleanup complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_database_integration())
