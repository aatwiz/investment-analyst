"""
Document analysis API endpoints
Analyzes documents for investment due diligence insights
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
from pathlib import Path
from pydantic import BaseModel

from utils.config import settings
from utils.logger import setup_logger
from services.document_analysis import DocumentAnalyzer

router = APIRouter()
logger = setup_logger(__name__)
analyzer = DocumentAnalyzer()


class AnalyzeRequest(BaseModel):
    """Request model for document analysis"""
    filename: str
    analysis_type: str = "comprehensive"  # comprehensive, summary, red_flags, financial


class BatchAnalyzeRequest(BaseModel):
    """Request model for batch document analysis"""
    filenames: List[str]
    analysis_type: str = "comprehensive"


@router.post("/analyze")
async def analyze_document(request: AnalyzeRequest):
    """
    Analyze a single document
    
    Args:
        request: Analysis request with filename and analysis type
        
    Returns:
        Analysis results with insights and recommendations
    """
    try:
        # Find file
        upload_path = Path(settings.UPLOAD_DIR)
        file_path = None
        
        # Search recursively for the file
        for fp in upload_path.rglob(f"*{request.filename}*"):
            if fp.is_file():
                file_path = fp
                break
        
        if not file_path:
            raise HTTPException(status_code=404, detail=f"File not found: {request.filename}")
        
        # Analyze document
        result = analyzer.analyze_document(file_path, request.analysis_type)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Analysis failed"))
        
        logger.info(f"Successfully analyzed: {request.filename}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing document: {str(e)}")


@router.post("/analyze/batch")
async def analyze_batch(request: BatchAnalyzeRequest):
    """
    Analyze multiple documents
    
    Args:
        request: Batch analysis request with filenames and analysis type
        
    Returns:
        Consolidated analysis results
    """
    try:
        upload_path = Path(settings.UPLOAD_DIR)
        file_paths = []
        
        # Find all files
        for filename in request.filenames:
            for fp in upload_path.rglob(f"*{filename}*"):
                if fp.is_file():
                    file_paths.append(fp)
                    break
        
        if not file_paths:
            raise HTTPException(status_code=404, detail="No files found")
        
        # Analyze documents
        result = analyzer.analyze_multiple_documents(file_paths, request.analysis_type)
        
        logger.info(f"Successfully analyzed {len(file_paths)} documents")
        return result
        
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
