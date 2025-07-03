#!/usr/bin/env python3
"""Test script for Phase 3 MCP tools (todo directory tools)."""

import sys
import os
import json
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import tools directly from their modules to avoid circular imports
import importlib.util

def import_tool_module(module_name: str):
    """Import a tool module directly."""
    module_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'src', 'healthie_mcp', 'tools', 'todo', f'{module_name}.py'
    )
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Import tool modules
input_validation_module = import_tool_module('input_validation')
performance_analyzer_module = import_tool_module('performance_analyzer')
healthcare_patterns_module = import_tool_module('healthcare_patterns')
rate_limit_advisor_module = import_tool_module('rate_limit_advisor')
field_usage_module = import_tool_module('field_usage')
integration_testing_module = import_tool_module('integration_testing')
webhook_configurator_module = import_tool_module('webhook_configurator')
api_usage_analytics_module = import_tool_module('api_usage_analytics')
environment_manager_module = import_tool_module('environment_manager')

# Mock MCP server
class MockMCP:
    def __init__(self):
        self.tools = {}
    
    def tool(self, name=None):
        def decorator(func):
            tool_name = name or func.__name__
            self.tools[tool_name] = func
            return func
        return decorator

# Mock schema manager
class MockSchemaManager:
    def get_schema_content(self):
        return """
        type Patient {
            id: ID!
            firstName: String!
            lastName: String!
            email: String
            phoneNumber: String
            dateOfBirth: String
            appointments: [Appointment!]!
        }
        
        type Appointment {
            id: ID!
            patient: Patient!
            provider: Provider!
            startTime: DateTime!
            endTime: DateTime!
            status: String!
        }
        
        type Provider {
            id: ID!
            firstName: String!
            lastName: String!
            specialty: String
        }
        
        type Query {
            patient(id: ID!): Patient
            patients(first: Int, after: String): PatientConnection!
            appointment(id: ID!): Appointment
        }
        """

def test_input_validation_tool():
    """Test the input validation tool."""
    print("\n=== Testing Input Validation Tool ===")
    
    mcp = MockMCP()
    schema_manager = MockSchemaManager()
    
    try:
        # Setup the tool
        input_validation_module.setup_input_validation_tool(mcp, schema_manager)
        validate_input = mcp.tools.get("validate_input")
        
        if not validate_input:
            print("❌ Failed to register input_validation tool")
            return False
        
        # Test 1: Valid patient data
        print("\nTest 1: Valid patient data")
        result = validate_input(
            input_data={
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@example.com",
                "phoneNumber": "+1-555-0123",
                "dateOfBirth": "1990-01-15"
            },
            expected_type="Patient",
            strict_mode=True
        )
        print(f"Result: {json.dumps(result, indent=2)}")
        
        # Test 2: Invalid email format
        print("\nTest 2: Invalid email format")
        result = validate_input(
            input_data={
                "firstName": "Jane",
                "lastName": "Smith",
                "email": "invalid-email",
                "phoneNumber": "+1-555-0124"
            },
            expected_type="Patient",
            strict_mode=True
        )
        print(f"Result: {json.dumps(result, indent=2)}")
        
        # Test 3: Custom validation rules
        print("\nTest 3: Custom validation rules")
        result = validate_input(
            input_data={
                "appointmentDate": "2024-12-25",
                "providerId": "prov_123",
                "duration": 30
            },
            expected_type="AppointmentRequest",
            custom_rules=[
                {"field": "duration", "rule": "min", "value": 15},
                {"field": "duration", "rule": "max", "value": 120}
            ]
        )
        print(f"Result: {json.dumps(result, indent=2)}")
        
        print("\n✅ Input validation tool tests completed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing input validation tool: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_performance_analyzer_tool():
    """Test the performance analyzer tool."""
    print("\n=== Testing Performance Analyzer Tool ===")
    
    mcp = MockMCP()
    schema_manager = MockSchemaManager()
    
    try:
        # Setup the tool
        performance_analyzer_module.setup_query_performance_tool(mcp, schema_manager)
        analyze_performance = mcp.tools.get("analyze_query_performance")
        
        if not analyze_performance:
            print("❌ Failed to register performance_analyzer tool")
            return False
        
        # Test 1: Simple query
        print("\nTest 1: Simple query")
        result = analyze_performance(
            query="""
            query GetPatient {
                patient(id: "123") {
                    id
                    firstName
                    lastName
                }
            }
            """,
            include_suggestions=True
        )
        print(f"Result: {json.dumps(result.model_dump() if hasattr(result, 'model_dump') else result, indent=2)}")
        
        # Test 2: Complex nested query
        print("\nTest 2: Complex nested query")
        result = analyze_performance(
            query="""
            query GetPatientWithAppointments {
                patients {
                    id
                    firstName
                    appointments {
                        id
                        provider {
                            id
                            firstName
                            specialty
                        }
                        startTime
                        status
                    }
                }
            }
            """,
            include_suggestions=True
        )
        print(f"Result: {json.dumps(result.model_dump() if hasattr(result, 'model_dump') else result, indent=2)}")
        
        # Test 3: Query with potential N+1 problem
        print("\nTest 3: Query with potential N+1 problem")
        result = analyze_performance(
            query="""
            query GetAllPatients {
                patients(first: 100) {
                    edges {
                        node {
                            id
                            appointments {
                                id
                                provider {
                                    id
                                    firstName
                                }
                            }
                        }
                    }
                }
            }
            """,
            include_suggestions=True
        )
        print(f"Result: {json.dumps(result.model_dump() if hasattr(result, 'model_dump') else result, indent=2)}")
        
        print("\n✅ Performance analyzer tool tests completed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing performance analyzer tool: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_healthcare_patterns_tool():
    """Test the healthcare patterns tool."""
    print("\n=== Testing Healthcare Patterns Tool ===")
    
    mcp = MockMCP()
    schema_manager = MockSchemaManager()
    
    try:
        # Setup the tool
        healthcare_patterns_module.setup_healthcare_patterns_tool(mcp, schema_manager)
        get_patterns = mcp.tools.get("get_healthcare_patterns")
        
        if not get_patterns:
            print("❌ Failed to register healthcare_patterns tool")
            return False
        
        # Test 1: Patient registration pattern
        print("\nTest 1: Patient registration pattern")
        result = get_patterns(
            pattern_type="patient_registration",
            include_examples=True,
            include_compliance=True
        )
        print(f"Result: {json.dumps(result, indent=2)}")
        
        # Test 2: Appointment scheduling pattern
        print("\nTest 2: Appointment scheduling pattern")
        result = get_patterns(
            pattern_type="appointment_scheduling",
            include_examples=True
        )
        print(f"Result: {json.dumps(result, indent=2)}")
        
        # Test 3: All patterns overview
        print("\nTest 3: All patterns overview")
        result = get_patterns(
            pattern_type=None,
            include_examples=False,
            include_compliance=False
        )
        print(f"Result: {json.dumps(result, indent=2)}")
        
        print("\n✅ Healthcare patterns tool tests completed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing healthcare patterns tool: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_rate_limit_advisor_tool():
    """Test the rate limit advisor tool."""
    print("\n=== Testing Rate Limit Advisor Tool ===")
    
    mcp = MockMCP()
    schema_manager = MockSchemaManager()
    
    try:
        # Setup the tool
        rate_limit_advisor_module.setup_rate_limit_advisor_tool(mcp, schema_manager)
        analyze_rate_limits = mcp.tools.get("analyze_rate_limits")
        
        if not analyze_rate_limits:
            print("❌ Failed to register rate_limit_advisor tool")
            return False
        
        # Test 1: Low volume scenario
        print("\nTest 1: Low volume scenario")
        result = analyze_rate_limits(
            query_patterns=["get_patient", "list_appointments", "create_appointment"],
            expected_requests_per_day=1000,
            peak_hour_percentage=20.0,
            concurrent_users=10,
            include_cost_analysis=True
        )
        print(f"Result: {json.dumps(result.model_dump() if hasattr(result, 'model_dump') else result, indent=2)}")
        
        # Test 2: High volume scenario
        print("\nTest 2: High volume scenario")
        result = analyze_rate_limits(
            query_patterns=["bulk_patient_export", "search_patients", "sync_appointments"],
            expected_requests_per_day=50000,
            peak_hour_percentage=30.0,
            concurrent_users=100,
            average_response_size_kb=50.0,
            include_cost_analysis=True
        )
        print(f"Result: {json.dumps(result.model_dump() if hasattr(result, 'model_dump') else result, indent=2)}")
        
        # Test 3: Healthcare-specific patterns
        print("\nTest 3: Healthcare-specific patterns")
        result = analyze_rate_limits(
            query_patterns=["patient_demographics", "patient_phi_data", "billing_operations"],
            expected_requests_per_day=10000,
            concurrent_users=50,
            include_cost_analysis=False
        )
        print(f"Result: {json.dumps(result.model_dump() if hasattr(result, 'model_dump') else result, indent=2)}")
        
        print("\n✅ Rate limit advisor tool tests completed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing rate limit advisor tool: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def save_test_results(tool_name: str, test_number: int, input_data: Dict[str, Any], output_data: Dict[str, Any]):
    """Save test results to markdown file."""
    filename = f"/Users/brandon/Healthie/python-mcp-server/test_results/phase3/{tool_name}_test_{test_number}.md"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w') as f:
        f.write(f"# {tool_name.replace('_', ' ').title()} - Test {test_number}\n\n")
        f.write("## Input\n\n")
        f.write("```python\n")
        f.write(json.dumps(input_data, indent=2))
        f.write("\n```\n\n")
        f.write("## Output\n\n")
        f.write("```json\n")
        f.write(json.dumps(output_data, indent=2))
        f.write("\n```\n\n")
        f.write("## Analysis\n\n")
        
        # Add analysis based on tool type
        if tool_name == "input_validation":
            if output_data.get("is_valid"):
                f.write("✅ Input validation passed successfully\n")
            else:
                f.write("❌ Input validation failed with errors:\n")
                for error in output_data.get("validation_errors", []):
                    f.write(f"- {error}\n")
        
        elif tool_name == "performance_analyzer":
            score = output_data.get("overall_score", 0)
            f.write(f"Performance Score: {score}/100\n\n")
            if score >= 80:
                f.write("✅ Query performance is good\n")
            elif score >= 60:
                f.write("⚠️ Query performance could be improved\n")
            else:
                f.write("❌ Query has significant performance issues\n")
        
        elif tool_name == "rate_limit_advisor":
            risk = output_data.get("forecast", {}).get("rate_limit_risk", "unknown")
            f.write(f"Rate Limit Risk: {risk}\n\n")
            if risk == "low":
                f.write("✅ Low risk of hitting rate limits\n")
            elif risk == "medium":
                f.write("⚠️ Moderate risk - monitor usage closely\n")
            else:
                f.write("❌ High risk - immediate action required\n")

def main():
    """Run all Phase 3 tool tests."""
    print("Starting Phase 3 MCP Tools Testing")
    print("=" * 50)
    
    results = {
        "input_validation": test_input_validation_tool(),
        "performance_analyzer": test_performance_analyzer_tool(),
        "healthcare_patterns": test_healthcare_patterns_tool(),
        "rate_limit_advisor": test_rate_limit_advisor_tool(),
    }
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for tool, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{tool}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)