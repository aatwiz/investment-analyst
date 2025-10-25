"""
Web Scraping Services - Feature 1: AI-Powered Deal Sourcing

This module handles web scraping for real funding data from TechCrunch.
"""

from .base_scraper import BaseScraper
from .techcrunch_scraper import TechCrunchScraper

__all__ = [
    'BaseScraper',
    'TechCrunchScraper',
]

