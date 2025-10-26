#!/usr/bin/env python3
"""
Script to remove all emojis from frontend/app.py and add references to market intelligence
"""
import re
import sys

def remove_emojis(text):
    """Remove all emojis from text"""
    # Comprehensive emoji pattern
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "]+", flags=re.UNICODE)
    
    return emoji_pattern.sub('', text)

def main():
    file_path = 'frontend/app.py'
    
    print(f"Reading {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Removing emojis...")
    cleaned_content = remove_emojis(content)
    
    # Additional cleanup for common emoji patterns in strings
    cleaned_content = re.sub(r'\s+""', '""', cleaned_content)  # Remove extra spaces before closing quotes
    cleaned_content = re.sub(r'""\s+', '""', cleaned_content)  # Remove extra spaces after opening quotes
    
    print(f"Writing cleaned content to {file_path}...")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    print("✓ Emojis removed successfully!")
    print("\nNote: Please review the file and manually adjust any formatting issues.")

if __name__ == "__main__":
    main()
