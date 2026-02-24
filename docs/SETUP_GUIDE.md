# Setup Guide

Complete step-by-step instructions to get Elastic Infra Commander running.

---

## Prerequisites

### Required Accounts

1. **Elasticsearch Cloud** ([Sign up](https://cloud.elastic.co/registration?cta=hackathon))
   - Free trial available
   - Need: Elasticsearch URL + API Key

2. **Blaxel** ([Sign up](https://blaxel.ai))
   - Free tier available
   - Need: API Key + Workspace name

3. **OpenAI** (for Agent Builder LLM)
   - Need: API Key for Claude Sonnet 4.5 connector

### Required Software

- Python 3.10 or higher
- pip (Python package manager)
- Git

---

## Step 1: Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/elastic-infra-commander.git
cd elastic-infra-commander
```

---

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `elasticsearch` - Elasticsearch Python client
- `python-dotenv` - Environment variable management
- `blaxel` - Blaxel SDK for VM management
- `asyncio` - Async/await support

---

## Step 3: Configure Environment

### 3.1 Create `.env` file

```bash
cp .env.example .env
```

### 3.2 Get Elasticsearch Credentials

1. Log in to [Elasticsearch Cloud](https://cloud.elastic.co)
2. Navigate to your deployment
3. Click **"Manage"** → **"API Keys"**
4. Create new API key named "elastic-infra-commander"
5. Copy the **Encoded** API key value
6. Copy your **Elasticsearch endpoint** URL

### 3.3 Get Blaxel Credentials

1. Log in to [Blaxel](https://blaxel.ai)
2. Navigate to **Settings** → **API Keys**
3. Create new API key
4. Copy API key and workspace name

### 3.4 Update `.env`

```bash
# Elasticsearch
ELASTICSEARCH_URL=https://your-project.es.us-central1.gcp.elastic.cloud:443
ELASTICSEARCH_API_KEY=your-encoded-api-key-here

# Blaxel
BL_API_KEY=bl_your-api-key-here
BL_WORKSPACE=your-workspace-name
```

---

## Step 4: Test Connections

### 4.1 Test Elasticsearch

```bash
python tests/test_elasticsearch.py
```

Expected output:
```
✅ Connected to Elasticsearch
✅ Cluster health: green
✅ Indices: 4 found
```

### 4.2 Test Blaxel

```bash
python tests/test_blaxel.py
```

Expected output:
```
✅ Connected to Blaxel
✅ Workspace: your-workspace-name
✅ API key valid
```

### 4.3 Test Both

```bash
python utils/verify_connections.py
```

Expected output:
```
✅ Elasticsearch: Connected
✅ Blaxel: Connected
✅ All systems ready
```

---

## Step 5: Upload Workflows to Kibana

### 5.1 Navigate to Workflows

1. Open Kibana
2. Click **"Agent Builder"** in left sidebar
3. Click **"Workflows"** tab
4. Click **"Create workflow"**

### 5.2 Upload Each Workflow

Upload these 3 workflows one by one:

**Workflow 1: Deploy to Blaxel Fleet**
- Click **"Import from file"**
- Select `workflows/deploy-to-fleet.yaml`
- Click **"Save"**

**Workflow 2: List Available VMs**
- Click **"Import from file"**
- Select `workflows/list-available-vms.yaml`
- Click **"Save"**

**Workflow 3: Check Deployment Status**
- Click **"Import from file"**
- Select `workflows/check-deployment-status.yaml`
- Click **"Save"**

### 5.3 Verify Workflows

You should see 3 workflows in the list:
- ✅ Deploy to Blaxel Fleet
- ✅ List Available VMs
- ✅ Check Deployment Status

---

## Step 6: Create Agent in Kibana

### 6.1 Create New Agent

1. In Kibana, click **"Agent Builder"** → **"Agents"**
2. Click **"Create agent"**
3. Name: `Elastic Infra Commander`
4. Description: `AI-powered deployment orchestrator for distributed infrastructure`

### 6.2 Configure System Prompt

1. Click **"Settings"** tab
2. In **"System Prompt"** field, paste the entire content from `agent/system-prompt.md`
3. Click **"Save"**

### 6.3 Enable Tools

In the **"Tools"** section, enable these tools:

**Platform Tools** (6 tools):
- ✅ `platform.core.search`
- ✅ `platform.core.execute_esql`
- ✅ `platform.core.get_document_by_id`
- ✅ `platform.core.list_indices`
- ✅ `platform.core.index_explorer`
- ✅ `platform.core.get_workflow_execution_status`

**Custom Workflow Tools** (3 tools):
- ✅ `deploy_to_fleet`
- ✅ `list_available_vms`
- ✅ `check_deployment_status`

**Total: 9 tools enabled**

### 6.4 Connect LLM

1. Click **"LLM"** tab
2. Select **"OpenAI"** connector
3. Choose **"Claude Sonnet 4.5"** model
4. Enter your OpenAI API key
5. Click **"Test connection"**
6. Click **"Save"**

### 6.5 Save Agent

Click **"Save"** at the top right.

---

## Step 7: Start Distributed Runner

### 7.1 Open Terminal

Open a new terminal window in the project directory.

### 7.2 Start Runner

```bash
python runner/distributed_runner.py
```

Expected output:
```
============================================================
Elastic Infra Commander - Distributed Runner
============================================================
✅ Distributed Runner initialized
   Workspace: your-workspace-name
   Polling: distributed-tool-requests

🔄 Starting polling loop (interval: 5s)
Press Ctrl+C to stop

.....
```

The dots (`.`) indicate the runner is polling Elasticsearch every 5 seconds.

### 7.3 Keep Runner Running

**Important**: Keep this terminal window open and the runner running. The runner must be active to execute deployments.

---

## Step 8: Test Deployment

### 8.1 Open Agent in Kibana

1. Navigate to **Agent Builder** → **"Agents"**
2. Click on **"Elastic Infra Commander"**
3. Click **"Chat"** tab

### 8.2 Send Test Prompt

Type this in the chat:

```
Deploy https://github.com/Nsuccess/mcp-leap.git to 2 VMs step by step
```

### 8.3 Expected Response

The agent should respond with a step-by-step deployment narrative:

```
I'll deploy the repo to 2 VMs step by step. Let's go!

Step 1: Create Deployment Request
✅ Deployment request created (ID: req-abc123)

Step 2: Provision 2 Sandboxes
✅ Sandbox 1: fleet-game-abc123 — Ready
✅ Sandbox 2: fleet-game-def456 — Ready

Step 3: Clone Repo & Install Dependencies
✅ Both sandboxes: Repository cloned, dependencies installed

Step 4: Build the Application
✅ Both sandboxes: Production bundle built

Step 5: Start the Servers
✅ Sandbox 1: Server running (54.2s)
✅ Sandbox 2: Server running (53.8s)

Step 6: Generate Preview URLs
🌐 Sandbox 1: https://xxx.preview.bl.run?bl_preview_token=yyy
🌐 Sandbox 2: https://zzz.preview.bl.run?bl_preview_token=www

🎉 Deployment Complete! (54.6s)
```

### 8.4 Verify Deployment

1. Click one of the preview URLs
2. The game should load in your browser
3. Verify it's fully playable

### 8.5 Check Runner Logs

In the runner terminal, you should see:

```
🚀 Executing deployment:
   Repo: https://github.com/Nsuccess/mcp-leap.git
   VMs: 2

📦 Creating 2 new sandboxes...
✅ Created 2 sandboxes

📦 Deploying to VM 1/2: fleet-game-abc123
   Cloning repository...
   Installing dependencies...
   Building application...
   Starting server...
   Generating preview URL...
   ✅ Deployed in 54.2s
   🌐 https://xxx.preview.bl.run?bl_preview_token=yyy

📦 Deploying to VM 2/2: fleet-game-def456
   ...
   ✅ Deployed in 53.8s
   🌐 https://zzz.preview.bl.run?bl_preview_token=www

✅ Deployment complete!
   Total time: 54.6s
   Live URLs: 2
```

---

## Troubleshooting

### Runner Not Picking Up Requests

**Symptom**: Agent creates request but runner doesn't execute

**Solutions**:
1. Verify runner is running: Check terminal for "Polling..." message
2. Check Elasticsearch connection: Run `python tests/test_elasticsearch.py`
3. Verify `.env` credentials are correct
4. Check runner logs for error messages

### Deployment Fails

**Symptom**: Runner shows "Deployment failed" error

**Solutions**:
1. Check Blaxel credentials: Run `python tests/test_blaxel.py`
2. Verify repository URL is accessible
3. Check runner logs for specific error message
4. Ensure Blaxel workspace has available quota

### Agent Doesn't Show URLs

**Symptom**: Agent says "deployment in progress" but never shows URLs

**Solutions**:
1. Wait longer (deployments take ~55 seconds)
2. Verify system prompt is updated in Kibana
3. Check `distributed-tool-results` index manually:
   ```bash
   # In Kibana Dev Tools
   GET distributed-tool-results/_search
   {
     "sort": [{"timestamp": "desc"}],
     "size": 1
   }
   ```
4. Restart agent conversation

### Connection Timeouts

**Symptom**: "Connection timeout" errors

**Solutions**:
1. Check internet connection
2. Verify Elasticsearch URL is correct (include port :443)
3. Verify API keys haven't expired
4. Check firewall settings

---

## Next Steps

### 1. Explore More Deployments

Try deploying different applications:

```
Deploy https://github.com/user/react-app.git to 3 VMs
```

```
Deploy https://github.com/user/api.git to 2 VMs on port 8080
```

### 2. Monitor Deployments

Query deployment history:

```
Show me the last 10 deployments and their status
```

### 3. Check VM Performance

Query VM metrics:

```
Show me available VMs sorted by latency
```

### 4. Customize Workflows

Edit workflow files in `workflows/` to customize:
- Build commands
- Start commands
- Port numbers
- VM specifications

### 5. Scale Up

Run multiple runner instances for parallel request processing:

```bash
# Terminal 1
python runner/distributed_runner.py

# Terminal 2
python runner/distributed_runner.py
```

---

## Support

### Documentation

- **Architecture**: See `docs/ARCHITECTURE.md`
- **Demo Script**: See `docs/DEMO_SCRIPT.md`
- **Comparison**: See `HONEST_COMPARISON.md`

### Issues

If you encounter issues:

1. Check troubleshooting section above
2. Verify all prerequisites are met
3. Run connection tests
4. Check runner logs for errors
5. Review Elasticsearch indices for data

### Community

- **Hackathon**: [Elasticsearch Agent Builder Hackathon](https://elasticsearch.devpost.com/)
- **Elastic Docs**: [Agent Builder Documentation](https://www.elastic.co/guide/en/kibana/current/agent-builder.html)
- **Blaxel Docs**: [Blaxel Documentation](https://docs.blaxel.ai)

---

## Success Checklist

Before submitting:

- [ ] All tests pass (`python utils/verify_connections.py`)
- [ ] Runner starts without errors
- [ ] Agent responds to deployment requests
- [ ] Deployments complete successfully
- [ ] Preview URLs work and are accessible
- [ ] Documentation is complete
- [ ] Demo video is recorded
- [ ] Social post on X with @elastic_devs tag

---

**You're ready to deploy! 🚀**
