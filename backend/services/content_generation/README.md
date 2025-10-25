# Content Generation Service

**Status**: 📦 Placeholder (Feature 5)

## Purpose
Auto-generate investment memos and pitch decks.

## Components

### `memo_generator.py` 📦
- `MemoGenerator` - Generate complete memos
- Section drafting with LLM
- Data aggregation from all sources

### `deck_generator.py` 📦
- `DeckGenerator` - Create PowerPoint presentations
- Slide layout and formatting
- Chart and visualization generation

### `section_drafter.py` 📦
- `SectionDrafter` - Draft individual memo sections
- Executive summary generation
- Investment thesis articulation

### `formatter.py` 📦
- `DocumentFormatter` - Apply consistent styling
- Export to Word/PowerPoint/PDF
- Template application

## Reuses
- ✅ `InvestmentAnalystAgent` - Draft sections with LLM
- 🔄 Financial Models - From Feature 4
- 🔄 Market Analysis - From Feature 3
- 🔄 DD Analysis - From Feature 2

## Usage (Planned)
```python
from services.content_generation import MemoGenerator

generator = MemoGenerator(llm_agent)
memo = await generator.generate_memo(
    company_data, analysis_data, financial_data, market_data
)
```
