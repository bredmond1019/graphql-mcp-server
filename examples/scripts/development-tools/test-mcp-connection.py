#!/usr/bin/env python3
"""
Test MCP Server Connection Script

What it does:
- Tests connection to the Healthie MCP server
- Validates all tool functionality
- Provides detailed diagnostics
- Helps debug connection issues

Usage:
    python test-mcp-connection.py
    python test-mcp-connection.py --tool search_schema
    python test-mcp-connection.py --verbose
"""

import sys
import json
import asyncio
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the MCP server to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from healthie_mcp.schema_manager import SchemaManager
    from healthie_mcp.config.settings import get_settings
    # Import server module to check it exists
    import healthie_mcp.server as server_module
    mcp = getattr(server_module, 'mcp', None)
except ImportError as e:
    print(f"❌ Failed to import MCP server: {e}")
    print("Make sure you're running from the correct directory and dependencies are installed.")
    print("Try: uv sync")
    sys.exit(1)


class MCPTester:
    """Test MCP server functionality"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = {}
        
    def log(self, message: str, level: str = "info"):
        """Log message with level"""
        if level == "error":
            print(f"❌ {message}")
        elif level == "warning":
            print(f"⚠️  {message}")
        elif level == "success":
            print(f"✅ {message}")
        elif self.verbose or level == "info":
            print(f"ℹ️  {message}")
    
    def test_server_import(self) -> bool:
        """Test if server can be imported"""
        try:
            self.log("Testing server import...")
            
            # Check if server module exists and mcp object is available
            if mcp is None:
                self.log("MCP server object not found", "error")
                return False
            
            # Debug: Show all attributes of the mcp object
            if self.verbose:
                attrs = [attr for attr in dir(mcp) if not attr.startswith('__')]
                self.log(f"MCP object attributes: {', '.join(attrs[:10])}...")
            
            # Check if server has tools - FastMCP uses different attribute names
            tools_attr = None
            possible_attrs = ['_tools', 'tools', '_handlers', '_tool_handlers', 'tool_list']
            for attr in possible_attrs:
                if hasattr(mcp, attr):
                    attr_value = getattr(mcp, attr)
                    if isinstance(attr_value, dict) and attr_value:
                        tools_attr = attr
                        break
                    elif hasattr(attr_value, '__len__') and len(attr_value) > 0:
                        tools_attr = attr
                        break
            
            if tools_attr is None:
                self.log("MCP server tools not found", "error")
                if self.verbose:
                    # Try to find any callable attributes that might be tools
                    callables = [attr for attr in dir(mcp) if callable(getattr(mcp, attr, None)) and not attr.startswith('_')]
                    self.log(f"Callable methods: {', '.join(callables[:5])}...")
                return False
            
            tools = getattr(mcp, tools_attr, {})
            if isinstance(tools, dict):
                self.log(f"Found {len(tools)} registered tools using '{tools_attr}'")
                if self.verbose:
                    for tool_name in tools.keys():
                        self.log(f"  - {tool_name}")
            else:
                self.log(f"Found tools in '{tools_attr}' (length: {len(tools)})")
                if self.verbose and hasattr(tools, '__iter__'):
                    for i, tool in enumerate(tools):
                        if i < 5:  # Show first 5
                            self.log(f"  - {getattr(tool, 'name', f'tool_{i}')}")
            
            self.results['server_import'] = True
            self.log("Server import successful", "success")
            return True
            
        except Exception as e:
            self.log(f"Server import failed: {e}", "error")
            self.results['server_import'] = False
            return False
    
    def test_configuration(self) -> bool:
        """Test configuration loading"""
        try:
            self.log("Testing configuration...")
            
            settings = get_settings()
            
            # Check required settings
            if not settings.healthie_api_url:
                self.log("API URL not configured", "warning")
            else:
                self.log(f"API URL: {settings.healthie_api_url}")
            
            if not settings.healthie_api_key:
                self.log("API key not configured (optional for some tools)", "warning")
            else:
                self.log("API key configured ✓")
            
            self.log(f"Schema directory: {settings.schema_dir}")
            self.log(f"Cache enabled: {settings.cache_enabled}")
            self.log(f"Cache duration: {settings.cache_duration_hours}h")
            
            self.results['configuration'] = True
            self.log("Configuration test successful", "success")
            return True
            
        except Exception as e:
            self.log(f"Configuration test failed: {e}", "error")
            self.results['configuration'] = False
            return False
    
    def test_schema_manager(self) -> bool:
        """Test schema manager functionality"""
        try:
            self.log("Testing schema manager...")
            
            settings = get_settings()
            schema_manager = SchemaManager(
                api_endpoint=str(settings.healthie_api_url),
                cache_dir=Path(settings.schema_dir)
            )
            
            # Test schema loading (if API key available)
            if settings.healthie_api_key:
                try:
                    schema_content = schema_manager.get_schema_content()
                    if schema_content:
                        self.log(f"Schema loaded: {len(schema_content)} characters")
                        self.log("Schema manager working with API", "success")
                    else:
                        self.log("Schema content empty", "warning")
                except Exception as e:
                    self.log(f"Schema loading failed: {e}", "warning")
                    self.log("Tools will work in limited mode without schema")
            else:
                self.log("No API key - schema loading skipped")
                self.log("Some tools require schema access")
            
            self.results['schema_manager'] = True
            return True
            
        except Exception as e:
            self.log(f"Schema manager test failed: {e}", "error")
            self.results['schema_manager'] = False
            return False
    
    async def test_individual_tool(self, tool_name: str) -> bool:
        """Test a specific tool"""
        try:
            self.log(f"Testing tool: {tool_name}")
            
            # Get the tool function from the server
            tools_attr = None
            for attr in ['_tools', 'tools', '_handlers']:
                if hasattr(mcp, attr):
                    tools_attr = attr
                    break
            
            if tools_attr is None:
                self.log(f"No tools found on server", "error")
                return False
            
            tools = getattr(mcp, tools_attr, {})
            if tool_name not in tools:
                self.log(f"Tool {tool_name} not found", "error")
                return False
            
            tool_func = tools[tool_name]
            
            # Test based on tool type
            test_params = self._get_test_params(tool_name)
            
            if test_params is None:
                self.log(f"No test parameters for {tool_name}", "warning")
                return True
            
            try:
                # Call the tool
                if asyncio.iscoroutinefunction(tool_func):
                    result = await tool_func(**test_params)
                else:
                    result = tool_func(**test_params)
                
                # Validate result
                if result:
                    self.log(f"Tool {tool_name} executed successfully", "success")
                    if self.verbose:
                        self._show_result_sample(tool_name, result)
                    return True
                else:
                    self.log(f"Tool {tool_name} returned empty result", "warning")
                    return False
                    
            except Exception as e:
                self.log(f"Tool {tool_name} execution failed: {e}", "error")
                return False
            
        except Exception as e:
            self.log(f"Tool test setup failed for {tool_name}: {e}", "error")
            return False
    
    def _get_test_params(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get test parameters for each tool"""
        test_params = {
            'search_schema': {
                'query': 'patient',
                'type_filter': 'type',
                'context_lines': 2
            },
            'introspect_type': {
                'type_name': 'Patient'
            },
            'query_templates': {
                'workflow': 'patient_management',
                'include_variables': True
            },
            'code_examples': {
                'category': 'patient_management',
                'language': 'javascript'
            },
            'healthcare_patterns': {
                'category': 'patient_workflows'
            },
            'workflow_sequences': {
                'category': 'patient_intake'
            },
            'field_relationships': {
                'source_type': 'Patient',
                'target_type': 'Appointment'
            },
            'input_validation': {
                'field_type': 'contact_information'
            },
            'error_decoder': {
                'error_message': 'Validation failed: Email already exists'
            },
            'performance_analyzer': {
                'category': 'best_practices'
            },
            'field_usage': {
                'type_name': 'Patient',
                'context': 'dashboard'
            }
        }
        
        return test_params.get(tool_name)
    
    def _show_result_sample(self, tool_name: str, result: Any):
        """Show a sample of the result"""
        try:
            if hasattr(result, 'dict'):
                # Pydantic model
                result_dict = result.dict()
            elif isinstance(result, dict):
                result_dict = result
            else:
                result_dict = {'result': str(result)}
            
            # Show key information
            if tool_name == 'search_schema' and 'matches' in result_dict:
                matches = result_dict['matches']
                self.log(f"  Found {len(matches)} matches")
                if matches:
                    self.log(f"  First match: {matches[0].get('match_type', 'unknown')} at line {matches[0].get('line_number', '?')}")
            
            elif tool_name == 'query_templates' and 'templates' in result_dict:
                templates = result_dict['templates']
                self.log(f"  Found {len(templates)} templates")
                if templates:
                    first_template = templates[0]
                    self.log(f"  First template: {first_template.get('name', 'unnamed')}")
            
            elif tool_name == 'code_examples' and 'examples' in result_dict:
                examples = result_dict['examples']
                self.log(f"  Found {len(examples)} examples")
                if examples:
                    first_example = examples[0]
                    self.log(f"  First example: {first_example.get('title', 'untitled')}")
            
            else:
                # Generic result info
                if isinstance(result_dict, dict):
                    keys = list(result_dict.keys())[:3]
                    self.log(f"  Result keys: {', '.join(keys)}")
                
        except Exception as e:
            self.log(f"  Could not parse result: {e}")
    
    async def test_all_tools(self) -> Dict[str, bool]:
        """Test all available tools"""
        self.log("Testing all tools...")
        
        # Get tools using the same logic
        tools_attr = None
        for attr in ['_tools', 'tools', '_handlers']:
            if hasattr(mcp, attr):
                tools_attr = attr
                break
        
        if tools_attr is None:
            self.log("No tools found on server", "error")
            return {}
        
        tools = getattr(mcp, tools_attr, {})
        results = {}
        
        for tool_name in tools.keys():
            try:
                success = await self.test_individual_tool(tool_name)
                results[tool_name] = success
            except Exception as e:
                self.log(f"Unexpected error testing {tool_name}: {e}", "error")
                results[tool_name] = False
        
        return results
    
    async def run_full_test(self, specific_tool: Optional[str] = None) -> Dict[str, Any]:
        """Run complete test suite"""
        self.log("🚀 Starting MCP Connection Test")
        self.log("=" * 50)
        
        # Basic tests
        self.test_server_import()
        self.test_configuration()
        self.test_schema_manager()
        
        # Tool tests
        if specific_tool:
            self.log(f"\nTesting specific tool: {specific_tool}")
            success = await self.test_individual_tool(specific_tool)
            self.results[f'tool_{specific_tool}'] = success
        else:
            self.log("\nTesting all tools...")
            tool_results = await self.test_all_tools()
            self.results['tools'] = tool_results
        
        # Summary
        self.log("\n" + "=" * 50)
        self.log("📊 Test Results Summary")
        self._show_summary()
        
        return self.results
    
    def _show_summary(self):
        """Show test results summary"""
        total_tests = 0
        passed_tests = 0
        
        # Basic tests
        basic_tests = ['server_import', 'configuration', 'schema_manager']
        for test in basic_tests:
            total_tests += 1
            if self.results.get(test, False):
                passed_tests += 1
                self.log(f"✅ {test.replace('_', ' ').title()}")
            else:
                self.log(f"❌ {test.replace('_', ' ').title()}")
        
        # Tool tests
        if 'tools' in self.results:
            for tool_name, success in self.results['tools'].items():
                total_tests += 1
                if success:
                    passed_tests += 1
                    self.log(f"✅ Tool: {tool_name}")
                else:
                    self.log(f"❌ Tool: {tool_name}")
        
        # Individual tool test
        for key, value in self.results.items():
            if key.startswith('tool_'):
                tool_name = key[5:]  # Remove 'tool_' prefix
                total_tests += 1
                if value:
                    passed_tests += 1
                    self.log(f"✅ Tool: {tool_name}")
                else:
                    self.log(f"❌ Tool: {tool_name}")
        
        # Overall status
        self.log(f"\n📈 Overall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            self.log("🎉 All tests passed! MCP server is working correctly.", "success")
        elif passed_tests > total_tests * 0.8:
            self.log("⚠️  Most tests passed. Check warnings above.", "warning")
        else:
            self.log("❌ Multiple test failures. Check configuration and setup.", "error")
        
        # Recommendations
        self.log("\n💡 Recommendations:")
        
        if not self.results.get('configuration', False):
            self.log("  - Check environment variables (HEALTHIE_API_URL, HEALTHIE_API_KEY)")
        
        if not self.results.get('schema_manager', False):
            self.log("  - Verify network connectivity to Healthie API")
            self.log("  - Check API key permissions")
        
        failed_tools = []
        if 'tools' in self.results:
            failed_tools = [name for name, success in self.results['tools'].items() if not success]
        
        if failed_tools:
            self.log(f"  - Failed tools: {', '.join(failed_tools)}")
            self.log("  - Some tools require valid schema access")
            self.log("  - Check individual tool requirements")


async def main():
    """Main test function"""
    parser = argparse.ArgumentParser(description="Test Healthie MCP server connection")
    parser.add_argument('--tool', help="Test specific tool only")
    parser.add_argument('--verbose', '-v', action='store_true', help="Verbose output")
    parser.add_argument('--json', action='store_true', help="Output results as JSON")
    
    args = parser.parse_args()
    
    tester = MCPTester(verbose=args.verbose)
    
    try:
        results = await tester.run_full_test(specific_tool=args.tool)
        
        if args.json:
            print(json.dumps(results, indent=2))
        
        # Exit code based on results
        if all(results.values()):
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())