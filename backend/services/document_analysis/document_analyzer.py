"""
Document Analysis Service for Investment Due Diligence
Analyzes extracted document content for key insights, red flags, and summaries
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
import re

from services.file_processor import FileProcessor
from utils.logger import setup_logger

logger = setup_logger(__name__)


class DocumentAnalyzer:
    """Analyze documents for investment due diligence"""
    
    def __init__(self):
        self.file_processor = FileProcessor()
        
        # Keywords for red flag detection
        self.red_flag_keywords = {
            "legal": [
                "lawsuit", "litigation", "pending litigation", "legal action",
                "dispute", "bankruptcy", "insolvency", "default", "breach",
                "violation", "non-compliance", "investigation", "penalty",
                "fraud", "misrepresentation", "regulatory action"
            ],
            "financial": [
                "loss", "losses", "negative cash flow", "debt", "liability",
                "going concern", "material weakness", "restatement",
                "writedown", "impairment", "covenant breach", "declining revenue",
                "cash burn", "insolvency", "liquidity issues"
            ],
            "operational": [
                "customer churn", "key personnel departure", "turnover",
                "supply chain disruption", "quality issues", "recall",
                "cybersecurity breach", "data breach", "systems failure"
            ],
            "market": [
                "market decline", "increased competition", "market share loss",
                "regulatory change", "technology disruption", "obsolete"
            ]
        }
        
        # Keywords for positive indicators
        self.positive_indicators = {
            "growth": [
                "revenue growth", "profit growth", "expansion", "market share gain",
                "new product", "innovation", "patent", "competitive advantage"
            ],
            "financial_health": [
                "positive cash flow", "profitable", "strong balance sheet",
                "low debt", "increasing margins", "consistent growth"
            ],
            "market_position": [
                "market leader", "dominant position", "strong brand",
                "customer loyalty", "recurring revenue", "long-term contracts"
            ]
        }
    
    def analyze_document(
        self,
        file_path: Path,
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Analyze a document for investment insights
        
        Args:
            file_path: Path to the document
            analysis_type: Type of analysis (comprehensive, summary, red_flags, financial)
            
        Returns:
            Analysis results with insights and recommendations
        """
        try:
            # Extract content from document
            logger.info(f"Analyzing document: {file_path.name}")
            extracted_data = self.file_processor.process_file(file_path)
            
            if extracted_data.get("status") == "error":
                return {
                    "success": False,
                    "error": extracted_data.get("error"),
                    "filename": file_path.name
                }
            
            # Perform analysis based on type
            if analysis_type == "comprehensive":
                analysis = self._comprehensive_analysis(extracted_data)
            elif analysis_type == "summary":
                analysis = self._generate_summary(extracted_data)
            elif analysis_type == "red_flags":
                analysis = self._detect_red_flags(extracted_data)
            elif analysis_type == "financial":
                analysis = self._financial_analysis(extracted_data)
            else:
                analysis = self._comprehensive_analysis(extracted_data)
            
            return {
                "success": True,
                "filename": file_path.name,
                "file_type": extracted_data.get("type"),
                "analysis_type": analysis_type,
                "analysis": analysis,
                "extracted_data_summary": extracted_data.get("summary", {})
            }
            
        except Exception as e:
            logger.error(f"Error analyzing document {file_path.name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "filename": file_path.name
            }
    
    def _comprehensive_analysis(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive analysis"""
        
        # Get text content
        text = extracted_data.get("text", "")
        
        # Perform all analyses
        summary = self._generate_summary(extracted_data)
        red_flags = self._detect_red_flags(extracted_data)
        positive_signals = self._detect_positive_signals(extracted_data)
        financial_metrics = self._extract_financial_metrics(extracted_data)
        key_entities = self._extract_key_entities(text)
        
        return {
            "summary": summary,
            "red_flags": red_flags,
            "positive_signals": positive_signals,
            "financial_metrics": financial_metrics,
            "key_entities": key_entities,
            "recommendation": self._generate_recommendation(red_flags, positive_signals)
        }
    
    def _generate_summary(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate document summary"""
        
        text = extracted_data.get("text", "")
        doc_type = extracted_data.get("type")
        
        # Basic statistics
        word_count = len(text.split())
        char_count = len(text)
        
        # Extract first few sentences as preview
        sentences = re.split(r'[.!?]+', text)
        preview = ". ".join(sentences[:3]).strip() if sentences else ""
        
        return {
            "document_type": doc_type,
            "word_count": word_count,
            "character_count": char_count,
            "preview": preview[:500] + "..." if len(preview) > 500 else preview,
            "has_tables": extracted_data.get("table_count", 0) > 0,
            "table_count": extracted_data.get("table_count", 0)
        }
    
    def _detect_red_flags(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect potential red flags in the document"""
        
        text = extracted_data.get("text", "").lower()
        
        detected_flags = {
            "legal": [],
            "financial": [],
            "operational": [],
            "market": []
        }
        
        flag_count = 0
        
        for category, keywords in self.red_flag_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    # Find context around the keyword
                    context = self._extract_context(text, keyword.lower())
                    detected_flags[category].append({
                        "keyword": keyword,
                        "context": context,
                        "severity": self._assess_severity(keyword)
                    })
                    flag_count += 1
        
        return {
            "total_flags": flag_count,
            "has_red_flags": flag_count > 0,
            "severity_level": "high" if flag_count > 10 else "medium" if flag_count > 5 else "low",
            "flags_by_category": detected_flags
        }
    
    def _detect_positive_signals(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect positive investment signals"""
        
        text = extracted_data.get("text", "").lower()
        
        detected_signals = {
            "growth": [],
            "financial_health": [],
            "market_position": []
        }
        
        signal_count = 0
        
        for category, keywords in self.positive_indicators.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    context = self._extract_context(text, keyword.lower())
                    detected_signals[category].append({
                        "keyword": keyword,
                        "context": context
                    })
                    signal_count += 1
        
        return {
            "total_signals": signal_count,
            "has_positive_signals": signal_count > 0,
            "strength_level": "strong" if signal_count > 10 else "moderate" if signal_count > 5 else "weak",
            "signals_by_category": detected_signals
        }
    
    def _extract_context(self, text: str, keyword: str, window: int = 100) -> str:
        """Extract context around a keyword"""
        
        try:
            index = text.find(keyword)
            if index == -1:
                return ""
            
            start = max(0, index - window)
            end = min(len(text), index + len(keyword) + window)
            
            context = text[start:end].strip()
            return f"...{context}..." if start > 0 or end < len(text) else context
        except:
            return ""
    
    def _assess_severity(self, keyword: str) -> str:
        """Assess severity of a red flag keyword"""
        
        high_severity = ["fraud", "bankruptcy", "insolvency", "breach", "investigation"]
        medium_severity = ["lawsuit", "dispute", "default", "violation", "loss"]
        
        keyword_lower = keyword.lower()
        
        if any(severe in keyword_lower for severe in high_severity):
            return "high"
        elif any(medium in keyword_lower for medium in medium_severity):
            return "medium"
        else:
            return "low"
    
    def _extract_financial_metrics(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract financial metrics from document"""
        
        text = extracted_data.get("text", "")
        
        # Extract numbers with currency symbols
        currency_pattern = r'\$\s*[\d,]+(?:\.\d{2})?(?:\s*(?:million|billion|M|B))?'
        currency_values = re.findall(currency_pattern, text, re.IGNORECASE)
        
        # Extract percentages
        percentage_pattern = r'\d+(?:\.\d+)?%'
        percentages = re.findall(percentage_pattern, text)
        
        return {
            "currency_values_found": len(currency_values),
            "sample_values": currency_values[:10] if currency_values else [],
            "percentages_found": len(percentages),
            "sample_percentages": percentages[:10] if percentages else [],
            "has_financial_data": len(currency_values) > 0 or len(percentages) > 0
        }
    
    def _financial_analysis(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform financial-focused analysis"""
        
        financial_metrics = self._extract_financial_metrics(extracted_data)
        
        # For Excel files, provide additional analysis
        if extracted_data.get("type") in ["excel", "csv"]:
            sheets_data = extracted_data.get("sheets", {})
            
            financial_sheets = []
            for sheet_name, sheet_data in sheets_data.items():
                if any(keyword in sheet_name.lower() for keyword in ["income", "balance", "cash", "financial"]):
                    financial_sheets.append({
                        "name": sheet_name,
                        "rows": sheet_data.get("rows"),
                        "columns": sheet_data.get("columns"),
                        "column_names": sheet_data.get("column_names", [])
                    })
            
            return {
                "metrics": financial_metrics,
                "financial_sheets": financial_sheets,
                "sheet_count": len(financial_sheets),
                "has_financial_statements": len(financial_sheets) > 0
            }
        
        return {
            "metrics": financial_metrics
        }
    
    def _extract_key_entities(self, text: str) -> Dict[str, Any]:
        """Extract key entities (companies, people, dates)"""
        
        # Extract dates (basic pattern)
        date_pattern = r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})\b'
        dates = re.findall(date_pattern, text, re.IGNORECASE)
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        # Extract capitalized words (potential company/person names)
        capitalized_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        capitalized = re.findall(capitalized_pattern, text)
        
        return {
            "dates_found": len(dates),
            "sample_dates": dates[:10] if dates else [],
            "emails_found": len(emails),
            "sample_emails": emails[:5] if emails else [],
            "capitalized_entities": len(capitalized),
            "sample_entities": list(set(capitalized))[:20] if capitalized else []
        }
    
    def _generate_recommendation(
        self,
        red_flags: Dict[str, Any],
        positive_signals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate investment recommendation based on analysis"""
        
        flag_count = red_flags.get("total_flags", 0)
        signal_count = positive_signals.get("total_signals", 0)
        
        # Simple scoring system
        score = signal_count - (flag_count * 2)  # Red flags weighted more heavily
        
        if score > 10:
            recommendation = "Strong Buy"
            confidence = "High"
        elif score > 5:
            recommendation = "Buy"
            confidence = "Medium"
        elif score > 0:
            recommendation = "Hold"
            confidence = "Medium"
        elif score > -5:
            recommendation = "Caution"
            confidence = "Medium"
        else:
            recommendation = "Avoid"
            confidence = "High"
        
        return {
            "recommendation": recommendation,
            "confidence": confidence,
            "score": score,
            "reasoning": f"Based on {signal_count} positive signals and {flag_count} red flags detected"
        }
    
    def analyze_multiple_documents(
        self,
        file_paths: List[Path],
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Analyze multiple documents and generate consolidated report"""
        
        results = []
        total_red_flags = 0
        total_positive_signals = 0
        
        for file_path in file_paths:
            analysis = self.analyze_document(file_path, analysis_type)
            results.append(analysis)
            
            if analysis.get("success"):
                analysis_data = analysis.get("analysis", {})
                if "red_flags" in analysis_data:
                    total_red_flags += analysis_data["red_flags"].get("total_flags", 0)
                if "positive_signals" in analysis_data:
                    total_positive_signals += analysis_data["positive_signals"].get("total_signals", 0)
        
        return {
            "success": True,
            "documents_analyzed": len(file_paths),
            "analysis_type": analysis_type,
            "results": results,
            "consolidated_summary": {
                "total_red_flags": total_red_flags,
                "total_positive_signals": total_positive_signals,
                "overall_score": total_positive_signals - (total_red_flags * 2),
                "documents_with_issues": sum(1 for r in results if r.get("analysis", {}).get("red_flags", {}).get("has_red_flags", False))
            }
        }
