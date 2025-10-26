#!/usr/bin/env python3
"""
Script to remove emojis and add source references to frontend/app.py
This version uses targeted replacements to avoid formatting issues.
"""
import re

def remove_emojis_from_text(text):
    """Remove all emojis from text using comprehensive Unicode ranges."""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub('', text)

def clean_extra_spaces(text):
    """Clean up extra spaces left after emoji removal."""
    # Fix multiple spaces
    text = re.sub(r'  +', ' ', text)
    # Fix space at start of quotes
    text = re.sub(r'"\s+([A-Z])', r'"\1', text)
    # Fix space after opening quote in navigation
    text = re.sub(r'label="\s+', r'label="', text)
    # Fix markdown headers with extra spaces
    text = re.sub(r'###\s\s+', r'### ', text)
    text = re.sub(r'##\s\s+', r'## ', text)
    # Fix leading spaces in navigation items
    text = re.sub(r'label="\s+', 'label="', text)
    return text

def add_source_references(content):
    """Add source reference sections after each market intelligence section."""
    
    # 1. After Market Overview
    content = re.sub(
        r'(st\.info\(data\[\'market_overview\'\]\))',
        r'\1\n\n        # Show sources for market overview\n        if data.get(\'sources\') and data[\'sources\'].get(\'market_overview\'):\n            with st.expander("📚 Sources & References"):\n                for i, source in enumerate(data[\'sources\'][\'market_overview\'], 1):\n                    st.caption(f"{i}. {source}")',
        content
    )
    
    # 2. After Key Trends
    content = re.sub(
        r'(for trend in data\[\'trends\'\]:\n\s+st\.write\(f"• \{trend\}"\))',
        r'\1\n\n        # Show sources for trends\n        if data.get(\'sources\') and data[\'sources\'].get(\'trends\'):\n            with st.expander("📚 Sources & References"):\n                for i, source in enumerate(data[\'sources\'][\'trends\'], 1):\n                    st.caption(f"{i}. {source}")',
        content
    )
    
    # 3. After Competitive Position
    content = re.sub(
        r'(for competitor in data\[\'competitors\'\]:\n\s+st\.write\(f"• \{competitor\}"\))',
        r'\1\n\n        # Show sources for competitors\n        if data.get(\'sources\') and data[\'sources\'].get(\'competitors\'):\n            with st.expander("📚 Sources & References"):\n                for i, source in enumerate(data[\'sources\'][\'competitors\'], 1):\n                    st.caption(f"{i}. {source}")',
        content
    )
    
    # 4. After Opportunities
    content = re.sub(
        r'(for opp in data\[\'opportunities\'\]:\n\s+st\.write\(f"• \{opp\}"\))',
        r'\1\n\n            # Show sources for opportunities\n            if data.get(\'sources\') and data[\'sources\'].get(\'opportunities\'):\n                with st.expander("📚 Sources & References"):\n                    for i, source in enumerate(data[\'sources\'][\'opportunities\'], 1):\n                        st.caption(f"{i}. {source}")',
        content
    )
    
    # 5. After Threats  
    content = re.sub(
        r'(for threat in data\[\'threats\'\]:\n\s+st\.write\(f"• \{threat\}"\))',
        r'\1\n\n            # Show sources for threats\n            if data.get(\'sources\') and data[\'sources\'].get(\'threats\'):\n                with st.expander("📚 Sources & References"):\n                    for i, source in enumerate(data[\'sources\'][\'threats\'], 1):\n                        st.caption(f"{i}. {source}")',
        content
    )
    
    # 6. After Key Drivers
    content = re.sub(
        r'(for driver in data\[\'key_drivers\'\]:\n\s+st\.write\(f"• \{driver\}"\))',
        r'\1\n\n        # Show sources for key drivers\n        if data.get(\'sources\') and data[\'sources\'].get(\'key_drivers\'):\n            with st.expander("📚 Sources & References"):\n                for i, source in enumerate(data[\'sources\'][\'key_drivers\'], 1):\n                    st.caption(f"{i}. {source}")',
        content
    )
    
    # 7. After Regulatory Environment
    content = re.sub(
        r'(st\.info\(data\[\'regulatory_environment\'\]\))',
        r'\1\n\n        # Show sources for regulatory environment\n        if data.get(\'sources\') and data[\'sources\'].get(\'regulatory_environment\'):\n            with st.expander("📚 Sources & References"):\n                for i, source in enumerate(data[\'sources\'][\'regulatory_environment\'], 1):\n                    st.caption(f"{i}. {source}")',
        content
    )
    
    return content

def main():
    filepath = 'frontend/app.py'
    
    print("Reading file...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Removing emojis...")
    content = remove_emojis_from_text(content)
    
    print("Cleaning up extra spaces...")
    content = clean_extra_spaces(content)
    
    print("Adding source references...")
    content = add_source_references(content)
    
    print("Writing updated file...")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Successfully updated frontend/app.py")
    print("   - Removed all emojis")
    print("   - Added source references to 7 market intelligence sections")

if __name__ == "__main__":
    main()
