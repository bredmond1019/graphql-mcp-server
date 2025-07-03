#!/usr/bin/env python3
"""Test script for MCP server with local Healthie instance."""

import os
import sys
import asyncio
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.healthie_mcp.config import get_settings
from src.healthie_mcp.schema_manager import SchemaManager
from src.healthie_mcp.tools.schema_search import SchemaSearchTool
from src.healthie_mcp.tools.query_templates import QueryTemplatesTool
from src.healthie_mcp.tools.code_examples import CodeExamplesTool

async def test_mcp_server():
    """Test MCP server functionality with local server."""
    
    # Get settings
    settings = get_settings()
    print(f"🔧 Configuration:")
    print(f"   API URL: {settings.healthie_api_url}")
    print(f"   API Key: {settings.healthie_api_key[:20]}..." if settings.healthie_api_key else "   API Key: Not set")
    print(f"   Schema Dir: {settings.schema_dir}\n")
    
    # Initialize schema manager
    schema_manager = SchemaManager(
        api_endpoint=str(settings.healthie_api_url),
        cache_dir=Path(settings.schema_dir)
    )
    
    # Test 1: Schema Download
    print("📥 Testing schema download...")
    try:
        # Download the full introspection query
        import httpx
        
        introspection_query = """
        query IntrospectionQuery {
          __schema {
            types {
              name
              kind
              description
              fields {
                name
                type {
                  name
                  kind
                }
              }
            }
          }
        }
        """
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.healthie_api_key}"
        }
        
        response = httpx.post(
            settings.healthie_api_url,
            json={"query": introspection_query},
            headers=headers,
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            if "data" in data and "__schema" in data["data"]:
                types = data["data"]["__schema"]["types"]
                print(f"   ✅ Schema downloaded successfully!")
                print(f"   📊 Found {len(types)} types")
                
                # Show some key types
                key_types = ["Patient", "User", "Appointment", "Organization"]
                for type_name in key_types:
                    type_info = next((t for t in types if t["name"] == type_name), None)
                    if type_info:
                        field_count = len(type_info.get("fields", [])) if type_info.get("fields") else 0
                        print(f"      - {type_name}: {field_count} fields")
        else:
            print(f"   ❌ Failed to download schema: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error downloading schema: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Schema Search Tool
    print("🔍 Testing Schema Search Tool...")
    search_tool = SchemaSearchTool(schema_manager)
    
    try:
        # Mock schema content for testing
        mock_schema = """
        type Patient {
            id: ID!
            name: String
            email: String
            appointments: [Appointment]
        }
        
        type Appointment {
            id: ID!
            patient: Patient
            provider: Provider
            datetime: String
        }
        """
        
        # Save mock schema for testing
        schema_path = Path(settings.schema_dir) / "schema.graphql"
        schema_path.parent.mkdir(exist_ok=True)
        schema_path.write_text(mock_schema)
        
        result = search_tool.execute(query="patient", type_filter="type", context_lines=2)
        print(f"   ✅ Schema search working!")
        print(f"   📋 Found {len(result.matches)} matches for 'patient'")
        for match in result.matches[:3]:
            print(f"      - Line {match.line_number}: {match.match_type}")
    except Exception as e:
        print(f"   ❌ Schema search failed: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: Query Templates Tool
    print("📝 Testing Query Templates Tool...")
    templates_tool = QueryTemplatesTool(None)  # Doesn't need schema manager
    
    try:
        result = templates_tool.execute(workflow="patient_management", include_variables=True)
        print(f"   ✅ Query templates working!")
        print(f"   📋 Found {len(result.templates)} templates")
        for template in result.templates[:3]:
            print(f"      - {template.name}: {template.description}")
    except Exception as e:
        print(f"   ❌ Query templates failed: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 4: Code Examples Tool
    print("💻 Testing Code Examples Tool...")
    examples_tool = CodeExamplesTool(None)  # Doesn't need schema manager
    
    try:
        result = examples_tool.execute(operation="create_patient", language="javascript")
        print(f"   ✅ Code examples working!")
        print(f"   📋 Found {len(result.examples)} examples")
        for example in result.examples[:3]:
            print(f"      - {example.title}")
    except Exception as e:
        print(f"   ❌ Code examples failed: {e}")
    
    print("\n" + "="*50 + "\n")
    
    print("✨ Test Summary:")
    print("   - Configuration: ✅")
    print("   - Schema Download: Check above")
    print("   - Tools: Check individual results above")
    print("\n🚀 Next step: Run 'uv run mcp dev src.healthie_mcp.server:mcp' to launch MCP Inspector")

if __name__ == "__main__":
    # Set environment variables if not already set
    if not os.getenv("HEALTHIE_API_URL"):
        os.environ["HEALTHIE_API_URL"] = "http://localhost:3000/graphql"
    if not os.getenv("HEALTHIE_API_KEY"):
        os.environ["HEALTHIE_API_KEY"] = "gh_sbox_KmRjkj8kBMYIN8sql7qEMf2oy47WCfWoTHTDun4k9NrYi1fP9PnFM1m54hITV1Am"
    
    asyncio.run(test_mcp_server())