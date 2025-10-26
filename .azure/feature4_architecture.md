# Feature 4: Financial Modeling - Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Streamlit)                         │
│                     http://localhost:8501                            │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ HTTP Requests
                                   │
┌─────────────────────────────────────────────────────────────────────┐
│                         API LAYER (FastAPI)                          │
│                     http://localhost:8000/api/v1                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  POST /modeling/extract                                              │
│  ├─ Extract financial data from documents                           │
│  └─ Uses FinancialDataExtractor + GPT-4o-mini                       │
│                                                                       │
│  POST /modeling/generate                                             │
│  ├─ Generate 36-month projection model                              │
│  └─ Uses ProjectionEngine                                            │
│                                                                       │
│  POST /modeling/scenario                                             │
│  ├─ Run best/base/worst scenario analysis                           │
│  └─ Uses ProjectionEngine.generate_scenario_comparison()            │
│                                                                       │
│  POST /modeling/export                                               │
│  ├─ Export to Excel (multi-sheet) or CSV                            │
│  └─ Uses pandas + openpyxl                                           │
│                                                                       │
│  GET /modeling/templates                                             │
│  └─ Return available model templates                                 │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ Calls
                                   │
┌─────────────────────────────────────────────────────────────────────┐
│                        BUSINESS LOGIC LAYER                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │           ProjectionEngine (417 lines)                       │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │                                                               │   │
│  │  + generate_projections(assumptions, months, scenario)       │   │
│  │    ├─ Monthly revenue growth modeling                        │   │
│  │    ├─ P&L calculation (Rev → COGS → GP → OpEx → EBITDA)    │   │
│  │    ├─ Cash flow (Opening + EBITDA + Equity - Capex = Close) │   │
│  │    ├─ Working capital changes                                │   │
│  │    ├─ Funding rounds (equity + debt)                         │   │
│  │    └─ Tax and depreciation                                   │   │
│  │                                                               │   │
│  │  + calculate_key_metrics(projections)                        │   │
│  │    ├─ Total revenue, CAGR                                    │   │
│  │    ├─ Months to profitability                                │   │
│  │    ├─ Cash runway                                            │   │
│  │    └─ Min/max cash balances                                  │   │
│  │                                                               │   │
│  │  + generate_scenario_comparison(assumptions, months)         │   │
│  │    ├─ BASE: As provided                                      │   │
│  │    ├─ BEST: +50% growth, -10% costs                         │   │
│  │    └─ WORST: -50% growth, +20% costs                        │   │
│  │                                                               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │        FinancialDataExtractor (219 lines)                    │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │                                                               │   │
│  │  + extract_from_document(file_path, doc_type)               │   │
│  │    ├─ Read CSV, Excel, TXT, PDF                             │   │
│  │    ├─ Call OpenAI GPT-4o-mini                               │   │
│  │    ├─ Parse unstructured financial data                      │   │
│  │    └─ Return structured JSON                                 │   │
│  │                                                               │   │
│  │  + parse_csv_financial_model(file_path)                     │   │
│  │    ├─ Handle user's CSV template format                      │   │
│  │    └─ Extract monthly arrays                                 │   │
│  │                                                               │   │
│  │  + infer_assumptions_from_historical(data)                   │   │
│  │    ├─ Calculate growth rates                                 │   │
│  │    ├─ Compute margins                                        │   │
│  │    └─ Return ModelAssumptions dict                           │   │
│  │                                                               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
         ┌────────────────────┐       ┌────────────────────┐
         │   OpenAI API       │       │   File System      │
         │   (GPT-4o-mini)    │       │   (Excel/CSV)      │
         └────────────────────┘       └────────────────────┘


═══════════════════════════════════════════════════════════════════════
                            DATA MODELS
═══════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────┐
│                        ModelAssumptions                              │
├─────────────────────────────────────────────────────────────────────┤
│  - revenue_start: float                                              │
│  - revenue_growth_rate: float                                        │
│  - cogs_percent: float                                               │
│  - opex_fixed: float                                                 │
│  - opex_variable_percent: float                                      │
│  - days_receivables: int                                             │
│  - days_payables: int                                                │
│  - equity_raises: List[Dict]  # [{"month": 6, "amount": 500000}]   │
│  - debt_raises: List[Dict]                                           │
│  - capex_schedule: List[Dict]                                        │
│  - tax_rate: float                                                   │
│  - depreciation_rate: float                                          │
│  - starting_cash: float                                              │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ Generates
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      MonthlyProjection (x36)                         │
├─────────────────────────────────────────────────────────────────────┤
│  INCOME STATEMENT                                                    │
│  - revenue                     CASH FLOW                            │
│  - cogs                        - opening_cash                        │
│  - gross_profit                - ebitda_cash                         │
│  - operating_expenses          - working_capital_change              │
│  - ebitda                      - equity_raised                       │
│  - depreciation                - debt_raised                         │
│  - ebit                        - interest_paid                       │
│  - interest_expense            - tax_paid                            │
│  - ebt                         - capex                               │
│  - tax                         - closing_cash                        │
│  - net_income                  - cash_flow_movement                  │
│                                - free_cash_flow                      │
│  METRICS                       - cash_runway_months                  │
│  - burn_rate                                                         │
└─────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════
                        FRONTEND UI STRUCTURE
═══════════════════════════════════════════════════════════════════════

💰 Financial Modeling Page
│
├─ 📊 Build Model Tab
│  ├─ Left Column: Configuration Form
│  │  ├─ Model name input
│  │  ├─ Projection period slider (12-60 months)
│  │  ├─ Revenue assumptions (start, growth rate)
│  │  ├─ Cost assumptions (COGS %, OpEx)
│  │  ├─ Funding (starting cash, equity raises)
│  │  ├─ Capex schedule
│  │  ├─ Tax rate
│  │  └─ [Generate Projections] button
│  │
│  └─ Right Column: Model Preview
│     ├─ Key Metrics (3 cards)
│     ├─ First 12 Months Table
│     ├─ Cash Balance Chart
│     ├─ Revenue Growth Chart
│     └─ Export buttons (Excel, CSV)
│
├─ 📈 Scenario Analysis Tab
│  ├─ Base assumptions display
│  ├─ Scenario selection (best/base/worst)
│  ├─ [Run Scenario Analysis] button
│  ├─ Comparison table
│  ├─ Cash balance comparison chart
│  └─ Revenue comparison chart
│
├─ 📁 Templates Tab
│  ├─ SaaS template card
│  ├─ E-commerce template card
│  ├─ Marketplace template card
│  └─ Generic template card
│
└─ 📥 Import from Documents Tab
   ├─ Document selector (from Feature 2)
   ├─ Document type dropdown
   ├─ [Extract Financial Data] button
   ├─ Extracted data display (JSON)
   ├─ Inferred assumptions display
   └─ [Build Model from This Data] button


═══════════════════════════════════════════════════════════════════════
                         INTEGRATION POINTS
═══════════════════════════════════════════════════════════════════════

Feature 2 (Document Upload)
     │
     │ GET /documents/list
     │ Returns uploaded documents
     ▼
Import from Documents Tab
     │
     │ POST /modeling/extract
     │ Extract financial data with GPT-4o-mini
     ▼
Inferred Assumptions
     │
     │ Import to Build Model
     ▼
Generate Projections
     │
     │ POST /modeling/generate
     ▼
Financial Model
     │
     │ POST /modeling/scenario
     ▼
Scenario Comparison
     │
     │ POST /modeling/export
     ▼
Excel/CSV File
     │
     │ (Future) POST /reports/generate
     ▼
Feature 5 (Investment Memo)


═══════════════════════════════════════════════════════════════════════
                          WORKFLOW EXAMPLE
═══════════════════════════════════════════════════════════════════════

1. User uploads pitch deck (Feature 2)
   → Document saved to storage

2. Navigate to "Import from Documents" tab
   → Select uploaded pitch deck
   → Click "Extract Financial Data"
   → GPT-4o-mini parses: Revenue $100K, Growth 15%, etc.

3. Click "Build Model from This Data"
   → Assumptions imported to Build Model tab

4. Review/adjust assumptions
   → Add equity raise: Month 6, $500K
   → Add capex: Month 3, $100K

5. Click "Generate Projections"
   → 36-month model created
   → Charts display
   → Metrics calculated

6. Switch to "Scenario Analysis" tab
   → Select: base, best, worst
   → Click "Run Scenario Analysis"
   → Compare outcomes

7. Export results
   → Click "Download Excel"
   → Multi-sheet workbook saved
   → Share with investment committee
