#!/usr/bin/env python3
"""Simple script to run the MCP server."""

import os
os.environ["HEALTHIE_API_URL"] = "http://localhost:3000/graphql"
os.environ["HEALTHIE_API_KEY"] = "gh_sbox_KmRjkj8kBMYIN8sql7qEMf2oy47WCfWoTHTDun4k9NrYi1fP9PnFM1m54hITV1Am"

from src.healthie_mcp.server import mcp

# Print server info
print(f"MCP Server initialized: {mcp}")
print(f"Server type: {type(mcp)}")

# The server would normally be launched by the MCP runtime
print("\nTo launch with MCP Inspector, run:")
print("  uv run mcp dev run_server.py:mcp")