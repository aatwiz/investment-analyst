"""
External Data Services - Feature 3: Market & Competitive Analysis

Handles integration with external APIs and data enrichment.
"""

from .news_aggregator import NewsAggregator
from .api_integrations import ExternalAPIManager
from .data_enrichment import DataEnricher

__all__ = [
    'NewsAggregator',
    'ExternalAPIManager',
    'DataEnricher'
]
