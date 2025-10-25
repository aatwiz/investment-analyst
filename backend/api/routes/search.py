"""
Semantic search API endpoints for finding similar documents
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel

from config.database import get_db
from services.embeddings.embedding_service import vector_search
from utils.logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)


class SearchResult(BaseModel):
    """Search result model"""
    document_id: int
    filename: str
    chunk_text: str
    similarity_score: float
    document_type: Optional[str] = None
    upload_date: Optional[str] = None


class SearchResponse(BaseModel):
    """Search response model"""
    success: bool
    query: str
    results_count: int
    results: List[SearchResult]


@router.post("/semantic", response_model=SearchResponse)
async def semantic_search(
    query: str = Query(..., description="Search query text"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results to return"),
    min_similarity: float = Query(0.2, ge=0.0, le=1.0, description="Minimum similarity threshold (0-1)"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform semantic search to find similar document chunks.
    
    Uses vector embeddings and cosine similarity to find the most relevant
    document chunks based on the semantic meaning of the query.
    
    Args:
        query: The search query text
        limit: Maximum number of results to return (1-50)
        min_similarity: Minimum similarity score threshold (0.0-1.0)
        document_type: Optional filter by document type
        db: Database session
    
    Returns:
        List of similar document chunks with similarity scores
    """
    try:
        if not query or len(query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        logger.info(f"Performing semantic search for: '{query[:100]}...'")
        
        # Perform vector search
        results = await vector_search(
            db=db,
            query_text=query,
            limit=limit,
            min_similarity=min_similarity,
            document_type=document_type
        )
        
        # Format results
        search_results = [
            SearchResult(
                document_id=result["document_id"],
                filename=result["filename"],
                chunk_text=result["chunk_text"],
                similarity_score=round(result["similarity"], 4),
                document_type=result.get("document_type"),
                upload_date=result.get("upload_date").isoformat() if result.get("upload_date") else None
            )
            for result in results
        ]
        
        logger.info(f"Found {len(search_results)} results for query")
        
        return SearchResponse(
            success=True,
            query=query,
            results_count=len(search_results),
            results=search_results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing semantic search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.get("/documents/{document_id}/similar")
async def find_similar_documents(
    document_id: int,
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """
    Find documents similar to a specific document.
    
    Args:
        document_id: ID of the reference document
        limit: Maximum number of similar documents to return
        db: Database session
    
    Returns:
        List of similar documents
    """
    try:
        from models.document import Document
        from sqlalchemy import select
        
        # Get the reference document
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if not document.full_text:
            raise HTTPException(
                status_code=400,
                detail="Document has no text content for similarity comparison"
            )
        
        # Use the document's text to find similar documents
        results = await vector_search(
            db=db,
            query_text=document.full_text[:1000],  # Use first 1000 chars
            limit=limit + 1,  # +1 to account for the document itself
            min_similarity=0.3
        )
        
        # Filter out the original document
        similar_docs = [
            r for r in results if r["document_id"] != document_id
        ][:limit]
        
        return {
            "success": True,
            "reference_document_id": document_id,
            "reference_filename": document.filename,
            "similar_documents_count": len(similar_docs),
            "similar_documents": [
                {
                    "document_id": r["document_id"],
                    "filename": r["filename"],
                    "similarity_score": round(r["similarity"], 4),
                    "document_type": r.get("document_type"),
                    "preview": r["chunk_text"][:200] + "..." if len(r["chunk_text"]) > 200 else r["chunk_text"]
                }
                for r in similar_docs
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding similar documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error finding similar documents: {str(e)}")


@router.get("/health")
async def search_health_check():
    """Health check endpoint for search service"""
    return {
        "status": "healthy",
        "service": "semantic-search",
        "features": ["vector_search", "document_similarity"]
    }
