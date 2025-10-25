"""
Query API endpoints for asking questions about documents using RAG.

This provides efficient, low-cost querying using:
- Vector search to find relevant chunks
- LLM to answer based on chunks only
- Cost: ~$0.0003 per query (8x cheaper than full analysis)
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from services.llm_agents import RAGQueryAgent
from config.database import get_db
from loguru import logger


router = APIRouter(prefix="/query", tags=["query"])


# Request/Response Models
class QueryRequest(BaseModel):
    """Request model for asking questions."""
    question: str = Field(..., description="The question to ask", min_length=5)
    document_ids: Optional[List[int]] = Field(
        None,
        description="Optional: Search within specific documents only"
    )
    max_chunks: int = Field(
        5,
        description="Maximum number of document chunks to use",
        ge=1,
        le=10
    )
    include_sources: bool = Field(
        True,
        description="Whether to include source information in response"
    )


class BatchQueryRequest(BaseModel):
    """Request model for batch questions."""
    questions: List[str] = Field(..., description="List of questions", min_items=1, max_items=20)
    document_ids: Optional[List[int]] = None


class ConversationalQueryRequest(BaseModel):
    """Request for chat-style queries with history."""
    question: str = Field(..., min_length=5)
    conversation_history: List[dict] = Field(
        default=[],
        description="Previous messages: [{'role': 'user/assistant', 'content': '...'}]"
    )
    document_ids: Optional[List[int]] = None


class QueryResponse(BaseModel):
    """Response model for query answers."""
    answer: str
    query: str
    chunks_used: int
    tokens: dict
    cost_usd: float
    response_time_ms: int
    model: str
    sources: Optional[List[dict]] = None


# Endpoints
@router.post("/ask", response_model=QueryResponse)
async def ask_question(
    request: QueryRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Ask a question about uploaded documents.
    
    **This is the EFFICIENT way to query documents:**
    - Uses vector search to find relevant chunks
    - Only sends ~2.5K chars to LLM (not 50K)
    - Cost: ~$0.0003 per query
    - Speed: 1-3 seconds
    
    **Example:**
    ```json
    {
        "question": "What was Baladna's net profit in Q1 2025?",
        "document_ids": [123],
        "max_chunks": 5,
        "include_sources": true
    }
    ```
    
    **Response:**
    ```json
    {
        "answer": "Baladna reported a net profit of QR 331.2M in H1 2025...",
        "query": "What was Baladna's net profit in Q1 2025?",
        "chunks_used": 3,
        "tokens": {"input": 1250, "output": 300, "total": 1550},
        "cost_usd": 0.00037,
        "response_time_ms": 1847,
        "sources": [...]
    }
    ```
    """
    try:
        logger.info(f"Received query: {request.question[:100]}...")
        
        # Initialize RAG agent
        rag_agent = RAGQueryAgent(session)
        
        # Get answer
        result = await rag_agent.answer_query(
            query=request.question,
            document_ids=request.document_ids,
            max_chunks=request.max_chunks,
            include_sources=request.include_sources
        )
        
        logger.info(
            f"Query completed: {result['chunks_used']} chunks, "
            f"${result['cost_usd']:.5f}, "
            f"{result['response_time_ms']}ms"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def batch_questions(
    request: BatchQueryRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Answer multiple questions in parallel.
    
    Efficient for processing many queries at once.
    
    **Example:**
    ```json
    {
        "questions": [
            "What is the company's revenue?",
            "What are the main risks?",
            "Who are the competitors?"
        ],
        "document_ids": [123]
    }
    ```
    """
    try:
        logger.info(f"Received batch query: {len(request.questions)} questions")
        
        rag_agent = RAGQueryAgent(session)
        
        results = await rag_agent.batch_query(
            queries=request.questions,
            document_ids=request.document_ids
        )
        
        total_cost = sum(r['cost_usd'] for r in results)
        avg_time = sum(r['response_time_ms'] for r in results) / len(results)
        
        logger.info(
            f"Batch completed: {len(results)} answers, "
            f"${total_cost:.5f} total, "
            f"{avg_time:.0f}ms average"
        )
        
        return {
            "results": results,
            "summary": {
                "total_questions": len(request.questions),
                "successful_answers": len(results),
                "total_cost_usd": total_cost,
                "average_response_time_ms": int(avg_time)
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing batch query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def conversational_query(
    request: ConversationalQueryRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Chat-style query with conversation history.
    
    Maintains context from previous messages for follow-up questions.
    
    **Example:**
    ```json
    {
        "question": "And what about their competitors?",
        "conversation_history": [
            {"role": "user", "content": "Tell me about Baladna's revenue"},
            {"role": "assistant", "content": "Baladna's revenue in H1 2025 was..."}
        ],
        "document_ids": [123]
    }
    ```
    """
    try:
        logger.info(
            f"Conversational query: {request.question[:100]}... "
            f"(history: {len(request.conversation_history)} messages)"
        )
        
        rag_agent = RAGQueryAgent(session)
        
        result = await rag_agent.conversational_query(
            query=request.question,
            conversation_history=request.conversation_history,
            document_ids=request.document_ids
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing conversational query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def query_statistics(
    days: int = 30,
    session: AsyncSession = Depends(get_db)
):
    """
    Get query usage statistics.
    
    Returns metrics like:
    - Total queries
    - Total cost
    - Average response time
    - Cache hit rate
    """
    try:
        rag_agent = RAGQueryAgent(session)
        stats = await rag_agent.get_query_stats(days=days)
        return stats
        
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Cost estimation endpoint
@router.post("/estimate-cost")
async def estimate_query_cost(questions: List[str]):
    """
    Estimate cost for queries without executing them.
    
    Useful for budget planning.
    """
    # Rough estimation: ~1500 tokens per query
    estimated_tokens_per_query = 1500
    cost_per_query = 0.0003  # Average cost
    
    total_queries = len(questions)
    estimated_total_cost = total_queries * cost_per_query
    
    return {
        "total_queries": total_queries,
        "estimated_tokens_per_query": estimated_tokens_per_query,
        "estimated_cost_per_query": cost_per_query,
        "estimated_total_cost_usd": estimated_total_cost,
        "note": "Actual costs may vary based on query complexity and document matches"
    }
