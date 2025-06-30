#!/usr/bin/env python3
"""Verify that the MCP package is accessible from the virtual environment."""

import sys
import importlib

def verify_mcp_package():
    """Verify that the MCP package can be imported."""
    try:
        import mcp
        print(f"✅ MCP package imported successfully!")
        print(f"   MCP version: {mcp.__version__ if hasattr(mcp, '__version__') else 'Unknown'}")
        print(f"   Python path: {sys.executable}")
        print(f"   Python version: {sys.version}")
        
        # Try to import specific MCP modules
        try:
            from mcp.server.fastmcp import FastMCP
            print("✅ FastMCP module imported successfully!")
        except ImportError as e:
            print(f"⚠️  FastMCP module not available: {e}")
            
    except ImportError as e:
        print(f"❌ Failed to import MCP package: {e}")
        print(f"   Python path: {sys.executable}")
        print(f"   Python version: {sys.version}")
        return False
    
    return True

if __name__ == "__main__":
    print("Verifying MCP package accessibility...")
    success = verify_mcp_package()
    sys.exit(0 if success else 1) 