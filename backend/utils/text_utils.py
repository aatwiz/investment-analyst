"""
Text utility functions for document processing.
"""
from typing import List


def split_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> List[str]:
    """
    Split text into overlapping chunks for better embedding coverage.
    Inspired by open-notebook's text splitting approach.
    
    Args:
        text: The text to split
        chunk_size: Target size of each chunk in characters
        chunk_overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text or len(text) == 0:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        # Calculate end position
        end = start + chunk_size
        
        # If this is not the last chunk and we're not at a space,
        # try to break at a word boundary
        if end < text_length:
            # Look for a space within the last 50 characters
            space_pos = text.rfind(' ', end - 50, end)
            if space_pos != -1 and space_pos > start:
                end = space_pos
        
        # Extract chunk
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - chunk_overlap if end < text_length else end
        
        # Prevent infinite loop if chunk_size is very small
        if start <= (end - chunk_size + chunk_overlap):
            start = end
    
    return chunks


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and special characters.
    
    Args:
        text: The text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Replace multiple whitespace with single space
    text = ' '.join(text.split())
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    return text.strip()


def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: The text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
