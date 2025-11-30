---
title: Blaxel Fleet Commander
emoji: 🚀
colorFrom: indigo
colorTo: purple
sdk: static
pinned: false
license: mit
tags:
  - building-mcp-track-enterprise
  - building-mcp-track-creative
---

# 🚀 Blaxel Fleet Commander

> **Turn Claude into a true deployment co-pilot.** From a simple prompt, you can provision cloud sandboxes, deploy apps, or spin up entire fleets—instantly and in parallel. It works for both experts managing production environments and developers who hate DevOps. Claude understands your intent, executes in parallel, and keeps everything observable.

[![Track](https://img.shields.io/badge/Track%201-Building%20MCP-blueviolet)]()
[![Enterprise](https://img.shields.io/badge/Category-Enterprise-blue)]()
[![Creative](https://img.shields.io/badge/Category-Creative-orange)]()
[![Blaxel](https://img.shields.io/badge/Sponsor-Blaxel-purple)]()
[![LlamaIndex](https://img.shields.io/badge/Sponsor-LlamaIndex-teal)]()

---

## 📋 Hackathon Submission Info

| Field | Details |
|-------|---------|
| **Hackathon** | MCP's 1st Birthday - Hosted by Anthropic and Gradio |
| **Track** | Track 1: Building MCP |
| **Categories** | Enterprise, Creative |
| **Team** | [InxCodm](https://huggingface.co/InxCodm) |
| **Demo Video** | [🎥 Watch on YouTube](https://youtu.be/FxCvfqcH0Vo) |
| **Social Post** | [View on X/Twitter](https://x.com/SuccessVsdworld/status/1995277010520936536) |

### Why These Categories?

| Category | How Fleet Commander Fits |
|----------|-------------------------|
| **🏢 Enterprise** | Platform teams managing staging/production fleets, parallel deployments, infrastructure automation at scale |
| **🎨 Creative** | Designers & creators deploying portfolio sites, demos, and experiments without touching a terminal |

### 🏆 Eligible for Sponsor Prizes

| Sponsor Prize | Eligibility |
|---------------|-------------|
| **Blaxel Choice Award ($2,500)** | ✅ Core integration - Blaxel sandboxes for deployment |
| **LlamaIndex Award ($1,000)** | ✅ Full RAG pipeline with LlamaIndex |
| **Best MCP Server - Enterprise ($750)** | ✅ Fleet management & parallel deployment |
| **Best MCP Server - Creative ($750)** | ✅ Zero-config deployment for creators |

### Sponsor Technologies Used

| Sponsor | Integration |
|---------|-------------|
| **Blaxel** | Cloud sandbox provisioning & parallel deployment |
| **LlamaIndex** | Production RAG pipeline for semantic search |
| **Mistral AI** | Text embeddings (1024 dimensions) |
| **Qdrant** | Vector database for deployment logs |

---

## What is Blaxel Fleet Commander?

**Blaxel Fleet Commander** transforms Claude into a true deployment co-pilot, solving one of the most persistent challenges in modern software delivery: the complexity barrier between human intent and live production URLs.

### The Problem We Solve

Whether you're a platform engineer managing hundreds of staging environments or a frontend developer who dreads anything beyond `npm start`, deployment has always been the same story: **tedious, error-prone, and time-consuming**.

You know what you want to achieve, but getting there means:
- Clicking through cloud consoles
- Managing SSH keys and credentials
- Writing YAML pipelines nobody understands
- Waiting for CI/CD queues
- Debugging cryptic build failures
- And worst of all—**doing everything sequentially, one environment at a time**

**What if you could simply describe what you want in natural language and have it deployed instantly across your entire fleet?**

### Our Solution

Blaxel Fleet Commander is a **Model Context Protocol (MCP) server** that bridges the gap between natural language and cloud deployment. It transforms Claude into an actual operator for your infrastructure, enabling you to:

- **Provision cloud sandboxes** with simple prompts
- **Deploy any app** to any number of environments simultaneously
- **Get live URLs instantly**—preview tokens included, ready to share
- **Search deployment history** with natural language queries
- **Execute deployments in parallel**—spin up your entire fleet in seconds, not hours

### Key Innovation: Natural Language → Live Production URLs

The principle is beautifully simple:

1. **Configure** your Blaxel credentials once
2. **Describe** your deployment intent to Claude in natural language
3. **Claude understands** and uses our MCP tools to execute
4. **Deployments run in parallel** across multiple sandboxes automatically
5. **Get live URLs** with preview tokens, ready to share with your team

### Built for Everyone

This isn't just for hardcore DevOps professionals. Thanks to our natural language interface, both seasoned infrastructure engineers and developers who prefer to avoid command lines can deploy apps with the same ease—**just by asking Claude**.

Blaxel Fleet Commander makes cloud deployment dead-simple for MCP clients while keeping access control transparent and configuration-first, ensuring your infrastructure remains secure and manageable at scale.

---

## Highlights

- ⚡ **Parallel Deployment** — Deploy to N sandboxes simultaneously, not sequentially
- 🗣️ **Natural Language** — No YAML, no CLI, just describe what you want
- 🌐 **Instant Live URLs** — Automatic preview tokens, ready to share
- 🔍 **Semantic Search** — Find past deployments with natural language (LlamaIndex RAG)
- 📊 **Full Observability** — Tracing with Weave (Weights & Biases)
- 🛡️ **Graceful Degradation** — Logging failures never break deployments
- 🔧 **Zero Pipeline Config** — No CI/CD setup, no build scripts to maintain

---

## Quick Start

### Prerequisites

- Python 3.11+
- [Blaxel Account](https://blaxel.ai) with API key
- Claude Desktop (for MCP integration)

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/blaxel-fleet-commander.git
cd blaxel-fleet-commander

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -e .
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

**Required:**
```env
BL_API_KEY=your-blaxel-api-key
BL_WORKSPACE=your-workspace
```

**Optional (for RAG features):**
```env
MISTRAL_API_KEY=your-mistral-key
QDRANT_URL=your-qdrant-url
QDRANT_API_KEY=your-qdrant-key
```

### 3. Configure Claude Desktop

Add to your `claude_desktop_config.json`:

**Windows:**
```json
{
    "mcpServers": {
        "Blaxel Fleet Commander": {
            "command": "C:\\path\\to\\your\\.venv\\Scripts\\python.exe",
            "args": ["C:\\path\\to\\your\\run_mcp_stdio.py"]
        }
    }
}
```

**macOS/Linux:**
```json
{
    "mcpServers": {
        "Blaxel Fleet Commander": {
            "command": "/path/to/your/.venv/bin/python",
            "args": ["/path/to/your/run_mcp_stdio.py"]
        }
    }
}
```

### 4. Start Deploying!

Open Claude Desktop and try:

> "Deploy https://github.com/user/my-react-app.git to 3 sandboxes"

Claude will:
1. ✅ Provision 3 Blaxel sandboxes in parallel
2. ✅ Clone your repository to each
3. ✅ Install dependencies (`npm ci`)
4. ✅ Build production bundles (`npm run build`)
5. ✅ Start servers on each sandbox
6. ✅ Return 3 live URLs with preview tokens

**All in under 60 seconds.**

---

## MCP Tools

### Deployment Tools

| Tool | Description |
|------|-------------|
| `fleet_provision_sandbox` | Create a new Blaxel cloud sandbox |
| `fleet_check_latency` | Measure network latency to a sandbox |
| `fleet_clone_repo` | Clone a GitHub repository to a sandbox |
| `fleet_install_deps` | Install npm dependencies |
| `fleet_build_app` | Build production bundle |
| `fleet_start_server` | Start server and get live URL |
| `fleet_deploy_game` | All-in-one: deploy to N sandboxes in parallel |
| `fleet_list_sandboxes` | List all available sandboxes with status |
| `fleet_verify_live` | Verify URLs are responding (health check) |

### RAG Tools (Semantic Search)

| Tool | Description |
|------|-------------|
| `fleet_search_logs` | Search deployment history with natural language |
| `fleet_suggest_fix` | Get AI-powered fix suggestions from successful deployments |

---

## Usage Examples

### Deploy to Multiple Environments

```
User: I want to deploy https://github.com/Nsuccess/mcp-leap.git to 2 VMs. Please do it step by step:

1. Provision 2 sandboxes
2. Check latency on each
3. Clone repo and install dependencies on each
4. Build the app on each
5. Start the server on each and give me the URLs
6. Verify the URLs are live with 200 OK
Show me each step as you do it.

Claude: I'll deploy your app to 3 Blaxel sandboxes in parallel...

🚀 Provisioning sandboxes...
📦 Cloning repository...
📚 Installing dependencies...
🔨 Building production bundles...
🌐 Starting servers...

✅ Deployment complete! Here are your live URLs:

• VM 1: https://fleet-abc123.blaxel.app?token=...
• VM 2: https://fleet-def456.blaxel.app?token=...

All 2 deployments completed in 47 seconds.
```

### Search Deployment History

```
User: Find deployments that failed with npm errors in the last 24 hours

Claude: [Uses fleet_search_logs with semantic search]

Found 3 matching deployments:

1. fleet-xyz (2 hours ago)
   Error: "npm ERR! peer dep missing: react@^18.0.0"
   
2. fleet-abc (6 hours ago)
   Error: "npm ERR! ERESOLVE unable to resolve dependency tree"
   
3. fleet-def (yesterday)
   Error: "npm ERR! code ENOENT"
```

### Get Fix Suggestions

```
User: How do I fix the ERESOLVE dependency error?

Claude: [Uses fleet_suggest_fix powered by RAG]

Based on 12 successful deployments with similar issues, here are fixes:

1. Use legacy peer deps: `npm install --legacy-peer-deps`
2. Update package.json to use compatible versions
3. Delete package-lock.json and reinstall

The most successful approach (89% success rate) was option 1.
```

### Quick Health Check

```
User: Are all my deployments still running?

Claude: [Uses fleet_verify_live]

Checking 3 URLs...

✅ fleet-abc123: 200 OK (latency: 45ms)
✅ fleet-def456: 200 OK (latency: 52ms)
❌ fleet-ghi789: 502 Bad Gateway

1 deployment needs attention. Would you like me to redeploy fleet-ghi789?
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Claude Desktop                          │
│                    (MCP Client)                             │
│                                                             │
│   "Deploy my app to 5 sandboxes"                           │
└─────────────────────┬───────────────────────────────────────┘
                      │ STDIO / JSON-RPC
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Blaxel Fleet Commander                         │
│                  (MCP Server)                               │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Deployment │  │    RAG      │  │    Observability    │  │
│  │    Tools    │  │   Tools     │  │      (Weave)        │  │
│  │             │  │             │  │                     │  │
│  │ • Provision │  │ • Search    │  │ • Trace all calls   │  │
│  │ • Clone     │  │ • Suggest   │  │ • Log deployments   │  │
│  │ • Build     │  │             │  │                     │  │
│  │ • Serve     │  │             │  │                     │  │
│  └──────┬──────┘  └──────┬──────┘  └─────────────────────┘  │
└─────────┼────────────────┼──────────────────────────────────┘
          │                │
          ▼                ▼
┌─────────────────┐  ┌─────────────────────────────────────────┐
│  Blaxel Cloud   │  │           LlamaIndex RAG                │
│   Sandboxes     │  │                                         │
│                 │  │  ┌─────────────┐  ┌─────────────────┐   │
│  Parallel       │  │  │   Mistral   │  │     Qdrant      │   │
│  Provisioning   │  │  │  Embeddings │  │   Vector DB     │   │
│  & Deployment   │  │  │  (1024 dim) │  │                 │   │
│                 │  │  └─────────────┘  └─────────────────┘   │
└─────────────────┘  └─────────────────────────────────────────┘
```

---

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BL_API_KEY` | ✅ | Blaxel API key for sandbox provisioning |
| `BL_WORKSPACE` | ✅ | Blaxel workspace name |
| `MISTRAL_API_KEY` | ❌ | Mistral AI key for embeddings (RAG) |
| `QDRANT_URL` | ❌ | Qdrant endpoint for vector storage (RAG) |
| `QDRANT_API_KEY` | ❌ | Qdrant API key (RAG) |
| `WANDB_API_KEY` | ❌ | Weights & Biases key for tracing |
| `GITHUB_TOKEN` | ❌ | GitHub token for private repositories |

### Notes

- If RAG variables are missing, deployment tools still work perfectly
- Logging failures never break deployments (graceful degradation)
- All credentials are stored in `.env` (never committed to git)

---

## Project Structure

```
├── src/
│   ├── blaxel/                 # Deployment tools
│   │   ├── tools.py            # fleet_deploy_game, fleet_list_sandboxes
│   │   ├── granular_tools.py   # Step-by-step deployment tools
│   │   └── types.py            # Type definitions
│   ├── qdrant/                 # LlamaIndex RAG system
│   │   ├── llamaindex_manager.py   # Production RAG pipeline
│   │   └── llamaindex_tools.py     # fleet_search_logs, fleet_suggest_fix
│   ├── config/                 # Configuration management
│   │   ├── manager.py          # YAML config loader
│   │   └── permissions.py      # Access control
│   ├── server.py               # MCP server (HTTP transport)
│   └── server_stdio.py         # MCP server (STDIO transport)
│
├── run_mcp_stdio.py            # Claude Desktop entry point
├── config.yaml                 # Sandbox configuration
├── .env.example                # Environment template
├── pyproject.toml              # Dependencies
└── README.md
```

---

## Troubleshooting

### MCP Server Not Connecting

1. Verify paths in `claude_desktop_config.json` are **absolute paths**
2. Ensure virtual environment has all dependencies: `pip install -e .`
3. Check `.env` file exists with valid `BL_API_KEY` and `BL_WORKSPACE`

### Deployment Failures

1. Verify your Blaxel API key is valid and not expired
2. Check that the GitHub repository is public (or provide `GITHUB_TOKEN`)
3. Ensure the repo has a valid `package.json` with `build` script

### RAG Features Not Working

1. Add `MISTRAL_API_KEY`, `QDRANT_URL`, and `QDRANT_API_KEY` to `.env`
2. Deployments still work without RAG—it's completely optional
3. Check Qdrant instance is accessible from your network

### Slow Startup

1. First run downloads LlamaIndex models—subsequent runs are faster
2. Set `WEAVE_DISABLED=true` in `.env` to skip observability setup

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| MCP Server | FastMCP | Tool registration & transport |
| Cloud Sandboxes | Blaxel | Instant VM provisioning |
| RAG Framework | LlamaIndex | Semantic search pipeline |
| Embeddings | Mistral AI | 1024-dimensional vectors |
| Vector Database | Qdrant | Fast similarity search |
| Observability | Weave (W&B) | Tracing & debugging |

---

## Why Blaxel Fleet Commander?

| Traditional Deployment | Fleet Commander |
|------------------------|-----------------|
| Write YAML pipelines | Just ask Claude |
| Click through consoles | Natural language |
| Deploy one at a time | Parallel execution |
| Wait for CI/CD queues | Instant provisioning |
| Debug cryptic errors | AI-powered suggestions |
| Manage SSH keys | Zero credential management |

---

## Demo Video

<a name="demo-video"></a>

🎥 **[Watch the full demo on YouTube](https://youtu.be/FxCvfqcH0Vo)**

*Shows: Deploying a React app to Blaxel sandboxes in parallel using natural language via Claude Desktop*

---

## License

MIT

---

## Acknowledgments

Built with ❤️ for the **MCP 1st Birthday Hackathon** 🎂

### Sponsor $ Technologies 

- [Blaxel](https://blaxel.ai) — Cloud sandbox infrastructure 
- [Mistral AI](https://mistral.ai) — Embeddings & AI
- [LlamaIndex](https://llamaindex.ai) — Production RAG framework
- [Qdrant](https://qdrant.tech) — Vector database
- [Weights & Biases](https://wandb.ai) — Observability platform

### Team

- **[InxCodm](https://huggingface.co/InxCodm)** — Solo developer

---

*Built for the MCP 1st Birthday Hackathon, November 2025*
