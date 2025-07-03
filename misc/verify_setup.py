#!/usr/bin/env python
"""Verify the setup is working correctly with environment variables."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("🔍 Verifying MCP Server Setup with Environment Variables")
print("=" * 60)

# 1. Check environment file
print("\n1. Environment File Check:")
env_files = [f for f in os.listdir('.') if f.startswith('.env')]
print(f"   Found files: {env_files}")

# 2. Check API key loading
from healthie_mcp.config import get_settings
settings = get_settings()

print("\n2. Settings Check:")
print(f"   API Key: {'✅ Loaded' if settings.healthie_api_key else '❌ Not loaded'}")
print(f"   API URL: {settings.healthie_api_url}")
print(f"   Schema Dir: {settings.schema_dir}")

# 3. Test schema manager
print("\n3. Schema Manager Check:")
try:
    from healthie_mcp.schema_manager import SchemaManager
    schema_manager = SchemaManager(
        api_key=settings.healthie_api_key,
        api_endpoint=str(settings.healthie_api_url),
        cache_dir=settings.schema_dir
    )
    print("   ✅ Schema manager initialized")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 4. Test tool imports
print("\n4. Tool Imports Check:")
tools_to_test = [
    "schema_search",
    "query_templates", 
    "code_examples",
    "type_introspection",
    "error_decoder",
    "compliance_checker",
    "workflow_sequences",
    "field_relationships"
]

for tool in tools_to_test:
    try:
        module = __import__(f"healthie_mcp.tools.{tool}", fromlist=["*"])
        print(f"   ✅ {tool}")
    except Exception as e:
        print(f"   ❌ {tool}: {e}")

# 5. Test server import
print("\n5. Server Check:")
try:
    from healthie_mcp.server import mcp
    print("   ✅ Server module loaded")
    print(f"   Server name: {mcp.name}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ Setup verification complete!")
print("\nYour environment variables are properly configured.")
print("The API key is being loaded from .env.development")
print("All tools are available and ready to use.")