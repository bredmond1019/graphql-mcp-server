#!/usr/bin/env python3
"""
Test script for 3 additional MCP tools:
1. field_relationships - Explore GraphQL field relationships
2. build_workflow_sequence - Get step-by-step workflow sequences
3. compliance_checker - Validate HIPAA compliance
"""

import json
import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, '.')

# Set environment variables if needed
if "HEALTHIE_API_URL" not in os.environ:
    os.environ["HEALTHIE_API_URL"] = "http://localhost:3000/graphql"

try:
    from src.healthie_mcp.config import get_settings
    from src.healthie_mcp.schema_manager import SchemaManager
    from src.healthie_mcp.tools.field_relationships import FieldRelationshipTool, FieldRelationshipInput
    from src.healthie_mcp.tools.workflow_sequences import WorkflowSequencesTool
    from src.healthie_mcp.tools.compliance_checker import ComplianceCheckerTool, ComplianceCheckerInput
    from src.healthie_mcp.models.compliance_checker import RegulatoryFramework
    
    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

def format_json(obj):
    """Format JSON for pretty printing"""
    return json.dumps(obj, indent=2, default=str)

def test_field_relationships():
    """Test the field_relationships tool with 3 examples"""
    print("\n" + "="*80)
    print("Testing field_relationships tool")
    print("="*80)
    
    results = []
    
    # Test 1: Explore patient_id relationships
    print("\n📝 Test 1: Exploring relationships for 'patient_id'")
    try:
        tool = FieldRelationshipTool(schema_manager)
        
        input_data = FieldRelationshipInput(
            field_name="patient_id",
            max_depth=2,
            include_scalars=False
        )
        
        result = tool.execute(input_data)
        result_dict = result.model_dump()
        
        print(f"✅ Success! Found {result_dict['total_relationships']} relationships")
        print(f"Related fields: {len(result_dict['related_fields'])}")
        if result_dict['related_fields']:
            print(f"Sample relationships: {result_dict['related_fields'][:3]}")
        
        results.append({
            "test": "patient_id relationships",
            "success": True,
            "relationships_found": result_dict['total_relationships'],
            "sample_fields": result_dict['related_fields'][:3] if result_dict['related_fields'] else []
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "patient_id relationships",
            "success": False,
            "error": str(e)
        })
    
    # Test 2: Explore appointment relationships
    print("\n📝 Test 2: Exploring relationships for 'appointment'")
    try:
        input_data = FieldRelationshipInput(
            field_name="appointment",
            max_depth=3,
            include_scalars=True
        )
        
        result = tool.execute(input_data)
        result_dict = result.model_dump()
        
        print(f"✅ Success! Found {result_dict['total_relationships']} relationships")
        print(f"Suggestions: {len(result_dict.get('suggestions', []))}")
        if result_dict.get('suggestions'):
            print(f"First suggestion: {result_dict['suggestions'][0]}")
        
        results.append({
            "test": "appointment relationships",
            "success": True,
            "relationships_found": result_dict['total_relationships'],
            "suggestions": result_dict.get('suggestions', [])
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "appointment relationships",
            "success": False,
            "error": str(e)
        })
    
    # Test 3: Explore insurance relationships
    print("\n📝 Test 3: Exploring relationships for 'insurance'")
    try:
        input_data = FieldRelationshipInput(
            field_name="insurance",
            max_depth=2,
            include_scalars=False
        )
        
        result = tool.execute(input_data)
        result_dict = result.model_dump()
        
        print(f"✅ Success! Found {result_dict['total_relationships']} relationships")
        print(f"Healthcare context detected: {'insurance' in str(result_dict).lower()}")
        
        results.append({
            "test": "insurance relationships",
            "success": True,
            "relationships_found": result_dict['total_relationships'],
            "healthcare_context": True
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "insurance relationships",
            "success": False,
            "error": str(e)
        })
    
    return results

def test_workflow_sequences():
    """Test the build_workflow_sequence tool with 3 examples"""
    print("\n" + "="*80)
    print("Testing build_workflow_sequence tool")
    print("="*80)
    
    results = []
    
    # Test 1: Get patient onboarding workflow
    print("\n📝 Test 1: Getting patient onboarding workflow")
    try:
        tool = WorkflowSequencesTool(schema_manager)
        
        result = tool.execute(
            workflow_name="patient_onboarding"
        )
        result_dict = result.model_dump()
        
        print(f"✅ Success! Found {result_dict['total_workflows']} workflows")
        if result_dict['workflows']:
            workflow = result_dict['workflows'][0]
            print(f"Workflow: {workflow['workflow_name']}")
            print(f"Steps: {workflow['total_steps']}")
            print(f"Duration: {workflow['estimated_duration']}")
        
        results.append({
            "test": "patient onboarding workflow",
            "success": True,
            "workflows_found": result_dict['total_workflows'],
            "workflow_details": result_dict['workflows'][0] if result_dict['workflows'] else None
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "patient onboarding workflow",
            "success": False,
            "error": str(e)
        })
    
    # Test 2: Get appointment booking workflow
    print("\n📝 Test 2: Getting appointment booking workflow")
    try:
        result = tool.execute(
            workflow_name="appointment"
        )
        result_dict = result.model_dump()
        
        print(f"✅ Success! Found {result_dict['total_workflows']} workflows")
        if result_dict['workflows']:
            workflow = result_dict['workflows'][0]
            print(f"Workflow has {len(workflow.get('steps', []))} steps")
            if workflow.get('steps'):
                print(f"First step: {workflow['steps'][0]['description']}")
        
        results.append({
            "test": "appointment booking workflow",
            "success": True,
            "workflows_found": result_dict['total_workflows'],
            "step_count": len(result_dict['workflows'][0].get('steps', [])) if result_dict['workflows'] else 0
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "appointment booking workflow",
            "success": False,
            "error": str(e)
        })
    
    # Test 3: Filter workflows by category
    print("\n📝 Test 3: Filtering workflows by category 'patient_management'")
    try:
        result = tool.execute(
            category="patient_management"
        )
        result_dict = result.model_dump()
        
        print(f"✅ Success! Found {result_dict['total_workflows']} workflows in category")
        print(f"Category filter applied: {result_dict.get('category_filter')}")
        
        results.append({
            "test": "filter by category",
            "success": True,
            "workflows_found": result_dict['total_workflows'],
            "category": result_dict.get('category_filter')
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "filter by category",
            "success": False,
            "error": str(e)
        })
    
    return results

def test_compliance_checker():
    """Test the compliance_checker tool with 3 examples"""
    print("\n" + "="*80)
    print("Testing compliance_checker tool")
    print("="*80)
    
    results = []
    
    # Test 1: Check query compliance
    print("\n📝 Test 1: Checking GraphQL query compliance")
    try:
        tool = ComplianceCheckerTool(schema_manager)
        
        # Test query with potential PHI
        test_query = """
        query GetPatient($id: ID!) {
            patient(id: $id) {
                id
                firstName
                lastName
                dateOfBirth
                ssn
                medicalRecordNumber
            }
        }
        """
        
        input_data = ComplianceCheckerInput(
            query=test_query,
            operation_type="query",
            frameworks=[RegulatoryFramework.HIPAA],
            check_phi_exposure=True,
            check_audit_requirements=True
        )
        
        result = tool.execute(input_data)
        result_dict = result.model_dump()
        
        print(f"✅ Success! Overall compliance: {result_dict['overall_compliance']}")
        print(f"Violations found: {len(result_dict.get('violations', []))}")
        print(f"PHI risks identified: {len(result_dict.get('phi_risks', []))}")
        
        results.append({
            "test": "query compliance check",
            "success": True,
            "compliance_level": result_dict['overall_compliance'],
            "violations": len(result_dict.get('violations', [])),
            "phi_risks": len(result_dict.get('phi_risks', []))
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "query compliance check",
            "success": False,
            "error": str(e)
        })
    
    # Test 2: Check mutation compliance
    print("\n📝 Test 2: Checking mutation compliance")
    try:
        test_mutation = """
        mutation UpdatePatient($id: ID!, $input: UpdatePatientInput!) {
            updatePatient(id: $id, input: $input) {
                patient {
                    id
                    email
                    phoneNumber
                }
            }
        }
        """
        
        input_data = ComplianceCheckerInput(
            query=test_mutation,
            operation_type="mutation",
            frameworks=[RegulatoryFramework.HIPAA],
            check_phi_exposure=True,
            check_audit_requirements=True,
            data_handling_context="Updating patient contact information"
        )
        
        result = tool.execute(input_data)
        result_dict = result.model_dump()
        
        print(f"✅ Success! Audit requirements checked: {len(result_dict.get('audit_requirements', []))}")
        print(f"Recommendations: {len(result_dict.get('recommendations', []))}")
        
        results.append({
            "test": "mutation compliance check",
            "success": True,
            "audit_requirements": len(result_dict.get('audit_requirements', [])),
            "recommendations": result_dict.get('recommendations', [])[:2]
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "mutation compliance check",
            "success": False,
            "error": str(e)
        })
    
    # Test 3: Check state-specific compliance
    print("\n📝 Test 3: Checking California state-specific compliance")
    try:
        input_data = ComplianceCheckerInput(
            query=test_query,
            frameworks=[RegulatoryFramework.HIPAA],
            state="CA",
            check_phi_exposure=True,
            data_handling_context="Processing California patient data"
        )
        
        result = tool.execute(input_data)
        result_dict = result.model_dump()
        
        print(f"✅ Success! State regulations checked: {len(result_dict.get('state_regulations', []))}")
        print(f"Resources provided: {len(result_dict.get('resources', []))}")
        
        results.append({
            "test": "state-specific compliance",
            "success": True,
            "state_regulations": len(result_dict.get('state_regulations', [])),
            "resources": len(result_dict.get('resources', []))
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "state-specific compliance",
            "success": False,
            "error": str(e)
        })
    
    return results

def save_results(tool_name, results, filename):
    """Save test results to a markdown file"""
    output_dir = Path("test_results")
    output_dir.mkdir(exist_ok=True)
    
    filepath = output_dir / filename
    
    with open(filepath, 'w') as f:
        f.write(f"# {tool_name} Test Results\n\n")
        f.write(f"*Generated on: {os.popen('date').read().strip()}*\n\n")
        
        # Summary
        success_count = sum(1 for r in results if r.get('success', False))
        f.write(f"## Summary\n\n")
        f.write(f"- Total tests: {len(results)}\n")
        f.write(f"- Successful: {success_count}\n")
        f.write(f"- Failed: {len(results) - success_count}\n")
        f.write(f"- Success rate: {(success_count/len(results)*100):.1f}%\n\n")
        
        # Detailed results
        f.write("## Test Results\n\n")
        for i, result in enumerate(results, 1):
            f.write(f"### Test {i}: {result['test']}\n\n")
            f.write(f"**Status**: {'✅ Success' if result['success'] else '❌ Failed'}\n\n")
            
            if result['success']:
                f.write("**Details**:\n")
                for key, value in result.items():
                    if key not in ['test', 'success']:
                        f.write(f"- {key}: {value}\n")
            else:
                f.write(f"**Error**: {result.get('error', 'Unknown error')}\n")
            
            f.write("\n")
    
    print(f"\n📄 Results saved to: {filepath}")

def main():
    """Run all tests for the 3 additional tools"""
    print("="*80)
    print("Testing 3 Additional MCP Tools")
    print("="*80)
    
    # Initialize schema manager
    global schema_manager
    settings = get_settings()
    schema_manager = SchemaManager(settings)
    
    # Test each tool
    field_results = test_field_relationships()
    save_results("field_relationships Tool", field_results, "06_field_relationships_results.md")
    
    workflow_results = test_workflow_sequences()
    save_results("build_workflow_sequence Tool", workflow_results, "07_workflow_sequences_results.md")
    
    compliance_results = test_compliance_checker()
    save_results("compliance_checker Tool", compliance_results, "08_compliance_checker_results.md")
    
    # Overall summary
    all_results = field_results + workflow_results + compliance_results
    total_success = sum(1 for r in all_results if r.get('success', False))
    
    print("\n" + "="*80)
    print("OVERALL SUMMARY")
    print("="*80)
    print(f"Total tests run: {len(all_results)}")
    print(f"Successful tests: {total_success}")
    print(f"Failed tests: {len(all_results) - total_success}")
    print(f"Overall success rate: {(total_success/len(all_results)*100):.1f}%")
    
    # Return exit code based on success
    return 0 if total_success == len(all_results) else 1

if __name__ == "__main__":
    sys.exit(main())