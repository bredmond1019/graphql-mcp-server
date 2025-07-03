#!/usr/bin/env python3
"""Test individual tools directly."""

import os
import sys
sys.path.insert(0, '.')

# Set environment variables
os.environ["HEALTHIE_API_URL"] = "http://localhost:3000/graphql"
os.environ["HEALTHIE_API_KEY"] = "gh_sbox_KmRjkj8kBMYIN8sql7qEMf2oy47WCfWoTHTDun4k9NrYi1fP9PnFM1m54hITV1Am"

from src.healthie_mcp.server import mcp
from src.healthie_mcp.config import get_settings

# Check server initialization
print("🚀 MCP Server Status:")
print(f"   Server initialized: {'✅' if mcp else '❌'}")

# List all registered tools
print("\n📦 Available Tools:")

# FastMCP stores tools differently, let's find them
import inspect

# Get all methods that might be tools
for name, method in inspect.getmembers(mcp):
    if name.startswith('_'):
        continue
    if callable(method):
        # Check if it has tool metadata
        if hasattr(method, '__tool__') or 'tool' in str(type(method)).lower():
            print(f"   - {name}")

# Check configuration
settings = get_settings()
print("\n⚙️  Configuration:")
print(f"   API URL: {settings.healthie_api_url}")
print(f"   API Key: {'Set' if settings.healthie_api_key else 'Not set'}")

print("\n✨ To use the MCP server:")
print("   1. Run: uv run mcp dev run_server.py:mcp")
print("   2. Open the URL shown in your browser")
print("   3. Use the MCP Inspector to test tools interactively")