#!/usr/bin/env python
"""Test all MCP tools to ensure they work with environment variables."""

import os
import sys
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from healthie_mcp.schema_manager import SchemaManager
from healthie_mcp.config import get_settings
from healthie_mcp.tools.schema_search import SchemaSearchTool
from healthie_mcp.tools.query_templates import QueryTemplatesTool
from healthie_mcp.tools.code_examples import CodeExampleTool
from healthie_mcp.tools.type_introspection import TypeIntrospectionTool
from healthie_mcp.tools.error_decoder import ErrorDecoderTool
from healthie_mcp.tools.compliance_checker import ComplianceCheckerTool
from healthie_mcp.tools.workflow_sequences import WorkflowSequenceTool
from healthie_mcp.tools.field_relationships import FieldRelationshipTool

from healthie_mcp.models.schema_tools import SchemaSearchInput, TypeIntrospectionInput
from healthie_mcp.models.external_dev_tools import (
    QueryTemplateInput, CodeExampleInput, ErrorDecoderInput,
    ComplianceCheckInput, WorkflowSequenceInput, FieldRelationshipInput
)


def print_result(tool_name: str, test_name: str, result: Dict[str, Any], error: Exception = None):
    """Print test results in a nice format."""
    print(f"\n{'='*80}")
    print(f"Tool: {tool_name} - Test: {test_name}")
    print(f"{'='*80}")
    
    if error:
        print(f"❌ ERROR: {str(error)}")
    else:
        print(f"✅ SUCCESS")
        if isinstance(result, dict):
            for key, value in result.items():
                if isinstance(value, list) and len(value) > 3:
                    print(f"  {key}: [{len(value)} items]")
                elif isinstance(value, str) and len(value) > 100:
                    print(f"  {key}: {value[:100]}...")
                else:
                    print(f"  {key}: {value}")


def test_all_tools():
    """Test all 8 working MCP tools."""
    print("Starting MCP Tools Test Suite")
    print(f"Environment: HEALTHIE_API_KEY = {'Set' if os.getenv('HEALTHIE_API_KEY') else 'Not Set'}")
    print(f"API URL: {get_settings().healthie_api_url}")
    
    # Initialize schema manager
    settings = get_settings()
    schema_manager = SchemaManager(
        api_key=settings.healthie_api_key,
        api_endpoint=str(settings.healthie_api_url),
        cache_dir=settings.schema_dir
    )
    
    # Test results summary
    results_summary = []
    
    # 1. Test search_schema
    print("\n" + "="*80)
    print("Testing Tool 1/8: search_schema")
    print("="*80)
    
    try:
        tool = SchemaSearchTool(schema_manager)
        
        # Test 1: Search for User type
        result = tool.execute(SchemaSearchInput(query="User", type_filter="type"))
        print_result("search_schema", "Search for User type", result.model_dump())
        results_summary.append(("search_schema", "User type search", True, None))
        
        # Test 2: Search for appointment queries
        result = tool.execute(SchemaSearchInput(query="appointment", type_filter="query"))
        print_result("search_schema", "Search for appointment queries", result.model_dump())
        results_summary.append(("search_schema", "appointment queries", True, None))
        
    except Exception as e:
        print_result("search_schema", "Failed", None, e)
        results_summary.append(("search_schema", "All tests", False, str(e)))
    
    # 2. Test query_templates
    print("\n" + "="*80)
    print("Testing Tool 2/8: query_templates")
    print("="*80)
    
    try:
        tool = QueryTemplatesTool(schema_manager)
        
        # Test: Get appointment templates
        result = tool.execute(QueryTemplateInput(workflow_category="appointments"))
        print_result("query_templates", "Appointment templates", result.model_dump())
        results_summary.append(("query_templates", "Appointment templates", True, None))
        
    except Exception as e:
        print_result("query_templates", "Failed", None, e)
        results_summary.append(("query_templates", "All tests", False, str(e)))
    
    # 3. Test code_examples
    print("\n" + "="*80)
    print("Testing Tool 3/8: code_examples")
    print("="*80)
    
    try:
        tool = CodeExampleTool(schema_manager)
        
        # Test: Generate authentication examples
        result = tool.execute(CodeExampleInput(
            operation_name="authentication",
            language="javascript"
        ))
        print_result("code_examples", "Authentication JS example", result.model_dump())
        results_summary.append(("code_examples", "Authentication examples", True, None))
        
    except Exception as e:
        print_result("code_examples", "Failed", None, e)
        results_summary.append(("code_examples", "All tests", False, str(e)))
    
    # 4. Test introspect_type
    print("\n" + "="*80)
    print("Testing Tool 4/8: introspect_type")
    print("="*80)
    
    try:
        tool = TypeIntrospectionTool(schema_manager)
        
        # Test: Introspect User type
        result = tool.execute(TypeIntrospectionInput(type_name="User"))
        print_result("introspect_type", "User type introspection", result.model_dump())
        results_summary.append(("introspect_type", "User type", True, None))
        
    except Exception as e:
        print_result("introspect_type", "Failed", None, e)
        results_summary.append(("introspect_type", "All tests", False, str(e)))
    
    # 5. Test error_decoder
    print("\n" + "="*80)
    print("Testing Tool 5/8: error_decoder")
    print("="*80)
    
    try:
        tool = ErrorDecoderTool(schema_manager)
        
        # Test: Decode authentication error
        result = tool.execute(ErrorDecoderInput(
            error_message="User not authenticated",
            error_code="UNAUTHENTICATED"
        ))
        print_result("error_decoder", "Authentication error", result.model_dump())
        results_summary.append(("error_decoder", "Auth error", True, None))
        
    except Exception as e:
        print_result("error_decoder", "Failed", None, e)
        results_summary.append(("error_decoder", "All tests", False, str(e)))
    
    # 6. Test compliance_checker
    print("\n" + "="*80)
    print("Testing Tool 6/8: compliance_checker")
    print("="*80)
    
    try:
        tool = ComplianceCheckerTool(schema_manager)
        
        # Test: Check patient data query
        result = tool.execute(ComplianceCheckInput(
            operation_type="query",
            data_fields=["name", "date_of_birth", "medical_record_number"]
        ))
        print_result("compliance_checker", "Patient data compliance", result.model_dump())
        results_summary.append(("compliance_checker", "Patient data", True, None))
        
    except Exception as e:
        print_result("compliance_checker", "Failed", None, e)
        results_summary.append(("compliance_checker", "All tests", False, str(e)))
    
    # 7. Test workflow_sequences
    print("\n" + "="*80)
    print("Testing Tool 7/8: workflow_sequences")
    print("="*80)
    
    try:
        tool = WorkflowSequenceTool(schema_manager)
        
        # Test: Patient onboarding workflow
        result = tool.execute(WorkflowSequenceInput(
            workflow_name="patient_onboarding"
        ))
        print_result("workflow_sequences", "Patient onboarding", result.model_dump())
        results_summary.append(("workflow_sequences", "Patient onboarding", True, None))
        
    except Exception as e:
        print_result("workflow_sequences", "Failed", None, e)
        results_summary.append(("workflow_sequences", "All tests", False, str(e)))
    
    # 8. Test field_relationships
    print("\n" + "="*80)
    print("Testing Tool 8/8: field_relationships")
    print("="*80)
    
    try:
        tool = FieldRelationshipTool(schema_manager)
        
        # Test: User field relationships
        result = tool.execute(FieldRelationshipInput(
            type_name="User",
            field_name="id"
        ))
        print_result("field_relationships", "User.id relationships", result.model_dump())
        results_summary.append(("field_relationships", "User.id", True, None))
        
    except Exception as e:
        print_result("field_relationships", "Failed", None, e)
        results_summary.append(("field_relationships", "All tests", False, str(e)))
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    total_tests = len(results_summary)
    passed_tests = sum(1 for _, _, success, _ in results_summary if success)
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nDetailed Results:")
    for tool, test, success, error in results_summary:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {tool}: {test}")
        if error:
            print(f"       Error: {error}")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    # Check if environment variables are loaded
    if not os.getenv('HEALTHIE_API_KEY'):
        print("⚠️  WARNING: HEALTHIE_API_KEY not found in environment")
        print("   The .env.development file should be automatically loaded")
        print("   Current working directory:", os.getcwd())
        print("   Looking for .env.development in:", os.path.join(os.getcwd(), '.env.development'))
    
    success = test_all_tools()
    sys.exit(0 if success else 1)