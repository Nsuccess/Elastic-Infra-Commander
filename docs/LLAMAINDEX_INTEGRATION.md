# LlamaIndex Integration - Production RAG for Fleet Deployment Logging

## Overview

We've migrated from manual embeddings + Qdrant to a **production-grade RAG pipeline** using **LlamaIndex**, the industry standard for retrieval-augmented generation.

## Why LlamaIndex?

### Before: Manual Implementation
```python
# Manual embedding
embedding = embed_text(f"COMMAND: {command}")

# Manual Qdrant upsert
qdrant_client.upsert(
    collection_name="blaxel_commands",
    points=[PointStruct(id=uuid, vector=embedding, payload=data)]
)

# Manual search
results = qdrant_client.query_points(
    collection_name="blaxel_commands",
    query=embedding,
    with_payload=True
)
```

**Problems:**
- 150+ lines of boilerplate code
- Manual chunking and parsing
- No automatic source citation
- Hard to add features (reranking, hybrid search, etc.)
- Not following industry best practices

### After: LlamaIndex
```python
# One-line logging
index.log_deployment_event(
    event_type="SUCCESS",
    sandbox_name=sandbox_name,
    job_id=job_id,
    repo_url=repo_url,
    stdout=stdout,
    return_code=0
)

# One-line search with automatic source citation
results = index.search(
    query="npm build failures",
    sandbox_name="fleet-game-abc",
    time_hours=6
)
```

**Benefits:**
- 3× less code
- Automatic document parsing and chunking
- Built-in metadata filtering
- Automatic source citation
- Easy to extend (reranking, hybrid search, agents)
- Production-grade architecture

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Deployment Event                             │
│         (START, SUCCESS, FAILURE + metadata)                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  LlamaIndex Document                            │
│  - Text: Event description + outputs                            │
│  - Metadata: sandbox, job_id, return_code, timestamp, etc.      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              LlamaIndex NodeParser                              │
│  - Automatic text chunking (512 tokens)                         │
│  - Overlap handling (50 tokens)                                 │
│  - Metadata preservation                                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│         Mistral AI Embeddings (via LlamaIndex)                  │
│  - Model: mistral-embed                                         │
│  - Dimensions: 1024                                             │
│  - Automatic batching and retry                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│         Qdrant Vector Store (via LlamaIndex)                    │
│  - Collection: fleet_deployment_logs                            │
│  - Distance: Cosine similarity                                  │
│  - Metadata indexes: sandbox, event_type, return_code, etc.     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              LlamaIndex VectorStoreIndex                        │
│  - Semantic search with metadata filtering                      │
│  - Automatic source citation                                    │
│  - Response synthesis                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Components

### 1. FleetLogIndex

Production-grade wrapper around LlamaIndex for fleet deployment logs.

**Features:**
- Automatic collection management
- Document creation with rich metadata
- Semantic search with filtering
- Fix suggestions from successful deployments
- Graceful error handling

**Usage:**
```python
from src.qdrant.llamaindex_manager import get_fleet_index

# Get global index instance
index = get_fleet_index()

# Log deployment event
index.log_deployment_event(
    event_type="SUCCESS",
    sandbox_name="fleet-game-abc",
    job_id="550e8400-e29b-41d4-a716-446655440000",
    repo_url="https://github.com/user/game.git",
    stdout="Successfully deployed. URL: https://test.bl.run. Time: 45.2s",
    return_code=0,
    deploy_time=45.2,
    preview_url="https://test.bl.run?token=abc"
)

# Search with filters
results = index.search(
    query="npm build failures",
    sandbox_name="fleet-game-abc",
    event_type="FAILURE",
    time_hours=6,
    limit=10
)

# Get fix suggestions
suggestions = index.suggest_fixes(
    problem_description="npm build failed with module not found",
    limit=5
)
```

### 2. LlamaIndex Document Schema

Each deployment event is stored as a LlamaIndex Document:

```python
Document(
    text="""
    Event: SUCCESS
    Repository: https://github.com/user/game.git
    Output: Successfully deployed. URL: https://test.bl.run. Time: 45.2s
    Preview URL: https://test.bl.run?token=abc
    Deploy Time: 45.20s
    """,
    metadata={
        "event_type": "SUCCESS",
        "sandbox_name": "fleet-game-abc",
        "job_id": "550e8400-e29b-41d4-a716-446655440000",
        "repo_url": "https://github.com/user/game.git",
        "return_code": 0,
        "timestamp": 1732584045.456,
        "deploy_time": 45.2,
        "preview_url": "https://test.bl.run?token=abc",
        "has_error": False
    }
)
```

### 3. Metadata Filtering

LlamaIndex provides powerful metadata filtering:

```python
# Filter by sandbox
results = index.search(
    query="deployment",
    sandbox_name="fleet-game-abc"
)

# Filter by event type
results = index.search(
    query="errors",
    event_type="FAILURE"
)

# Filter by success/failure
results = index.search(
    query="deployment",
    return_code=0  # Only successful
)

# Filter by time range
results = index.search(
    query="deployment",
    time_hours=6  # Last 6 hours
)

# Combine filters
results = index.search(
    query="npm build",
    sandbox_name="fleet-game-abc",
    event_type="FAILURE",
    time_hours=24,
    limit=10
)
```

### 4. Automatic Source Citation

Every search result includes full source metadata:

```python
{
    "relevance_score": 0.8542,
    "text": "Event: SUCCESS\nRepository: ...",
    "event_type": "SUCCESS",
    "sandbox_name": "fleet-game-abc",
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "repo_url": "https://github.com/user/game.git",
    "return_code": 0,
    "timestamp": 1732584045.456,
    "deploy_time": 45.2,
    "preview_url": "https://test.bl.run?token=abc",
    "has_error": False,
    "formatted_time": "2025-11-26 01:20:45"
}
```

---

## MCP Tools

### fleet_search_logs

**LlamaIndex-powered semantic search** across deployment history.

**Features:**
- Natural language queries
- Metadata filtering (sandbox, event type, return code, time)
- Relevance-ranked results
- Automatic source citation

**Examples:**
```python
# Find build errors
fleet_search_logs(
    query="npm build failed",
    time_hours=6,
    limit=10
)

# Find successful deployments
fleet_search_logs(
    query="deployment success",
    sandbox_name="fleet-game-abc",
    return_code=0
)

# Find nginx issues
fleet_search_logs(
    query="nginx not starting",
    event_type="FAILURE"
)
```

### fleet_suggest_fix

**AI-powered fix suggestions** from successful deployments.

**Features:**
- Semantic similarity matching
- Only suggests from successful deployments (return_code=0)
- Automatic deduplication
- Relevance-ranked suggestions

**Examples:**
```python
# Get fix suggestions
fleet_suggest_fix(
    context="npm build failed with module not found",
    limit=5
)

# Sandbox-specific suggestions
fleet_suggest_fix(
    context="deployment timeout",
    sandbox_name="fleet-game-abc"
)
```

---

## Installation

### 1. Install Dependencies

```bash
# Install LlamaIndex and integrations
pip install llama-index llama-index-embeddings-mistralai llama-index-vector-stores-qdrant llama-index-llms-mistralai

# Or use pyproject.toml
pip install -e .
```

### 2. Environment Variables

```env
# Required for LlamaIndex
MISTRAL_API_KEY=your-mistral-api-key
QDRANT_URL=https://your-cluster.cloud.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key

# Optional
WANDB_API_KEY=your-wandb-key
```

### 3. Verify Installation

```bash
python test_llamaindex_integration.py
```

---

## Migration from Old System

### Backward Compatibility

The old `log_blaxel_operation()` interface still works:

```python
# Old interface (still works)
await log_blaxel_operation(
    sandbox_name=sandbox_name,
    command=f"DEPLOYMENT_SUCCESS: {repo_url}",
    job_id=job_id,
    stdout=stdout,
    stderr=stderr,
    return_code=0
)
```

This is automatically converted to LlamaIndex Documents internally.

### New Interface

For new code, use the FleetLogIndex directly:

```python
# New interface (recommended)
index = get_fleet_index()
index.log_deployment_event(
    event_type="SUCCESS",
    sandbox_name=sandbox_name,
    job_id=job_id,
    repo_url=repo_url,
    stdout=stdout,
    return_code=0,
    deploy_time=45.2,
    preview_url=preview_url
)
```

---

## Performance

### Logging Overhead

- **Document creation**: ~10ms
- **Embedding generation**: ~100-200ms (Mistral API)
- **Qdrant storage**: ~50-100ms
- **Total per event**: ~200-300ms

### Search Performance

- **Semantic search**: ~100-300ms
- **With metadata filters**: ~50-150ms
- **Fix suggestions**: ~100-300ms

### Storage

- **Per deployment**: 3 events (START, SUCCESS/FAILURE, outputs)
- **Per event**: ~1-2KB (including vector)
- **Total per deployment**: ~3-6KB

---

## Advanced Features

### 1. Hybrid Search (Future)

LlamaIndex makes it easy to add keyword + semantic search:

```python
from llama_index.core.retrievers import QueryFusionRetriever

# Combine semantic and keyword search
retriever = QueryFusionRetriever(
    retrievers=[vector_retriever, keyword_retriever],
    similarity_top_k=10
)
```

### 2. Reranking (Future)

Add reranking for better results:

```python
from llama_index.core.postprocessor import SimilarityPostprocessor

query_engine = index.as_query_engine(
    node_postprocessors=[
        SimilarityPostprocessor(similarity_cutoff=0.7)
    ]
)
```

### 3. Response Synthesis (Future)

Generate natural language summaries:

```python
query_engine = index.as_query_engine()
response = query_engine.query("Why did the last deployment fail?")

print(response.response)  # Natural language answer
print(response.source_nodes)  # Citations
```

### 4. Agents (Future)

Build autonomous troubleshooting agents:

```python
from llama_index.core.agent import ReActAgent

agent = ReActAgent.from_tools(
    tools=[search_tool, suggest_fix_tool],
    llm=llm,
    verbose=True
)

response = agent.chat("Debug the last deployment failure")
```

---

## Testing

### Run Tests

```bash
# Test LlamaIndex integration
python test_llamaindex_integration.py

# Test backward compatibility
python test_deployment_logging.py

# Test search tools
python test_search_tools.py
```

### Expected Output

```
🚀 Testing LlamaIndex Integration for Deployment Logging
✅ LlamaIndex initialized successfully
   Collection: fleet_deployment_logs
   Embed Model: Mistral AI (mistral-embed, 1024 dims)
   Vector Store: Qdrant Cloud

📝 Test 1: Logging Deployment Events
   ✅ START event logged
   ✅ SUCCESS event logged

🔍 Test 2: Semantic Search
   Found 5 results
   ✅ Semantic search works

🎯 Test 3: Metadata Filtering
   ✅ Sandbox filtering works
   ✅ Event type filtering works
   ✅ Return code filtering works
   ✅ Time filtering works

💡 Test 4: Fix Suggestions
   ✅ Fix suggestions work
   ✅ All suggestions are from successful deployments

📚 Test 5: Source Citation
   ✅ Source citation works (sandbox + timestamp + job_id)

🎉 Production-grade RAG pipeline is operational!
```

---

## Troubleshooting

### Issue: LlamaIndex not initialized

```
⚠️  LlamaIndex not initialized (missing credentials)
```

**Solution**: Set environment variables in `.env`:
```env
MISTRAL_API_KEY=your-key
QDRANT_URL=your-url
QDRANT_API_KEY=your-key
```

### Issue: Import errors

```
ModuleNotFoundError: No module named 'llama_index'
```

**Solution**: Install LlamaIndex:
```bash
pip install llama-index llama-index-embeddings-mistralai llama-index-vector-stores-qdrant
```

### Issue: Slow search

**Solution**: Add metadata filters to narrow results:
```python
results = index.search(
    query="deployment",
    sandbox_name="specific-sandbox",  # Filter
    time_hours=6,  # Filter
    limit=10
)
```

---

## Best Practices

### 1. Use Metadata Filters

Always filter by time range for better performance:
```python
results = index.search(
    query="errors",
    time_hours=24,  # Last 24 hours only
    limit=10
)
```

### 2. Descriptive Queries

Use descriptive natural language queries:
```python
# ❌ Bad
query="error"

# ✅ Good
query="npm build failed with module not found"
```

### 3. Combine Filters

Combine multiple filters for precise results:
```python
results = index.search(
    query="deployment issues",
    sandbox_name="fleet-game-abc",
    event_type="FAILURE",
    time_hours=6,
    limit=10
)
```

### 4. Check Source Citations

Always check source metadata for context:
```python
for result in results:
    print(f"Sandbox: {result['sandbox_name']}")
    print(f"Time: {result['formatted_time']}")
    print(f"Job ID: {result['job_id']}")
```

---

## Comparison: Before vs After

| Feature | Before (Manual) | After (LlamaIndex) |
|---------|----------------|-------------------|
| **Code Lines** | 150+ lines | 30 lines |
| **Document Parsing** | Manual | Automatic |
| **Chunking** | Manual | Automatic (SentenceSplitter) |
| **Embeddings** | Manual API calls | LlamaIndex wrapper |
| **Storage** | Manual upsert | Automatic |
| **Search** | Custom code | One-line |
| **Metadata Filtering** | Manual | Built-in |
| **Source Citation** | Manual | Automatic |
| **Reranking** | Not available | Easy to add |
| **Hybrid Search** | Not available | Easy to add |
| **Response Synthesis** | Not available | Easy to add |
| **Agents** | Not available | Easy to add |
| **Maintainability** | Hard | Easy |
| **Industry Standard** | No | Yes ✅ |

---

## Conclusion

The LlamaIndex integration provides:

✅ **Production-grade architecture** - Industry standard RAG pipeline  
✅ **3× less code** - Cleaner, more maintainable  
✅ **Better features** - Automatic parsing, chunking, source citation  
✅ **Future-proof** - Easy to add reranking, hybrid search, agents  
✅ **Backward compatible** - Old interface still works  
✅ **Well-tested** - Comprehensive test suite  
✅ **Documented** - Full documentation and examples  

This is **exactly** how LlamaIndex is meant to be used in production systems.

---

**Last Updated**: November 26, 2025  
**Version**: 2.0.0 (LlamaIndex Migration)  
**Status**: 🚀 Production Ready
