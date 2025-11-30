"""STDIO MCP server for Claude Desktop integration.

This is a separate entry point that runs the same MCP tools but using STDIO transport
instead of HTTP. Use this for Claude Desktop demos.

Usage:
    python -m src.server_stdio

Claude Desktop config (claude_desktop_config.json):
{
    "mcpServers": {
        "Blaxel Fleet Commander": {
            "command": "C:\\Users\\NewUserName\\Desktop\\Blaxel Fleet Commander MCP Server\\.venv\\Scripts\\python.exe",
            "args": ["-m", "src.server_stdio"],
            "cwd": "C:\\Users\\NewUserName\\Desktop\\Blaxel Fleet Commander MCP Server"
        }
    }
}
"""

import logging
import os
import sys

# CRITICAL: Suppress ALL output before any imports
# MCP STDIO protocol requires clean stdout - any print() breaks it

# Disable wandb/weave BEFORE any imports
os.environ["WANDB_SILENT"] = "true"
os.environ["WANDB_MODE"] = "disabled"
os.environ["WANDB_DISABLED"] = "true"
os.environ["WEAVE_DISABLED"] = "true"

# Save original stderr
_original_stderr = sys.stderr

# Create a null device for suppressing output
_devnull = open(os.devnull, 'w')

# Redirect stderr to devnull during imports
sys.stderr = _devnull

logging.basicConfig(
    level=logging.CRITICAL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=_devnull,
)

# Suppress ALL loggers
logging.getLogger().setLevel(logging.CRITICAL)
for logger_name in ["httpx", "httpcore", "weave", "wandb", "qdrant_client", "llama_index", "root", "mcp-server"]:
    logging.getLogger(logger_name).setLevel(logging.CRITICAL)

# Load environment variables BEFORE any imports that need them
from dotenv import load_dotenv
load_dotenv()


def main():
    """Run the MCP server in STDIO mode for Claude Desktop."""
    # Keep stderr suppressed during imports
    from src.server import mcp
    
    # Restore stderr only after all imports are done
    sys.stderr = _original_stderr
    
    # Run with STDIO transport (overrides the HTTP config)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
