"""
Financial modeling API endpoints
Feature 4: Financial Modeling & Scenario Planning
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import io
import pandas as pd
from datetime import datetime

from utils.logger import setup_logger
from services.financial_modeling.projection_engine import ProjectionEngine, ModelAssumptions, ScenarioType
from services.financial_modeling.data_extractor import FinancialDataExtractor

router = APIRouter()
logger = setup_logger(__name__)

# Initialize services
projection_engine = ProjectionEngine()
data_extractor = FinancialDataExtractor()


class ExtractRequest(BaseModel):
    """Request to extract financial data from document"""
    file_path: str = Field(..., description="Path to uploaded document")
    document_type: str = Field(default="financial_statement", description="Type of financial document")


class GenerateModelRequest(BaseModel):
    """Request to generate financial projection model"""
    assumptions: Dict[str, Any] = Field(..., description="Model assumptions")
    months: int = Field(default=36, ge=12, le=60, description="Number of months to project (12-60)")
    start_date: Optional[str] = Field(None, description="Starting date (YYYY-MM-DD)")


class ScenarioRequest(BaseModel):
    """Request to run scenario analysis"""
    assumptions: Dict[str, Any] = Field(..., description="Base model assumptions")
    months: int = Field(default=36, ge=12, le=60)
    scenarios: List[str] = Field(default=["base", "best", "worst"], description="Scenarios to run")


class ExportRequest(BaseModel):
    """Request to export model"""
    projections_data: Dict[str, Any] = Field(..., description="Projection data to export")
    format: str = Field(default="excel", description="Export format: excel, csv")
    file_name: str = Field(default="financial_model", description="Output file name")


@router.post("/extract")
async def extract_financial_data(request: ExtractRequest):
    """
    Extract financial data from uploaded documents
    
    Integrates with Feature 2 (Document Analysis) to parse financial statements
    and extract historical data for model building.
    
    Args:
        request: Extract request with file path and document type
    
    Returns:
        Extracted financial data in structured format
    """
    try:
        logger.info(f"Extracting financial data from: {request.file_path}")
        
        # Check if CSV (use direct parser)
        if request.file_path.endswith('.csv'):
            extracted_data = data_extractor.parse_csv_financial_model(request.file_path)
        else:
            # Use LLM extraction for other formats
            extracted_data = await data_extractor.extract_from_document(
                file_path=request.file_path,
                document_type=request.document_type
            )
        
        # Infer assumptions from historical data
        inferred_assumptions = data_extractor.infer_assumptions_from_historical(extracted_data)
        
        return {
            "success": True,
            "extracted_data": extracted_data,
            "inferred_assumptions": inferred_assumptions,
            "file_path": request.file_path,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error extracting financial data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.post("/generate")
async def generate_projection_model(request: GenerateModelRequest):
    """
    Generate financial projection model
    
    Creates detailed monthly projections including:
    - Income Statement (Revenue, COGS, OpEx, EBITDA, Net Income)
    - Cash Flow Statement (Operating, Investing, Financing activities)
    - Key Metrics (Burn rate, runway, growth rates)
    
    Args:
        request: Model generation request with assumptions and parameters
    
    Returns:
        Complete financial projection model
    """
    try:
        logger.info(f"Generating {request.months}-month projection model")
        
        # Parse assumptions
        assumptions = ModelAssumptions(**request.assumptions)
        
        # Parse start date if provided
        start_date = datetime.fromisoformat(request.start_date) if request.start_date else None
        
        # Generate projections
        projections = projection_engine.generate_projections(
            assumptions=assumptions,
            months=request.months,
            start_date=start_date,
            scenario=ScenarioType.BASE
        )
        
        # Calculate key metrics
        metrics = projection_engine.calculate_key_metrics(projections)
        
        # Convert to dict format
        projections_data = [p.to_dict() for p in projections]
        
        return {
            "success": True,
            "model": {
                "projections": projections_data,
                "assumptions": assumptions.__dict__,
                "metrics": metrics,
                "months": request.months,
                "created_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Model generation failed: {str(e)}")


@router.post("/scenario")
async def run_scenario_analysis(request: ScenarioRequest):
    """
    Run what-if scenario analysis
    
    Generates projections for multiple scenarios (Best/Base/Worst case)
    to help understand sensitivity to key assumptions.
    
    Args:
        request: Scenario request with base assumptions and scenario types
    
    Returns:
        Projections and metrics for each scenario
    """
    try:
        logger.info(f"Running scenario analysis for {len(request.scenarios)} scenarios")
        
        # Parse assumptions
        assumptions = ModelAssumptions(**request.assumptions)
        
        # Generate scenarios
        scenario_results = {}
        
        for scenario_name in request.scenarios:
            try:
                scenario_type = ScenarioType(scenario_name)
            except ValueError:
                logger.warning(f"Unknown scenario type: {scenario_name}, skipping")
                continue
            
            # Generate projections for this scenario
            projections = projection_engine.generate_projections(
                assumptions=assumptions,
                months=request.months,
                scenario=scenario_type
            )
            
            # Calculate metrics
            metrics = projection_engine.calculate_key_metrics(projections)
            
            # Store results
            scenario_results[scenario_name] = {
                "projections": [p.to_dict() for p in projections],
                "metrics": metrics
            }
        
        # Generate comparison summary
        comparison = {
            scenario: {
                "final_cash": results["metrics"]["final_cash_balance"],
                "total_revenue": results["metrics"]["total_revenue"],
                "months_to_profitability": results["metrics"]["months_to_profitability"]
            }
            for scenario, results in scenario_results.items()
        }
        
        return {
            "success": True,
            "scenarios": scenario_results,
            "comparison": comparison,
            "base_assumptions": assumptions.__dict__,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error running scenario analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scenario analysis failed: {str(e)}")


@router.post("/export")
async def export_model(request: ExportRequest):
    """
    Export financial model to Excel or CSV
    
    Creates downloadable file with all projection data formatted
    similar to the provided template.
    
    Args:
        request: Export request with projection data and format
    
    Returns:
        Downloadable file (Excel or CSV)
    """
    try:
        logger.info(f"Exporting model as {request.format}")
        
        # Convert projections to DataFrame
        df = pd.DataFrame(request.projections_data.get("projections", []))
        
        if request.format == "excel":
            # Create Excel file with multiple sheets
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Cash Flow sheet
                cash_flow_cols = [
                    'month', 'date_start', 'date_end', 'opening_cash', 'ebitda_cash',
                    'working_capital_change', 'equity_raised', 'debt_raised',
                    'interest_paid', 'tax_paid', 'capex', 'closing_cash',
                    'cash_flow_movement', 'free_cash_flow', 'cash_runway_months'
                ]
                df[cash_flow_cols].to_excel(writer, sheet_name='Cash Flow', index=False)
                
                # Income Statement sheet
                income_cols = [
                    'month', 'date_start', 'revenue', 'cogs', 'gross_profit',
                    'operating_expenses', 'ebitda', 'depreciation', 'ebit',
                    'interest_expense', 'ebt', 'tax', 'net_income'
                ]
                df[income_cols].to_excel(writer, sheet_name='Income Statement', index=False)
                
                # Metrics sheet
                if 'metrics' in request.projections_data:
                    metrics_df = pd.DataFrame([request.projections_data['metrics']])
                    metrics_df.to_excel(writer, sheet_name='Key Metrics', index=False)
            
            output.seek(0)
            
            return StreamingResponse(
                output,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename={request.file_name}.xlsx"}
            )
        
        elif request.format == "csv":
            # Create CSV
            output = io.StringIO()
            df.to_csv(output, index=False)
            output.seek(0)
            
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={request.file_name}.csv"}
            )
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")
        
    except Exception as e:
        logger.error(f"Error exporting model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/templates")
async def get_model_templates():
    """
    Get available financial model templates
    
    Returns:
        List of available templates with descriptions
    """
    templates = [
        {
            "id": "saas",
            "name": "SaaS Financial Model",
            "description": "Monthly projections for SaaS businesses with MRR/ARR tracking",
            "fields": ["mrr", "churn_rate", "cac", "ltv"]
        },
        {
            "id": "ecommerce",
            "name": "E-commerce Model",
            "description": "Projections for e-commerce with order volume and AOV",
            "fields": ["orders", "aov", "repeat_rate", "cogs_percent"]
        },
        {
            "id": "marketplace",
            "name": "Marketplace Model",
            "description": "Two-sided marketplace with GMV and take rate",
            "fields": ["gmv", "take_rate", "supply_growth", "demand_growth"]
        },
        {
            "id": "generic",
            "name": "Generic Startup Model",
            "description": "Standard revenue and expense projections",
            "fields": ["revenue_start", "growth_rate", "cogs_percent", "opex_fixed"]
        }
    ]
    
    return {
        "success": True,
        "templates": templates
    }


# Legacy endpoints (deprecated - use new endpoints above)
@router.post("/create-legacy")
async def create_financial_model_legacy(file_id: str, model_type: str):
    """Deprecated: Use /extract and /generate instead"""
    return {
        "success": False,
        "message": "This endpoint is deprecated. Use POST /modeling/extract and POST /modeling/generate instead."
    }
