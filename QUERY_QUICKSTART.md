# Quick Start: Cost-Efficient Querying

## 🎯 TL;DR

**Problem:** Full document analysis costs $0.025 per query and takes 30 seconds.  
**Solution:** RAG querying costs $0.0003 per query and takes 2 seconds.  
**Result:** 8x cheaper, 15x faster! ✅

---

## 📋 Two-Tier Architecture

### 1. Initial Analysis (Expensive but Necessary)
**When:** Document is first uploaded  
**Purpose:** Generate comprehensive executive summary  
**Cost:** $0.02-0.05 per document  
**Frequency:** ONCE per document  

**Endpoint:** `POST /api/v1/analysis/analyze`

```bash
curl -X POST http://localhost:8000/api/v1/analysis/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "financial_statement.pdf",
    "analysis_type": "comprehensive"
  }'
```

### 2. Query Documents (Cheap and Fast)
**When:** User asks questions about documents  
**Purpose:** Answer specific questions  
**Cost:** $0.0003 per query  
**Frequency:** MANY times  

**Endpoint:** `POST /api/v1/query/ask`

```bash
curl -X POST http://localhost:8000/api/v1/query/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What was the company'\''s net profit in Q1?",
    "document_ids": [123],
    "max_chunks": 5
  }'
```

---

## 💰 Cost Comparison

| Operation | Model | Tokens | Cost | Time |
|-----------|-------|--------|------|------|
| **Full Analysis** | GPT-4o-mini | ~12,500 | $0.025 | 30s |
| **RAG Query** | GPT-4o-mini | ~1,500 | $0.0003 | 2s |

**Monthly Costs (1000 queries):**
- Old way (full doc every time): **$25.00/month** 😱
- New way (RAG queries): **$0.30/month** ✅

**Savings: 98%!**

---

## 🚀 Usage Examples

### Simple Question
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/query/ask",
    json={
        "question": "What is Baladna's revenue growth?",
        "max_chunks": 5
    }
)

print(response.json()["answer"])
# Output: "Baladna's revenue grew 8% YoY to QR 642.5M in H1 2025..."
```

### Search Specific Documents
```python
response = requests.post(
    "http://localhost:8000/api/v1/query/ask",
    json={
        "question": "What are the main risk factors?",
        "document_ids": [123, 456],  # Only search these docs
        "max_chunks": 5
    }
)
```

### Batch Questions
```python
response = requests.post(
    "http://localhost:8000/api/v1/query/batch",
    json={
        "questions": [
            "What is the revenue?",
            "What are the profit margins?",
            "Who are the competitors?"
        ],
        "document_ids": [123]
    }
)

# Get all answers at once
for result in response.json()["results"]:
    print(f"Q: {result['query']}")
    print(f"A: {result['answer']}\n")
```

### Chat Interface (with history)
```python
conversation_history = [
    {"role": "user", "content": "Tell me about Baladna's performance"},
    {"role": "assistant", "content": "Baladna showed strong performance..."}
]

response = requests.post(
    "http://localhost:8000/api/v1/query/chat",
    json={
        "question": "What about their expansion plans?",
        "conversation_history": conversation_history,
        "document_ids": [123]
    }
)
```

---

## 📊 How It Works

### Behind the Scenes

1. **Your Question**
   ```
   "What was Baladna's profit in Q1 2025?"
   ```

2. **Vector Search** (Fast!)
   ```
   Searches document_embeddings table
   Finds 5 most relevant chunks (~2.5K chars)
   ```

3. **LLM Analysis** (Cheap!)
   ```
   Sends only relevant chunks to GPT-4o-mini
   Gets focused answer
   Cost: $0.0003
   ```

4. **Response**
   ```json
   {
     "answer": "Baladna reported net profit of QR 331.2M...",
     "chunks_used": 3,
     "cost_usd": 0.00037,
     "response_time_ms": 1847,
     "sources": [...]
   }
   ```

---

## 🎨 Frontend Integration

### React Example
```typescript
const queryDocument = async (question: string) => {
  const response = await fetch('/api/v1/query/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      max_chunks: 5,
      include_sources: true
    })
  });
  
  const data = await response.json();
  
  return {
    answer: data.answer,
    cost: data.cost_usd,
    responseTime: data.response_time_ms,
    sources: data.sources
  };
};

// Usage
const result = await queryDocument("What is the company's revenue?");
console.log(`Answer: ${result.answer}`);
console.log(`Cost: $${result.cost.toFixed(4)}`);
console.log(`Time: ${result.responseTime}ms`);
```

---

## 📈 Monitoring Costs

### Get Usage Stats
```bash
curl http://localhost:8000/api/v1/query/stats?days=30
```

### Estimate Costs
```bash
curl -X POST http://localhost:8000/api/v1/query/estimate-cost \
  -H "Content-Type: application/json" \
  -d '{
    "questions": [
      "Question 1?",
      "Question 2?",
      "Question 3?"
    ]
  }'

# Response:
{
  "total_queries": 3,
  "estimated_cost_per_query": 0.0003,
  "estimated_total_cost_usd": 0.0009
}
```

---

## 🔧 Configuration

### Adjust Chunk Size
```python
# backend/services/embeddings/embedding_service.py
CHUNK_SIZE = 500  # Characters per chunk (default)
CHUNK_OVERLAP = 50  # Overlap between chunks

# Smaller chunks = more precise but more queries
# Larger chunks = more context per query
```

### Adjust LLM Settings
```python
# In RAGQueryAgent
await self.client.chat.completions.create(
    model="gpt-4o-mini",  # Or "gpt-4o" for higher quality
    temperature=0.3,       # Lower = more deterministic
    max_tokens=1000        # Max response length
)
```

---

## ⚡ Performance Tips

### 1. Cache Frequent Queries
```python
# TODO: Add Redis caching for common questions
cache_key = f"query:{hash(question)}"
cached_answer = redis.get(cache_key)
if cached_answer:
    return cached_answer  # Cost: $0!
```

### 2. Use Batch Endpoint
```python
# More efficient than multiple individual calls
questions = [
    "What is the revenue?",
    "What are the risks?",
    "Who are competitors?"
]

# Process all at once
results = await rag_agent.batch_query(questions)
```

### 3. Limit Document Scope
```python
# Search specific documents only
{
    "question": "...",
    "document_ids": [123, 456]  # Faster, more relevant
}
```

---

## 🆚 When to Use Each Method

### Use Full Analysis When:
- ✅ First time uploading document
- ✅ Need comprehensive executive summary
- ✅ Want full risk assessment
- ✅ Generating investment memo

### Use RAG Queries When:
- ✅ Asking specific questions
- ✅ Looking up particular metrics
- ✅ Comparing across documents
- ✅ Chat/conversational interface
- ✅ Real-time user queries

---

## 📚 Additional Resources

- **Full Strategy:** See `COST_OPTIMIZATION_STRATEGY.md`
- **RAG Agent Code:** `backend/services/llm_agents/rag_agent.py`
- **Query API:** `backend/api/routes/query.py`
- **Embedding Service:** `backend/services/embeddings/embedding_service.py`

---

## 🎯 Bottom Line

**Initial Analysis:** $0.025 once per document (worth it for quality)  
**All Queries After:** $0.0003 each (cheap and fast!)  

**Total monthly cost for 1000 queries:** **< $1** 🎉

---

**Last Updated:** October 25, 2025  
**Status:** ✅ Implemented and Ready to Use
