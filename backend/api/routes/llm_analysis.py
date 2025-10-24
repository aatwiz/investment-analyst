"""
LLM-powered analysis API endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from utils.logger import setup_logger
from services.llm_agents import InvestmentAnalystAgent, LLMConfig

router = APIRouter()
logger = setup_logger(__name__)


class LLMAnalyzeRequest(BaseModel):
    """Request model for LLM-powered analysis"""
    filename: str
    focus_areas: Optional[List[str]] = None


class LLMConfigRequest(BaseModel):
    """Request model for updating LLM configuration"""
    provider: str = "openai"
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    api_key: Optional[str] = None


# Global agent instance (will be configured via API)
agent: Optional[InvestmentAnalystAgent] = None


@router.post("/configure")
async def configure_llm_agent(config: LLMConfigRequest):
    """
    Configure the LLM agent with API keys and settings.
    
    **TODO**: Before using this endpoint, you need to:
    1. Sign up for OpenAI API key at https://platform.openai.com/
    2. Set environment variable: OPENAI_API_KEY
    3. Call this endpoint to initialize the agent
    """
    global agent
    
    try:
        llm_config = LLMConfig(
            provider=config.provider,
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            api_key=config.api_key
        )
        
        agent = InvestmentAnalystAgent(config=llm_config)
        
        return {
            "status": "success",
            "message": "LLM Agent configured successfully",
            "config": {
                "provider": config.provider,
                "model": config.model,
                "temperature": config.temperature
            }
        }
    except Exception as e:
        logger.error(f"Failed to configure LLM agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_with_llm(request: LLMAnalyzeRequest):
    """
    Perform LLM-powered analysis on a document.
    
    This combines keyword-based pre-processing with LLM reasoning
    for comprehensive investment insights.
    
    **Status**: Infrastructure ready, LLM API integration pending
    """
    global agent
    
    # Initialize with default config if not configured
    if agent is None:
        agent = InvestmentAnalystAgent()
        logger.warning("Using default LLM config - agent not yet configured")
    
    try:
        result = await agent.analyze_document(
            filename=request.filename,
            focus_areas=request.focus_areas
        )
        
        return {
            "status": "success",
            "filename": request.filename,
            "analysis": result
        }
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.filename}")
    except Exception as e:
        logger.error(f"LLM analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prompt-preview/{filename}")
async def preview_llm_prompt(filename: str):
    """
    Preview the LLM prompt that would be generated for a document.
    
    Useful for debugging and understanding what data the LLM will see.
    Does not call the LLM API - just shows the prompt.
    """
    global agent
    
    if agent is None:
        agent = InvestmentAnalystAgent()
    
    try:
        prompt = agent.generate_prompt_preview(filename)
        
        return {
            "status": "success",
            "filename": filename,
            "prompt": prompt,
            "prompt_length": len(prompt),
            "estimated_tokens": len(prompt) // 4  # Rough estimate
        }
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")
    except Exception as e:
        logger.error(f"Prompt preview failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_llm_agent_status():
    """
    Get the current status of the LLM agent.
    """
    global agent
    
    if agent is None:
        return {
            "status": "not_configured",
            "message": "LLM Agent not initialized. Call /configure first.",
            "ready": False
        }
    
    return {
        "status": "configured",
        "provider": agent.config.provider,
        "model": agent.config.model,
        "ready": agent.llm is not None,
        "message": "Agent configured but LLM API not yet implemented"
    }
