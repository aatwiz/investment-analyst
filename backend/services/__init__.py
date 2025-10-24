"""
Services Module

Organized service layer with subdirectories for different capabilities:
- document_analysis: Analysis, red flags, recommendations
- file_processing: Document extraction and processing
- llm_agents: LLM-powered agents (coming soon)
- data_extraction: Structured data extraction
"""

from .document_analysis import DocumentAnalyzer
from .file_processing import FileProcessor

__all__ = ["DocumentAnalyzer", "FileProcessor"]
