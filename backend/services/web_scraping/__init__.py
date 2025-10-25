"""
Web Scraping Services - Feature 1: AI-Powered Deal Sourcing

This module handles web scraping from various sources:
- Accelerators (Y Combinator, TechStars, 500 Startups)
- Funding platforms (Crunchbase, AngelList, PitchBook)
- News sources for funding announcements
"""

from .scraper_base import BaseScraper
from .accelerator_scrapers import YCombinatorScraper, TechStarsScraper
from .funding_platform_scrapers import CrunchbaseScraper, AngelListScraper
from .news_scrapers import NewsAggregator

__all__ = [
    'BaseScraper',
    'YCombinatorScraper',
    'TechStarsScraper',
    'CrunchbaseScraper',
    'AngelListScraper',
    'NewsAggregator'
]
