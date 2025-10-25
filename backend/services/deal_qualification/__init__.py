"""
Deal Qualification Services - Feature 1: AI-Powered Deal Sourcing

This module handles:
- Deal scoring and qualification
- Company deduplication
- Profile building and enrichment
"""

from .scoring_engine import DealScoringEngine
from .deduplication import CompanyDeduplicator
from .profile_builder import CompanyProfileBuilder

__all__ = [
    'DealScoringEngine',
    'CompanyDeduplicator',
    'CompanyProfileBuilder'
]
