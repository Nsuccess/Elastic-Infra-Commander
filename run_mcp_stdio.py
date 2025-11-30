#!/usr/bin/env python
"""Wrapper script to run MCP server in STDIO mode for Claude Desktop.

This script ensures the correct working directory and Python path are set
before launching the MCP server.

Usage in claude_desktop_config.json:
{
    "mcpServers": {
        "Blaxel Fleet Commander": {
            "command": "C:\\Users\\NewUserName\\Desktop\\Blaxel Fleet Commander MCP Server\\.venv\\Scripts\\python.exe",
            "args": ["C:\\Users\\NewUserName\\Desktop\\Blaxel Fleet Commander MCP Server\\run_mcp_stdio.py"]
        }
    }
}
"""

import os
import sys

# CRITICAL: Suppress ALL output BEFORE any imports
# MCP STDIO protocol requires clean stdout/stderr
os.environ["WANDB_SILENT"] = "true"
os.environ["WANDB_MODE"] = "disabled"
os.environ["WANDB_DISABLED"] = "true"
os.environ["WEAVE_DISABLED"] = "true"

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Change to the project directory
os.chdir(SCRIPT_DIR)

# Add the project directory to Python path
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# Now run the server
from src.server_stdio import main

if __name__ == "__main__":
    main()
