# Investment Analyst AI - Master Guide 📘

**Last Updated:** October 25, 2025  
**Status:** Core Platform Complete ✅ | Ready for Feature Integration 🚀

---

## 🎯 What We Have Built

### ✅ Core Infrastructure (Complete)

**1. Document Analysis Pipeline**
- Multi-format processing (PDF, Word, Excel, CSV, PowerPoint)
- LLM-powered analysis with GPT-4o-mini ($0.025/doc)
- Accurate financial statement comprehension (fixed keyword bias issue)
- Risk scoring, investment recommendations, opportunity analysis

**2. Cost-Efficient Querying System**
- RAG (Retrieval-Augmented Generation) agent
- Vector search with pgvector
- 8x cheaper than full analysis ($0.0003 vs $0.025 per query)
- 15x faster (2s vs 30s)

**3. Database & Storage**
- PostgreSQL 16 with pgvector extension
- Document embeddings (500-char chunks)
- Analysis results caching
- Full-text search ready

**4. API Endpoints**
- `POST /api/v1/analysis/analyze` - Full document analysis
- `POST /api/v1/query/ask` - RAG-based queries
- `POST /api/v1/query/batch` - Multiple queries
- `POST /api/v1/query/chat` - Conversational interface
- `POST /api/v1/files/upload` - File upload
- `POST /api/v1/search/semantic` - Vector search

---

## 💡 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    DOCUMENT UPLOAD                          │
└─────────────────────────────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
        ┌───────▼────────┐       ┌───────▼────────┐
        │ FileProcessor  │       │ EmbeddingService│
        │ (Extract Text) │       │ (Chunk & Embed) │
        └───────┬────────┘       └───────┬─────────┘
                │                        │
                │                        ▼
                │              [document_embeddings]
                │              500-char chunks
                │              Ready for RAG queries
                │
        ┌───────▼──────────────┐
        │ InvestmentAnalystAgent│
        │ (GPT-4o-mini Analysis)│
        └───────┬───────────────┘
                │
                ▼
        [analyses table]
        Cached forever
        
┌─────────────────────────────────────────────────────────────┐
│                    USER QUERIES                             │
└─────────────────────────────────────────────────────────────┘
                             │
                   ┌─────────▼─────────┐
                   │   RAGQueryAgent   │
                   └─────────┬─────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
         Vector Search   Build Context  LLM Answer
         (0.1s)         (chunks only)   (2s)
                │            │            │
                └────────────┴────────────┘
                             │
                         Response
                      ($0.0003, 2s)
```

---

## 🚀 Next Features to Build

### Feature 1: Company Management
**Goal:** Track investment targets and their data

**What to Build:**
```python
# backend/api/routes/companies.py
@router.post("/companies")
async def create_company(name, industry, stage, website, ...):
    """Create company profile"""
    
@router.get("/companies/{id}")
async def get_company(id):
    """Get company details + all linked documents/analyses"""
    
@router.put("/companies/{id}")
async def update_company(id, updates):
    """Update company information"""
    
@router.get("/companies")
async def list_companies(filters):
    """List companies with filtering"""
```

**Database Model:**
```python
# backend/models/company.py
class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    industry = Column(String)
    stage = Column(String)  # Seed, Series A, B, C, etc.
    website = Column(String)
    description = Column(Text)
    founded_year = Column(Integer)
    employee_count = Column(Integer)
    
    # Relationships
    documents = relationship("Document", back_populates="company")
    analyses = relationship("Analysis", back_populates="company")
    financial_models = relationship("FinancialModel")
    memos = relationship("InvestmentMemo")
```

**Leverage Existing:**
- Use RAGQueryAgent to answer "Tell me about Company X" across all their docs
- Link Document.company_id to companies table
- Auto-populate company info from analyzed documents

---

### Feature 3: Market Research
**Goal:** Generate market intelligence and competitive analysis

**What to Build:**
```python
# backend/api/routes/market.py
@router.post("/market/analyze")
async def analyze_market(industry, geography, company_ids):
    """
    Generate market analysis using:
    1. RAG search across all documents for market mentions
    2. LLM to synthesize market size, trends, competitors
    3. Return structured market report
    """
    
@router.get("/market/competitors")
async def get_competitors(company_id):
    """Find competitors mentioned in documents"""
    
@router.post("/market/trends")
async def identify_trends(industry, timeframe):
    """Extract trends from document corpus"""
```

**Implementation Pattern:**
```python
# backend/services/llm_agents/market_analyst_agent.py
class MarketAnalystAgent:
    def __init__(self):
        self.rag_agent = RAGQueryAgent()
        self.client = AsyncOpenAI()
    
    async def analyze_market(self, industry: str, docs: List[int]):
        # Step 1: RAG search for market-related content
        market_context = await self.rag_agent.answer_query(
            query=f"What is the market size and growth for {industry}?",
            document_ids=docs,
            max_chunks=10
        )
        
        # Step 2: Search for competitors
        competitors = await self.rag_agent.answer_query(
            query=f"Who are the main competitors in {industry}?",
            document_ids=docs
        )
        
        # Step 3: LLM synthesis
        prompt = f"""
        Analyze this market intelligence:
        
        Market Context: {market_context['answer']}
        Competitors: {competitors['answer']}
        
        Generate:
        1. Market size estimate
        2. Growth trends
        3. Key players and market share
        4. Entry barriers
        5. Opportunities and threats
        """
        
        analysis = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "market_overview": analysis.choices[0].message.content,
            "sources": market_context['sources'] + competitors['sources']
        }
```

**Leverage Existing:**
- RAGQueryAgent for information retrieval
- Document embeddings for finding relevant market data
- Same LLM patterns as InvestmentAnalystAgent

---

### Feature 4: Financial Modeling
**Goal:** Build financial projections and scenarios

**What to Build:**
```python
# backend/api/routes/financial.py
@router.post("/financial/extract")
async def extract_financials(document_id):
    """
    Extract financial data from documents:
    - Revenue, costs, profit over time
    - Use RAG to find financial tables
    - Parse and structure the data
    """
    
@router.post("/financial/project")
async def create_projection(company_id, assumptions):
    """
    Generate 3-5 year projections:
    - Use historical data from documents
    - Apply growth assumptions
    - Calculate metrics (CAC, LTV, unit economics)
    """
    
@router.post("/financial/scenarios")
async def run_scenarios(model_id, scenarios):
    """
    Run what-if scenarios:
    - Best case, base case, worst case
    - Sensitivity analysis
    - Return comparison tables
    """
```

**Database Model:**
```python
class FinancialModel(Base):
    __tablename__ = "financial_models"
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    model_type = Column(String)  # projection, scenario, valuation
    assumptions = Column(JSON)
    projections = Column(JSON)  # {year: {revenue, costs, ...}}
    metrics = Column(JSON)      # {cac, ltv, burn_rate, ...}
    created_at = Column(DateTime)
```

**Implementation:**
```python
# backend/services/llm_agents/financial_analyst_agent.py
class FinancialAnalystAgent:
    async def extract_financials(self, doc_id: int):
        # Use RAG to find financial data
        queries = [
            "What was the revenue for the past 3 years?",
            "What are the main cost categories?",
            "What is the cash burn rate?"
        ]
        
        financial_data = {}
        for query in queries:
            result = await rag_agent.answer_query(
                query=query,
                document_ids=[doc_id],
                max_chunks=5
            )
            financial_data[query] = result['answer']
        
        # LLM to structure the data
        structured = await self.structure_financials(financial_data)
        return structured
    
    async def create_projection(self, historical, assumptions):
        # LLM-powered projection logic
        # Apply growth rates, calculate metrics
        # Return structured forecast
        pass
```

**Leverage Existing:**
- RAGQueryAgent to extract financial data from documents
- LLM to parse and structure numbers
- Save models to database, reuse for scenarios

---

### Feature 5: Investment Memos
**Goal:** Auto-generate professional investment memos

**What to Build:**
```python
# backend/api/routes/memos.py
@router.post("/memos/generate")
async def generate_memo(company_id, include_sections):
    """
    Generate investment memo by pulling:
    1. Company info from companies table
    2. Analysis from analyses table
    3. Market research from market analysis
    4. Financial projections from financial_models
    5. Use LLM to write coherent memo
    """
    
@router.get("/memos/{id}")
async def get_memo(id):
    """Retrieve saved memo"""
    
@router.put("/memos/{id}")
async def update_memo(id, edits):
    """Edit memo sections"""
```

**Implementation:**
```python
# backend/services/llm_agents/memo_writer_agent.py
class MemoWriterAgent:
    async def generate_memo(self, company_id: int):
        # Step 1: Gather all data
        company = await db.get(Company, company_id)
        analyses = await db.query(Analysis).filter_by(company_id=company_id).all()
        market = await db.query(MarketAnalysis).filter_by(company_id=company_id).first()
        financials = await db.query(FinancialModel).filter_by(company_id=company_id).first()
        
        # Step 2: Build comprehensive prompt
        prompt = f"""
        Write a professional investment memo for {company.name}.
        
        ## Company Overview
        {company.description}
        Industry: {company.industry}
        Stage: {company.stage}
        
        ## Due Diligence Analysis
        {analyses[0].result_data['executive_summary']}
        Risk Score: {analyses[0].result_data['risk_assessment']['score']}/10
        Recommendation: {analyses[0].result_data['recommendation']['action']}
        
        ## Market Analysis
        {market.market_overview if market else 'Not available'}
        
        ## Financial Projections
        {json.dumps(financials.projections) if financials else 'Not available'}
        
        Generate a memo with these sections:
        1. Executive Summary
        2. Investment Thesis
        3. Company Background
        4. Market Opportunity
        5. Financial Overview
        6. Risk Assessment
        7. Recommendation
        
        Use professional investment memo style.
        """
        
        memo_content = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        # Save to database
        memo = InvestmentMemo(
            company_id=company_id,
            content=memo_content.choices[0].message.content,
            sections=self.parse_sections(memo_content)
        )
        await db.save(memo)
        
        return memo
```

**Leverage Existing:**
- All data already collected from previous features
- LLM synthesis with same patterns
- RAGQueryAgent to pull additional details if needed

---

## 💰 Cost Considerations

### Current Costs (Monthly, 1000 docs, 10K queries)

| Operation | Cost per Call | Monthly Volume | Monthly Cost |
|-----------|--------------|----------------|--------------|
| Initial Analysis | $0.025 | 1,000 docs | $25 |
| RAG Queries | $0.0003 | 10,000 queries | $3 |
| Market Analysis | $0.010 | 100 reports | $1 |
| Financial Modeling | $0.005 | 200 models | $1 |
| Memo Generation | $0.020 | 50 memos | $1 |
| **TOTAL** | - | - | **~$31/month** |

**Key Insight:** RAG queries are 8x cheaper than full analysis, use them wherever possible!

---

## 🔧 Development Patterns

### Pattern 1: Create New LLM Agent
```python
# backend/services/llm_agents/your_agent.py
from openai import AsyncOpenAI
from services.llm_agents.rag_agent import RAGQueryAgent

class YourAgent:
    def __init__(self):
        self.client = AsyncOpenAI()
        self.rag_agent = RAGQueryAgent(session)
        self.model = "gpt-4o-mini"
    
    async def do_something(self, input_data):
        # 1. Use RAG to gather context if needed
        context = await self.rag_agent.answer_query(
            query="Your search query",
            document_ids=[...],
            max_chunks=5
        )
        
        # 2. Build prompt
        prompt = f"Your task... Context: {context['answer']}"
        
        # 3. Get LLM response
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        return response.choices[0].message.content
```

### Pattern 2: Create New API Route
```python
# backend/api/routes/your_feature.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_db

router = APIRouter(prefix="/your-feature", tags=["your-feature"])

@router.post("/action")
async def your_action(
    input: YourModel,
    db: AsyncSession = Depends(get_db)
):
    # Use your agent
    agent = YourAgent(db)
    result = await agent.do_something(input)
    
    # Save to database if needed
    await db.save(...)
    
    return result
```

### Pattern 3: Add Database Model
```python
# backend/models/your_model.py
from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from config.database import Base

class YourModel(Base):
    __tablename__ = "your_table"
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## 📋 Quick Start Commands

```bash
# Start everything
./scripts/start_all.sh

# Backend only
cd backend && uvicorn main:app --reload

# Frontend only
streamlit run frontend/app.py

# Database
docker-compose up postgres

# Run migrations
alembic upgrade head

# Test analysis
curl -X POST http://localhost:8000/api/v1/analysis/analyze \
  -H "Content-Type: application/json" \
  -d '{"filename": "doc.pdf", "analysis_type": "comprehensive"}'

# Test RAG query
curl -X POST http://localhost:8000/api/v1/query/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the revenue?", "max_chunks": 5}'
```

---

## 🎯 Implementation Priority

**Week 1: Feature 1 (Companies)**
- Create companies table and model
- Build CRUD endpoints
- Link documents to companies
- Test with RAG queries

**Week 2: Feature 3 (Market Research)**
- Create MarketAnalystAgent
- Market analysis endpoints
- Store results in database
- Generate first market report

**Week 3: Feature 4 (Financial Modeling)**
- Create FinancialAnalystAgent
- Financial extraction logic
- Projection engine
- Scenario comparison

**Week 4: Feature 5 (Investment Memos)**
- Create MemoWriterAgent
- Pull all data sources
- Generate professional memos
- Add editing capabilities

---

## 📚 Key Files Reference

**Core Services:**
- `backend/services/llm_agents/investment_analyst_agent.py` - Document analysis
- `backend/services/llm_agents/rag_agent.py` - Efficient querying
- `backend/services/file_processing/file_processor.py` - Document extraction
- `backend/services/embeddings/embedding_service.py` - Vector embeddings

**API Routes:**
- `backend/api/routes/analysis.py` - Analysis endpoints
- `backend/api/routes/query.py` - Query endpoints
- `backend/api/routes/files.py` - File upload
- `backend/api/routes/search.py` - Search endpoints

**Database:**
- `backend/models/document.py` - Document model
- `backend/models/analysis.py` - Analysis model
- `backend/config/database.py` - Database config

---

## 💡 Tips & Best Practices

1. **Always use RAG for queries** - 8x cheaper than full analysis
2. **Cache everything** - Check database before calling LLM
3. **Batch operations** - Process multiple items in parallel
4. **Use async/await** - FastAPI is async, leverage it
5. **Structure LLM output** - Use JSON mode for consistent results
6. **Track costs** - Add cost tracking to all LLM calls
7. **Test with real data** - Use actual financial documents
8. **Leverage existing** - Reuse RAGQueryAgent, don't duplicate code

---

**Status:** ✅ Core platform complete and cost-optimized  
**Next:** Build Features 1, 3, 4, 5 using established patterns  
**Cost:** ~$31/month for production workload  
**Speed:** 2s avg query response, 30s full analysis
