# Investment Analyst AI - System Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Frontend Layer                                  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         Streamlit UI                                  │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │  │
│  │  │   Home   │  │   Deal   │  │  Market  │  │ Document │            │  │
│  │  │   Page   │  │ Sourcing │  │   Intel  │  │ Analysis │            │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │  │
│  │  │ Upload   │  │ Library  │  │Financial │  │ Reports  │            │  │
│  │  │   Docs   │  │  Viewer  │  │ Modeling │  │Generator │            │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│                         HTTP/REST API Calls                                  │
│                                  ▼                                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                            Backend Layer (FastAPI)                           │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                          API Routes                                   │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  │  │
│  │  │  Files  │  │  Deals  │  │ Market  │  │Analysis │  │ Reports │  │  │
│  │  │ /files  │  │ /deals  │  │/market  │  │/analyze │  │/reports │  │  │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  │  │
│  └───────┼────────────┼────────────┼────────────┼────────────┼────────┘  │
│          │            │            │            │            │            │
│  ┌───────▼────────────▼────────────▼────────────▼────────────▼────────┐  │
│  │                      Service Layer                                   │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │  │
│  │  │   File      │  │    Deal     │  │   Market    │                │  │
│  │  │  Manager    │  │  Scraper    │  │ Intelligence│                │  │
│  │  │             │  │   Service   │  │   Agent     │                │  │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                │  │
│  │         │                │                │                        │  │
│  │  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐                │  │
│  │  │  Document   │  │    Deal     │  │  Financial  │                │  │
│  │  │  Processor  │  │ Qualifier   │  │   Modeler   │                │  │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                │  │
│  │         │                │                │                        │  │
│  │  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐                │  │
│  │  │   PDF/DOC   │  │  Pipeline   │  │   Report    │                │  │
│  │  │  Extractor  │  │  Tracker    │  │  Generator  │                │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI/ML Layer                                        │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        LangChain Framework                            │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │  │
│  │  │   Agents    │  │   Chains    │  │  Prompts    │                │  │
│  │  │  - Market   │  │  - RAG      │  │  - System   │                │  │
│  │  │  - Analyst  │  │  - Query    │  │  - Task     │                │  │
│  │  │  - Deal     │  │  - Summary  │  │  - Context  │                │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      OpenAI API Integration                           │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │  │
│  │  │  GPT-4o     │  │   GPT-4     │  │Embeddings   │                │  │
│  │  │  (Primary)  │  │  (Fallback) │  │text-embed-3 │                │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Data & Storage Layer                                  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      Vector Database (ChromaDB)                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │  │
│  │  │  Document   │  │    Deal     │  │   Market    │                │  │
│  │  │ Embeddings  │  │ Embeddings  │  │ Intelligence│                │  │
│  │  │             │  │             │  │  Embeddings │                │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                │  │
│  │                                                                      │  │
│  │  Features:                                                           │  │
│  │  • Semantic search across documents                                 │  │
│  │  • Similarity matching for deals                                    │  │
│  │  • Context retrieval for AI agents                                  │  │
│  │  • Metadata filtering                                               │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │              File Storage (Segmented Chunk Storage)                   │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐│  │
│  │  │                    uploads/ Directory                            ││  │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       ││  │
│  │  │  │pitch_deck│  │ financials│  │contracts │  │   due_   │       ││  │
│  │  │  │   .pdf   │  │   .xlsx   │  │   .pdf   │  │diligence │       ││  │
│  │  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘       ││  │
│  │  └─────────────────────────────────────────────────────────────────┘│  │
│  │                                                                      │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐│  │
│  │  │                  chunks/ Directory                               ││  │
│  │  │  (Segmented Document Chunks for Fast Retrieval)                 ││  │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         ││  │
│  │  │  │pitch_deck_   │  │financials_   │  │contract_     │         ││  │
│  │  │  │chunk_1.json  │  │chunk_1.json  │  │chunk_1.json  │         ││  │
│  │  │  │chunk_2.json  │  │chunk_2.json  │  │chunk_2.json  │         ││  │
│  │  │  │chunk_3.json  │  │chunk_3.json  │  │chunk_3.json  │         ││  │
│  │  │  └──────────────┘  └──────────────┘  └──────────────┘         ││  │
│  │  │                                                                 ││  │
│  │  │  Chunk Structure:                                               ││  │
│  │  │  {                                                              ││  │
│  │  │    "content": "text content",                                   ││  │
│  │  │    "metadata": {"page": 1, "section": "..."},                  ││  │
│  │  │    "embedding": [0.1, 0.2, ...]                                ││  │
│  │  │  }                                                              ││  │
│  │  └─────────────────────────────────────────────────────────────────┘│  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    Session & Cache Storage                            │  │
│  │  • In-memory caching for API responses                               │  │
│  │  • Deal pipeline state management                                     │  │
│  │  • Analysis results caching                                           │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      External Integrations Layer                             │
│                                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │  Crunchbase │  │  PitchBook  │  │   AngelList │  │    Y.C.     │       │
│  │     API     │  │     API     │  │     API     │  │   Startups  │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
│                                                                              │
│  Purpose: Deal sourcing, company data, funding information                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Architecture

### 1. Document Upload & Processing Flow
```
User Upload → FastAPI Endpoint → File Validation → 
PDF/DOCX Extraction → Text Chunking (1000 tokens) → 
Embedding Generation → ChromaDB Storage → 
Chunk Files Saved → Success Response
```

### 2. Market Intelligence Flow
```
User Request → API Endpoint → Research Agent Initialization →
Multiple AI Agent Calls (Market Overview, Trends, Competitors) →
Source Reference Generation → Data Aggregation →
Response with Sources → Frontend Display with Expandable References
```

### 3. Deal Sourcing Flow
```
User Criteria → Scraper Service → External API Calls →
Deal Data Collection → Deal Qualification (AI Scoring) →
Pipeline Tracking → Deal Storage → Frontend Display
```

### 4. Document Analysis Flow
```
Document Selection → Chunk Retrieval → Context Assembly →
LangChain RAG Pipeline → GPT-4o Analysis →
Structured Response → Frontend Visualization
```

## Component Interactions

### Frontend ↔ Backend Communication
- **Protocol**: HTTP/REST
- **Format**: JSON
- **Authentication**: API Key (future implementation)
- **Error Handling**: Structured error responses with status codes

### Backend ↔ AI Services
- **LangChain**: Orchestrates AI workflows
- **OpenAI API**: Direct calls for embeddings and completions
- **Retry Logic**: Exponential backoff for API failures
- **Token Management**: Dynamic context sizing

### Backend ↔ Storage
- **ChromaDB**: Async operations for vector storage
- **File System**: Direct I/O for document and chunk management
- **Caching**: In-memory caching for frequent queries

## Scalability Considerations

### Current Architecture
- Single-instance deployment
- In-memory state management
- Local file storage
- Direct API integrations

### Future Scalability Path
1. **Database Layer**: PostgreSQL for relational data
2. **Message Queue**: Redis/RabbitMQ for async processing
3. **Object Storage**: S3 for document storage
4. **Container Orchestration**: Docker + Kubernetes
5. **Load Balancing**: NGINX for traffic distribution
6. **Microservices**: Service decomposition for independent scaling

## Security Architecture

### Current Implementation
- Input validation on all endpoints
- File type restrictions
- Size limits on uploads
- API timeout protection

### Planned Enhancements
- JWT authentication
- Role-based access control (RBAC)
- Encrypted storage for sensitive documents
- API rate limiting
- Audit logging

## Performance Optimizations

1. **Chunked Document Processing**: 1000-token chunks for optimal retrieval
2. **Vector Search**: ChromaDB indexing for sub-second queries
3. **Async Operations**: Non-blocking I/O for concurrent requests
4. **Caching**: Response caching for repeated queries
5. **Lazy Loading**: Frontend pagination for large datasets

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Streamlit | Rapid UI development |
| Backend | FastAPI | High-performance API |
| AI Framework | LangChain | AI workflow orchestration |
| LLM | GPT-4o / GPT-4 | Natural language processing |
| Vector DB | ChromaDB | Semantic search |
| Storage | File System | Document & chunk storage |
| Document Processing | PyPDF2, python-docx | Text extraction |
| HTTP Client | Requests | External API calls |

---

*Last Updated: October 26, 2025*
