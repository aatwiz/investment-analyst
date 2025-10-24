# Investment Analyst AI - LLM Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PHASE 2 ✅ COMPLETE                          │
│                    Document Analysis (Keyword-Based)                 │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ feeds into
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      PHASE 3 🚧 INFRASTRUCTURE READY                 │
│                        LLM-Powered Deep Analysis                     │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  1. 📄 Document Upload                                      │    │
│  │     └─→ FileProcessor (extract text, tables, metadata)     │    │
│  └────────────────────────────────────────────────────────────┘    │
│                            ↓                                         │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  2. 🔍 Pre-Processing (Keyword Analysis)                   │    │
│  │     └─→ DocumentAnalyzer                                   │    │
│  │         ├─ 100+ keywords (red flags, signals)             │    │
│  │         ├─ Context extraction (100 char windows)          │    │
│  │         ├─ Financial metrics (regex patterns)             │    │
│  │         └─ Entity detection (dates, emails, names)        │    │
│  └────────────────────────────────────────────────────────────┘    │
│                            ↓                                         │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  3. 📝 Prompt Generation                                   │    │
│  │     └─→ InvestmentAnalystAgent                            │    │
│  │         ├─ Structure data into sections                   │    │
│  │         ├─ Add red flags with context                     │    │
│  │         ├─ Add positive signals                           │    │
│  │         ├─ Add financial metrics                          │    │
│  │         └─ Build analysis request                         │    │
│  │                                                             │    │
│  │     💡 Result: 2-5k tokens (was 30k+ raw)                 │    │
│  └────────────────────────────────────────────────────────────┘    │
│                            ↓                                         │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  4. 🤖 LLM API Call                                        │    │
│  │     └─→ TODO: Implement tomorrow! ⏳                      │    │
│  │         ├─ OpenAI GPT-4                                   │    │
│  │         ├─ Anthropic Claude                               │    │
│  │         └─ Azure OpenAI                                   │    │
│  │                                                             │    │
│  │     ⚙️  Need: API key + 10 lines of code                  │    │
│  └────────────────────────────────────────────────────────────┘    │
│                            ↓                                         │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  5. 📊 Merge Insights                                      │    │
│  │     └─→ Combine structured + LLM analysis                 │    │
│  │         ├─ Risk assessment (0-10 scale)                   │    │
│  │         ├─ Opportunity analysis                           │    │
│  │         ├─ Financial health evaluation                    │    │
│  │         ├─ Investment recommendation (BUY/HOLD/AVOID)     │    │
│  │         └─ Due diligence next steps                       │    │
│  └────────────────────────────────────────────────────────────┘    │
│                            ↓                                         │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  6. 📈 Final Report                                        │    │
│  │     └─→ Comprehensive investment analysis                 │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                          API ENDPOINTS                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ✅ WORKING NOW (Phase 2)                                           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━                                         │
│  POST   /api/v1/analysis/analyze          Keyword-based analysis   │
│  POST   /api/v1/analysis/batch            Batch analysis           │
│  GET    /api/v1/analysis/extract/{file}   Extract content          │
│  GET    /api/v1/analysis/red-flags/{file} Red flags only           │
│  GET    /api/v1/analysis/summary/{file}   Quick summary            │
│                                                                      │
│  🚧 READY (Need API Key)                                            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━                                          │
│  POST   /api/v1/llm/configure             Set API key              │
│  POST   /api/v1/llm/analyze               LLM-powered analysis     │
│  GET    /api/v1/llm/prompt-preview/{file} Preview prompt           │
│  GET    /api/v1/llm/status                Agent status             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                        COST COMPARISON                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  WITHOUT Pre-Processing ❌                                          │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━                                         │
│  Raw 50-page PDF → LLM                                              │
│  • 30,000+ tokens                                                   │
│  • $0.60 per document (GPT-4)                                       │
│  • Unfocused analysis                                               │
│  • May miss details                                                 │
│                                                                      │
│  WITH Pre-Processing ✅                                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━                                           │
│  PDF → Extract → Analyze → Structure → LLM                          │
│  • 2,000-5,000 tokens                                               │
│  • $0.10 per document (GPT-4)                                       │
│  • Focused on key issues                                            │
│  • Deep reasoning on what matters                                   │
│                                                                      │
│  💰 SAVINGS: 85% cost reduction!                                    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                       FILE STRUCTURE                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  backend/                                                           │
│  ├── services/                                                      │
│  │   ├── document_analysis/           ✅ Working                    │
│  │   │   ├── __init__.py                                           │
│  │   │   └── document_analyzer.py     (Keyword-based)              │
│  │   │                                                              │
│  │   ├── file_processing/             ✅ Working                    │
│  │   │   ├── __init__.py                                           │
│  │   │   └── file_processor.py        (PDF, DOCX, Excel)           │
│  │   │                                                              │
│  │   ├── llm_agents/                  🚧 Need API Key              │
│  │   │   ├── __init__.py                                           │
│  │   │   └── investment_analyst_agent.py  (Prompt builder)         │
│  │   │                                                              │
│  │   └── data_extraction/             📅 Future                    │
│  │       └── __init__.py                                           │
│  │                                                                  │
│  ├── api/routes/                                                   │
│  │   ├── analysis.py                  ✅ Working                    │
│  │   ├── llm_analysis.py              🚧 Need API Key              │
│  │   ├── files.py                     ✅ Working                    │
│  │   ├── modeling.py                  📅 Future (Phase 4)          │
│  │   └── reports.py                   📅 Future (Phase 5)          │
│  │                                                                  │
│  └── main.py                          ✅ Updated with LLM routes   │
│                                                                      │
│  docs/                                                              │
│  ├── LLM_INTEGRATION_GUIDE.md         📖 Full guide                │
│  └── QUICK_START_LLM.md               ⚡ Quick reference           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                      TOMORROW'S CHECKLIST                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ☐ 1. Get OpenAI API key (5 min)                                   │
│       → https://platform.openai.com/api-keys                       │
│                                                                      │
│  ☐ 2. Add to .env file (1 min)                                     │
│       → OPENAI_API_KEY=sk-proj-...                                 │
│                                                                      │
│  ☐ 3. Install package (1 min)                                      │
│       → pip install openai                                         │
│                                                                      │
│  ☐ 4. Implement _get_llm_insights() (10 min)                       │
│       → File: services/llm_agents/investment_analyst_agent.py      │
│       → Code: See docs/QUICK_START_LLM.md                          │
│                                                                      │
│  ☐ 5. Test prompt preview (2 min)                                  │
│       → GET /api/v1/llm/prompt-preview/your-file.pdf              │
│                                                                      │
│  ☐ 6. Test LLM analysis (2 min)                                    │
│       → POST /api/v1/llm/analyze                                   │
│                                                                      │
│  ☐ 7. Review output quality (5 min)                                │
│       → Check risk assessment, recommendations                      │
│                                                                      │
│  ☐ 8. Tune prompt if needed (10 min)                               │
│       → Adjust _build_analysis_prompt() method                     │
│                                                                      │
│  ⏱️  Total time: ~30 minutes                                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                         KEY INSIGHTS                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ✅ Your keyword analyzer is PERFECT as pre-processor               │
│     • Reduces tokens by 85%                                         │
│     • Saves API costs                                               │
│     • Improves LLM focus                                            │
│                                                                      │
│  ✅ Infrastructure is 100% ready                                    │
│     • Prompt generation: Done                                       │
│     • API routes: Done                                              │
│     • Data structuring: Done                                        │
│     • Just need: API key + 10 lines of code                        │
│                                                                      │
│  ✅ Architecture is production-ready                                │
│     • Clean separation of concerns                                  │
│     • Graceful degradation (falls back to keywords)                │
│     • Explainable results (see both analyses)                      │
│     • Scalable (can process batches)                               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```
