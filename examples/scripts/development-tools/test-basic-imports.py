#!/usr/bin/env python3
"""
Basic Import Test Script

What it does:
- Tests basic imports and module structure
- Validates configuration loading
- Checks schema manager functionality
- Verifies tool modules can be imported

Usage:
    python test-basic-imports.py
    python test-basic-imports.py --verbose
"""

import sys
import traceback
from pathlib import Path

# Add the MCP server to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

def test_imports():
    """Test all important imports"""
    print("🧪 Testing Basic Imports")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Basic configuration
    total_tests += 1
    try:
        from healthie_mcp.config.settings import get_settings
        settings = get_settings()
        print("✅ Settings import and loading")
        print(f"   API URL: {settings.healthie_api_url}")
        print(f"   Schema dir: {settings.schema_dir}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Settings import failed: {e}")
    
    # Test 2: Schema manager
    total_tests += 1
    try:
        from healthie_mcp.schema_manager import SchemaManager
        schema_manager = SchemaManager(
            api_endpoint=str(settings.healthie_api_url),
            cache_dir=Path(settings.schema_dir)
        )
        print("✅ Schema manager import and creation")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Schema manager failed: {e}")
    
    # Test 3: Base classes
    total_tests += 1
    try:
        from healthie_mcp.base import BaseTool, SchemaManagerProtocol
        print("✅ Base classes import")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Base classes failed: {e}")
    
    # Test 4: Models
    total_tests += 1
    try:
        from healthie_mcp.models.schema_search import SchemaSearchResult
        from healthie_mcp.models.query_templates import QueryTemplatesResult
        print("✅ Pydantic models import")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Models import failed: {e}")
    
    # Test 5: Configuration loader
    total_tests += 1
    try:
        from healthie_mcp.config.loader import get_config_loader
        config_loader = get_config_loader()
        queries_config = config_loader.load_queries()
        print("✅ Configuration loader and YAML loading")
        print(f"   Loaded {len(queries_config)} query categories")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Configuration loader failed: {e}")
    
    # Test 6: Individual tool modules
    tool_modules = [
        'schema_search',
        'query_templates', 
        'healthcare_patterns',
        'code_examples',
        'input_validation'
    ]
    
    for tool_name in tool_modules:
        total_tests += 1
        try:
            module = __import__(f'healthie_mcp.tools.{tool_name}', fromlist=[tool_name])
            print(f"✅ Tool module: {tool_name}")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Tool module {tool_name} failed: {e}")
    
    # Test 7: FastMCP import (without initialization)
    total_tests += 1
    try:
        from mcp.server.fastmcp import FastMCP
        print("✅ FastMCP import")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FastMCP import failed: {e}")
    
    # Test 8: Server module structure
    total_tests += 1
    try:
        import healthie_mcp.server as server_module
        # Check it has the expected components
        assert hasattr(server_module, 'mcp')
        assert hasattr(server_module, 'schema_manager')
        assert hasattr(server_module, 'settings')
        print("✅ Server module structure")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Server module structure failed: {e}")
    
    # Summary
    print("\n" + "=" * 40)
    print(f"📊 Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All imports working correctly!")
        return True
    else:
        print("⚠️  Some imports failed. Check dependencies.")
        return False

def test_tool_creation():
    """Test creating tool instances"""
    print("\n🔧 Testing Tool Creation")
    print("=" * 40)
    
    try:
        from healthie_mcp.config.settings import get_settings
        from healthie_mcp.schema_manager import SchemaManager
        from healthie_mcp.tools.query_templates import QueryTemplatesTool
        from healthie_mcp.tools.healthcare_patterns import setup_healthcare_patterns_tool
        
        settings = get_settings()
        schema_manager = SchemaManager(
            api_endpoint=str(settings.healthie_api_url),
            cache_dir=Path(settings.schema_dir)
        )
        
        # Test creating tool instances
        query_tool = QueryTemplatesTool(schema_manager)
        print("✅ QueryTemplatesTool created")
        
        # Test tool methods
        tool_name = query_tool.get_tool_name()
        tool_desc = query_tool.get_tool_description()
        print(f"✅ Tool metadata: {tool_name} - {tool_desc[:50]}...")
        
        # Test that setup functions exist
        print("✅ Healthcare patterns setup function imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool creation failed: {e}")
        traceback.print_exc()
        return False

def test_tool_execution():
    """Test executing tools"""
    print("\n⚡ Testing Tool Execution")
    print("=" * 40)
    
    try:
        from healthie_mcp.config.settings import get_settings
        from healthie_mcp.schema_manager import SchemaManager
        from healthie_mcp.tools.query_templates import QueryTemplatesTool
        
        settings = get_settings()
        schema_manager = SchemaManager(
            api_endpoint=str(settings.healthie_api_url),
            cache_dir=Path(settings.schema_dir)
        )
        
        # Test query templates (config-driven)
        query_tool = QueryTemplatesTool(schema_manager)
        result = query_tool.execute(workflow="patient_management", include_variables=True)
        print(f"✅ Query templates: Found {result.total_count} templates")
        
        # Test individual template details
        if result.templates:
            first_template = result.templates[0]
            print(f"✅ Template details: {first_template.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool execution failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Healthie MCP Server - Basic Import Tests")
    print("=" * 50)
    
    all_passed = True
    
    # Run tests in order
    if not test_imports():
        all_passed = False
    
    if not test_tool_creation():
        all_passed = False
        
    if not test_tool_execution():
        all_passed = False
    
    # Final summary
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! MCP server is ready to use.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()