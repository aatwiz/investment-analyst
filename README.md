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
│   ├── services/           # Business logic (organized by capability)
│   │   ├── document_analysis/    # Keyword-based analysis ✅
│   │   ├── file_processing/      # Document extraction ✅
│   │   ├── llm_agents/          # LLM-powered agents 🚧
│   │   └── data_extraction/     # Specialized extraction
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
│   ├── LLM_INTEGRATION_GUIDE.md
│   ├── QUICK_START_LLM.md
│   ├── ARCHITECTURE_DIAGRAM.md
│   └── HANDOFF_SUMMARY.md
├── models/                 # AI/ML models
├── tests/                  # Test suite
└── requirements.txt        # Python dependencies
```

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
- [ ] **Phase 3**: LLM-powered analysis (🚧 Infrastructure ready)
  - Pre-processing pipeline built
  - Prompt generation complete
  - Need: OpenAI API key + 10 lines of code
  - See: `docs/QUICK_START_LLM.md`
- [ ] **Phase 4**: Market & competitive analysis
- [ ] **Phase 5**: Financial modeling
- [ ] **Phase 6**: Memo and presentation generation

## 📚 Documentation

- 📖 **[LLM Integration Guide](docs/LLM_INTEGRATION_GUIDE.md)** - Complete implementation guide
- ⚡ **[Quick Start LLM](docs/QUICK_START_LLM.md)** - Fast reference for tomorrow
- 🏗️ **[Architecture Diagram](docs/ARCHITECTURE_DIAGRAM.md)** - Visual architecture
- 📧 **[Handoff Summary](docs/HANDOFF_SUMMARY.md)** - Team handoff document

## 🤝 Contributing

This project is built for investment analysts to accelerate their due diligence process.

## 📄 License

MIT License
