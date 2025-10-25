"""
Template Management - Feature 5: Investment Memo & Presentation Draft

Manage memo and presentation templates.
"""

from .memo_templates import MemoTemplateManager
from .slide_templates import SlideTemplateManager
from .branding import BrandingManager

__all__ = [
    'MemoTemplateManager',
    'SlideTemplateManager',
    'BrandingManager'
]
