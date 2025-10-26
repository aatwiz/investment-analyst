"""
Report generation API endpoints
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import io

from utils.logger import setup_logger
from services.report_generation import InvestmentMemoGenerator, PitchDeckGenerator

router = APIRouter()
logger = setup_logger(__name__)

# Initialize generators
memo_generator = InvestmentMemoGenerator()
deck_generator = PitchDeckGenerator()


class MemoRequest(BaseModel):
    """Request model for investment memo generation"""
    company_id: Optional[str] = None
    company_data: Dict[str, Any]
    deal_data: Optional[Dict[str, Any]] = None
    market_data: Optional[Dict[str, Any]] = None
    financial_model: Optional[Dict[str, Any]] = None
    template_type: str = "standard"
    analyst_name: str = "Investment Analyst"
    firm_name: str = "Investment Firm"


class DeckRequest(BaseModel):
    """Request model for pitch deck generation"""
    company_id: Optional[str] = None
    company_data: Dict[str, Any]
    deal_data: Optional[Dict[str, Any]] = None
    market_data: Optional[Dict[str, Any]] = None
    financial_model: Optional[Dict[str, Any]] = None
    template_type: str = "standard"
    analyst_name: Optional[str] = None
    

@router.post("/generate-memo")
async def generate_memo(request: MemoRequest):
    """
    Generate investment memo document (DOCX)
    
    Args:
        request: Memo generation request with company data
    
    Returns:
        DOCX file as streaming response
    """
    try:
        logger.info(f"Generating investment memo for company: {request.company_data.get('name', 'Unknown')}")
        
        # Generate memo
        memo_bytes = await memo_generator.generate_memo(
            company_data=request.company_data,
            deal_data=request.deal_data,
            market_data=request.market_data,
            financial_model=request.financial_model,
            template_type=request.template_type,
            analyst_name=request.analyst_name,
            firm_name=request.firm_name
        )
        
        # Generate filename
        company_name = request.company_data.get("name", "Company").replace(" ", "_")
        filename = f"Investment_Memo_{company_name}.docx"
        
        # Return as streaming response
        return StreamingResponse(
            memo_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating memo: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate memo: {str(e)}")


@router.post("/generate-deck")
async def generate_deck(request: DeckRequest):
    """
    Generate pitch deck presentation (PPTX)
    
    Args:
        request: Deck generation request with company data
    
    Returns:
        PPTX file as streaming response
    """
    try:
        logger.info(f"Generating pitch deck for company: {request.company_data.get('name', 'Unknown')}")
        
        # Generate deck
        deck_bytes = await deck_generator.generate_deck(
            company_data=request.company_data,
            deal_data=request.deal_data,
            market_data=request.market_data,
            financial_model=request.financial_model,
            template_type=request.template_type
        )
        
        # Generate filename
        company_name = request.company_data.get("name", "Company").replace(" ", "_")
        filename = f"Pitch_Deck_{company_name}.pptx"
        
        # Return as streaming response
        return StreamingResponse(
            deck_bytes,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating deck: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate deck: {str(e)}")


@router.get("/templates")
async def list_templates():
    """
    List available report templates
    
    Returns:
        List of available memo and deck templates
    """
    return {
        "success": True,
        "templates": {
            "memos": [
                {
                    "id": "standard",
                    "name": "Standard Investment Memo",
                    "description": "Comprehensive investment memo with all sections",
                    "sections": [
                        "Executive Summary",
                        "Investment Rationale",
                        "Key Terms",
                        "Risk Factors",
                        "Recommendation",
                        "Appendices"
                    ]
                },
                {
                    "id": "detailed",
                    "name": "Detailed Investment Memo",
                    "description": "Extended memo with additional analysis",
                    "sections": [
                        "Executive Summary",
                        "Company Overview",
                        "Market Analysis",
                        "Investment Rationale",
                        "Financial Analysis",
                        "Key Terms",
                        "Risk Factors",
                        "Recommendation",
                        "Appendices"
                    ]
                },
                {
                    "id": "summary",
                    "name": "Investment Summary",
                    "description": "Quick summary memo for initial review",
                    "sections": [
                        "Executive Summary",
                        "Investment Highlights",
                        "Key Terms",
                        "Recommendation"
                    ]
                }
            ],
            "decks": [
                {
                    "id": "standard",
                    "name": "Standard Pitch Deck",
                    "description": "Comprehensive 12-slide investor presentation",
                    "slides": [
                        "Title",
                        "Problem",
                        "Solution",
                        "Market Opportunity",
                        "Product/Technology",
                        "Business Model",
                        "Traction & Milestones",
                        "Financial Projections",
                        "Team",
                        "Competitive Landscape",
                        "Investment Ask",
                        "Closing"
                    ]
                },
                {
                    "id": "detailed",
                    "name": "Detailed Pitch Deck",
                    "description": "Extended deck with additional slides",
                    "slides": [
                        "Title",
                        "Problem",
                        "Solution",
                        "Market Opportunity",
                        "Product/Technology",
                        "Business Model",
                        "Go-to-Market Strategy",
                        "Traction & Milestones",
                        "Financial Projections",
                        "Unit Economics",
                        "Team",
                        "Competitive Landscape",
                        "Investment Ask",
                        "Use of Funds",
                        "Exit Strategy",
                        "Closing"
                    ]
                }
            ]
        }
    }


@router.post("/preview")
async def preview_report(request: MemoRequest):
    """
    Generate preview data for a report (metadata and first section)
    
    Args:
        request: Report generation request
    
    Returns:
        Preview data including company info, template, and estimated sections
    """
    try:
        company_name = request.company_data.get("name", "Unknown Company")
        company_stage = request.company_data.get("stage", "Unknown")
        
        # Determine report type based on template
        template_info = None
        if request.template_type in ["standard", "detailed", "summary"]:
            # Memo templates
            templates_response = await list_templates()
            for template in templates_response["templates"]["memos"]:
                if template["id"] == request.template_type:
                    template_info = template
                    break
        
        preview_data = {
            "success": True,
            "company_name": company_name,
            "company_stage": company_stage,
            "template_type": request.template_type,
            "template_info": template_info,
            "analyst_name": request.analyst_name,
            "firm_name": request.firm_name,
            "estimated_pages": 8 if request.template_type == "detailed" else 5 if request.template_type == "standard" else 3,
            "has_financial_data": request.financial_model is not None,
            "has_market_data": request.market_data is not None,
            "has_deal_data": request.deal_data is not None
        }
        
        return preview_data
        
    except Exception as e:
        logger.error(f"Error generating preview: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate preview: {str(e)}")
