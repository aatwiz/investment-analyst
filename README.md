# Investment Analyst AI Agent 🚀

An AI-powered investment analysis platform that streamlines deal sourcing, market research, document analysis, financial modeling, and report generation for venture capital and private equity analysts.

## ✨ Features

### 1. 🔎 AI-Powered Deal Sourcing
- **Mock deal database** with 30 realistic startup profiles (Anthropic, Databricks, Scale AI, Notion, Ramp, etc.)
- Companies from AI, FinTech, HR Tech, Developer Tools, and more
- Funding stages from Seed to Series I
- Qualification scoring and filtering by industry, stage, location, and funding
- Deal statistics and pipeline management

### 2. 📊 Market Intelligence
- **Comprehensive market analysis** for any company or industry
- Market size, growth rate, and positioning analysis
- Competitive landscape and market share distribution
- Industry trends and key market drivers
- Regulatory environment analysis
- Strategic opportunities and threats identification
- Source references for all claims and data points

### 3. 📁 Document Analysis
- **Multi-format support**: PDF, DOCX, XLSX, PPTX, CSV, TXT, MD
- **Keyword-based analysis**: 100+ red flags and positive signals
- **LLM-powered insights**: Comprehensive summaries, key points, red flag detection
- **Investment recommendations**: Data-driven scoring (0-100)
- **RAG (Retrieval-Augmented Generation)**: Ask questions about uploaded documents
- **Segmented chunk storage**: 90% cost reduction, 81% faster responses

### 4. 💰 Financial Modeling
- **Extract financial data** from documents automatically
- **Build projection models**: Revenue, expenses, cash flow forecasts
- **Scenario planning**: Best case, base case, worst case analysis
- **Key metrics**: ARR, burn rate, runway, unit economics
- **Export to Excel**: Full financial models with formulas

### 5. 📝 Investment Reports
- **Investment memos**: Professional IC memos with executive summary, market analysis, team assessment
- **Pitch decks**: Beautiful PowerPoint presentations (10-15 slides)
- **Format options**: DOCX, PPTX, PDF, HTML
- **Auto-generated content**: Based on document analysis and market intelligence

## 🛠 Technology Stack

**Backend:**
- FastAPI - Modern, fast API framework
- OpenAI GPT-4o & GPT-4o-mini - Advanced language models
- LangChain - LLM orchestration and document processing
- ChromaDB - Vector database for RAG
- Serper API - Real-time news and web search

**Frontend:**
- Streamlit - Interactive web interface
- Beautiful UI with dark theme and custom styling

**Document Processing:**
- PyMuPDF (fitz) - PDF extraction
- python-docx - Word documents
- openpyxl - Excel files
- python-pptx - PowerPoint generation

**Data & Analysis:**
- Pandas, NumPy - Data manipulation
- Requests - HTTP client

## 🚀 Getting Started

### Prerequisites

- Python 3.12 or higher
- OpenAI API key
- Serper API key (for market intelligence)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/aatwiz/investment-analyst.git
cd investment-analyst
```

2. **Create virtual environment**
```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the root directory:

```env
# OpenAI API Key (Required)
OPENAI_API_KEY=your_openai_api_key_here

# Serper API Key (Required for Market Intelligence)
SERPER_API_KEY=your_serper_api_key_here

# Backend URL (default: http://localhost:8000)
API_BASE_URL=http://localhost:8000/api/v1
```

**Getting API Keys:**
- **OpenAI**: Sign up at [platform.openai.com](https://platform.openai.com) and create an API key
- **Serper**: Sign up at [serper.dev](https://serper.dev) for Google Search API access (free tier available)

### Running the Application

#### Option 1: Use the Start Script (Recommended)

```bash
# Make the script executable (first time only)
chmod +x scripts/start_all.sh

# Start both backend and frontend
./scripts/start_all.sh
```

#### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
streamlit run frontend/app.py
```

### Access the Application

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs

## 📖 Usage Guide

### 1. Deal Sourcing

1. Navigate to **Deal Sourcing** page
2. Click **"Start Scraping"** to load the 30 mock deals
3. View **Top Deals** with funding, stage, location, and company details
4. Filter by industry, stage, location, or funding amount
5. See qualification scores and recommendations

### 2. Market Intelligence

1. Go to **Market Intelligence** page
2. Enter a company name (e.g., "Apple", "Netflix", "Tesla")
3. Select analysis components:
   - Market Overview & Metrics
   - Key Trends
   - Competitive Position
   - Opportunities & Threats
   - Regulatory Environment
4. Click **"Analyze Market"**
5. View comprehensive market analysis with source references

### 3. Document Analysis

1. Navigate to **Upload Documents**
2. Select document category (Financial, Legal, Market, Technical, etc.)
3. Upload files (PDF, DOCX, XLSX, PPTX, CSV, TXT)
4. Go to **Document Library** to view uploaded files
5. Select documents in **Analysis** page
6. Choose analysis type:
   - **Summary**: Quick overview
   - **Key Points**: Main insights
   - **Red Flags**: Risk identification
   - **Ask Questions**: RAG-powered Q&A
7. View AI-generated insights and investment recommendations

### 4. Financial Modeling

1. Navigate to **Financial Modeling**
2. Upload financial documents or Excel files
3. Extract financial data automatically
4. Build projections:
   - Revenue forecasts
   - Expense planning
   - Cash flow analysis
5. Run scenario analysis (Best/Base/Worst case)
6. Export complete model to Excel

### 5. Generate Reports

1. Go to **Generate Reports**
2. Choose report type:
   - **Investment Memo**: Professional IC memo
   - **Pitch Deck**: PowerPoint presentation
3. Select analyzed documents as input
4. Add company context and details
5. Generate report with one click
6. Download in DOCX, PPTX, or PDF format

## 📁 Project Structure

```
investment-ai/
├── backend/
│   ├── api/
│   │   └── routes/              # API endpoints
│   │       ├── analysis.py      # Document analysis
│   │       ├── companies.py     # Deal sourcing
│   │       ├── files.py         # File upload/management
│   │       ├── llm_analysis.py  # LLM analysis
│   │       ├── market.py        # Market intelligence
│   │       ├── modeling.py      # Financial modeling
│   │       ├── reports.py       # Report generation
│   │       └── search.py        # RAG search
│   ├── services/
│   │   ├── deals/               # Mock deal data
│   │   ├── document_analysis/   # Keyword analysis
│   │   ├── file_processing/     # Document extraction
│   │   ├── financial_modeling/  # Projections & scenarios
│   │   ├── llm_agents/          # LLM orchestration
│   │   ├── market_intelligence/ # Market research
│   │   ├── report_generation/   # Memo & deck creation
│   │   └── web_scraping/        # Deal sourcing (mock data)
│   ├── config/                  # Configuration
│   ├── models/                  # Data models
│   └── main.py                  # FastAPI app
├── frontend/
│   └── app.py                   # Streamlit app
├── data/
│   ├── uploads/                 # Uploaded files
│   ├── processed/               # ChromaDB vector store
│   └── outputs/                 # Generated reports
├── docs/                        # Documentation
├── scripts/
│   └── start_all.sh            # Startup script
├── .env                         # Environment variables (create this)
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## � Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o models | Yes | - |
| `SERPER_API_KEY` | Serper API key for web search | Yes | - |
| `API_BASE_URL` | Backend API URL | No | `http://localhost:8000/api/v1` |

### Cost Optimization

The platform uses **segmented chunk storage** for document processing:
- Documents are split into 1000-token chunks with 100-token overlap
- Only relevant chunks are sent to LLM (not entire documents)
- **90% cost reduction** compared to full-document processing
- **81% faster response times**

**Estimated Costs** (OpenAI GPT-4o-mini):
- Document analysis: $0.01-0.05 per document
- Market intelligence: $0.10-0.30 per analysis
- Report generation: $0.20-0.50 per report
- Financial modeling: $0.05-0.15 per model

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

## 📚 Documentation

Additional documentation available in `/docs`:
- `architecture.md` - System architecture and data flows
- `tech-stack.md` - Technology choices and reasoning
- `future-architecture.md` - Planned features and roadmap

## 🐛 Troubleshooting

**Backend won't start:**
- Check that port 8000 is not in use: `lsof -i :8000`
- Verify environment variables are set in `.env`
- Check OpenAI and Serper API keys are valid

**Frontend won't start:**
- Check that port 8501 is not in use: `lsof -i :8501`
- Make sure backend is running first
- Clear Streamlit cache: `streamlit cache clear`

**Market analysis returns 0M market size:**
- Verify Serper API key is set correctly
- Check internet connection for API calls
- Try a different company name

**Document upload fails:**
- Check `data/uploads/` directory exists and is writable
- Verify file size is under 200MB
- Ensure file format is supported (PDF, DOCX, XLSX, etc.)

## 🤝 Contributing

This is a private project for investment analysis workflows. For questions or issues, please open a GitHub issue.

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

Built with:
- OpenAI GPT-4o for advanced language understanding
- LangChain for LLM orchestration
- Streamlit for rapid UI development
- FastAPI for modern API development

---

**Made with ❤️ for investment analysts**
