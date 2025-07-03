#!/usr/bin/env python3
"""Test MCP tools with the downloaded schema."""

import os
import sys
sys.path.insert(0, '.')

# Set environment variables
os.environ["HEALTHIE_API_URL"] = "http://localhost:3000/graphql"
# API key should be set in environment variables
# Example: export HEALTHIE_API_KEY="your-api-key"
if not os.getenv('HEALTHIE_API_KEY'):
    raise ValueError("HEALTHIE_API_KEY environment variable must be set")

from src.healthie_mcp.config import get_settings
from src.healthie_mcp.schema_manager import SchemaManager
from pathlib import Path

# Import the setup functions we need
from src.healthie_mcp.tools.schema_search import setup_schema_search_tool
from src.healthie_mcp.server import mcp

print("🧪 Testing MCP Server with downloaded schema\n")

# Initialize schema manager
settings = get_settings()
schema_manager = SchemaManager(
    api_endpoint=str(settings.healthie_api_url),
    cache_dir=Path(settings.schema_dir)
)

# Test 1: Schema content
print("📋 Testing schema access...")
try:
    schema_content = schema_manager.get_schema_content()
    print(f"✅ Schema loaded: {len(schema_content)} characters")
    
    # Check for key types
    key_types = ["type Patient", "type User", "type Appointment", "type Organization"]
    found_types = []
    for type_name in key_types:
        if type_name in schema_content:
            found_types.append(type_name.replace("type ", ""))
    
    print(f"✅ Found key types: {', '.join(found_types)}")
except Exception as e:
    print(f"❌ Failed to load schema: {e}")

print("\n" + "="*50 + "\n")

# Test 2: Search functionality
print("🔍 Testing schema search...")
try:
    # Direct test of schema search
    from src.healthie_mcp.tools.schema_search import SchemaSearcher
    
    searcher = SchemaSearcher(schema_content)
    
    # Search for Patient type
    result = searcher.search("Patient", "type", 2)
    print(f"✅ Search for 'Patient' found {result.total_matches} matches")
    
    if result.matches:
        print("📍 First few matches:")
        for match in result.matches[:3]:
            print(f"   - Line {match.line_number}: {match.match_type} - {match.content[:60]}...")
    
    # Search for appointment mutations
    result = searcher.search("appointment", "mutation", 1)
    print(f"\n✅ Search for 'appointment' mutations found {result.total_matches} matches")
    
    if result.matches:
        print("📍 First few mutation matches:")
        for match in result.matches[:3]:
            print(f"   - {match.content.strip()}")
            
except Exception as e:
    print(f"❌ Schema search failed: {e}")

print("\n" + "="*50 + "\n")

print("✨ Schema is ready for use!")
print("\n🚀 To use the MCP Inspector with full schema support:")
print("   uv run mcp dev run_server_with_auth.py:mcp")
print("\n📊 Available operations:")
print("   - Search for types, queries, mutations")
print("   - Get query templates for healthcare workflows") 
print("   - Generate code examples")
print("   - Analyze performance and relationships")