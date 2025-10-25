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
import os

from openai import AsyncOpenAI

from utils.logger import setup_logger
from services.file_processing import FileProcessor  # Use FileProcessor instead

logger = setup_logger(__name__)


@dataclass
class LLMConfig:
    """Configuration for LLM providers"""
    provider: str = "openai"  # openai, anthropic, azure
    model: str = "gpt-4o-mini"  # gpt-4o-mini supports JSON mode and is cost-effective
    temperature: float = 0.3  # Lower temperature for more consistent analysis
    max_tokens: int = 3000  # More tokens for detailed analysis
    api_key: Optional[str] = None


class InvestmentAnalystAgent:
    """
    LLM-powered investment analyst that provides deep analysis and recommendations.
    
    Directly extracts text from documents and feeds to LLM for analysis,
    avoiding keyword-based pre-processing that can introduce bias.
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self.file_processor = FileProcessor()  # Extract raw text only
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
        from pathlib import Path
        from utils.config import settings
        
        logger.info(f"LLM Agent analyzing: {filename}")
        
        # Find the file (it might be in a subdirectory)
        upload_dir = Path(settings.UPLOAD_DIR)
        file_path = None
        
        # First try direct path
        direct_path = upload_dir / filename
        if direct_path.exists():
            file_path = direct_path
        else:
            # Search recursively in subdirectories
            for found_file in upload_dir.rglob(filename):
                if found_file.is_file():
                    file_path = found_file
                    break
        
        if file_path is None:
            raise FileNotFoundError(f"File not found: {filename}")
        
        logger.info(f"Found file at: {file_path}")
        
        # Step 1: Extract raw text and tables from document (NO keyword analysis)
        extracted_data = self.file_processor.process_file(file_path)
        
        # Check if extraction was successful
        if extracted_data.get("status") == "error":
            raise Exception(f"Document extraction failed: {extracted_data.get('error')}")
        
        # Get raw text content
        raw_text = extracted_data.get("text", "")
        tables = extracted_data.get("tables", [])
        metadata = extracted_data.get("metadata", {})
        
        # Step 2: Build LLM prompt from raw content (not keyword analysis)
        prompt = self._build_analysis_prompt_from_raw_text(
            raw_text=raw_text,
            tables=tables,
            metadata=metadata,
            focus_areas=focus_areas
        )
        
        # Step 3: Get LLM insights
        llm_insights = await self._get_llm_insights(prompt)
        
        # Step 4: Return LLM analysis directly
        final_analysis = {
            "analysis_type": "llm_powered",
            "extraction_method": "raw_text",
            "document_info": {
                "filename": filename,
                "file_type": extracted_data.get("type"),
                "page_count": metadata.get("page_count", 0),
                "word_count": len(raw_text.split())
            },
            "llm_analysis": llm_insights,
            "model_used": self.config.model
        }
        
        logger.info(f"LLM Agent completed analysis: {filename}")
        return final_analysis
    
    def _build_analysis_prompt_from_raw_text(
        self,
        raw_text: str,
        tables: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        focus_areas: Optional[List[str]] = None
    ) -> str:
        """
        Build LLM prompt directly from raw extracted text.
        
        This avoids keyword-based bias and lets the LLM read the actual content.
        """
        
        # Truncate text if too long (keep first ~50K characters for context)
        max_chars = 50000
        text_preview = raw_text[:max_chars]
        if len(raw_text) > max_chars:
            text_preview += f"\n\n... [Document continues for {len(raw_text) - max_chars} more characters]"
        
        # Build prompt
        prompt_parts = [
            "# Investment Due Diligence Analysis",
            "",
            "You are an experienced investment analyst with 15+ years in venture capital and private equity.",
            "You specialize in financial statement analysis, due diligence, and investment recommendations.",
            "",
            "## Task",
            "Analyze the financial document provided below and give a comprehensive investment recommendation.",
            "",
            "## Document Information",
            f"- File Type: {metadata.get('type', 'Unknown')}",
            f"- Pages: {metadata.get('page_count', 'Unknown')}",
            f"- Word Count: {len(raw_text.split())}",
            "",
            "## IMPORTANT INSTRUCTIONS",
            "",
            "**READ THE DOCUMENT CAREFULLY**. This is likely a financial statement with:",
            "- Income statements showing Revenue, Costs, Profit/Loss",
            "- Balance sheets with Assets, Liabilities, Equity",
            "- Cash flow statements",
            "- Notes and disclosures",
            "",
            "**DO NOT confuse accounting terms with problems:**",
            "- 'Loss from death of livestock' = normal operational cost, NOT a business loss",
            "- 'Liabilities' = standard balance sheet item, NOT necessarily bad",
            "- 'Impairment' = accounting adjustment, NOT a crisis",
            "",
            "**FOCUS ON THE ACTUAL NUMBERS:**",
            "- Is Revenue growing or declining?",
            "- Is the company profitable? (Check NET PROFIT/LOSS)",
            "- Are profit margins improving?",
            "- Is cash flow positive?",
            "- Are assets greater than liabilities?",
            "",
            "---",
            "",
            "## DOCUMENT CONTENT",
            "",
            text_preview,
            "",
        ]
        
        # Add tables if present
        if tables:
            prompt_parts.extend([
                "",
                "## EXTRACTED TABLES",
                "",
                f"The document contains {len(tables)} tables with financial data.",
                "Key tables have been extracted above in the document content.",
                ""
            ])
        
        # Add focus areas if specified
        if focus_areas:
            prompt_parts.extend([
                "## SPECIFIC FOCUS AREAS REQUESTED",
                ""
            ])
            for area in focus_areas:
                prompt_parts.append(f"- {area}")
            prompt_parts.append("")
        
        # Analysis requirements
        prompt_parts.extend([
            "---",
            "",
            "## REQUIRED OUTPUT",
            "",
            "**CRITICAL**: Respond with ONLY valid JSON. No markdown, no code blocks, no text outside JSON.",
            "",
            "Required JSON structure:",
            "",
            "```json",
            "{",
            '  "executive_summary": "2-3 sentences summarizing the investment case",',
            '  "financial_health": {',
            '    "analysis": "Detailed financial assessment based on ACTUAL numbers from the document",',
            '    "key_metrics": {',
            '      "revenue_trend": "Growing/Stable/Declining - cite actual figures",',
            '      "profitability": "Profitable/Breakeven/Unprofitable - cite NET PROFIT figure",',
            '      "cash_position": "Strong/Adequate/Weak - based on cash flow"',
            '    },',
            '    "concerns": ["Real financial issues based on numbers, not accounting terms"],',
            '    "positives": ["Financial strengths with specific figures"]',
            '  },',
            '  "risk_assessment": {',
            '    "score": 3,  // 0-10 (0=no risk, 10=critical risk) - base on ACTUAL performance',
            '    "analysis": "Risk evaluation based on financial performance trends",',
            '    "critical_risks": [',
            '      {',
            '        "category": "financial/operational/market/legal",',
            '        "issue": "Specific issue with evidence from document",',
            '        "severity": 6,  // 0-10',
            '        "impact": "Concrete impact description",',
            '        "mitigation": "Recommended mitigation"',
            '      }',
            '    ]',
            '  },',
            '  "opportunity_analysis": {',
            '    "analysis": "Growth opportunities and competitive advantages",',
            '    "key_strengths": [',
            '      {',
            '        "area": "Market position/Technology/Financials/etc",',
            '        "description": "Specific strength",',
            '        "competitive_advantage": "Why this matters"',
            '      }',
            '    ],',
            '    "growth_potential": {',
            '      "market": "Market opportunity assessment",',
            '      "scalability": "Scalability evaluation",',
            '      "timeline": "Expected growth trajectory"',
            '    }',
            '  },',
            '  "recommendation": {',
            '    "action": "BUY/HOLD/AVOID",',
            '    "confidence": 80,  // 0-100% - base on quality of data',
            '    "reasoning": "Clear reasoning based on financial performance",',
            '    "target_valuation": "Suggested valuation if applicable",',
            '    "conditions": ["Key factors to monitor"]',
            '  },',
            '  "next_steps": [',
            '    {',
            '      "category": "documentation/verification/questions",',
            '      "action": "Specific action",',
            '      "priority": "high/medium/low",',
            '      "rationale": "Why needed"',
            '    }',
            '  ]',
            "}",
            "```",
            "",
            "### CRITICAL REMINDERS:",
            "",
            "1. **READ THE ACTUAL NUMBERS** - Don't guess based on keywords",
            "2. **NET PROFIT > 0 = Profitable** - Even if document mentions some losses",
            "3. **Revenue Growth% = ((Current - Previous) / Previous) × 100**",
            "4. **Check the Statement Period** - Q1, Q2, H1, Annual?",
            "5. **Compare Year-over-Year** - Is performance improving?",
            "",
            "Analyze the document now and provide your JSON response."
        ])
        
        return "\n".join(prompt_parts)
        """
        Build the LLM prompt from pre-processed structured data.
        
        This is the KEY function - it transforms keyword-based analysis
        into a focused prompt for deep LLM reasoning.
        """
        
        # Extract key components from structured analysis
        red_flags_data = structured_data.get("red_flags", {})
        positive_signals_data = structured_data.get("positive_signals", {})
        financial_metrics = structured_data.get("financial_metrics", {})
        entities = structured_data.get("entities", {})
        recommendation = structured_data.get("recommendation", {})
        
        # Flatten red flags from categories to list
        red_flags = []
        if isinstance(red_flags_data, dict):
            flags_by_category = red_flags_data.get("flags_by_category", {})
            for category, flags_list in flags_by_category.items():
                if isinstance(flags_list, list):
                    for flag in flags_list:
                        flag['category'] = category  # Add category to each flag
                        red_flags.append(flag)
        
        # Flatten positive signals from categories to list
        positive_signals = []
        if isinstance(positive_signals_data, dict):
            signals_by_category = positive_signals_data.get("signals_by_category", {})
            for category, signals_list in signals_by_category.items():
                if isinstance(signals_list, list):
                    for signal in signals_list:
                        signal['category'] = category  # Add category to each signal
                        positive_signals.append(signal)
        
        # Safely get confidence as float
        confidence = recommendation.get('confidence', 0)
        try:
            confidence = float(confidence) if confidence else 0.0
        except (ValueError, TypeError):
            confidence = 0.0
        
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
            f"- Confidence Score: {confidence:.1%}",
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
            "---",
            "",
            "## 📊 Investment Analysis Request",
            "",
            "Based on the pre-processed data above, provide a comprehensive investment analysis.",
            "",
            "### Output Requirements:",
            "",
            "**CRITICAL**: Respond with ONLY a valid JSON object. No markdown, no code blocks, no text outside JSON.",
            "",
            "Required JSON structure:",
            "",
            "```json",
            "{",
            '  "risk_assessment": {',
            '    "score": 5,  // 0-10 scale (0=no risk, 10=critical risk)',
            '    "analysis": "Detailed risk evaluation...",',
            '    "critical_risks": [',
            '      {',
            '        "category": "legal/financial/operational/market",',
            '        "issue": "Specific risk description",',
            '        "severity": 8,  // 0-10',
            '        "impact": "Potential impact if realized",',
            '        "mitigation": "Recommended mitigation strategy"',
            '      }',
            '    ],',
            '    "risk_factors_missed": ["Additional risks not caught by keyword scan"]',
            '  },',
            '  "opportunity_analysis": {',
            '    "analysis": "Overall opportunity evaluation...",',
            '    "key_strengths": [',
            '      {',
            '        "area": "Market position/Technology/Team/etc",',
            '        "description": "Specific strength",',
            '        "competitive_advantage": "Why this matters"',
            '      }',
            '    ],',
            '    "growth_potential": {',
            '      "market_size": "TAM/SAM assessment",',
            '      "scalability": "Scalability evaluation",',
            '      "timeline": "Expected growth trajectory"',
            '    }',
            '  },',
            '  "financial_health": {',
            '    "analysis": "Financial health overview...",',
            '    "key_metrics": {',
            '      "revenue_trend": "Growing/Stable/Declining",',
            '      "profitability": "Assessment based on extracted metrics",',
            '      "cash_position": "Runway and burn rate if applicable"',
            '    },',
            '    "concerns": ["Any financial red flags"],',
            '    "positives": ["Financial strengths"]',
            '  },',
            '  "recommendation": {',
            '    "action": "BUY/HOLD/AVOID",  // Clear recommendation',
            '    "confidence": 75,  // 0-100%',
            '    "reasoning": "Detailed reasoning for recommendation...",',
            '    "conditions": [',
            '      "Key conditions or milestones to watch",',
            '      "Deal-breaker factors"',
            '    ],',
            '    "suggested_structure": "Investment structure if applicable (e.g., convertible note, equity)",',
            '    "target_valuation": "Suggested valuation range if applicable"',
            '  },',
            '  "next_steps": [',
            '    {',
            '      "category": "documentation/verification/questions",',
            '      "action": "Specific action to take",',
            '      "priority": "high/medium/low",',
            '      "rationale": "Why this step is needed"',
            '    }',
            '  ],',
            '  "executive_summary": "2-3 sentence investment thesis"',
            "}",
            "```",
            "",
            "### Analysis Guidelines:",
            "",
            "1. **Be Evidence-Based**: Reference specific data points from the sections above",
            "2. **Be Balanced**: Acknowledge both risks and opportunities",
            "3. **Be Actionable**: Provide specific, implementable next steps",
            "4. **Be Professional**: Suitable for presentation to investment committee",
            "5. **Be Honest**: If data is insufficient, state clearly",
            "",
            "### Key Questions to Address:",
            "",
            "- Do the red flags represent deal-breakers or manageable risks?",
            "- Do the positive signals indicate sustainable competitive advantage?",
            "- Are the financial metrics consistent with the company's stage and industry?",
            "- What additional information is critical for making a final decision?",
            "- What is the risk/reward profile of this opportunity?",
        ])
        
        return "\n".join(prompt_parts)
    
    async def _get_llm_insights(self, prompt: str) -> Dict[str, Any]:
        """
        Get insights from LLM provider (OpenAI GPT-4).
        
        Returns structured JSON with investment analysis including:
        - Risk assessment with severity scores
        - Opportunity evaluation
        - Financial health analysis
        - Investment recommendation with confidence
        - Due diligence next steps
        """
        
        # Get API key from config or environment
        api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            logger.warning("No OpenAI API key found - returning placeholder")
            return {
                "status": "error",
                "message": "OpenAI API key not configured. Set OPENAI_API_KEY environment variable.",
                "risk_assessment": {
                    "score": 0,
                    "analysis": "API key required for LLM analysis"
                },
                "opportunity_analysis": {
                    "analysis": "API key required for LLM analysis"
                },
                "financial_health": {
                    "analysis": "API key required for LLM analysis"
                },
                "recommendation": {
                    "action": "PENDING",
                    "confidence": 0,
                    "reasoning": "Configure API key to enable LLM-powered analysis"
                },
                "next_steps": []
            }
        
        try:
            # Initialize OpenAI client with context manager for proper cleanup
            async with AsyncOpenAI(api_key=api_key) as client:
                # System prompt for investment analyst persona
                system_prompt = """You are a highly experienced investment analyst with 15+ years in venture capital and private equity. 
You specialize in due diligence, risk assessment, and investment recommendations.

Your analysis is:
- Thorough and evidence-based
- Balanced (acknowledge both risks and opportunities)
- Actionable (provide specific next steps)
- Professional (suitable for investment committee presentation)

CRITICAL: Respond ONLY with valid JSON. No markdown, no code blocks, no explanations outside the JSON structure."""

                # Call OpenAI API
                logger.info(f"Calling OpenAI API with model: {self.config.model}")
                
                response = await client.chat.completions.create(
                    model=self.config.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    response_format={"type": "json_object"}  # Ensure JSON response
                )
                
                # Parse JSON response
                result_text = response.choices[0].message.content
                result = json.loads(result_text)
                
                logger.info("Successfully received LLM analysis")
                
                # Validate and normalize response structure
                normalized_result = {
                    "status": "success",
                    "model_used": self.config.model,
                    "risk_assessment": result.get("risk_assessment", {
                        "score": 0,
                        "analysis": "No risk assessment provided"
                    }),
                    "opportunity_analysis": result.get("opportunity_analysis", {
                        "analysis": "No opportunity analysis provided"
                    }),
                    "financial_health": result.get("financial_health", {
                        "analysis": "No financial health evaluation provided"
                    }),
                    "recommendation": result.get("recommendation", {
                        "action": "HOLD",
                        "confidence": 50,
                        "reasoning": "Insufficient data for clear recommendation"
                    }),
                    "next_steps": result.get("next_steps", [])
                }
                
                return normalized_result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return {
                "status": "error",
                "message": f"LLM returned invalid JSON: {str(e)}",
                "risk_assessment": {"score": 0, "analysis": "Parse error"},
                "opportunity_analysis": {"analysis": "Parse error"},
                "financial_health": {"analysis": "Parse error"},
                "recommendation": {
                    "action": "ERROR",
                    "confidence": 0,
                    "reasoning": "Failed to parse LLM response"
                },
                "next_steps": []
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return {
                "status": "error",
                "message": f"API error: {str(e)}",
                "risk_assessment": {"score": 0, "analysis": str(e)},
                "opportunity_analysis": {"analysis": str(e)},
                "financial_health": {"analysis": str(e)},
                "recommendation": {
                    "action": "ERROR",
                    "confidence": 0,
                    "reasoning": f"API call failed: {str(e)}"
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
        
        # Extract red flags and positive signals counts safely
        red_flags_data = structured_data.get("red_flags", {})
        positive_signals_data = structured_data.get("positive_signals", {})
        
        red_flags_count = red_flags_data.get("total_flags", 0) if isinstance(red_flags_data, dict) else 0
        positive_signals_count = positive_signals_data.get("total_signals", 0) if isinstance(positive_signals_data, dict) else 0
        
        return {
            "analysis_type": "llm_powered",
            "structured_analysis": {
                "method": "keyword_based",
                "red_flags_count": red_flags_count,
                "positive_signals_count": positive_signals_count,
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
        from pathlib import Path
        from utils.config import settings
        
        # Find the file (it might be in a subdirectory)
        upload_dir = Path(settings.UPLOAD_DIR)
        file_path = None
        
        # First try direct path
        direct_path = upload_dir / filename
        if direct_path.exists():
            file_path = direct_path
        else:
            # Search recursively in subdirectories
            for found_file in upload_dir.rglob(filename):
                if found_file.is_file():
                    file_path = found_file
                    break
        
        if file_path is None:
            raise FileNotFoundError(f"File not found: {filename}")
        
        analyzer_result = self.analyzer.analyze_document(file_path, "comprehensive")
        
        if not analyzer_result.get("success"):
            raise Exception(f"Document analysis failed: {analyzer_result.get('error')}")
        
        structured_data = analyzer_result.get("analysis", {})
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
