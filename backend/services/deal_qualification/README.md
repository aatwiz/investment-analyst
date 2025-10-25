# Deal Qualification Service

**Status**: 📦 Placeholder (Feature 1)

## Purpose
Qualify investment opportunities using scoring engine and LLM evaluation.

## Components

### `scoring_engine.py` 📦
- `DealScoringEngine` - Score deals against criteria
- `ScoringCriteria` - Define qualification criteria
- Integration with LLM for qualitative assessment

### `deduplication.py` 📦
- `CompanyDeduplicator` - Find duplicate companies
- Fuzzy name matching
- URL/domain comparison
- Intelligent merging

### `profile_builder.py` 📦
- `CompanyProfileBuilder` - Build comprehensive profiles
- Aggregate data from multiple sources
- External API enrichment
- Profile validation

## Reuses
- ✅ `InvestmentAnalystAgent` - For LLM-powered qualification
- ✅ `DocumentAnalyzer` - For risk screening

## Usage (Planned)
```python
from services.deal_qualification import DealScoringEngine

engine = DealScoringEngine(criteria)
score = await engine.score_deal(company_data)
```
