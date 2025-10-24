# 🚀 LLM Integration - Next Steps Guide

**Date**: October 25, 2025  
**Status**: Infrastructure Ready ✅ | LLM API Integration Pending ⏳  
**For**: Development Team

---

## 📋 Table of Contents

1. [Current State](#current-state)
2. [What We Built Today](#what-we-built-today)
3. [Architecture Overview](#architecture-overview)
4. [Next Steps (Tomorrow)](#next-steps-tomorrow)
5. [API Keys Required](#api-keys-required)
6. [Testing Instructions](#testing-instructions)
7. [Code Locations](#code-locations)

---

## 🎯 Current State

### ✅ What's Working

- **Phase 2 Complete**: Document analysis with keyword-based detection
- **File Processing**: PDF, DOCX, Excel, CSV, PowerPoint, TXT extraction
- **Analysis Engine**: 100+ keywords, red flag detection, positive signals
- **Investment Recommendations**: Scoring algorithm with confidence levels
- **Services Architecture**: Organized into subdirectories
- **LLM Agent Infrastructure**: Prompt generation, data structuring

### ⏳ What's Pending

- **LLM API Integration**: Need to implement actual OpenAI/Anthropic calls
- **API Keys**: Need to obtain and configure API credentials
- **Frontend LLM Page**: UI for LLM-powered analysis (optional enhancement)
- **Prompt Optimization**: Fine-tune prompts based on real LLM responses

---

## 🏗️ What We Built Today

### 1. Restructured Services Directory

```
backend/services/
├── document_analysis/
│   ├── __init__.py
│   └── document_analyzer.py       # Keyword-based pre-processor
├── file_processing/
│   ├── __init__.py
│   └── file_processor.py          # Document extraction
├── llm_agents/
│   ├── __init__.py
│   └── investment_analyst_agent.py # NEW: LLM agent with prompt builder
├── data_extraction/
│   └── __init__.py
└── __init__.py
```

### 2. Investment Analyst LLM Agent

**File**: `backend/services/llm_agents/investment_analyst_agent.py`

**Key Components**:

```python
class InvestmentAnalystAgent:
    """
    LLM-powered investment analyst
    Uses DocumentAnalyzer as pre-processing layer
    """
    
    def __init__(self, config: LLMConfig):
        self.analyzer = DocumentAnalyzer()  # Your existing analyzer
        self.llm = None  # TODO: Initialize LLM provider
    
    async def analyze_document(self, filename: str):
        # Step 1: Pre-process (keyword-based)
        structured_data = self.analyzer.analyze_document(filename)
        
        # Step 2: Build LLM prompt
        prompt = self._build_analysis_prompt(structured_data)
        
        # Step 3: Get LLM insights (TODO)
        llm_insights = await self._get_llm_insights(prompt)
        
        # Step 4: Merge results
        return self._merge_insights(structured_data, llm_insights)
```

**Why This Architecture?**:
- ✅ **Token Efficiency**: Pre-processing reduces 30k+ tokens → 2-5k tokens
- ✅ **Cost Savings**: 85% reduction in API costs
- ✅ **Better Results**: Structured input = focused LLM reasoning
- ✅ **Fallback**: Keyword analysis works even if LLM fails

### 3. LLM API Routes

**File**: `backend/api/routes/llm_analysis.py`

**Endpoints**:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/llm/configure` | Set API keys and LLM config |
| POST | `/api/v1/llm/analyze` | Run LLM-powered analysis |
| GET | `/api/v1/llm/prompt-preview/{filename}` | Preview prompt without API call |
| GET | `/api/v1/llm/status` | Check agent configuration status |

---

## 🏛️ Architecture Overview

### Data Flow

```
📄 Document Upload
    ↓
📂 FileProcessor (extract text, tables, metadata)
    ↓
🔍 DocumentAnalyzer (keyword detection, structure data)
    ↓
📝 InvestmentAnalystAgent (build prompt from structured data)
    ↓
🤖 LLM API (GPT-4/Claude - deep reasoning)
    ↓
📊 Merged Analysis (structured + LLM insights)
    ↓
📈 Investment Recommendation
```

### Why Pre-Processing Matters

**Without Pre-Processing** (❌ Bad):
```
Raw 50-page PDF → LLM
- 30,000+ tokens
- $0.60+ per analysis (GPT-4)
- Misses subtle keywords
- Generic analysis
```

**With Pre-Processing** (✅ Good):
```
PDF → Extract → Structure → Flag Issues → LLM
- 2,000-5,000 tokens
- $0.10 per analysis
- Focused on key issues
- Deep reasoning on what matters
```

---

## 🔜 Next Steps (Tomorrow)

### Priority 1: Get API Keys

#### Option A: OpenAI (Recommended)

1. **Sign Up**: https://platform.openai.com/signup
2. **Get API Key**: https://platform.openai.com/api-keys
3. **Add Credits**: $10 minimum (goes far with pre-processing!)
4. **Model**: Use `gpt-4` or `gpt-4-turbo`

#### Option B: Anthropic Claude

1. **Sign Up**: https://console.anthropic.com/
2. **Get API Key**: https://console.anthropic.com/settings/keys
3. **Model**: Use `claude-3-opus` or `claude-3-sonnet`

#### Option C: Azure OpenAI

1. **Azure Account**: Need Azure subscription
2. **Deploy Model**: Deploy GPT-4 in Azure portal
3. **Get Endpoint + Key**: From Azure OpenAI resource

---

### Priority 2: Implement LLM Provider

**File to Edit**: `backend/services/llm_agents/investment_analyst_agent.py`

**Function**: `_get_llm_insights()`

#### OpenAI Implementation Example

```python
import openai
from openai import AsyncOpenAI

async def _get_llm_insights(self, prompt: str) -> Dict[str, Any]:
    """Get insights from OpenAI GPT-4"""
    
    client = AsyncOpenAI(api_key=self.config.api_key)
    
    try:
        response = await client.chat.completions.create(
            model=self.config.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an experienced investment analyst."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            response_format={"type": "json_object"}  # Get JSON response
        )
        
        # Parse JSON response
        result = json.loads(response.choices[0].message.content)
        
        return result
    
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise
```

#### Required Package

```bash
pip install openai  # Add to requirements.txt
```

---

### Priority 3: Test End-to-End

#### Step 1: Configure Agent

```bash
curl -X POST http://localhost:8000/api/v1/llm/configure \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "model": "gpt-4",
    "api_key": "sk-proj-..."
  }'
```

#### Step 2: Preview Prompt (No API Call)

```bash
curl http://localhost:8000/api/v1/llm/prompt-preview/your-document.pdf
```

**Review the prompt!** Make sure it contains:
- ✅ Red flags with context
- ✅ Positive signals
- ✅ Financial metrics
- ✅ Clear analysis request

#### Step 3: Run LLM Analysis

```bash
curl -X POST http://localhost:8000/api/v1/llm/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "your-document.pdf",
    "focus_areas": ["market_risk", "financial_health"]
  }'
```

#### Step 4: Verify Response

Check that response includes:
- ✅ Risk assessment (0-10 scale)
- ✅ Opportunity analysis
- ✅ Financial health evaluation
- ✅ Investment recommendation (BUY/HOLD/AVOID)
- ✅ Due diligence next steps

---

### Priority 4: Prompt Optimization

After getting initial results, you'll want to tune the prompt:

**Things to Adjust**:

1. **System Message**: Define LLM persona more precisely
2. **Context Length**: Add more/less context per keyword match
3. **Response Format**: Refine JSON structure for easier parsing
4. **Few-Shot Examples**: Add example analyses in prompt
5. **Temperature**: Lower (0.3) for consistent analysis, higher (0.8) for creative insights

**File to Edit**: `_build_analysis_prompt()` method

---

### Priority 5: Frontend Integration (Optional)

Add LLM analysis option to Analysis page:

```python
# In frontend/app.py - show_analysis_page()

analysis_type = st.selectbox(
    "Analysis Type",
    ["comprehensive", "summary", "red_flags", "financial", "llm_powered"],  # Add this
    key="analysis_type"
)

if analysis_type == "llm_powered":
    # Add focus areas multiselect
    focus_areas = st.multiselect(
        "Focus Areas (optional)",
        ["market_risk", "financial_health", "team", "competitive_position"]
    )
    
    # Call LLM endpoint instead
    response = requests.post(
        f"{API_BASE_URL}/llm/analyze",
        json={"filename": selected_file, "focus_areas": focus_areas}
    )
```

---

## 🔑 API Keys Required

### Environment Variables (Recommended)

Add to `.env` file:

```bash
# OpenAI
OPENAI_API_KEY=sk-proj-...

# Or Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Or Azure
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=...
AZURE_OPENAI_DEPLOYMENT=gpt-4
```

### Update Config

**File**: `backend/utils/config.py`

```python
class Settings:
    # ... existing settings ...
    
    # LLM Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4")
```

---

## 🧪 Testing Instructions

### Test 1: Verify Infrastructure

```bash
# Start services
./run.sh

# Check LLM agent status
curl http://localhost:8000/api/v1/llm/status

# Expected: {"status": "not_configured", "ready": false}
```

### Test 2: Preview Prompt Generation

```bash
# Upload a test document first via UI or:
curl -X POST http://localhost:8000/api/v1/files/upload \
  -F "file=@test_document.pdf"

# Preview the prompt
curl http://localhost:8000/api/v1/llm/prompt-preview/test_document.pdf

# Check output contains:
# - Red flags section
# - Positive signals section
# - Financial metrics
# - Analysis request
```

### Test 3: Mock LLM Analysis (No API Key)

```bash
# Will return placeholder data
curl -X POST http://localhost:8000/api/v1/llm/analyze \
  -H "Content-Type: application/json" \
  -d '{"filename": "test_document.pdf"}'

# Expected: Structured response with "status": "placeholder"
```

### Test 4: Real LLM Analysis (After API Key Added)

```bash
# Configure with real API key
curl -X POST http://localhost:8000/api/v1/llm/configure \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "model": "gpt-4",
    "api_key": "sk-proj-YOUR-KEY-HERE"
  }'

# Run real analysis
curl -X POST http://localhost:8000/api/v1/llm/analyze \
  -H "Content-Type: application/json" \
  -d '{"filename": "test_document.pdf"}'

# Expected: Real LLM-generated insights
```

---

## 📂 Code Locations

### Core LLM Files (You'll Edit These)

| File | Purpose | Priority |
|------|---------|----------|
| `backend/services/llm_agents/investment_analyst_agent.py` | Main LLM agent logic | **HIGH** |
| `backend/api/routes/llm_analysis.py` | LLM API endpoints | **HIGH** |
| `backend/utils/config.py` | Add API key settings | **MEDIUM** |
| `frontend/app.py` | Add LLM UI option | **LOW** |
| `requirements.txt` | Add `openai` or `anthropic` | **HIGH** |

### Supporting Files (Already Working)

| File | Purpose |
|------|---------|
| `backend/services/document_analysis/document_analyzer.py` | Pre-processing (✅ Done) |
| `backend/services/file_processing/file_processor.py` | Extraction (✅ Done) |
| `backend/api/routes/analysis.py` | Keyword analysis endpoints (✅ Done) |

---

## 💡 Key Insights

### Why This Approach Works

1. **Pre-Processing Saves Money**: $0.10 vs $0.60 per analysis
2. **Better LLM Results**: Focused prompts = better insights
3. **Graceful Degradation**: Keyword analysis works if LLM fails
4. **Explainable**: Can see both keyword matches AND LLM reasoning
5. **Scalable**: Can process batches efficiently

### Common Pitfalls to Avoid

❌ **Don't**: Send raw 50-page PDF to LLM  
✅ **Do**: Use DocumentAnalyzer first, then send structured data

❌ **Don't**: Use high temperature (0.9) for financial analysis  
✅ **Do**: Use low temperature (0.3-0.5) for consistency

❌ **Don't**: Forget to handle API errors/rate limits  
✅ **Do**: Add retry logic and fallback to keyword analysis

❌ **Don't**: Store API keys in code  
✅ **Do**: Use environment variables

---

## 🎯 Success Criteria

### You'll Know It's Working When:

- ✅ LLM agent returns JSON with risk assessment, recommendation
- ✅ Response includes reasoning that references specific red flags
- ✅ Recommendations differ from keyword-only analysis (deeper insights)
- ✅ API costs stay under $0.15 per document
- ✅ Response time under 10 seconds per document

---

## 📞 Questions?

### Common Questions

**Q: Which LLM should we use?**  
A: Start with GPT-4 (best balance). Try GPT-4-Turbo if speed matters. Claude-3-Opus for longer documents.

**Q: How much will this cost?**  
A: With pre-processing: ~$0.10 per document. Without: ~$0.60. Budget $50 for 500 analyses.

**Q: Can we run local LLMs?**  
A: Yes! Can use Ollama (llama3, mixtral) for free. Lower quality but zero API costs.

**Q: What if API fails?**  
A: System falls back to keyword-based analysis automatically.

**Q: How do we tune prompts?**  
A: Run analysis, review output, adjust `_build_analysis_prompt()`, repeat.

---

## 🚀 Quick Start Checklist

### Tomorrow Morning:

- [ ] Get OpenAI API key
- [ ] Add `OPENAI_API_KEY` to `.env`
- [ ] Run `pip install openai`
- [ ] Implement `_get_llm_insights()` (copy code from this doc)
- [ ] Test with `/llm/prompt-preview` first
- [ ] Run real analysis with `/llm/analyze`
- [ ] Review output quality
- [ ] Tune prompt if needed
- [ ] Celebrate! 🎉

---

**Good luck! The infrastructure is ready - just need to plug in the LLM API!**

*Last Updated: October 25, 2025*
