# Feature 1: AI-Powered Deal Sourcing

## Overview

Automated deal sourcing system that scrapes startup funding data from 6 major platforms, deduplicates across sources, and uses AI to qualify investment opportunities.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (/api/v1/companies)            │
│  POST /scrape | GET /deals | GET /deals/{id} | POST /qualify│
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         │  DealSourcingManager      │
         │  - Orchestration          │
         │  - Deduplication          │
         │  - Filtering & Ranking    │
         └──────┬────────────────────┘
                │
    ┌───────────┴───────────┐
    │   Platform Scrapers   │
    ├───────────────────────┤
    │  • Crunchbase (API)   │
    │  • AngelList (Web)    │
    │  • Bloomberg (News)   │
    │  • Magnitt (MENA)     │
    │  • Wamda (MENA)       │
    │  • PitchBook (API)    │
    └───────────────────────┘
                │
    ┌───────────┴───────────┐
    │    DealQualifier      │
    │  GPT-4o-mini Scoring  │
    │  6 Dimensions:        │
    │  - Market             │
    │  - Team               │
    │  - Product            │
    │  - Traction           │
    │  - Financials         │
    │  - Strategic Fit      │
    └───────────────────────┘
```

## Components

### 1. Platform Scrapers

#### Base Scraper (`base_scraper.py`)
Abstract class providing:
- Rate limiting (configurable req/sec)
- HTTP retries with exponential backoff
- User agent rotation (3 agents)
- HTML parsing with BeautifulSoup
- Standard deal schema normalization
- Async context manager support

#### Platform-Specific Scrapers

**Crunchbase** (`crunchbase_scraper.py`)
- API v4 integration
- Requires: `CRUNCHBASE_API_KEY`
- Searches funding rounds with filters
- Fetches detailed company information
- Autocomplete search support

**AngelList** (`angellist_scraper.py`)
- Web scraping (no public API)
- JSON extraction from page data
- HTML parsing fallback
- Conservative rate limiting (3 sec)

**Bloomberg** (`bloomberg_scraper.py`)
- Technology news section scraping
- Funding announcement detection
- Public content only (paywall limits)
- News article parsing

**Magnitt** (`magnitt_scraper.py`)
- MENA region focus
- Startup profiles and funding
- Industry and location filtering

**Wamda** (`wamda_scraper.py`)
- MENA ecosystem coverage
- Funding news articles
- Company name and amount extraction

**PitchBook** (`pitchbook_scraper.py`)
- API template (requires paid access)
- Requires: `PITCHBOOK_API_KEY`
- Enterprise-grade data
- Company profiles and deals

### 2. Deal Sourcing Manager (`deal_sourcing_manager.py`)

Orchestrates the entire scraping process:

```python
manager = DealSourcingManager()

# Scrape from multiple platforms
deals = await manager.scrape_all_platforms(
    platforms=['crunchbase', 'magnitt', 'wamda'],
    filters={
        'industries': ['fintech', 'healthtech'],
        'locations': ['UAE', 'Saudi Arabia'],
        'min_funding': 1000000
    }
)

# Deduplicate across sources
unique_deals = manager.deduplicate_deals(deals)

# Rank by criteria
ranked = manager.rank_deals(unique_deals, criteria={
    'funding_amount': 0.3,
    'recent': 0.2,
    'stage': 0.2,
    'completeness': 0.3
})

# Generate summary stats
summary = manager.generate_summary(unique_deals)
```

**Features:**
- Concurrent scraping (asyncio)
- Fuzzy name matching for deduplication
- Company name normalization
- Deal merging across sources
- Configurable ranking criteria
- Filtering by multiple dimensions
- Summary statistics generation

### 3. Deal Qualifier (`deal_qualification/qualifier.py`)

AI-powered deal scoring using GPT-4o-mini:

```python
qualifier = DealQualifier()

# Qualify single deal
result = await qualifier.qualify_deal(deal, context={
    'target_industries': ['fintech'],
    'target_stages': ['Series A', 'Series B'],
    'geographic_focus': ['MENA']
})

# Result structure:
{
    'score': 85.5,  # Overall 0-100
    'recommendation': 'Strong Pass',  # Pass/Strong Pass/Review/Reject
    'scores': {
        'market_opportunity': 90,
        'team': 85,
        'product': 80,
        'traction': 85,
        'financials': 75,
        'strategic_fit': 95
    },
    'strengths': ['Strong market', 'Experienced team'],
    'concerns': ['Limited traction'],
    'analysis': 'Detailed narrative...'
}
```

**Scoring Dimensions (Weights):**
- Market Opportunity (25%): Size, growth, competition, timing
- Team (20%): Experience, track record, execution ability
- Product (20%): Innovation, differentiation, scalability
- Traction (20%): Revenue, users, growth rate, unit economics
- Financials (10%): Burn rate, runway, capital efficiency
- Strategic Fit (5%): Thesis alignment, portfolio synergies

**Recommendations:**
- **Strong Pass** (≥80): High-priority opportunity
- **Pass** (65-79): Solid opportunity worth pursuing
- **Review** (50-64): Requires deeper analysis
- **Reject** (<50 or red flag): Pass on opportunity

### 4. API Endpoints (`api/routes/companies.py`)

#### POST `/api/v1/companies/scrape`
Trigger multi-platform scraping with qualification:

```bash
curl -X POST http://localhost:8000/api/v1/companies/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "platforms": ["crunchbase", "magnitt"],
    "filters": {
      "industries": ["fintech", "healthtech"],
      "locations": ["UAE", "Saudi Arabia"],
      "min_funding": 1000000
    },
    "qualify": true,
    "min_score": 60.0
  }'
```

Response:
```json
{
  "success": true,
  "summary": {
    "total_scraped": 150,
    "unique_companies": 98,
    "qualified_deals": 45,
    "total_funding": 2450000000,
    "avg_funding": 16333333,
    "platforms": {"Crunchbase": 75, "Magnitt": 75},
    "top_industries": {"Fintech": 30, "HealthTech": 15},
    "top_locations": {"UAE": 40, "Saudi Arabia": 5}
  },
  "deals": [...],  // Top 20 qualified deals
  "message": "Successfully scraped 98 unique deals"
}
```

#### GET `/api/v1/companies/deals`
List deals with filtering and pagination:

```bash
curl "http://localhost:8000/api/v1/companies/deals?\
industries=fintech,healthtech&\
min_score=70&\
stages=Series%20A&\
limit=20&\
offset=0"
```

Query Parameters:
- `platforms`: Comma-separated platform names
- `industries`: Comma-separated industries
- `locations`: Comma-separated locations
- `stages`: Comma-separated funding stages
- `min_funding`: Minimum funding amount
- `max_funding`: Maximum funding amount
- `min_score`: Minimum qualification score
- `recommendations`: Comma-separated recommendations
- `limit`: Max results (default 50, max 200)
- `offset`: Pagination offset

#### GET `/api/v1/companies/deals/{id}`
Get detailed deal information:

```bash
curl http://localhost:8000/api/v1/companies/deals/123
```

#### POST `/api/v1/companies/qualify`
Qualify or re-qualify deals:

```bash
curl -X POST http://localhost:8000/api/v1/companies/qualify \
  -H "Content-Type: application/json" \
  -d '{
    "deal_ids": [1, 2, 3],
    "context": {
      "target_industries": ["fintech", "healthtech"],
      "target_stages": ["Series A", "Series B"],
      "geographic_focus": ["MENA"]
    },
    "min_score": 60.0
  }'
```

#### GET `/api/v1/companies/stats`
Get pipeline statistics:

```bash
curl http://localhost:8000/api/v1/companies/stats
```

#### DELETE `/api/v1/companies/deals/{id}`
Remove a deal:

```bash
curl -X DELETE http://localhost:8000/api/v1/companies/deals/123
```

## Standard Deal Schema

All scrapers normalize to this schema:

```python
{
    'name': str,              # Company name
    'description': str,       # Brief description
    'website': str,           # Company website
    'industry': str,          # Industry/sector
    'stage': str,             # Funding stage (Seed, Series A, etc.)
    'location': str,          # Geographic location
    'founded_year': int,      # Year founded
    'funding_amount': float,  # Latest funding amount (USD)
    'funding_date': str,      # Date of latest funding
    'investors': list,        # List of investor names
    'total_funding': float,   # Total funding to date (USD)
    'employee_count': str,    # Number of employees
    'source': str,            # Platform name
    'source_url': str,        # Direct link to deal
    'scraped_at': str,        # ISO timestamp
    'raw_data': dict          # Original platform data
}
```

## Setup & Configuration

### Environment Variables

Required:
```bash
# OpenAI for deal qualification
OPENAI_API_KEY=sk-...

# Platform API keys (optional but recommended)
CRUNCHBASE_API_KEY=...       # For Crunchbase scraper
PITCHBOOK_API_KEY=...        # For PitchBook scraper
```

### Installation

```bash
# Install dependencies
pip install aiohttp beautifulsoup4 openai loguru

# Or use requirements.txt
pip install -r requirements.txt
```

### Usage Examples

#### Basic Scraping

```python
from backend.services.web_scraping import DealSourcingManager

manager = DealSourcingManager()

# Scrape from all platforms
deals = await manager.scrape_all_platforms()

# Scrape specific platforms
deals = await manager.scrape_all_platforms(
    platforms=['crunchbase', 'magnitt']
)

# With filters
deals = await manager.scrape_all_platforms(
    platforms=['crunchbase', 'angellist'],
    filters={
        'industries': ['fintech'],
        'min_funding': 5_000_000
    }
)
```

#### Deal Qualification

```python
from backend.services.deal_qualification import DealQualifier

qualifier = DealQualifier()

# Qualify deals
results = await qualifier.qualify_batch(deals, context={
    'target_industries': ['fintech', 'healthtech'],
    'target_stages': ['Series A', 'Series B']
})

# Filter by score
qualified = qualifier.filter_by_threshold(
    results,
    min_score=70.0,
    recommendations=['Strong Pass', 'Pass']
)
```

#### Complete Flow

```python
# 1. Scrape
manager = DealSourcingManager()
deals = await manager.scrape_all_platforms(
    platforms=['crunchbase', 'magnitt', 'wamda']
)

# 2. Deduplicate
unique_deals = manager.deduplicate_deals(deals)

# 3. Qualify
qualifier = DealQualifier()
results = await qualifier.qualify_batch(unique_deals)

# 4. Filter and rank
top_deals = qualifier.filter_by_threshold(results, min_score=70)
ranked = manager.rank_deals(
    [r['deal'] for r in top_deals],
    criteria={'funding_amount': 0.4, 'stage': 0.3, 'completeness': 0.3}
)

# 5. Get summary
summary = manager.generate_summary(ranked)
```

## Rate Limiting

Each scraper has configurable rate limiting:

```python
# Default rates
CrunchbaseScraper()      # 1 req/sec (API-based)
AngelListScraper()       # 3 req/sec (conservative)
BloombergScraper()       # 3 req/sec (public content)
MagnittScraper()         # 2 req/sec
WamdaScraper()           # 2 req/sec
PitchBookScraper()       # 2 req/sec (API-based)

# Customize rate limits
scraper = CrunchbaseScraper()
scraper.rate_limit = 2.0  # 2 seconds between requests
```

## Cost Analysis

### OpenAI Costs (GPT-4o-mini)

Per deal qualification:
- Input: ~1,000 tokens (deal info + prompt)
- Output: ~500 tokens (scores + analysis)
- Cost: ~$0.00045 per deal

Batch of 100 deals: ~$0.045

### API Costs

- **Crunchbase**: Paid subscription required (~$29-$99/month)
- **PitchBook**: Enterprise pricing (contact sales)
- **Others**: Free (web scraping)

## Performance

### Scraping Speed

- Concurrent scraping: 2-6 platforms in parallel
- ~30-60 seconds per 100 deals (varies by platform)
- Rate limiting prevents blocks

### Qualification Speed

- ~0.5-1 second per deal (GPT-4o-mini)
- Batch processing supported
- 100 deals: ~50-100 seconds

## Database Integration (TODO)

The system is ready for database integration. Add:

1. Update `Company` model with fields:
   - `source`, `source_url`, `scraped_at`
   - `qualification_score`, `recommendation`
   - `qualification_analysis`, `raw_data`

2. Implement in API endpoints (marked with TODO):
   - Store deals after scraping
   - Query from database in list/get endpoints
   - Update qualification results

## Testing

```bash
# Test scraping (requires API keys)
pytest tests/test_deal_sourcing.py

# Test qualification
pytest tests/test_deal_qualifier.py

# Test API endpoints
pytest tests/test_companies_api.py

# Manual testing with curl
./test_feature_1.sh
```

## Next Steps

1. ✅ Web scraping infrastructure (6 platforms)
2. ✅ Deal qualification engine
3. ✅ API endpoints
4. ⏳ Database models and storage
5. ⏳ Frontend UI for deal browsing
6. ⏳ Daily digest email generation
7. ⏳ Automated scheduling (cron jobs)
8. ⏳ Deal tracking and pipeline management

## Files

```
backend/
├── services/
│   ├── web_scraping/
│   │   ├── __init__.py
│   │   ├── base_scraper.py              # Abstract base (242 lines)
│   │   ├── crunchbase_scraper.py        # Crunchbase API (263 lines)
│   │   ├── angellist_scraper.py         # AngelList web (315 lines)
│   │   ├── bloomberg_scraper.py         # Bloomberg news (282 lines)
│   │   ├── magnitt_scraper.py           # Magnitt MENA (189 lines)
│   │   ├── wamda_scraper.py            # Wamda MENA (269 lines)
│   │   ├── pitchbook_scraper.py        # PitchBook API (280 lines)
│   │   └── deal_sourcing_manager.py    # Orchestration (368 lines)
│   └── deal_qualification/
│       ├── __init__.py
│       └── qualifier.py                 # AI scoring (391 lines)
└── api/
    └── routes/
        └── companies.py                 # REST API (379 lines)

Total: ~2,977 lines of code
```

## License

MIT

---

**Status**: ✅ Complete - Ready for database integration and testing
**Branch**: `1-feature-1-deal-sourcing`
**Commits**: 3 (web scraping, qualification, API)
