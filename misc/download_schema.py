#!/usr/bin/env python3
"""Download GraphQL schema from Healthie API using introspection."""

import os
import httpx
import json
from pathlib import Path
from graphql import get_introspection_query, build_client_schema, print_schema

# Configuration
API_URL = "http://localhost:3000/graphql"
# API key should be set in environment variables
# Example: export HEALTHIE_API_KEY="your-api-key"
API_KEY = os.getenv('HEALTHIE_API_KEY')
if not API_KEY:
    raise ValueError("HEALTHIE_API_KEY environment variable must be set")
SCHEMA_DIR = Path("schemas")

def download_schema():
    """Download schema using introspection query."""
    print("📥 Downloading schema from Healthie API...")
    
    # Get the introspection query
    introspection_query = get_introspection_query()
    
    # Set up headers with proper authentication
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {API_KEY}",
        "AuthorizationSource": "API"
    }
    
    # Make the request
    try:
        response = httpx.post(
            API_URL,
            json={"query": introspection_query},
            headers=headers,
            timeout=60.0  # Longer timeout for introspection
        )
        response.raise_for_status()
        
        result = response.json()
        
        if "errors" in result:
            print(f"❌ GraphQL errors: {result['errors']}")
            return False
            
        if "data" not in result:
            print("❌ No data in response")
            return False
            
        # Build the client schema from introspection result
        schema = build_client_schema(result["data"])
        
        # Convert to SDL format
        schema_sdl = print_schema(schema)
        
        # Save to file
        SCHEMA_DIR.mkdir(exist_ok=True)
        schema_file = SCHEMA_DIR / "schema.graphql"
        schema_file.write_text(schema_sdl)
        
        # Also save the introspection result
        introspection_file = SCHEMA_DIR / "introspection.json"
        with open(introspection_file, "w") as f:
            json.dump(result["data"], f, indent=2)
        
        print(f"✅ Schema downloaded successfully!")
        print(f"   SDL saved to: {schema_file}")
        print(f"   Introspection saved to: {introspection_file}")
        print(f"   Schema size: {len(schema_sdl)} characters")
        
        # Show some stats
        type_count = len(result["data"]["__schema"]["types"])
        query_fields = len([f for f in result["data"]["__schema"]["types"] 
                          if f["name"] == "Query"][0]["fields"] or [])
        mutation_fields = len([f for f in result["data"]["__schema"]["types"] 
                             if f["name"] == "Mutation"][0]["fields"] or [])
        
        print(f"\n📊 Schema Statistics:")
        print(f"   Total types: {type_count}")
        print(f"   Query fields: {query_fields}")
        print(f"   Mutation fields: {mutation_fields}")
        
        return True
        
    except httpx.HTTPError as e:
        print(f"❌ HTTP error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error downloading schema: {e}")
        return False

if __name__ == "__main__":
    success = download_schema()
    if success:
        print("\n🚀 Schema is ready for use with MCP server!")
    else:
        print("\n❌ Failed to download schema")