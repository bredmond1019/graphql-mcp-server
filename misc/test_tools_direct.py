#!/usr/bin/env python
"""Direct test of MCP tools using the tool classes."""

import os
import sys
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from healthie_mcp.config import get_settings
from healthie_mcp.schema_manager import SchemaManager

# Import tool classes
from healthie_mcp.tools.query_templates import QueryTemplatesTool
from healthie_mcp.tools.code_examples import CodeExampleTool
from healthie_mcp.tools.error_decoder import ErrorDecoderTool
from healthie_mcp.tools.compliance_checker import ComplianceCheckerTool
from healthie_mcp.tools.workflow_sequences import WorkflowSequencesTool
from healthie_mcp.tools.field_relationships import FieldRelationshipTool

# Import input models
from healthie_mcp.models.external_dev_tools import (
    QueryTemplateInput, CodeExampleInput, ErrorDecoderInput,
    ComplianceCheckInput, WorkflowSequenceInput, FieldRelationshipInput
)


def test_tool(tool_name, tool_class, input_model, test_params):
    """Test a tool directly."""
    print(f"\n{'='*60}")
    print(f"Testing: {tool_name}")
    print(f"Input: {json.dumps(test_params, indent=2)}")
    print(f"{'='*60}")
    
    try:
        # Create schema manager
        settings = get_settings()
        schema_manager = SchemaManager(
            api_key=settings.healthie_api_key,
            api_endpoint=str(settings.healthie_api_url),
            cache_dir=settings.schema_dir
        )
        
        # Create tool instance
        tool = tool_class(schema_manager)
        
        # Create input
        input_data = input_model(**test_params)
        
        # Execute tool
        result = tool.execute(input_data)
        
        print("✅ SUCCESS")
        # Print a summary of the result
        result_dict = result.model_dump()
        for key, value in result_dict.items():
            if isinstance(value, list):
                print(f"  {key}: {len(value)} items")
                if value and len(value) > 0:
                    print(f"    First item: {json.dumps(value[0], indent=4, default=str)[:200]}...")
            elif isinstance(value, dict):
                print(f"  {key}: {json.dumps(value, indent=2, default=str)[:200]}...")
            elif isinstance(value, str) and len(value) > 100:
                print(f"  {key}: {value[:100]}...")
            else:
                print(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run direct tests on tools."""
    print("Direct MCP Tools Test")
    settings = get_settings()
    print(f"API Key: {'Set' if settings.healthie_api_key else 'Not Set'}")
    print(f"API URL: {settings.healthie_api_url}")
    
    # Run tests
    tests = [
        # Test 1: Query Templates
        {
            "name": "Query Templates - Appointments",
            "tool_class": QueryTemplatesTool,
            "input_model": QueryTemplateInput,
            "params": {"workflow_category": "appointments"}
        },
        
        # Test 2: Code Examples
        {
            "name": "Code Examples - Authentication",
            "tool_class": CodeExampleTool,
            "input_model": CodeExampleInput,
            "params": {"operation_name": "authentication", "language": "javascript"}
        },
        
        # Test 3: Error Decoder
        {
            "name": "Error Decoder - Auth Error",
            "tool_class": ErrorDecoderTool,
            "input_model": ErrorDecoderInput,
            "params": {"error_message": "User not authenticated", "error_code": "UNAUTHENTICATED"}
        },
        
        # Test 4: Compliance Checker
        {
            "name": "Compliance Checker - PHI Query",
            "tool_class": ComplianceCheckerTool,
            "input_model": ComplianceCheckInput,
            "params": {"operation_type": "query", "data_fields": ["name", "date_of_birth", "ssn"]}
        },
        
        # Test 5: Workflow Sequences
        {
            "name": "Workflow Sequences - Patient Onboarding",
            "tool_class": WorkflowSequencesTool,
            "input_model": WorkflowSequenceInput,
            "params": {"workflow_name": "patient_onboarding"}
        },
        
        # Test 6: Field Relationships
        {
            "name": "Field Relationships - User.id",
            "tool_class": FieldRelationshipTool,
            "input_model": FieldRelationshipInput,
            "params": {"type_name": "User", "field_name": "id"}
        }
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test_tool(
            test["name"],
            test["tool_class"],
            test["input_model"],
            test["params"]
        ):
            passed += 1
    
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)