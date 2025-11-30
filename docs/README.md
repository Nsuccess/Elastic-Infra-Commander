# Blaxel Fleet Commander MCP Server

> Deploy games to multiple Blaxel sandboxes in parallel with live preview URLs

[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)]()
[![Success Rate](https://img.shields.io/badge/success%20rate-100%25-brightgreen)]()
[![Deploy Time](https://img.shields.io/badge/deploy%20time-~45s-blue)]()

## 🎉 Status: Fully Operational

**Test Results**: 100% Success Rate (3/3 parallel deployments)  
**Deployment Time**: ~45 seconds per sandbox  
**Game Accessibility**: Confirmed working with live preview URLs

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
# Required for deployment
BL_WORKSPACE=your-workspace
BL_API_KEY=your-api-key

# Optional for deployment logging and search
MISTRAL_API_KEY=your-mistral-key
QDRANT_URL=your-qdrant-url
QDRANT_API_KEY=your-qdrant-key

# Optional for observability
WANDB_API_KEY=your-wandb-key

# Optional for private repos
GITHUB_TOKEN=your-github-token
```

**Note**: Mistral and Qdrant are optional. If not configured, deployments continue normally without logging.

### 3. Run MCP Server
```bash
python -m src.server
```

### 4. Test Deployment
```bash
python test_official_pattern.py  # Test single deployment
python test_final_fleet_deploy.py  # Test parallel deployment
```

---

## MCP Tools

### Core Deployment Tools

### 1. fleet_list_sandboxes
Lists all sandboxes with latency measurements.

### 2. fleet_deploy_game ⭐
Deploys game to n fastest sandboxes in parallel.

```python
result = await fleet_deploy_game(
    repo_url="https://github.com/user/game.git",
    n=3
)
```

Returns live preview URLs with token authentication.

**Automatic Logging**: Every deployment logs 3 events to Qdrant:
- `DEPLOYMENT_START`: When deployment begins
- `DEPLOYMENT_SUCCESS`: When complete (includes URL and timing)
- `DEPLOYMENT_FAILURE`: When failed (includes error traceback)

### 3. fleet_verify_live
Verifies URLs are live and responding.

### Search & Intelligence Tools

### 4. fleet_search_logs 🔍
Search deployment history using natural language.

**Example queries**:
```
"Find npm build errors from last 6 hours"
"Show deployment failures in test-sandbox"
"Search for nginx startup issues"
```

**Parameters**:
- `query`: Natural language search
- `collection`: 'commands', 'stdout', or 'stderr'
- `sandbox_name`: Filter by sandbox
- `time_hours`: Filter by time range
- `limit`: Number of results

### 5. fleet_suggest_fix 💡
Get AI-powered fix suggestions from successful deployments.

**Example queries**:
```
"Suggest fixes for build failures"
"How to fix nginx not starting?"
"What worked for deployment errors?"
```

Returns commands that successfully solved similar problems, ranked by relevance.

---

## Architecture

The solution uses the **official Blaxel pattern** discovered from their NextJS example:

### Key Components

1. **Sandbox Creation with Preview Port**
```python
{
    "metadata": {"name": "sandbox-name"},
    "spec": {
        "runtime": {
            "image": "blaxel/node:latest",
            "memory": 4096,
            "ports": [
                {
                    "name": "preview",  # ← CRITICAL!
                    "target": 3000,
                    "protocol": "HTTP"
                }
            ]
        }
    }
}
```

2. **Direct Port 3000 Serving**
- No proxy needed
- Simple: `npx serve -s dist -l 3000`

3. **Token Authentication**
- `public: false` + preview token
- 24-hour token expiry
- Format: `{url}?bl_preview_token={token}`

---

## Critical Requirements

✅ **Preview Port Declaration**: Must be in sandbox spec  
✅ **Image**: Use `blaxel/node:latest`  
✅ **Direct Serving**: Port 3000 (no proxy)  
✅ **Token Auth**: `public: false` + token  
✅ **CORS Headers**: Include all Blaxel headers  
✅ **Wait Time**: 10 seconds for server startup  

---

## Test Results

```bash
python test_final_fleet_deploy.py
```

Expected output:
```
✅ Successful: 3
❌ Failed: 0
📊 Success Rate: 100.0%
🎉 ALL DEPLOYMENTS SUCCESSFUL!
```

---

## Project Structure

```
.
├── src/
│   ├── blaxel/
│   │   ├── tools.py          # MCP tools (fleet_deploy_game, etc.)
│   │   ├── types.py          # Type definitions
│   │   └── session_manager.py
│   ├── qdrant/
│   │   ├── tools.py          # Vector search tools
│   │   ├── embeddings.py     # Nebius AI embeddings
│   │   └── log_manager.py
│   ├── config/
│   │   └── permissions.py
│   └── server.py             # MCP server entry point
├── .kiro/
│   └── specs/                # Feature specifications
├── docs/                     # Documentation
├── test_official_pattern.py  # Single deployment test
├── test_final_fleet_deploy.py # Parallel deployment test
├── get_full_urls.py          # Get live preview URLs
├── config.yaml               # MCP server config
└── README.md
```

---

## Documentation

- **COMPLETE_SUCCESS_SUMMARY.md** - Full journey from problem to solution
- **FINAL_SOLUTION.md** - Complete technical implementation guide
- **COMPETITION_SUBMISSION.md** - Competition entry details

---

## Technology Stack

### Core (Required)
- **Blaxel SDK**: Sandbox orchestration and deployment
- **FastMCP**: MCP server framework
- **Node.js**: Runtime environment in sandboxes

### Logging & Search (Optional)
- **Mistral AI**: Text embeddings (1024 dimensions)
- **Qdrant**: Vector database for deployment logs
- **Weave (W&B)**: Observability and tracing

### Features
- ✅ Automatic deployment logging with semantic search
- ✅ AI-powered fix suggestions
- ✅ Graceful degradation if logging unavailable
- ✅ Full deployment traceability

---

## Common Issues

### Issue: 502 Error on Preview URL
**Cause**: Missing preview port in sandbox spec  
**Solution**: Add port declaration when creating sandbox

### Issue: 404 Not Found
**Cause**: Sandbox or preview was deleted  
**Solution**: Deploy fresh sandboxes

### Issue: Unauthorized Error
**Cause**: Missing or expired token  
**Solution**: Create new token and append to URL

---

## Credits

Solution discovered by analyzing the official Blaxel NextJS example:
- Repository: `blaxel-ai/sdk-typescript`
- Path: `tests/sandbox/nextjs-sandbox-test/`

---

## License

MIT

---

## Support

For issues or questions:
1. Check `FINAL_SOLUTION.md` for detailed troubleshooting and implementation
2. Review `COMPLETE_SUCCESS_SUMMARY.md` for the full journey and test results
3. See `COMPETITION_SUBMISSION.md` for project overview

---

**Status**: Production Ready 🚀  
**Last Updated**: November 25, 2025  
**Success Rate**: 100%
