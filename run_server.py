#!/usr/bin/env python
"""Simple wrapper to run the MCP server."""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Now import and run the server
from healthie_mcp.server import mcp

if __name__ == "__main__":
    # Run with MCP dev
    import subprocess
    subprocess.run([sys.executable, "-m", "mcp", "dev", __file__ + ":mcp"] + sys.argv[1:])