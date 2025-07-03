#!/usr/bin/env python3
"""Direct testing of todo tools without MCP framework."""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import base classes and models
from src.healthie_mcp.base import SchemaManagerProtocol
from src.healthie_mcp.models.input_validation import InputValidationInput, ValidationRule
from src.healthie_mcp.models.external_dev_tools import QueryPerformanceResult
from src.healthie_mcp.models.healthcare_patterns import HealthcarePatternsInput

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
        }
        """

def test_input_validation():
    """Test input validation tool directly."""
    print("\n=== Testing Input Validation Tool ===")
    
    try:
        # Import the tool class directly
        from src.healthie_mcp.tools.todo.input_validation import InputValidationTool
        
        # Create tool instance
        schema_manager = MockSchemaManager()
        tool = InputValidationTool(schema_manager)
        
        # Test 1: Valid patient data
        print("\nTest 1: Valid patient data")
        input_data = InputValidationInput(
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
        result = tool.execute(input_data)
        print(f"Valid: {result.is_valid}")
        print(f"Errors: {result.validation_errors}")
        
        # Test 2: Invalid email
        print("\nTest 2: Invalid email")
        input_data = InputValidationInput(
            input_data={
                "firstName": "Jane",
                "lastName": "Smith",
                "email": "invalid-email",
                "phoneNumber": "+1-555-0124"
            },
            expected_type="Patient",
            strict_mode=True
        )
        result = tool.execute(input_data)
        print(f"Valid: {result.is_valid}")
        print(f"Errors: {result.validation_errors}")
        
        # Test 3: Custom validation rules
        print("\nTest 3: Custom validation rules")
        input_data = InputValidationInput(
            input_data={
                "appointmentDate": "2024-12-25",
                "providerId": "prov_123",
                "duration": 30
            },
            expected_type="AppointmentRequest",
            custom_rules=[
                ValidationRule(field="duration", rule="min", value=15),
                ValidationRule(field="duration", rule="max", value=120)
            ]
        )
        result = tool.execute(input_data)
        print(f"Valid: {result.is_valid}")
        print(f"Errors: {result.validation_errors}")
        
        print("\n✅ Input validation tool works!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_performance_analyzer():
    """Test performance analyzer tool directly."""
    print("\n=== Testing Performance Analyzer Tool ===")
    
    try:
        # Import the tool class directly
        from src.healthie_mcp.tools.todo.performance_analyzer import QueryPerformanceTool
        
        # Create tool instance
        schema_manager = MockSchemaManager()
        tool = QueryPerformanceTool(schema_manager)
        
        # Test 1: Simple query
        print("\nTest 1: Simple query")
        result = tool.execute(
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
        print(f"Performance Score: {result.overall_score}/100")
        print(f"Complexity Score: {result.complexity_score}")
        print(f"Issues Found: {result.total_issues}")
        print(f"Execution Time: {result.estimated_execution_time}")
        
        # Test 2: Complex query with nesting
        print("\nTest 2: Complex nested query")
        result = tool.execute(
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
        print(f"Performance Score: {result.overall_score}/100")
        print(f"Complexity Score: {result.complexity_score}")
        print(f"Issues Found: {result.total_issues}")
        for issue in result.issues:
            print(f"  - {issue.severity}: {issue.description}")
        
        print("\n✅ Performance analyzer tool works!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_healthcare_patterns():
    """Test healthcare patterns tool directly."""
    print("\n=== Testing Healthcare Patterns Tool ===")
    
    try:
        # Import the tool class directly
        from src.healthie_mcp.tools.todo.healthcare_patterns import HealthcarePatternsTool
        
        # Create tool instance
        schema_manager = MockSchemaManager()
        tool = HealthcarePatternsTool(schema_manager)
        
        # Test 1: Patient registration pattern
        print("\nTest 1: Patient registration pattern")
        input_data = HealthcarePatternsInput(
            pattern_type="patient_registration",
            include_examples=True,
            include_compliance=True
        )
        result = tool.execute(input_data)
        print(f"Pattern: {result.pattern_name}")
        print(f"Steps: {len(result.implementation_steps)}")
        for i, step in enumerate(result.implementation_steps[:3]):
            print(f"  {i+1}. {step.description}")
        
        # Test 2: Appointment scheduling pattern
        print("\nTest 2: Appointment scheduling pattern")
        input_data = HealthcarePatternsInput(
            pattern_type="appointment_scheduling",
            include_examples=True
        )
        result = tool.execute(input_data)
        print(f"Pattern: {result.pattern_name}")
        print(f"Required Fields: {result.required_fields}")
        
        # Test 3: List all patterns
        print("\nTest 3: List all patterns")
        input_data = HealthcarePatternsInput()
        result = tool.execute(input_data)
        print(f"Available Patterns: {len(result.available_patterns)}")
        for pattern in result.available_patterns:
            print(f"  - {pattern}")
        
        print("\n✅ Healthcare patterns tool works!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_rate_limit_advisor():
    """Test rate limit advisor tool directly."""
    print("\n=== Testing Rate Limit Advisor Tool ===")
    
    try:
        # Import the analyzer class directly
        from src.healthie_mcp.tools.todo.rate_limit_advisor import RateLimitAnalyzer
        
        # Test 1: Low volume scenario
        print("\nTest 1: Low volume scenario")
        analyzer = RateLimitAnalyzer(
            query_patterns=["get_patient", "list_appointments", "create_appointment"],
            expected_requests_per_day=1000,
            peak_hour_percentage=20.0,
            concurrent_users=10,
            include_cost_analysis=True
        )
        result = analyzer.analyze()
        print(f"Rate Limit Risk: {result.forecast.rate_limit_risk}")
        print(f"Recommended Tier: {result.forecast.recommended_tier}")
        print(f"Summary: {result.summary}")
        
        # Test 2: High volume scenario
        print("\nTest 2: High volume scenario")
        analyzer = RateLimitAnalyzer(
            query_patterns=["bulk_patient_export", "search_patients", "sync_appointments"],
            expected_requests_per_day=50000,
            peak_hour_percentage=30.0,
            concurrent_users=100,
            average_response_size_kb=50.0,
            include_cost_analysis=True
        )
        result = analyzer.analyze()
        print(f"Rate Limit Risk: {result.forecast.rate_limit_risk}")
        print(f"Recommended Tier: {result.forecast.recommended_tier}")
        print(f"Optimization Tips: {len(result.optimization_tips)}")
        for tip in result.optimization_tips[:3]:
            print(f"  - {tip.title}")
        
        print("\n✅ Rate limit advisor tool works!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def save_test_result(tool_name: str, success: bool, details: dict):
    """Save test results to file."""
    os.makedirs("test_results/phase3", exist_ok=True)
    
    result = {
        "tool": tool_name,
        "timestamp": datetime.now().isoformat(),
        "success": success,
        "details": details
    }
    
    filename = f"test_results/phase3/{tool_name}_test_result.json"
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Saved test result to {filename}")

def main():
    """Run all tests."""
    print("Testing TODO Tools Directly")
    print("=" * 50)
    
    results = {
        "input_validation": test_input_validation(),
        "performance_analyzer": test_performance_analyzer(),
        "healthcare_patterns": test_healthcare_patterns(),
        "rate_limit_advisor": test_rate_limit_advisor(),
    }
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for tool, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{tool}: {status}")
        save_test_result(tool, success, {"test_type": "direct"})
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)