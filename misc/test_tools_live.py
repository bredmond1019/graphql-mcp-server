#!/usr/bin/env python
"""Test MCP tools by calling them directly through the server functions."""

import os
import sys
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the server module to get access to the registered tools
from healthie_mcp.server import mcp
from healthie_mcp.config import get_settings


def test_tool(tool_name: str, params: dict):
    """Test a tool by calling it through the MCP server."""
    print(f"\n{'='*80}")
    print(f"Testing: {tool_name}")
    print(f"Parameters: {json.dumps(params, indent=2)}")
    print(f"{'='*80}")
    
    try:
        # Get the tool function from the MCP server
        tool_func = None
        for tool in mcp._tools:
            if tool.name == tool_name:
                tool_func = tool.function
                break
        
        if not tool_func:
            print(f"❌ Tool '{tool_name}' not found in MCP server")
            return False
            
        # Call the tool
        result = tool_func(**params)
        
        print(f"✅ SUCCESS")
        print(f"Result: {json.dumps(result, indent=2, default=str)}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False


def main():
    """Run tests for all tools."""
    print("MCP Tools Live Test")
    print(f"Environment: HEALTHIE_API_KEY = {'Set' if os.getenv('HEALTHIE_API_KEY') else 'Not Set'}")
    print(f"API URL: {get_settings().healthie_api_url}")
    
    # Define test cases for each tool
    test_cases = [
        # 1. search_schema
        {
            "tool": "search_schema",
            "tests": [
                {"query": "User", "type_filter": "type"},
                {"query": "appointment", "type_filter": "query"},
                {"query": "create", "type_filter": "mutation"}
            ]
        },
        
        # 2. query_templates
        {
            "tool": "query_templates",
            "tests": [
                {"workflow_category": "appointments"},
                {"workflow_category": "patient_management"},
                {"workflow_category": "billing"}
            ]
        },
        
        # 3. code_examples
        {
            "tool": "code_examples",
            "tests": [
                {"operation_name": "authentication", "language": "javascript"},
                {"operation_name": "create_appointment", "language": "python"},
                {"operation_name": "patient_search", "language": "curl"}
            ]
        },
        
        # 4. introspect_type
        {
            "tool": "introspect_type",
            "tests": [
                {"type_name": "User"},
                {"type_name": "Appointment"},
                {"type_name": "Mutation"}
            ]
        },
        
        # 5. error_decoder
        {
            "tool": "error_decoder",
            "tests": [
                {"error_message": "User not authenticated", "error_code": "UNAUTHENTICATED"},
                {"error_message": "Field 'xyz' not found", "error_code": "FIELD_NOT_FOUND"},
                {"error_message": "Rate limit exceeded"},
            ]
        },
        
        # 6. compliance_checker
        {
            "tool": "compliance_checker",
            "tests": [
                {"operation_type": "query", "data_fields": ["name", "date_of_birth", "ssn"]},
                {"operation_type": "mutation", "data_fields": ["medical_record_number", "diagnosis"]},
                {"operation_type": "query", "data_fields": ["email", "phone"]}
            ]
        },
        
        # 7. workflow_sequences
        {
            "tool": "workflow_sequences",
            "tests": [
                {"workflow_name": "patient_onboarding"},
                {"workflow_name": "appointment_scheduling"},
                {"workflow_name": "billing_cycle"}
            ]
        },
        
        # 8. field_relationships
        {
            "tool": "field_relationships",
            "tests": [
                {"type_name": "User", "field_name": "id"},
                {"type_name": "Appointment", "field_name": "patient"},
                {"type_name": "Query", "field_name": "appointments"}
            ]
        }
    ]
    
    # Run tests
    total_tests = 0
    passed_tests = 0
    
    for tool_config in test_cases:
        tool_name = tool_config["tool"]
        print(f"\n\n{'#'*80}")
        print(f"# Testing Tool: {tool_name}")
        print(f"{'#'*80}")
        
        for test_params in tool_config["tests"]:
            total_tests += 1
            if test_tool(tool_name, test_params):
                passed_tests += 1
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)