"""
Web Scraping Services - Feature 1: AI-Powered Deal Sourcing

This module handles web scraping from various sources:
- Funding platforms (Crunchbase, AngelList, PitchBook)
- MENA platforms (Magnitt, Wamda)
- News sources (Bloomberg)
"""

from .base_scraper import BaseScraper
from .crunchbase_scraper import CrunchbaseScraper
from .angellist_scraper import AngelListScraper
from .bloomberg_scraper import BloombergScraper
from .magnitt_scraper import MagnittScraper
from .wamda_scraper import WamdaScraper
from .pitchbook_scraper import PitchBookScraper

__all__ = [
    'BaseScraper',
    'CrunchbaseScraper',
    'AngelListScraper',
    'BloombergScraper',
    'MagnittScraper',
    'WamdaScraper',
    'PitchBookScraper',
]
