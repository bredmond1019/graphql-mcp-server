#!/usr/bin/env python3
"""Simple script to run the MCP server."""

import os
os.environ["HEALTHIE_API_URL"] = "http://localhost:3000/graphql"
# API key should be set in environment variables
# Example: export HEALTHIE_API_KEY="your-api-key"
if not os.getenv('HEALTHIE_API_KEY'):
    raise ValueError("HEALTHIE_API_KEY environment variable must be set")

from src.healthie_mcp.server import mcp

# Print server info
print(f"MCP Server initialized: {mcp}")
print(f"Server type: {type(mcp)}")

# The server would normally be launched by the MCP runtime
print("\nTo launch with MCP Inspector, run:")
print("  uv run mcp dev run_server.py:mcp")