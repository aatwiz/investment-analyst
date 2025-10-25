# Investment Analyst AI Agent 🚀

An AI-powered investment analysis platform that assists analysts in due diligence, financial modeling, and memo drafting.

## 🎯 Project Vision

Build a unified AI agent that accelerates deal sourcing, reduces manual effort, and improves investment decision-making quality.

## ✨ MVP Features

1. **AI-Powered Deal Sourcing** - Scrape and qualify startup deals
2. **Automated DD Document Analysis** - Analyze legal and financial documents
3. **Market & Competitive Analysis** - Generate market insights
4. **Financial Modeling & Scenario Planning** - Build projection models
5. **Investment Memo & Presentation Draft** - Auto-draft memos and decks

## 🛠 Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit
- **AI/NLP**: OpenAI GPT-4, LangChain, Ollama (local LLMs)
- **Document Processing**: PyMuPDF, python-docx, openpyxl, Tesseract OCR
- **Data Processing**: Pandas, NumPy
- **Web Scraping**: BeautifulSoup, Playwright
- **Vector DB**: FAISS/Chroma (for RAG)
- **Database**: PostgreSQL/MongoDB

## 📁 Project Structure

```
investment-ai/
├── backend/                 # FastAPI backend
│   ├── api/                # API endpoints
│   ├── services/           # Business logic (organized by feature)
│   │   ├── document_analysis/       # Keyword-based analysis ✅
│   │   ├── file_processing/         # Document extraction ✅
│   │   ├── llm_agents/             # LLM-powered agents ✅
│   │   ├── data_extraction/        # Specialized extraction 🚧
│   │   ├── web_scraping/           # Deal sourcing scrapers 📦
│   │   ├── deal_qualification/     # Deal scoring & profiling 📦
│   │   ├── market_intelligence/    # Market & competitor analysis 📦
│   │   ├── external_data/          # External API integrations 📦
│   │   ├── financial_modeling/     # Financial projections 📦
│   │   ├── content_generation/     # Memo & deck generation 📦
│   │   └── template_management/    # Templates & branding 📦
│   ├── models/             # Data models
│   ├── utils/              # Utility functions
│   └── main.py             # FastAPI app entry
├── frontend/               # Streamlit frontend
│   ├── pages/              # Multi-page app
│   ├── components/         # Reusable UI components
│   └── app.py              # Main Streamlit app
├── data/                   # Data storage
│   ├── uploads/            # Uploaded files
│   ├── processed/          # Processed documents
│   └── outputs/            # Generated reports
├── docs/                   # Documentation
├── MASTER_GUIDE.md         # ⭐ START HERE - Complete implementation guide
├── models/                 # AI/ML models
├── tests/                  # Test suite
└── requirements.txt        # Python dependencies
```

**Legend**: ✅ Complete | 🚧 In Progress | 📦 Placeholder

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Backend (FastAPI)

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

### 3. Run Frontend (Streamlit)

```bash
streamlit run frontend/app.py
```

Frontend will be available at: http://localhost:8501

## 📝 Development Roadmap

- [x] **Phase 1**: Project setup with file upload capabilities ✅
- [x] **Phase 2**: Document processing and extraction ✅
  - PDF, DOCX, Excel, CSV, PowerPoint, TXT extraction
  - Keyword-based analysis (100+ red flags & positive signals)
  - Investment recommendation engine
  - Complete Analysis UI with 4 display modes
  - **LLM-powered analysis with OpenAI GPT-4o-mini** ⭐ NEW
- [ ] **Phase 3**: AI-Powered Deal Sourcing (🚧 In Progress)
  - Web scraping infrastructure
  - Deal qualification engine
  - Company profile builder
- [ ] **Phase 4**: Market & Competitive Analysis (🚧 In Progress)
  - Market sizing and trends
  - Competitor tracking
  - Sentiment analysis
- [ ] **Phase 5**: Financial Modeling & Scenario Planning (🚧 In Progress)
  - Projection model builder
  - Scenario planning
  - Valuation engine
- [ ] **Phase 6**: Investment Memo & Presentation Generation (🚧 In Progress)
  - Memo generation with LLM
  - Pitch deck creation
  - Template management

## 📚 Documentation

📘 **[MASTER_GUIDE.md](./MASTER_GUIDE.md)** ⭐ **START HERE** - Everything you need:
- Core platform overview (analysis, RAG queries, database)
- Implementation guide for Features 1, 3, 4, 5
- Code patterns and examples
- Cost optimization strategies
- Quick start commands

Additional docs in `/docs` folder for deep dives.

## 🤝 Contributing

This project is built for investment analysts to accelerate their due diligence process.

## 📄 License

MIT License
