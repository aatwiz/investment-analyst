"""
Market Intelligence Services - Feature 3: Market & Competitive Analysis

This module handles:
- Market size and trend analysis
- Competitor tracking
- Sentiment analysis
- Trend detection
"""

from .market_analyzer import MarketAnalyzer
from .competitor_tracker import CompetitorTracker
from .sentiment_analyzer import SentimentAnalyzer
from .trend_detector import TrendDetector

__all__ = [
    'MarketAnalyzer',
    'CompetitorTracker',
    'SentimentAnalyzer',
    'TrendDetector'
]
