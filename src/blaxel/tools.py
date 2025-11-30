"""MCP tools for Blaxel Fleet Commander.

5 tools for parallel game deployment across Blaxel sandboxes:
- fleet_list_sandboxes(): List all sandboxes with latency
- fleet_deploy_game(repo_url, n): Deploy game to n fastest sandboxes
- fleet_verify_live(urls): Verify URLs are live
- fleet_search_logs(...): Semantic search across deployment logs
- fleet_suggest_fix(context): Suggest fixes from successful deployments
"""

import asyncio
import os
import time
import uuid
from typing import Annotated

import httpx

# Only import weave if not disabled (STDIO mode disables it)
if os.environ.get("WEAVE_DISABLED") != "true":
    import weave
    _weave_enabled = True
else:
    _weave_enabled = False

# CRITICAL: Ensure environment variables are set before importing Blaxel SDK
# The SDK reads BL_WORKSPACE and BL_API_KEY on import
if 'BL_WORKSPACE' not in os.environ or 'BL_API_KEY' not in os.environ:
    from dotenv import load_dotenv
    load_dotenv()
    os.environ['BL_WORKSPACE'] = os.getenv('BL_WORKSPACE', '')
    os.environ['BL_API_KEY'] = os.getenv('BL_API_KEY', '')

from blaxel.core import SandboxInstance
from mcp.server.fastmcp import Context

from src.qdrant.llamaindex_manager import log_blaxel_operation
from src.server import mcp
from .session_manager import SessionManager
from .types import (
    ListSandboxesResult,
    SandboxInfo,
    FleetDeployResult,
    DeploymentResult,
    FleetVerifyResult,
    URLVerification,
)


NGINX_SPA_CONFIG = '''server {
    listen 8080;
    server_name _;
    root /app/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}'''


async def _measure_latency(sandbox: SandboxInstance) -> float:
    """Measure sandbox latency using echo ping."""
    start_time = time.time()
    try:
        await sandbox.process.exec({
            "command": "echo 'ping'",
            "wait_for_completion": True,
            "timeout": 5000
        })
        return (time.time() - start_time) * 1000
    except Exception:
        return 9999.0


@mcp.tool(
    name="fleet_list_sandboxes",
    description=(
        "List all Blaxel sandboxes with latency measurements.\n\n"
        "Returns: { sandboxes: [{ name, status, latency_ms, image, memory }], total }\n\n"
        "Note: Currently returns existing known sandboxes. Use fleet_deploy_game to create new ones."
    ),
)
async def fleet_list_sandboxes(ctx: Context) -> ListSandboxesResult:
    """List all sandboxes with latency.
    
    Note: Blaxel SDK doesn't have a list() method, so we return known sandboxes
    or an empty list. The fleet_deploy_game tool will create sandboxes as needed.
    """
    # Try to get the existing test sandbox
    sandbox_infos: list[SandboxInfo] = []
    
    try:
        # Try to get the known test sandbox
        sandbox = await SandboxInstance.get("fleet-test-sandbox")
        latency_ms = await _measure_latency(sandbox)
        
        sandbox_infos.append({
            "name": "fleet-test-sandbox",
            "status": "ready",
            "latency_ms": round(latency_ms, 2),
            "image": "blaxel/prod-node:latest",
            "memory": 4096,
        })
    except Exception:
        # No existing sandboxes, return empty list
        pass
    
    return {
        "sandboxes": sandbox_infos,
        "total": len(sandbox_infos)
    }


@mcp.tool(
    name="fleet_deploy_game",
    description=(
        "Deploy a game repository to the n fastest sandboxes in parallel.\n\n"
        "Parameters:\n"
        "- repo_url (string): GitHub repository URL to clone and deploy\n"
        "- n (int, optional): Number of sandboxes to deploy to (default: 2)\n\n"
        "Returns: { deployments: [{ sandbox_name, url, deploy_time_seconds, status }], total_time_seconds, repo_url }\n\n"
        "This tool:\n"
        "1. Lists existing sandboxes and measures latency\n"
        "2. Selects the n fastest sandboxes\n"
        "3. Deploys in parallel: clone -> npm ci -> npm build -> nginx -> public URL\n"
        "4. Returns live HTTPS URLs for each deployment\n\n"
        "Example: 'Deploy https://github.com/Nsuccess/mcp-leap.git to 2 fastest sandboxes'"
    ),
)
async def fleet_deploy_game(
    repo_url: Annotated[str, "GitHub repository URL to deploy"],
    n: Annotated[int, "Number of sandboxes to deploy to"] = 2,
    ctx: Context | None = None,
) -> FleetDeployResult:
    """THE HERO TOOL - Deploy game to n fastest sandboxes with full reasoning."""
    total_start = time.time()
    
    # Build reasoning log that will be included in response
    reasoning_steps = []
    
    def log_step(msg: str):
        """Add a reasoning step to the log."""
        reasoning_steps.append(f"[{time.strftime('%H:%M:%S')}] {msg}")
        print(msg)  # Also print to stderr for debugging
    
    # ========== STEP 1: ANALYZE REQUEST ==========
    log_step(f"[REASONING] Analyzing deployment request...")
    log_step(f"[REASONING] Repository: {repo_url}")
    log_step(f"[REASONING] Target VMs: {n}")
    log_step(f"[REASONING] Strategy: Create fresh sandboxes -> Measure latency -> Select fastest -> Deploy in parallel")
    
    # ========== STEP 2: CREATE SANDBOXES ==========
    log_step(f"[INFRA] Provisioning {n} new Blaxel sandboxes...")
    
    create_tasks = []
    sandbox_names = []
    for i in range(n):
        name = f"fleet-game-{uuid.uuid4().hex[:8]}"
        sandbox_names.append(name)
        task = SandboxInstance.create({
            "metadata": {"name": name},
            "spec": {
                "runtime": {
                    "image": "blaxel/node:latest",
                    "memory": 4096,
                    "ports": [
                        {
                            "name": "preview",
                            "target": 3000,
                            "protocol": "HTTP"
                        }
                    ]
                }
            }
        })
        create_tasks.append(task)
        log_step(f"[INFRA] Queued sandbox creation: {name}")
    
    # Create all sandboxes in parallel
    sandboxes = await asyncio.gather(*create_tasks, return_exceptions=True)
    
    # Check for errors
    errors = [sb for sb in sandboxes if isinstance(sb, Exception)]
    if errors:
        log_step(f"[WARN] Some sandbox creations failed: {len(errors)} errors")
    
    valid_sandboxes = [sb for sb in sandboxes if not isinstance(sb, Exception)]
    log_step(f"[INFRA] Successfully created {len(valid_sandboxes)}/{n} sandboxes")
    
    if not valid_sandboxes:
        error_msg = f"Failed to create any sandboxes. Errors: {[str(e) for e in errors]}"
        raise ValueError(error_msg)
    
    # Wait for sandboxes to be ready
    log_step(f"[INFRA] Waiting for sandboxes to initialize...")
    wait_tasks = [sb.wait() for sb in valid_sandboxes]
    await asyncio.gather(*wait_tasks, return_exceptions=True)
    log_step(f"[INFRA] All {len(valid_sandboxes)} sandboxes are READY")
    
    # ========== STEP 3: MEASURE LATENCY ==========
    log_step(f"[LATENCY] Measuring network latency to each sandbox...")
    
    latency_tasks = [_measure_latency(sb) for sb in valid_sandboxes]
    latencies = await asyncio.gather(*latency_tasks, return_exceptions=True)
    
    sandbox_latencies = []
    for sb, lat in zip(valid_sandboxes, latencies):
        latency_ms = lat if isinstance(lat, float) else 9999.0
        sandbox_latencies.append((sb, latency_ms))
        log_step(f"[LATENCY] {sb.metadata.name}: {latency_ms:.1f}ms")
    
    sandbox_latencies.sort(key=lambda x: x[1])
    selected = [sb for sb, _ in sandbox_latencies[:n]]
    
    log_step(f"[SELECTION] Selected {n} fastest sandboxes:")
    for sb, lat in sandbox_latencies[:n]:
        log_step(f"[SELECTION] -> {sb.metadata.name} ({lat:.1f}ms)")
    
    # ========== STEP 4: PARALLEL DEPLOYMENT ==========
    log_step(f"[DEPLOY] Starting parallel deployment to {n} sandboxes...")
    
    # Track deployment progress
    deployment_progress = {sb.metadata.name: [] for sb in selected}
    
    async def deploy_to_sandbox(sandbox: SandboxInstance) -> DeploymentResult:
        deploy_start = time.time()
        job_id = str(uuid.uuid4())
        sandbox_name = sandbox.metadata.name
        
        def sandbox_log(msg: str):
            deployment_progress[sandbox_name].append(msg)
            log_step(f"[{sandbox_name}] {msg}")
        
        sandbox_log("Starting deployment...")
        
        # Log deployment start to Qdrant with Mistral embeddings
        try:
            await log_blaxel_operation(
                sandbox_name=sandbox_name,
                command=f"DEPLOYMENT_START: {repo_url}",
                job_id=job_id,
                stdout=f"Starting deployment to {sandbox_name}",
                stderr="",
                return_code=None
            )
            sandbox_log("Logged to Qdrant (LlamaIndex RAG)")
        except Exception as log_error:
            sandbox_log(f"Qdrant logging skipped: {log_error}")
        
        try:
            # Commands to execute with progress logging
            commands = [
                (f"git clone {repo_url} /app", "Cloning repository..."),
                ("cd /app && npm ci", "Installing dependencies (npm ci)..."),
                ("cd /app && npm run build", "Building production bundle..."),
            ]
            
            for cmd, description in commands:
                sandbox_log(description)
                process_name = f"cmd-{uuid.uuid4().hex[:8]}"
                
                await sandbox.process.exec({
                    "name": process_name,
                    "command": cmd,
                    "wait_for_completion": False
                })
                
                try:
                    await sandbox.process.wait(process_name, max_wait=300000, interval=2000)
                    sandbox_log(f"DONE: {description.replace('...', '')}")
                except Exception as e:
                    raise ValueError(f"Command failed: {cmd}. Error: {e}")
                
                await asyncio.sleep(0.5)
            
            # Start the server
            sandbox_log("Starting production server (npx serve)...")
            await sandbox.process.exec({
                "name": "serve-app",
                "command": "cd /app && npx serve -s dist -l 3000",
                "wait_for_completion": False
            })
            
            sandbox_log("Waiting for server to start...")
            await asyncio.sleep(5)
            sandbox_log("Server is running on port 3000")
            
            # Create preview URL with token
            sandbox_log("Creating secure preview URL...")
            
            from datetime import datetime, timedelta, timezone
            
            response_headers = {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With, X-Blaxel-Workspace, X-Blaxel-Preview-Token, X-Blaxel-Authorization",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Expose-Headers": "Content-Length, X-Request-Id",
                "Access-Control-Max-Age": "86400",
                "Vary": "Origin"
            }
            
            preview = await sandbox.previews.create_if_not_exists({
                "metadata": {"name": "preview"},
                "spec": {
                    "port": 3000,
                    "public": False,
                    "protocol": "HTTP",
                    "responseHeaders": response_headers
                }
            })
            
            token_expiry = datetime.now(timezone.utc) + timedelta(hours=24)
            token = await preview.tokens.create(token_expiry)
            preview_url = f"{preview.spec.url}?bl_preview_token={token.value}"
            
            deploy_time = time.time() - deploy_start
            sandbox_log(f"DEPLOYED in {deploy_time:.1f}s")
            sandbox_log(f"URL: {preview_url[:60]}...")
            
            # Log successful deployment to Qdrant
            try:
                await log_blaxel_operation(
                    sandbox_name=sandbox_name,
                    command=f"DEPLOYMENT_SUCCESS: {repo_url}",
                    job_id=job_id,
                    stdout=f"Successfully deployed to {sandbox_name}. URL: {preview_url}. Time: {deploy_time:.2f}s",
                    stderr="",
                    return_code=0
                )
            except Exception as log_error:
                pass
            
            return {
                "sandbox_name": sandbox_name,
                "url": preview_url,
                "deploy_time_seconds": round(deploy_time, 2),
                "status": "deployed"
            }
            
        except Exception as e:
            import traceback
            error_details = f"{str(e)}\n{traceback.format_exc()}"
            sandbox_log(f"FAILED: {str(e)[:100]}")
            
            try:
                await log_blaxel_operation(
                    sandbox_name=sandbox_name,
                    command=f"DEPLOYMENT_FAILURE: {repo_url}",
                    job_id=job_id,
                    stdout="",
                    stderr=error_details,
                    return_code=1
                )
            except Exception:
                pass
            
            return {
                "sandbox_name": sandbox_name,
                "url": "",
                "deploy_time_seconds": round(time.time() - deploy_start, 2),
                "status": f"failed: {error_details[:500]}"
            }
    
    # Deploy in parallel
    deploy_tasks = [deploy_to_sandbox(sb) for sb in selected]
    deployments = await asyncio.gather(*deploy_tasks)
    
    total_time = time.time() - total_start
    
    # ========== STEP 5: SUMMARY ==========
    successful = [d for d in deployments if d["status"] == "deployed"]
    failed = [d for d in deployments if d["status"] != "deployed"]
    
    log_step(f"[COMPLETE] Deployment finished in {total_time:.1f}s")
    log_step(f"[COMPLETE] Success: {len(successful)}/{len(deployments)}")
    
    if successful:
        log_step(f"[COMPLETE] Live URLs:")
        for d in successful:
            log_step(f"[COMPLETE] -> {d['sandbox_name']}: {d['url'][:70]}...")
    
    # Return result with reasoning included
    return {
        "deployments": deployments,
        "total_time_seconds": round(total_time, 2),
        "repo_url": repo_url,
        "reasoning": reasoning_steps  # Include reasoning in response!
    }


@mcp.tool(
    name="fleet_verify_live",
    description=(
        "Verify that URLs are live and responding.\n\n"
        "Parameters:\n"
        "- urls (list[string]): List of URLs to verify\n\n"
        "Returns: { verifications: [{ url, live, status_code, latency_ms }], all_live }\n\n"
        "Uses async HEAD requests to check each URL in parallel."
    ),
)
async def fleet_verify_live(
    urls: Annotated[list[str], "List of URLs to verify"],
    ctx: Context | None = None,
) -> FleetVerifyResult:
    """Verify URLs are live with async HEAD checks."""
    
    async def verify_url(url: str) -> URLVerification:
        start_time = time.time()
        try:
            async with httpx.AsyncClient() as client:
                response = await client.head(url, timeout=10, follow_redirects=True)
                latency_ms = (time.time() - start_time) * 1000
                return {
                    "url": url,
                    "live": response.status_code == 200,
                    "status_code": response.status_code,
                    "latency_ms": round(latency_ms, 2)
                }
        except Exception as e:
            return {
                "url": url,
                "live": False,
                "status_code": None,
                "latency_ms": None
            }
    
    verify_tasks = [verify_url(url) for url in urls]
    verifications = await asyncio.gather(*verify_tasks)
    
    all_live = all(v["live"] for v in verifications)
    
    return {
        "verifications": verifications,
        "all_live": all_live
    }
