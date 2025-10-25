# PostgreSQL Database with pgvector Setup

This document explains the PostgreSQL database setup with pgvector for semantic search capabilities, inspired by the open-notebook repository's architecture.

## Architecture Overview

The database system provides:
- **Structured storage** for documents, analyses, companies, market data, financial models, and memos
- **Vector search** using pgvector for semantic document similarity
- **Async operations** with SQLAlchemy async engine
- **Migrations** managed by Alembic
- **Embeddings** generated via OpenAI's embedding models

## Database Schema

### Core Tables

#### 1. Documents (`documents`)
Stores uploaded documents and their metadata.

**Key Fields:**
- `filename`, `file_type`, `file_path` - File information
- `document_type` - Classification (financial_statement, pitch_deck, etc.)
- `full_text` - Extracted text content
- `is_vectorized` - Whether embeddings have been generated
- `tags`, `topics` - Categorization

**Relations:**
- → `document_chunks` (one-to-many)
- → `document_embeddings` (one-to-many)
- → `analyses` (one-to-many)

#### 2. Document Chunks (`document_chunks`)
Text chunks for granular embedding.

**Purpose:** Similar to open-notebook's `source_embedding`, splits documents into ~500 character chunks for better embedding accuracy.

**Key Fields:**
- `chunk_index` - Order in document
- `content` - Chunk text
- `page_number` - Source page

#### 3. Document Embeddings (`document_embeddings`)
Vector embeddings for semantic search.

**Key Fields:**
- `embedding` - Vector(1536) - pgvector column
- `content` - Text that was embedded
- `embedding_model` - Model used (e.g., "text-embedding-3-small")

**Vector Operations:**
```sql
-- Cosine similarity search
SELECT *, 1 - (embedding <-> query_embedding) AS similarity
FROM document_embeddings
WHERE 1 - (embedding <-> query_embedding) > 0.2
ORDER BY embedding <-> query_embedding
LIMIT 10;
```

#### 4. Analyses (`analyses`)
LLM analysis results for documents.

**Key Fields:**
- `analysis_type` - Type of analysis (financial, market, risk, etc.)
- `llm_model`, `llm_provider` - Model configuration
- `result_data` - Full JSON analysis result
- `confidence_score` - Quality metric
- `token_usage`, `cost_usd` - Usage tracking

**Relations:**
- → `analysis_results` (one-to-many)

#### 5. Companies (`companies`)
Company profiles for deal sourcing (Feature 1).

**Key Fields:**
- `name`, `website`, `description`
- `industry`, `sector`, `stage`
- `qualification_score` - Deal qualification metric
- `tags`, `topics`

**Relations:**
- → `company_metrics` (one-to-many)
- → `company_funding` (one-to-many)

#### 6. Market Data (`market_data`)
Market intelligence (Feature 3).

**Key Fields:**
- `market_name`, `market_segment`
- `data_type` - Size, growth, trends
- `metric_value`, `metric_unit`
- `source`, `confidence`

#### 7. Financial Models (`financial_models`)
Financial projections (Feature 4).

**Key Fields:**
- `model_name`, `model_type` (DCF, multiples, etc.)
- `assumptions` - JSON configuration
- `valuation`, `currency`

**Relations:**
- → `financial_projections` (one-to-many)

#### 8. Memos (`memos`)
Generated investment memos (Feature 5).

**Key Fields:**
- `title`, `memo_type`
- `full_content`, `executive_summary`
- `source_documents` - JSON references
- `status` - draft, review, final

**Relations:**
- → `memo_sections` (one-to-many)

#### 9. AI Models (`ai_models`)
AI model configurations.

**Purpose:** Track different AI models (language, embedding, etc.) similar to open-notebook's model management.

**Key Fields:**
- `name`, `provider` (openai, anthropic, etc.)
- `model_type` - language_model, embedding_model, etc.
- `input_cost_per_1k_tokens`, `output_cost_per_1k_tokens`
- `total_requests`, `total_tokens_used`, `total_cost_usd`

## Setup Instructions

### 1. Install PostgreSQL

**macOS (Homebrew):**
```bash
brew install postgresql@16
brew services start postgresql@16
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Docker:**
```bash
docker run -d \
  --name investment-ai-postgres \
  -e POSTGRES_USER=investment_user \
  -e POSTGRES_PASSWORD=investment_pass \
  -e POSTGRES_DB=investment_ai \
  -p 5432:5432 \
  -v investment_ai_data:/var/lib/postgresql/data \
  postgres:16
```

### 2. Create Database and User

```bash
# Connect to PostgreSQL
psql postgres

# Create user and database
CREATE USER investment_user WITH PASSWORD 'investment_pass';
CREATE DATABASE investment_ai OWNER investment_user;
GRANT ALL PRIVILEGES ON DATABASE investment_ai TO investment_user;

# Exit psql
\q
```

### 3. Configure Environment Variables

Update `.env`:
```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://investment_user:investment_pass@localhost:5432/investment_ai
DATABASE_ECHO=False
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10

# Vector Search Settings
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
VECTOR_SEARCH_LIMIT=10
VECTOR_SEARCH_MIN_SIMILARITY=0.2

# OpenAI API Key (for embeddings)
OPENAI_API_KEY=your_openai_key_here
```

### 4. Install Python Dependencies

Already done! But if needed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

Dependencies added:
- `alembic==1.13.1` - Database migrations
- `pgvector==0.2.5` - PostgreSQL vector extension
- `asyncpg==0.29.0` - Async PostgreSQL driver
- `greenlet==3.0.3` - SQLAlchemy async support

### 5. Run Migrations

```bash
cd backend

# Create initial migration
alembic revision --autogenerate -m "Initial schema with pgvector"

# Apply migrations
alembic upgrade head
```

### 6. Verify Setup

Test database connection:
```python
import asyncio
from backend.config.database import test_connection

asyncio.run(test_connection())
```

## Usage Examples

### 1. Document Storage and Embedding

```python
from backend.config.database import get_db_session
from backend.models.document import Document
from backend.services.embeddings.embedding_service import embed_document_chunks

async def store_and_embed_document():
    async with get_db_session() as session:
        # Create document record
        doc = Document(
            filename="financial_report.pdf",
            original_filename="Q4_2024_Financial_Report.pdf",
            file_path="/data/uploads/financial/financial_report.pdf",
            file_type="pdf",
            document_type="financial_statement",
            full_text="...",  # Extracted text
            is_processed=True
        )
        session.add(doc)
        await session.commit()
        
        # Generate embeddings
        chunk_count = await embed_document_chunks(
            session,
            doc.id,
            doc.full_text
        )
        
        # Update document status
        doc.is_vectorized = True
        await session.commit()
        
        print(f"Created document with {chunk_count} embeddings")
```

### 2. Semantic Search

```python
from backend.services.embeddings.embedding_service import vector_search

async def search_documents():
    async with get_db_session() as session:
        results = await vector_search(
            session,
            query_text="What are the revenue projections for 2025?",
            limit=5,
            minimum_similarity=0.3
        )
        
        for result in results:
            print(f"Similarity: {result['similarity']:.3f}")
            print(f"Content: {result['content'][:200]}...")
            print(f"Document ID: {result['document_id']}")
            print("---")
```

### 3. Storing Analysis Results

```python
from backend.models.analysis import Analysis

async def store_analysis():
    async with get_db_session() as session:
        analysis = Analysis(
            document_id=1,
            analysis_type="financial_analysis",
            llm_model="gpt-4o-mini",
            llm_provider="openai",
            status="completed",
            result_data={
                "revenue_trend": "increasing",
                "profit_margin": "23.5%",
                "key_risks": ["market volatility", "competition"]
            },
            summary="Strong financial performance with consistent growth...",
            confidence_score=0.85,
            token_usage=2500,
            cost_usd=0.015
        )
        session.add(analysis)
        await session.commit()
```

### 4. Company Tracking (Feature 1)

```python
from backend.models.company import Company, CompanyFunding

async def track_company():
    async with get_db_session() as session:
        company = Company(
            name="TechStartup Inc",
            website="https://techstartup.com",
            industry="SaaS",
            sector="Enterprise Software",
            stage="series_a",
            qualification_score=78.5,
            is_qualified=True
        )
        session.add(company)
        await session.flush()
        
        # Add funding round
        funding = CompanyFunding(
            company_id=company.id,
            round_type="series_a",
            amount_raised=5000000,
            post_money_valuation=25000000,
            lead_investors=["VC Firm A", "Angel Investor B"]
        )
        session.add(funding)
        await session.commit()
```

## Key Design Decisions

### 1. Why pgvector over Faiss/ChromaDB?

**Advantages:**
- ✅ Unified storage (no separate vector DB)
- ✅ ACID transactions for consistency
- ✅ Easier deployment (one database)
- ✅ Better for relational queries with vector search
- ✅ Production-ready scaling with PostgreSQL

**Inspired by open-notebook but improved:**
- open-notebook uses SurrealDB (NoSQL)
- We use PostgreSQL (battle-tested, more enterprise-ready)
- Better integration with existing tools

### 2. Async vs Sync

All database operations are async for:
- Better concurrency
- Non-blocking I/O
- Scalability with FastAPI async endpoints

### 3. Chunking Strategy

Following open-notebook's approach:
- **500 characters per chunk** (optimal for embeddings)
- **50 character overlap** (prevents context loss at boundaries)
- Stored separately for efficient vector search

### 4. Embedding Model

Default: `text-embedding-3-small` (1536 dimensions)
- Fast and cost-effective
- High quality for semantic search
- Can upgrade to `text-embedding-3-large` (3072 dimensions) for better accuracy

## Comparison: open-notebook vs Our Implementation

| Aspect | open-notebook | Our Implementation |
|--------|---------------|-------------------|
| **Database** | SurrealDB | PostgreSQL |
| **Vector Store** | SurrealDB native | pgvector extension |
| **Language** | Python | Python |
| **ORM** | Custom repository pattern | SQLAlchemy async |
| **Migrations** | Custom SQL files | Alembic |
| **Vector Search** | `fn::vector_search()` | pgvector `<->` operator |
| **Embedding Storage** | `array<number>` | `VECTOR(1536)` |
| **Async** | ✅ Yes | ✅ Yes |
| **Chunks** | `source_embedding` table | `document_chunks` + `document_embeddings` |

## Performance Optimization

### 1. Vector Index

After creating embeddings, create an HNSW index:
```sql
-- Create HNSW index for fast similarity search
CREATE INDEX idx_document_embeddings_vector 
ON document_embeddings 
USING hnsw (embedding vector_cosine_ops);
```

### 2. Connection Pooling

Already configured in `database.py`:
- Pool size: 5
- Max overflow: 10
- Pre-ping: Enabled

### 3. Batch Operations

Use `embed_document_chunks` for bulk embedding generation:
- Processes all chunks in one OpenAI API call
- Reduces latency and cost

## Troubleshooting

### Issue: pgvector extension not found

```sql
-- Connect to database and install extension
psql -U investment_user -d investment_ai
CREATE EXTENSION IF NOT EXISTS vector;
```

### Issue: Migration fails with "table already exists"

```bash
# Drop and recreate database
dropdb investment_ai
createdb investment_ai -O investment_user

# Rerun migrations
alembic upgrade head
```

### Issue: Slow vector search

```bash
# Check if index exists
psql -U investment_user -d investment_ai
\d document_embeddings

# Create index if missing
CREATE INDEX idx_document_embeddings_vector 
ON document_embeddings 
USING hnsw (embedding vector_cosine_ops);
```

## Next Steps

1. ✅ Database schema created
2. ✅ Migrations configured
3. ✅ Embedding service implemented
4. ✅ Vector search ready
5. ⏳ Update file upload API to use database
6. ⏳ Update analysis API to save results
7. ⏳ Create search endpoints
8. ⏳ Add frontend components for search
9. ⏳ Implement remaining features (1, 3, 4, 5)

## References

- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [open-notebook Repository](https://github.com/lfnovo/open-notebook)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
