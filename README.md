# 🚀 Elastic Infra Commander

> **Turn Elasticsearch into a true DevOps co-pilot.** Deploy applications to distributed VMs from a simple prompt—no manual config needed. Built for infrastructure engineers and developers who hate DevOps. Executes in parallel, keeps everything observable through Elasticsearch. From prompt to production in 55 seconds.

[![Hackathon](https://img.shields.io/badge/Hackathon-Elasticsearch%20Agent%20Builder-blueviolet)]()
[![Prize](https://img.shields.io/badge/Prize-$20,000-green)]()
[![Deadline](https://img.shields.io/badge/Deadline-Feb%2027%202026-red)]()
[![Elasticsearch](https://img.shields.io/badge/Powered%20by-Elasticsearch-005571)]()

---

## 📋 Hackathon Submission

| Field | Details |
|-------|---------|
| **Hackathon** | Elasticsearch Agent Builder Hackathon |
| **Prize** | $20,000 |
| **Deadline** | February 27, 2026 at 1:15 PM ET |
| **Team** | [Nsuccess](https://github.com/Nsuccess) |
| **Demo Video** | [🎥 Watch on YouTube](https://youtu.be/FxCvfqcH0Vo) |
| **Social Post** | [View on X/Twitter](https://x.com/SuccessVsdworld/status/1995277010520936536) |

---

## What is Elastic Infra Commander?

**Elastic Infra Commander** transforms Elasticsearch into a DevOps co-pilot that deploys applications to distributed VMs through natural language commands.

### The Problem

Deployment is tedious:
- Manual VM configuration
- Sequential deployments (slow)
- Complex CI/CD pipelines
- No visibility into what's happening

### Our Solution

Simple prompts → Live production URLs in 55 seconds

```
"Deploy this app to 2 VMs: https://github.com/user/app.git"
```

The agent:
1. ✅ Provisions 2 VMs in parallel
2. ✅ Clones repo and installs dependencies
3. ✅ Builds production bundle
4. ✅ Starts servers
5. ✅ Returns live URLs with preview tokens

**All logged to Elasticsearch for full observability.**

---

## Key Features

- ⚡ **Parallel Deployment** — Deploy to N VMs simultaneously
- 🗣️ **Natural Language** — No YAML, just describe what you want
- 🌐 **Instant Live URLs** — Automatic preview tokens, ready to share
- 📊 **Elasticsearch Logging** — Every action logged and searchable
- 🔍 **Semantic Search** — Find past deployments with natural language
- 🛡️ **Graceful Degradation** — Logging failures never break deployments

---

## Quick Start

### Prerequisites

- Python 3.11+
- [Blaxel Account](https://blaxel.ai) with API key
- Elasticsearch cluster with API key

### 1. Install

```bash
git clone https://github.com/Nsuccess/Elastic-Infra-Commander.git
cd Elastic-Infra-Commander

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your credentials
```

**Required:**
```env
# Elasticsearch
ELASTICSEARCH_URL=https://your-cluster.es.cloud:443
ELASTICSEARCH_API_KEY=your-api-key

# Blaxel (for VM provisioning)
BL_API_KEY=your-blaxel-api-key
BL_WORKSPACE=your-workspace
```

### 3. Run

**Step 1: Start the Distributed Runner**

The runner polls Elasticsearch for deployment requests and executes them on Blaxel VMs:

```bash
py runner/distributed_runner.py
```

You should see:
```
======================================================================
🚀 Elastic Infra Commander - Distributed Runner
======================================================================
Elasticsearch: https://your-cluster.es.cloud:443
Blaxel Workspace: your-workspace

⏳ Polling for deployment requests...
   (Press Ctrl+C to stop)
```

**Step 2: Create Deployment Request in Kibana**

1. Open **Kibana** → **Management** → **Dev Tools** or **Agent Builder**
2. Use the Elasticsearch Agent Builder to create an agent
3. In the agent chat, run:

```
Deploy https://github.com/user/my-app.git to 2 VMs
```

**What Happens:**

1. The agent uses the `deploy-to-fleet` workflow
2. Workflow creates a deployment request in Elasticsearch index `distributed-tool-requests`
3. The runner (polling every 2 seconds) picks up the request
4. Runner deploys to 2 VMs in parallel:
   - Creates Blaxel sandboxes
   - Clones repository
   - Installs dependencies (`npm ci`)
   - Builds application (`npm run build`)
   - Starts server on port 3000
   - Creates preview URLs with 24-hour tokens
5. Results stored in `distributed-tool-results` index
6. Runner displays live URLs

**Expected Output (from runner):**

```
======================================================================
📦 Processing Deployment Request: abc123
======================================================================
Repository: https://github.com/user/my-app.git
Target VMs: 2

🚀 Deploying to 2 VMs in parallel...
  VM 1: Creating sandbox...
  VM 1: ✅ Sandbox created: elastic-deploy-a1b2c3d4
  VM 1: Cloning repository...
  VM 1: Installing dependencies...
  VM 1: Building application...
  VM 1: Starting server...
  VM 1: Creating preview URL...
  VM 1: ✅ DEPLOYED in 52.3s
  VM 1: 🌐 https://xxx.preview.bl.run?bl_preview_token=yyy

  VM 2: Creating sandbox...
  VM 2: ✅ Sandbox created: elastic-deploy-e5f6g7h8
  VM 2: Cloning repository...
  VM 2: Installing dependencies...
  VM 2: Building application...
  VM 2: Starting server...
  VM 2: Creating preview URL...
  VM 2: ✅ DEPLOYED in 54.1s
  VM 2: 🌐 https://zzz.preview.bl.run?bl_preview_token=www

======================================================================
✅ Deployment Complete!
======================================================================
Total Time: 54.1s
Successful: 2/2

Live URLs:
  • VM 1: https://xxx.preview.bl.run?bl_preview_token=yyy
  • VM 2: https://zzz.preview.bl.run?bl_preview_token=www
======================================================================
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Kibana Agent Builder                     │
│         User: "Deploy this app to 2 VMs"                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Elasticsearch Workflow Engine                  │
│           (workflows/deploy-to-fleet.yaml)                  │
│                                                             │
│  Creates deployment request in ES index:                    │
│  distributed-tool-requests                                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Elasticsearch                            │
│         Index: distributed-tool-requests                    │
│         Status: pending → processing → completed            │
└─────────────────────┬───────────────────────────────────────┘
                      │ (polls every 2s)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Distributed Runner (Python)                    │
│           (runner/distributed_runner.py)                    │
│                                                             │
│  Polls ES → Picks up request → Deploys in parallel         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Blaxel Cloud VMs                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │    VM 1      │  │    VM 2      │  │    VM 3      │     │
│  │  Port: 3000  │  │  Port: 3000  │  │  Port: 3000  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Live Preview URLs (HTTPS + Token)              │
│  https://xxx.preview.bl.run?bl_preview_token=yyy            │
│  https://zzz.preview.bl.run?bl_preview_token=www            │
└─────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Elasticsearch                            │
│         Index: distributed-tool-results                     │
│         Stores: URLs, timing, status for each VM            │
└─────────────────────────────────────────────────────────────┘
```

### Project Structure

```
├── runner/                     # Distributed deployment runner
│   └── distributed_runner.py   # Polls ES, executes deployments in parallel
│
├── workflows/                  # Elasticsearch workflow definitions
│   ├── deploy-to-fleet.yaml    # Main deployment workflow (creates ES request)
│   ├── check-deployment-status.yaml # Query deployment status
│   └── list-available-vms.yaml # List available Blaxel VMs
│
├── src/                        # Core libraries
│   ├── blaxel/                 # Blaxel SDK integration (if needed)
│   └── config/                 # Configuration management
│
├── tests/                      # Test suite
│   ├── test_elasticsearch.py   # Elasticsearch connection test
│   ├── test_runner_connections.py # Runner connectivity test
│   └── test_official_pattern.py # Full deployment test
│
├── utils/                      # Utility scripts
│   ├── verify_connections.py   # Verify ES + Blaxel connections
│   └── get_full_urls.py        # Retrieve preview URLs
│
├── config.yaml                 # Blaxel VM templates & RBAC
├── .env                        # API credentials (not committed)
└── README.md                   # This file
```

### Elasticsearch Indices

The system uses these Elasticsearch indices:

| Index | Purpose | Created By |
|-------|---------|------------|
| `distributed-tool-requests` | Deployment requests (pending/processing/completed) | Workflow |
| `distributed-tool-results` | Deployment results with URLs and timing | Runner |
| `deployment-logs` | Event logs for each deployment step | Workflow & Runner |
| `sandbox-latency` | VM latency measurements | Runner (optional) |

---

## How It Works

### 1. Agent Understands Intent

The agent parses your natural language request and determines:
- Repository URL
- Number of VMs needed
- Deployment steps required

### 2. Parallel Execution

Deploys to multiple VMs simultaneously using Blaxel sandboxes:
- Provision VMs
- Clone repository
- Install dependencies
- Build application
- Start servers

### 3. Elasticsearch Logging

Every action is logged to Elasticsearch:
- Deployment start/end
- Command execution
- Build output
- Errors and failures
- Performance metrics

### 4. Live URLs

Returns secure preview URLs with 24-hour tokens, ready to share.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Agent Framework | Python |
| VM Provisioning | Blaxel Cloud |
| Logging & Search | Elasticsearch |
| Embeddings | Mistral AI |
| Vector Store | Qdrant |

---

## Performance

- **Single VM**: ~45 seconds
- **2 VMs (parallel)**: ~55 seconds
- **3 VMs (parallel)**: ~62 seconds

---

## Why Elastic Infra Commander?

| Traditional Deployment | Elastic Infra Commander |
|------------------------|-------------------------|
| Write YAML pipelines | Natural language prompts |
| Click through consoles | Single command |
| Deploy sequentially | Parallel execution |
| Wait for CI/CD queues | Instant provisioning |
| Limited visibility | Full Elasticsearch logging |
| Manual troubleshooting | Semantic search history |

---

## Demo Video

🎥 **[Watch the full demo on YouTube](https://youtu.be/FxCvfqcH0Vo)**

*Shows: Deploying a React app to distributed VMs in parallel using natural language*

---

## License

MIT

---

## Acknowledgments

Built for the **Elasticsearch Agent Builder Hackathon** 🚀

### Technologies

- [Elasticsearch](https://www.elastic.co/) — Logging & observability
- [Blaxel](https://blaxel.ai) — Cloud VM infrastructure
- [Mistral AI](https://mistral.ai) — Embeddings
- [Qdrant](https://qdrant.tech) — Vector database

### Team

- **[Nsuccess](https://github.com/Nsuccess)** — Solo developer

---

*From prompt to production in 55 seconds* ⚡
