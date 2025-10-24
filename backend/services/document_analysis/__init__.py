"""
Document Analysis Service

This service provides comprehensive document analysis capabilities for due diligence,
including red flag detection, positive signal identification, financial metrics extraction,
and investment recommendations.

Tomorrow: LLM-powered analysis agents will be integrated here.
"""

from .document_analyzer import DocumentAnalyzer

__all__ = ["DocumentAnalyzer"]
