# LlamaIndex Installation Guide

## Quick Start

### 1. Install Dependencies

```bash
# Option 1: Install from pyproject.toml (recommended)
pip install -e .

# Option 2: Install manually
pip install llama-index llama-index-embeddings-mistralai llama-index-vector-stores-qdrant llama-index-llms-mistralai
```

### 2. Verify Installation

```bash
python -c "import llama_index; print('✅ LlamaIndex installed')"
python -c "from llama_index.embeddings.mistralai import MistralAIEmbedding; print('✅ Mistral integration installed')"
python -c "from llama_index.vector_stores.qdrant import QdrantVectorStore; print('✅ Qdrant integration installed')"
```

### 3. Set Environment Variables

Add to `.env`:
```env
# Required for LlamaIndex
MISTRAL_API_KEY=your-mistral-api-key
QDRANT_URL=https://your-cluster.cloud.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key

# Optional
WANDB_API_KEY=your-wandb-key
GITHUB_TOKEN=your-github-token
```

### 4. Test Integration

```bash
# Run comprehensive tests
python test_llamaindex_integration.py

# Expected output:
# ✅ LlamaIndex initialized successfully
# ✅ Document creation and logging
# ✅ Semantic search
# ✅ Metadata filtering
# ✅ Fix suggestions
# 🎉 Production-grade RAG pipeline is operational!
```

---

## Troubleshooting

### Issue: Import Error

```
ModuleNotFoundError: No module named 'llama_index'
```

**Solution**:
```bash
pip install llama-index
```

### Issue: Mistral Integration Not Found

```
ModuleNotFoundError: No module named 'llama_index.embeddings.mistralai'
```

**Solution**:
```bash
pip install llama-index-embeddings-mistralai
```

### Issue: Qdrant Integration Not Found

```
ModuleNotFoundError: No module named 'llama_index.vector_stores.qdrant'
```

**Solution**:
```bash
pip install llama-index-vector-stores-qdrant
```

### Issue: Missing Environment Variables

```
⚠️  Warning: Missing environment variables: MISTRAL_API_KEY
```

**Solution**: Add to `.env`:
```env
MISTRAL_API_KEY=your-key
QDRANT_URL=your-url
QDRANT_API_KEY=your-key
```

---

## Verify Everything Works

```bash
# 1. Test LlamaIndex integration
python test_llamaindex_integration.py

# 2. Test deployment logging
python test_deployment_logging.py

# 3. Test search tools
python test_search_tools.py

# 4. Run MCP server
python -m src.server
```

---

## Next Steps

1. Read **LLAMAINDEX_INTEGRATION.md** for complete documentation
2. Read **LLAMAINDEX_MIGRATION_COMPLETE.md** for migration details
3. Try the new search tools:
   - `fleet_search_logs`: Semantic search
   - `fleet_suggest_fix`: AI-powered fix suggestions

---

**Status**: ✅ Ready to use!
