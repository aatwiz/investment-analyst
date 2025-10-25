"""
Document analysis API endpoints
Analyzes documents for investment due diligence insights
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional
from pathlib import Path
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from utils.config import settings
from utils.logger import setup_logger
from services.llm_agents import InvestmentAnalystAgent
from config.database import get_db
from models.document import Document
from models.analysis import Analysis

router = APIRouter()
logger = setup_logger(__name__)
analyzer = InvestmentAnalystAgent()  # Use LLM-powered agent instead of keyword matcher


class AnalyzeRequest(BaseModel):
    """Request model for document analysis"""
    filename: str
    analysis_type: str = "comprehensive"  # comprehensive, summary, red_flags, financial


class BatchAnalyzeRequest(BaseModel):
    """Request model for batch document analysis"""
    filenames: List[str]
    analysis_type: str = "comprehensive"


@router.post("/analyze")
async def analyze_document(request: AnalyzeRequest, db: AsyncSession = Depends(get_db)):
    """
    Analyze a single document and save results to database
    
    Args:
        request: Analysis request with filename and analysis type
        db: Database session
        
    Returns:
        Analysis results with insights and recommendations
    """
    try:
        # Find file in database first
        result = await db.execute(
            select(Document).where(Document.filename.contains(request.filename))
        )
        document = result.scalar_one_or_none()
        
        if not document:
            # Fallback to file system search
            upload_path = Path(settings.UPLOAD_DIR)
            file_path = None
            
            for fp in upload_path.rglob(f"*{request.filename}*"):
                if fp.is_file():
                    file_path = fp
                    break
            
            if not file_path:
                raise HTTPException(status_code=404, detail=f"File not found: {request.filename}")
        else:
            file_path = Path(document.file_path)
            if not file_path.exists():
                raise HTTPException(status_code=404, detail=f"File not found on disk: {document.file_path}")
        
        # Analyze document using LLM-powered agent
        # Pass filename (not path) as the agent expects it
        analysis_result = await analyzer.analyze_document(
            filename=file_path.name,
            focus_areas=None  # Could be extended to support specific focus areas
        )
        
        # Extract LLM analysis and recommendation
        llm_analysis = analysis_result.get("llm_analysis", {})
        recommendation = llm_analysis.get("recommendation", {})
        
        # Save analysis to database if document exists in DB
        if document:
            try:
                analysis_record = Analysis(
                    document_id=document.id,
                    analysis_type=request.analysis_type,
                    llm_model=analysis_result.get("model_used", "gpt-4o-mini"),
                    result_data=llm_analysis,
                    summary=llm_analysis.get("executive_summary", "")[:1000],
                    token_usage=0,  # TODO: Track token usage from OpenAI response
                    cost_usd=0.0,  # TODO: Calculate cost based on tokens
                    status="completed"
                )
                
                db.add(analysis_record)
                await db.commit()
                await db.refresh(analysis_record)
                
                analysis_result["analysis_id"] = analysis_record.id
                analysis_result["document_id"] = document.id
                logger.info(f"Saved analysis to database: ID {analysis_record.id}")
                
            except Exception as e:
                logger.error(f"Error saving analysis to database: {str(e)}")
                await db.rollback()
                # Continue anyway - we still return the analysis result
        
        logger.info(f"Successfully analyzed: {request.filename}")
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing document: {str(e)}")


@router.post("/analyze/batch")
async def analyze_batch(request: BatchAnalyzeRequest):
    """
    Analyze multiple documents using LLM agent
    
    Args:
        request: Batch analysis request with filenames and analysis type
        
    Returns:
        Consolidated analysis results
    """
    try:
        results = []
        
        # Analyze each document
        for filename in request.filenames:
            try:
                analysis = await analyzer.analyze_document(filename, focus_areas=None)
                results.append({
                    "filename": filename,
                    "success": True,
                    "analysis": analysis
                })
            except Exception as e:
                logger.error(f"Error analyzing {filename}: {str(e)}")
                results.append({
                    "filename": filename,
                    "success": False,
                    "error": str(e)
                })
        
        logger.info(f"Successfully analyzed {len([r for r in results if r['success']])} of {len(request.filenames)} documents")
        return {
            "total": len(request.filenames),
            "successful": len([r for r in results if r['success']]),
            "failed": len([r for r in results if not r['success']]),
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing batch: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing batch: {str(e)}")


@router.get("/extract/{filename}")
async def extract_content(
    filename: str,
    include_tables: bool = Query(True, description="Include extracted tables"),
    include_metadata: bool = Query(True, description="Include metadata")
):
    """
    Extract raw content from a document
    
    Args:
        filename: Name of the file to extract
        include_tables: Whether to include tables in response
        include_metadata: Whether to include metadata
        
    Returns:
        Extracted content and metadata
    """
    try:
        # Find file
        upload_path = Path(settings.UPLOAD_DIR)
        file_path = None
        
        for fp in upload_path.rglob(f"*{filename}*"):
            if fp.is_file():
                file_path = fp
                break
        
        if not file_path:
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")
        
        # Extract content
        from services.file_processing import FileProcessor
        processor = FileProcessor()
        result = processor.process_file(file_path)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        # Filter response based on parameters
        response = {
            "success": True,
            "filename": filename,
            "type": result.get("type"),
            "text": result.get("text", ""),
            "text_length": result.get("text_length", 0),
            "summary": result.get("summary", {})
        }
        
        if include_tables and "tables" in result:
            response["tables"] = result.get("tables", [])
            response["table_count"] = result.get("table_count", 0)
        
        if include_metadata and "metadata" in result:
            response["metadata"] = result.get("metadata", [])
        
        # For Excel/CSV files
        if result.get("type") in ["excel", "csv"]:
            response["sheets"] = result.get("sheets", {})
            response["data_preview"] = result.get("data_preview", [])
        
        logger.info(f"Successfully extracted content from: {filename}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error extracting content: {str(e)}")


@router.get("/red-flags/{filename}")
async def detect_red_flags(filename: str):
    """
    Detect red flags in a document (focused analysis)
    
    Args:
        filename: Name of the file to analyze
        
    Returns:
        Red flags and risk assessment
    """
    try:
        request = AnalyzeRequest(filename=filename, analysis_type="red_flags")
        return await analyze_document(request)
        
    except Exception as e:
        logger.error(f"Error detecting red flags: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error detecting red flags: {str(e)}")


@router.get("/summary/{filename}")
async def get_summary(filename: str):
    """
    Get a quick summary of a document
    
    Args:
        filename: Name of the file to summarize
        
    Returns:
        Document summary
    """
    try:
        request = AnalyzeRequest(filename=filename, analysis_type="summary")
        return await analyze_document(request)
        
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")


@router.post("/market")
async def market_analysis(company_name: str):
    """
    Perform market analysis for a company
    
    Args:
        company_name: Name of the company to analyze
    
    Returns:
        Market analysis results
    """
    # Placeholder for Phase 3
    return {
        "success": True,
        "message": "Market analysis feature coming in Phase 3",
        "company_name": company_name
    }


@router.get("/history/{document_id}")
async def get_analysis_history(
    document_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get analysis history for a specific document
    
    Args:
        document_id: ID of the document
        db: Database session
    
    Returns:
        List of all analyses performed on the document
    """
    try:
        # Get document
        doc_result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = doc_result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get all analyses for this document
        analyses_result = await db.execute(
            select(Analysis)
            .where(Analysis.document_id == document_id)
            .order_by(Analysis.created_at.desc())
        )
        analyses = analyses_result.scalars().all()
        
        return {
            "success": True,
            "document_id": document_id,
            "filename": document.filename,
            "analysis_count": len(analyses),
            "analyses": [
                {
                    "id": analysis.id,
                    "analysis_type": analysis.analysis_type,
                    "llm_model": analysis.llm_model,
                    "summary": analysis.summary,
                    "token_usage": analysis.token_usage,
                    "cost_usd": analysis.cost_usd,
                    "status": analysis.status,
                    "created_at": analysis.created_at.isoformat(),
                    "execution_time_seconds": analysis.execution_time_seconds
                }
                for analysis in analyses
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching analysis history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching analysis history: {str(e)}")


@router.get("/list")
async def list_all_analyses(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    List all analyses with pagination
    
    Args:
        limit: Maximum number of results
        offset: Number of results to skip
        db: Database session
    
    Returns:
        List of all analyses
    """
    try:
        # Get analyses with their documents
        from sqlalchemy.orm import selectinload
        
        result = await db.execute(
            select(Analysis)
            .options(selectinload(Analysis.document))
            .order_by(Analysis.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        analyses = result.scalars().all()
        
        return {
            "success": True,
            "count": len(analyses),
            "limit": limit,
            "offset": offset,
            "analyses": [
                {
                    "id": analysis.id,
                    "document_id": analysis.document_id,
                    "filename": analysis.document.filename if analysis.document else "Unknown",
                    "analysis_type": analysis.analysis_type,
                    "llm_model": analysis.llm_model,
                    "summary": analysis.summary,
                    "status": analysis.status,
                    "created_at": analysis.created_at.isoformat(),
                    "token_usage": analysis.token_usage,
                    "cost_usd": analysis.cost_usd
                }
                for analysis in analyses
            ]
        }
        
    except Exception as e:
        logger.error(f"Error listing analyses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing analyses: {str(e)}")
