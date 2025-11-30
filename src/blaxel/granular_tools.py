"""Granular MCP tools for step-by-step deployment.

These tools allow Claude to show multiple dropdowns in the UI by calling
each step separately:
- fleet_provision_sandbox: Create a single sandbox
- fleet_check_latency: Measure latency to a sandbox
- fleet_clone_repo: Clone a repo to a sandbox
- fleet_install_deps: Install npm dependencies
- fleet_build_app: Build the production bundle
- fleet_start_server: Start the server and get URL
"""

import asyncio
import os
import time
import uuid
from typing import Annotated
from typing_extensions import TypedDict

# Only import weave if not disabled
if os.environ.get("WEAVE_DISABLED") != "true":
    import weave
    _weave_enabled = True
else:
    _weave_enabled = False

if 'BL_WORKSPACE' not in os.environ or 'BL_API_KEY' not in os.environ:
    from dotenv import load_dotenv
    load_dotenv()
    os.environ['BL_WORKSPACE'] = os.getenv('BL_WORKSPACE', '')
    os.environ['BL_API_KEY'] = os.getenv('BL_API_KEY', '')

from blaxel.core import SandboxInstance
from mcp.server.fastmcp import Context

from src.server import mcp

# Store active sandboxes in memory for the session
_active_sandboxes: dict[str, SandboxInstance] = {}


class ProvisionResult(TypedDict):
    sandbox_name: str
    status: str
    message: str


class LatencyResult(TypedDict):
    sandbox_name: str
    latency_ms: float
    status: str


class CloneResult(TypedDict):
    sandbox_name: str
    repo_url: str
    status: str
    message: str


class BuildResult(TypedDict):
    sandbox_name: str
    step: str
    status: str
    message: str


class CloneAndInstallResult(TypedDict):
    sandbox_name: str
    repo_url: str
    status: str
    message: str


class ServerResult(TypedDict):
    sandbox_name: str
    url: str
    status: str
    message: str


@mcp.tool(
    name="fleet_provision_sandbox",
    description=(
        "Provision a new Blaxel sandbox for deployment.\n\n"
        "Returns: { sandbox_name, status, message }\n\n"
        "Call this first to create a sandbox before deploying."
    ),
)
async def fleet_provision_sandbox(
    ctx: Context | None = None,
) -> ProvisionResult:
    """Create a new sandbox."""
    name = f"fleet-game-{uuid.uuid4().hex[:8]}"
    
    try:
        sandbox = await SandboxInstance.create({
            "metadata": {"name": name},
            "spec": {
                "runtime": {
                    "image": "blaxel/node:latest",
                    "memory": 4096,
                    "ports": [{"name": "preview", "target": 3000, "protocol": "HTTP"}]
                }
            }
        })
        
        await sandbox.wait()
        _active_sandboxes[name] = sandbox
        
        return {
            "sandbox_name": name,
            "status": "ready",
            "message": f"Sandbox {name} provisioned and ready"
        }
    except Exception as e:
        return {
            "sandbox_name": name,
            "status": "failed",
            "message": str(e)
        }


@mcp.tool(
    name="fleet_check_latency",
    description=(
        "Measure network latency to a sandbox.\n\n"
        "Parameters:\n"
        "- sandbox_name: Name of the sandbox to check\n\n"
        "Returns: { sandbox_name, latency_ms, status }"
    ),
)
async def fleet_check_latency(
    sandbox_name: Annotated[str, "Name of the sandbox"],
    ctx: Context | None = None,
) -> LatencyResult:
    """Measure latency to sandbox."""
    sandbox = _active_sandboxes.get(sandbox_name)
    if not sandbox:
        try:
            sandbox = await SandboxInstance.get(sandbox_name)
            _active_sandboxes[sandbox_name] = sandbox
        except Exception:
            return {"sandbox_name": sandbox_name, "latency_ms": -1, "status": "not_found"}
    
    start = time.time()
    try:
        await sandbox.process.exec({
            "command": "echo ping",
            "wait_for_completion": True,
            "timeout": 5000
        })
        latency = (time.time() - start) * 1000
        return {
            "sandbox_name": sandbox_name,
            "latency_ms": round(latency, 1),
            "status": "ok"
        }
    except Exception as e:
        return {"sandbox_name": sandbox_name, "latency_ms": -1, "status": f"error: {e}"}


@mcp.tool(
    name="fleet_clone_repo",
    description=(
        "Clone a GitHub repository to a sandbox.\n\n"
        "Parameters:\n"
        "- sandbox_name: Target sandbox\n"
        "- repo_url: GitHub repository URL\n\n"
        "Returns: { sandbox_name, repo_url, status, message }"
    ),
)
async def fleet_clone_repo(
    sandbox_name: Annotated[str, "Name of the sandbox"],
    repo_url: Annotated[str, "GitHub repository URL"],
    ctx: Context | None = None,
) -> CloneResult:
    """Clone repo to sandbox."""
    sandbox = _active_sandboxes.get(sandbox_name)
    if not sandbox:
        return {"sandbox_name": sandbox_name, "repo_url": repo_url, "status": "failed", "message": "Sandbox not found"}
    
    try:
        process_name = f"clone-{uuid.uuid4().hex[:8]}"
        # Use wait_for_completion=True to get output directly
        result = await sandbox.process.exec({
            "name": process_name,
            "command": f"git clone --depth 1 {repo_url} /app 2>&1",
            "wait_for_completion": True,
            "timeout": 120000
        })
        
        # Check return code from result
        return_code = getattr(result, 'return_code', None) or getattr(result, 'exit_code', None)
        stdout = getattr(result, 'stdout', '') or getattr(result, 'output', '') or ''
        stderr = getattr(result, 'stderr', '') or ''
        
        if return_code is not None and return_code != 0:
            error_msg = stderr or stdout or f"Exit code {return_code}"
            return {
                "sandbox_name": sandbox_name,
                "repo_url": repo_url,
                "status": "failed",
                "message": f"Clone failed: {error_msg[:200]}"
            }
        
        # Verify clone succeeded by checking /app exists
        verify = await sandbox.process.exec({
            "command": "ls -la /app 2>&1",
            "wait_for_completion": True,
            "timeout": 5000
        })
        verify_output = getattr(verify, 'stdout', '') or getattr(verify, 'output', '') or ''
        
        if 'No such file' in verify_output or not verify_output.strip():
            return {
                "sandbox_name": sandbox_name,
                "repo_url": repo_url,
                "status": "failed",
                "message": f"Clone may have failed - /app not found. Output: {stdout[:100]}"
            }
        
        return {
            "sandbox_name": sandbox_name,
            "repo_url": repo_url,
            "status": "cloned",
            "message": "Repository cloned to /app"
        }
    except Exception as e:
        return {"sandbox_name": sandbox_name, "repo_url": repo_url, "status": "failed", "message": f"Exception: {str(e)}"}


@mcp.tool(
    name="fleet_clone_and_install",
    description=(
        "Clone a GitHub repository and install dependencies in one step.\n\n"
        "Parameters:\n"
        "- sandbox_name: Target sandbox\n"
        "- repo_url: GitHub repository URL\n\n"
        "Returns: { sandbox_name, repo_url, status, message }\n\n"
        "This combines clone + npm install for faster deployment."
    ),
)
async def fleet_clone_and_install(
    sandbox_name: Annotated[str, "Name of the sandbox"],
    repo_url: Annotated[str, "GitHub repository URL"],
    ctx: Context | None = None,
) -> CloneAndInstallResult:
    """Clone repo and install dependencies in one step."""
    sandbox = _active_sandboxes.get(sandbox_name)
    if not sandbox:
        return {"sandbox_name": sandbox_name, "repo_url": repo_url, "status": "failed", "message": "Sandbox not found"}
    
    try:
        # Clone and install in one command to reduce API calls
        process_name = f"clone-install-{uuid.uuid4().hex[:8]}"
        await sandbox.process.exec({
            "name": process_name,
            "command": f"git clone --depth 1 {repo_url} /app && cd /app && npm ci",
            "wait_for_completion": False
        })
        await sandbox.process.wait(process_name, max_wait=300000, interval=2000)
        
        return {
            "sandbox_name": sandbox_name,
            "repo_url": repo_url,
            "status": "complete",
            "message": "Repository cloned and dependencies installed"
        }
    except Exception as e:
        return {"sandbox_name": sandbox_name, "repo_url": repo_url, "status": "failed", "message": str(e)}


@mcp.tool(
    name="fleet_install_deps",
    description=(
        "Install npm dependencies in a sandbox.\n\n"
        "Parameters:\n"
        "- sandbox_name: Target sandbox\n\n"
        "Returns: { sandbox_name, step, status, message }"
    ),
)
async def fleet_install_deps(
    sandbox_name: Annotated[str, "Name of the sandbox"],
    ctx: Context | None = None,
) -> BuildResult:
    """Install npm dependencies."""
    sandbox = _active_sandboxes.get(sandbox_name)
    if not sandbox:
        return {"sandbox_name": sandbox_name, "step": "npm ci", "status": "failed", "message": "Sandbox not found"}
    
    try:
        process_name = f"install-{uuid.uuid4().hex[:8]}"
        await sandbox.process.exec({
            "name": process_name,
            "command": "cd /app && npm ci",
            "wait_for_completion": False
        })
        await sandbox.process.wait(process_name, max_wait=300000, interval=2000)
        
        return {
            "sandbox_name": sandbox_name,
            "step": "npm ci",
            "status": "complete",
            "message": "Dependencies installed"
        }
    except Exception as e:
        return {"sandbox_name": sandbox_name, "step": "npm ci", "status": "failed", "message": str(e)}


@mcp.tool(
    name="fleet_build_app",
    description=(
        "Build the production bundle in a sandbox.\n\n"
        "Parameters:\n"
        "- sandbox_name: Target sandbox\n\n"
        "Returns: { sandbox_name, step, status, message }"
    ),
)
async def fleet_build_app(
    sandbox_name: Annotated[str, "Name of the sandbox"],
    ctx: Context | None = None,
) -> BuildResult:
    """Build production bundle."""
    sandbox = _active_sandboxes.get(sandbox_name)
    if not sandbox:
        return {"sandbox_name": sandbox_name, "step": "npm build", "status": "failed", "message": "Sandbox not found"}
    
    try:
        process_name = f"build-{uuid.uuid4().hex[:8]}"
        await sandbox.process.exec({
            "name": process_name,
            "command": "cd /app && npm run build",
            "wait_for_completion": False
        })
        await sandbox.process.wait(process_name, max_wait=300000, interval=2000)
        
        return {
            "sandbox_name": sandbox_name,
            "step": "npm build",
            "status": "complete",
            "message": "Production bundle built"
        }
    except Exception as e:
        return {"sandbox_name": sandbox_name, "step": "npm build", "status": "failed", "message": str(e)}


@mcp.tool(
    name="fleet_start_server",
    description=(
        "Start the production server and get the live URL.\n\n"
        "Parameters:\n"
        "- sandbox_name: Target sandbox\n\n"
        "Returns: { sandbox_name, url, status, message }"
    ),
)
async def fleet_start_server(
    sandbox_name: Annotated[str, "Name of the sandbox"],
    ctx: Context | None = None,
) -> ServerResult:
    """Start server and get URL."""
    sandbox = _active_sandboxes.get(sandbox_name)
    if not sandbox:
        return {"sandbox_name": sandbox_name, "url": "", "status": "failed", "message": "Sandbox not found"}
    
    try:
        # Start server
        await sandbox.process.exec({
            "name": "serve-app",
            "command": "cd /app && npx serve -s dist -l 3000",
            "wait_for_completion": False
        })
        
        await asyncio.sleep(5)
        
        # Create preview URL
        from datetime import datetime, timedelta, timezone
        
        preview = await sandbox.previews.create_if_not_exists({
            "metadata": {"name": "preview"},
            "spec": {
                "port": 3000,
                "public": False,
                "protocol": "HTTP",
                "responseHeaders": {"Access-Control-Allow-Origin": "*"}
            }
        })
        
        token_expiry = datetime.now(timezone.utc) + timedelta(hours=24)
        token = await preview.tokens.create(token_expiry)
        url = f"{preview.spec.url}?bl_preview_token={token.value}"
        
        return {
            "sandbox_name": sandbox_name,
            "url": url,
            "status": "live",
            "message": "Server running, game is playable!"
        }
    except Exception as e:
        return {"sandbox_name": sandbox_name, "url": "", "status": "failed", "message": str(e)}
