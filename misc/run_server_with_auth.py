#!/usr/bin/env python3
"""Run MCP server with proper Healthie authentication."""

import os

# Set environment variables with correct authentication
os.environ["HEALTHIE_API_URL"] = "http://localhost:3000/graphql"
os.environ["HEALTHIE_API_KEY"] = "gh_sbox_KmRjkj8kBMYIN8sql7qEMf2oy47WCfWoTHTDun4k9NrYi1fP9PnFM1m54hITV1Am"
os.environ["HEALTHIE_AUTH_TYPE"] = "Basic"  # Use Basic instead of Bearer
os.environ["HEALTHIE_AUTH_SOURCE"] = "API"  # Add AuthorizationSource header

from src.healthie_mcp.server import mcp

print("✅ MCP Server initialized with proper Healthie authentication")
print(f"   API URL: {os.environ['HEALTHIE_API_URL']}")
print(f"   Auth Type: Basic")
print(f"   Auth Source: API")
print("\n🚀 To launch with MCP Inspector, run:")
print("   uv run mcp dev run_server_with_auth.py:mcp")