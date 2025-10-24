"""
Investment Analyst LLM Agent

This agent takes pre-processed document analysis and performs deep reasoning
to generate comprehensive investment recommendations.

Architecture:
    Document → DocumentAnalyzer (structure) → LLM Agent (reasoning) → Report
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json

from utils.logger import setup_logger
from services.document_analysis import DocumentAnalyzer

logger = setup_logger(__name__)


@dataclass
class LLMConfig:
    """Configuration for LLM providers"""
    provider: str = "openai"  # openai, anthropic, azure
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    api_key: Optional[str] = None


class InvestmentAnalystAgent:
    """
    LLM-powered investment analyst that provides deep analysis and recommendations.
    
    Uses the DocumentAnalyzer as a pre-processing layer to structure information,
    then applies LLM reasoning for nuanced insights.
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self.analyzer = DocumentAnalyzer()
        self.llm = None  # Will be initialized when API keys are added
        logger.info(f"Investment Analyst Agent initialized with {self.config.provider}")
    
    async def analyze_document(
        self, 
        filename: str, 
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive LLM-powered analysis of a document.
        
        Args:
            filename: Name of the document to analyze
            focus_areas: Optional list of specific areas to focus on
                        (e.g., ["market_risk", "financial_health", "team"])
        
        Returns:
            Dict containing structured analysis and LLM insights
        """
        logger.info(f"LLM Agent analyzing: {filename}")
        
        # Step 1: Pre-process with DocumentAnalyzer (keyword-based)
        structured_data = self.analyzer.analyze_document(filename, "comprehensive")
        
        # Step 2: Build LLM prompt from structured data
        prompt = self._build_analysis_prompt(structured_data, focus_areas)
        
        # Step 3: Get LLM insights (TODO: implement when API keys added)
        llm_insights = await self._get_llm_insights(prompt)
        
        # Step 4: Combine structured + LLM insights
        final_analysis = self._merge_insights(structured_data, llm_insights)
        
        logger.info(f"LLM Agent completed analysis: {filename}")
        return final_analysis
    
    def _build_analysis_prompt(
        self, 
        structured_data: Dict[str, Any],
        focus_areas: Optional[List[str]] = None
    ) -> str:
        """
        Build the LLM prompt from pre-processed structured data.
        
        This is the KEY function - it transforms keyword-based analysis
        into a focused prompt for deep LLM reasoning.
        """
        
        # Extract key components from structured analysis
        red_flags = structured_data.get("red_flags", [])
        positive_signals = structured_data.get("positive_signals", [])
        financial_metrics = structured_data.get("financial_metrics", {})
        entities = structured_data.get("entities", {})
        recommendation = structured_data.get("recommendation", {})
        
        # Build prompt sections
        prompt_parts = [
            "# Investment Due Diligence Analysis Request",
            "",
            "You are an experienced investment analyst reviewing a potential investment opportunity.",
            "Below is pre-processed structured data extracted from the due diligence documents.",
            "Provide deep analysis and actionable recommendations.",
            "",
            "## Document Summary",
            f"- Analysis Type: Comprehensive Due Diligence",
            f"- Preliminary Recommendation: {recommendation.get('action', 'N/A')}",
            f"- Confidence Score: {recommendation.get('confidence', 0):.1%}",
            "",
        ]
        
        # RED FLAGS SECTION
        if red_flags:
            prompt_parts.extend([
                "## ⚠️ Identified Risk Factors",
                f"Found {len(red_flags)} potential red flags requiring investigation:",
                ""
            ])
            for flag in red_flags[:10]:  # Top 10 most critical
                category = flag.get('category', 'unknown')
                keyword = flag.get('keyword', '')
                context = flag.get('context', '')
                prompt_parts.append(f"**{category.upper()}**: `{keyword}`")
                prompt_parts.append(f"Context: {context[:200]}...")
                prompt_parts.append("")
        else:
            prompt_parts.extend([
                "## ✅ Risk Assessment",
                "No major red flags detected in initial keyword scan.",
                ""
            ])
        
        # POSITIVE SIGNALS SECTION
        if positive_signals:
            prompt_parts.extend([
                "## 📈 Positive Indicators",
                f"Found {len(positive_signals)} positive signals:",
                ""
            ])
            for signal in positive_signals[:10]:
                category = signal.get('category', 'unknown')
                keyword = signal.get('keyword', '')
                context = signal.get('context', '')
                prompt_parts.append(f"**{category.upper()}**: `{keyword}`")
                prompt_parts.append(f"Context: {context[:200]}...")
                prompt_parts.append("")
        
        # FINANCIAL METRICS SECTION
        if financial_metrics:
            prompt_parts.extend([
                "## 💰 Financial Metrics Extracted",
                ""
            ])
            
            currencies = financial_metrics.get('currencies', [])
            percentages = financial_metrics.get('percentages', [])
            
            if currencies:
                prompt_parts.append(f"**Currency Values**: {', '.join(currencies[:5])}")
            if percentages:
                prompt_parts.append(f"**Percentages**: {', '.join(percentages[:5])}")
            prompt_parts.append("")
        
        # ENTITIES SECTION
        if entities:
            prompt_parts.extend([
                "## 📋 Key Entities Identified",
                ""
            ])
            
            dates = entities.get('dates', [])
            emails = entities.get('emails', [])
            entities_list = entities.get('entities', [])
            
            if dates:
                prompt_parts.append(f"**Dates**: {', '.join(dates[:5])}")
            if emails:
                prompt_parts.append(f"**Contacts**: {len(emails)} email addresses found")
            if entities_list:
                prompt_parts.append(f"**Named Entities**: {', '.join(entities_list[:10])}")
            prompt_parts.append("")
        
        # FOCUS AREAS (if specified)
        if focus_areas:
            prompt_parts.extend([
                "## 🎯 Specific Focus Areas Requested",
                ""
            ])
            for area in focus_areas:
                prompt_parts.append(f"- {area}")
            prompt_parts.append("")
        
        # ANALYSIS REQUEST
        prompt_parts.extend([
            "## 📊 Analysis Required",
            "",
            "Please provide:",
            "",
            "1. **Risk Assessment** (0-10 scale)",
            "   - Evaluate each identified red flag",
            "   - Assess severity and likelihood of impact",
            "   - Identify any missing risk factors not caught by keywords",
            "",
            "2. **Opportunity Analysis**",
            "   - Evaluate strength of positive signals",
            "   - Identify competitive advantages",
            "   - Assess growth potential based on metrics",
            "",
            "3. **Financial Health Evaluation**",
            "   - Analyze extracted financial metrics in context",
            "   - Identify trends (positive/negative)",
            "   - Flag any concerning financial patterns",
            "",
            "4. **Investment Recommendation**",
            "   - Clear recommendation: BUY / HOLD / AVOID",
            "   - Confidence level (0-100%)",
            "   - Key conditions or milestones to watch",
            "   - Suggested investment structure (if applicable)",
            "",
            "5. **Due Diligence Next Steps**",
            "   - Additional documents to request",
            "   - Key questions for management",
            "   - Areas requiring third-party verification",
            "",
            "Format your response as structured JSON for easy parsing.",
        ])
        
        return "\n".join(prompt_parts)
    
    async def _get_llm_insights(self, prompt: str) -> Dict[str, Any]:
        """
        Get insights from LLM provider.
        
        TODO: Implement actual LLM API calls tomorrow
        - OpenAI GPT-4
        - Anthropic Claude
        - Azure OpenAI
        """
        
        # For now, return placeholder
        logger.warning("LLM API not yet configured - returning placeholder")
        
        return {
            "status": "placeholder",
            "message": "LLM integration pending - API keys needed",
            "risk_assessment": {
                "score": 0,
                "analysis": "LLM analysis will appear here"
            },
            "opportunity_analysis": {
                "analysis": "LLM analysis will appear here"
            },
            "financial_health": {
                "analysis": "LLM analysis will appear here"
            },
            "recommendation": {
                "action": "PENDING",
                "confidence": 0,
                "reasoning": "LLM recommendation will appear here"
            },
            "next_steps": []
        }
    
    def _merge_insights(
        self, 
        structured_data: Dict[str, Any], 
        llm_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge keyword-based analysis with LLM insights.
        
        Returns comprehensive analysis combining both approaches.
        """
        
        return {
            "analysis_type": "llm_powered",
            "structured_analysis": {
                "method": "keyword_based",
                "red_flags_count": len(structured_data.get("red_flags", [])),
                "positive_signals_count": len(structured_data.get("positive_signals", [])),
                "preliminary_recommendation": structured_data.get("recommendation", {})
            },
            "llm_analysis": llm_insights,
            "combined_recommendation": {
                "action": llm_insights.get("recommendation", {}).get("action", "PENDING"),
                "confidence": llm_insights.get("recommendation", {}).get("confidence", 0),
                "structured_score": structured_data.get("recommendation", {}).get("confidence", 0),
                "reasoning": llm_insights.get("recommendation", {}).get("reasoning", "")
            },
            "raw_structured_data": structured_data,
            "prompt_used": "Available in logs"
        }
    
    def generate_prompt_preview(self, filename: str) -> str:
        """
        Generate a preview of the LLM prompt without calling the API.
        Useful for debugging and understanding what data the LLM will see.
        """
        structured_data = self.analyzer.analyze_document(filename, "comprehensive")
        return self._build_analysis_prompt(structured_data)


# TODO: Add LLM provider implementations
class OpenAIProvider:
    """OpenAI GPT-4 implementation"""
    pass


class AnthropicProvider:
    """Anthropic Claude implementation"""
    pass


class AzureOpenAIProvider:
    """Azure OpenAI implementation"""
    pass
