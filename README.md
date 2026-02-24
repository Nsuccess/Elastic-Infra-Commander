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

```bash
python agent/main.py
```

Then ask:
> "Deploy https://github.com/user/my-app.git to 2 VMs"

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Natural Language Input                     │
│         "Deploy this app to 2 VMs in parallel"              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Elastic Infra Commander Agent                  │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Deployment  │  │ Elasticsearch│  │   Blaxel     │     │
│  │   Runner     │  │   Logger     │  │   SDK        │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
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
│         All deployment events logged & searchable           │
└─────────────────────────────────────────────────────────────┘
```

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
