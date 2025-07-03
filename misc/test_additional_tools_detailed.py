#!/usr/bin/env python3
"""
Detailed test script for 3 additional MCP tools with comprehensive output capture
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from pprint import pformat

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

def test_field_relationships_detailed():
    """Test field_relationships with detailed output capture"""
    print("\n" + "="*80)
    print("Testing field_relationships tool - DETAILED")
    print("="*80)
    
    results = []
    
    # Initialize tool
    settings = get_settings()
    schema_manager = SchemaManager(
        api_endpoint=str(settings.healthie_api_url),
        cache_dir=Path(settings.schema_dir)
    )
    tool = FieldRelationshipTool(schema_manager)
    
    # Test 1: Patient field relationships
    print("\n📝 Test 1: Exploring 'patient' field relationships")
    try:
        input_data = FieldRelationshipInput(
            field_name="patient",
            max_depth=3,
            include_scalars=True
        )
        
        result = tool.execute(input_data)
        result_dict = result.model_dump()
        
        print(f"\n✅ Execution successful!")
        print(f"\nFull result structure:")
        print(format_json(result_dict))
        
        test_result = {
            "test": "patient field relationships",
            "success": True,
            "input": {
                "field_name": "patient",
                "max_depth": 3,
                "include_scalars": True
            },
            "output": result_dict,
            "analysis": {
                "relationships_found": result_dict['total_relationships'],
                "has_suggestions": len(result_dict.get('suggestions', [])) > 0,
                "has_related_fields": len(result_dict.get('related_fields', [])) > 0,
                "error": result_dict.get('error')
            }
        }
        
        results.append(test_result)
        
    except Exception as e:
        print(f"❌ Failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        results.append({
            "test": "patient field relationships", 
            "success": False,
            "input": {
                "field_name": "patient",
                "max_depth": 3,
                "include_scalars": True
            },
            "error": str(e),
            "traceback": traceback.format_exc()
        })
    
    # Test 2: Try with a specific GraphQL field that might exist
    print("\n📝 Test 2: Exploring 'appointments' field (common in Patient type)")
    try:
        input_data = FieldRelationshipInput(
            field_name="appointments",
            max_depth=2,
            include_scalars=False
        )
        
        result = tool.execute(input_data)
        result_dict = result.model_dump()
        
        print(f"\n✅ Execution successful!")
        print(f"\nResult summary:")
        print(f"- Total relationships: {result_dict['total_relationships']}")
        print(f"- Suggestions: {result_dict.get('suggestions', [])}")
        if result_dict.get('related_fields'):
            print(f"- Sample related fields:")
            for field in result_dict['related_fields'][:3]:
                print(f"  - {field}")
        
        results.append({
            "test": "appointments field exploration",
            "success": True,
            "input": input_data.model_dump(),
            "output": result_dict
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "appointments field exploration",
            "success": False,
            "input": {
                "field_name": "appointments",
                "max_depth": 2,
                "include_scalars": False
            },
            "error": str(e)
        })
    
    return results

def test_workflow_sequences_detailed():
    """Test workflow sequences with full output"""
    print("\n" + "="*80)
    print("Testing build_workflow_sequence tool - DETAILED")
    print("="*80)
    
    results = []
    
    # Initialize
    settings = get_settings()
    schema_manager = SchemaManager(
        api_endpoint=str(settings.healthie_api_url),
        cache_dir=Path(settings.schema_dir)
    )
    tool = WorkflowSequencesTool(schema_manager)
    
    # Test 1: Get all workflows
    print("\n📝 Test 1: Getting ALL available workflows")
    try:
        result = tool.execute()  # No filters
        result_dict = result.model_dump()
        
        print(f"\n✅ Found {result_dict['total_workflows']} total workflows")
        
        if result_dict['workflows']:
            for i, workflow in enumerate(result_dict['workflows']):
                print(f"\n--- Workflow {i+1} ---")
                print(f"Name: {workflow['workflow_name']}")
                print(f"Category: {workflow['category']}")
                print(f"Description: {workflow['description']}")
                print(f"Total Steps: {workflow['total_steps']}")
                print(f"Duration: {workflow.get('estimated_duration', 'N/A')}")
                
                if workflow.get('steps'):
                    print("\nSteps:")
                    for step in workflow['steps']:
                        print(f"  {step['step_number']}. {step['description']}")
                        print(f"     - Operation: {step['operation_type']} {step['operation_name']}")
                        print(f"     - Required inputs: {step.get('required_inputs', [])}")
        
        results.append({
            "test": "get all workflows",
            "success": True,
            "input": {
                "workflow_name": None,
                "category": None,
                "description": "No filters - retrieve all available workflows"
            },
            "workflows_found": result_dict['total_workflows'],
            "workflows": result_dict['workflows']
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "get all workflows", 
            "success": False, 
            "input": {
                "workflow_name": None,
                "category": None,
                "description": "No filters - retrieve all available workflows"
            },
            "error": str(e)
        })
    
    # Test 2: Get specific workflow with full details
    print("\n📝 Test 2: Getting appointment booking workflow with FULL details")
    try:
        result = tool.execute(workflow_name="appointment")
        result_dict = result.model_dump()
        
        if result_dict['workflows'] and result_dict['workflows'][0].get('steps'):
            workflow = result_dict['workflows'][0]
            print(f"\n✅ Found workflow: {workflow['workflow_name']}")
            print(f"\nFull workflow structure:")
            print(format_json(workflow))
            
            # Show GraphQL examples
            print("\n--- GraphQL Examples from Steps ---")
            for step in workflow['steps']:
                if step.get('graphql_example'):
                    print(f"\nStep {step['step_number']}: {step['operation_name']}")
                    print(step['graphql_example'])
        
        results.append({
            "test": "appointment workflow details",
            "success": True,
            "input": {
                "workflow_name": "appointment",
                "category": None,
                "description": "Filter for appointment-related workflows"
            },
            "workflow": result_dict['workflows'][0] if result_dict['workflows'] else None
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "appointment workflow details", 
            "success": False, 
            "input": {
                "workflow_name": "appointment",
                "category": None,
                "description": "Filter for appointment-related workflows"
            },
            "error": str(e)
        })
    
    return results

def test_compliance_checker_detailed():
    """Test compliance checker with comprehensive output"""
    print("\n" + "="*80)
    print("Testing compliance_checker tool - DETAILED")
    print("="*80)
    
    results = []
    
    # Initialize
    settings = get_settings()
    schema_manager = SchemaManager(
        api_endpoint=str(settings.healthie_api_url),
        cache_dir=Path(settings.schema_dir)
    )
    tool = ComplianceCheckerTool(schema_manager)
    
    # Test 1: Detailed PHI exposure check
    print("\n📝 Test 1: Comprehensive PHI exposure analysis")
    
    test_query = """
    query GetPatientDetails($id: ID!) {
        patient(id: $id) {
            id
            firstName
            lastName
            dateOfBirth
            ssn
            medicalRecordNumber
            email
            phoneNumber
            addresses {
                line1
                line2
                city
                state
                zipCode
            }
            diagnoses {
                icdCode
                description
            }
            medications {
                name
                dosage
            }
        }
    }
    """
    
    try:
        input_data = ComplianceCheckerInput(
            query=test_query,
            operation_type="query",
            frameworks=[RegulatoryFramework.HIPAA],
            check_phi_exposure=True,
            check_audit_requirements=True,
            data_handling_context="Displaying patient information in provider portal"
        )
        
        result = tool.execute(input_data)
        result_dict = result.model_dump()
        
        print(f"\n✅ Analysis complete!")
        print(f"\n=== COMPLIANCE SUMMARY ===")
        print(f"Overall Compliance Level: {result_dict['overall_compliance']}")
        print(f"Summary: {result_dict['summary']}")
        
        print(f"\n=== VIOLATIONS FOUND ({len(result_dict.get('violations', []))}) ===")
        for i, violation in enumerate(result_dict.get('violations', []), 1):
            print(f"\nViolation {i}:")
            print(f"  Severity: {violation['severity']}")
            print(f"  Field: {violation.get('field', 'N/A')}")
            print(f"  Message: {violation['message']}")
            print(f"  Recommendation: {violation.get('recommendation', 'N/A')}")
            print(f"  Regulation: {violation.get('regulation_reference', 'N/A')}")
        
        print(f"\n=== PHI RISKS IDENTIFIED ({len(result_dict.get('phi_risks', []))}) ===")
        for i, risk in enumerate(result_dict.get('phi_risks', []), 1):
            print(f"\nPHI Risk {i}:")
            print(f"  Category: {risk['category']}")
            print(f"  Fields: {risk['fields']}")
            print(f"  Risk Level: {risk['risk_level']}")
            print(f"  Description: {risk['description']}")
            print(f"  Mitigation: {risk.get('mitigation', 'N/A')}")
        
        print(f"\n=== AUDIT REQUIREMENTS ({len(result_dict.get('audit_requirements', []))}) ===")
        for req in result_dict.get('audit_requirements', []):
            print(f"\n{req['requirement']}:")
            print(f"  Met: {'✅ Yes' if req['met'] else '❌ No'}")
            print(f"  Description: {req['description']}")
            if req.get('implementation_guide'):
                print(f"  Implementation: {req['implementation_guide']}")
        
        print(f"\n=== RECOMMENDATIONS ({len(result_dict.get('recommendations', []))}) ===")
        for i, rec in enumerate(result_dict.get('recommendations', [])[:5], 1):
            print(f"{i}. {rec}")
        
        if len(result_dict.get('recommendations', [])) > 5:
            print(f"... and {len(result_dict['recommendations']) - 5} more recommendations")
        
        results.append({
            "test": "comprehensive PHI analysis",
            "success": True,
            "input_query": test_query,
            "full_result": result_dict
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        results.append({
            "test": "comprehensive PHI analysis",
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        })
    
    # Test 2: Mutation with audit requirements
    print("\n📝 Test 2: Mutation compliance with data handling context")
    
    mutation_query = """
    mutation UpdatePatientMedicalInfo($id: ID!, $input: UpdatePatientInput!) {
        updatePatient(id: $id, input: $input) {
            patient {
                id
                medicalRecordNumber
                diagnoses {
                    icdCode
                    description
                    dateRecorded
                }
                medications {
                    name
                    dosage
                    prescribedBy
                }
                allergies {
                    allergen
                    severity
                    reaction
                }
            }
        }
    }
    """
    
    try:
        input_data = ComplianceCheckerInput(
            query=mutation_query,
            operation_type="mutation",
            frameworks=[RegulatoryFramework.HIPAA, RegulatoryFramework.HITECH],
            check_phi_exposure=True,
            check_audit_requirements=True,
            data_handling_context="Provider updating patient medical information after consultation"
        )
        
        result = tool.execute(input_data)
        result_dict = result.model_dump()
        
        print(f"\n✅ Mutation analysis complete!")
        print(f"\nKey findings:")
        print(f"- Compliance level: {result_dict['overall_compliance']}")
        print(f"- Audit requirements needed: {len(result_dict.get('audit_requirements', []))}")
        print(f"- Data handling practices evaluated: {len(result_dict.get('data_handling', []))}")
        
        # Show data handling practices
        if result_dict.get('data_handling'):
            print(f"\n=== DATA HANDLING PRACTICES ===")
            for practice in result_dict['data_handling']:
                print(f"\n{practice['practice']}:")
                print(f"  Compliant: {'✅' if practice['compliant'] else '❌'}")
                print(f"  Framework: {practice['framework']}")
                print(f"  Description: {practice.get('description', 'N/A')}")
                if practice.get('recommendation'):
                    print(f"  Recommendation: {practice['recommendation']}")
        
        results.append({
            "test": "mutation audit requirements",
            "success": True,
            "mutation_query": mutation_query,
            "result_summary": {
                "compliance_level": result_dict['overall_compliance'],
                "audit_requirements": len(result_dict.get('audit_requirements', [])),
                "violations": len(result_dict.get('violations', [])),
                "recommendations_count": len(result_dict.get('recommendations', []))
            }
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "mutation audit requirements",
            "success": False,
            "error": str(e)
        })
    
    return results

def save_detailed_results(tool_name, results, filename):
    """Save detailed test results with full output"""
    output_dir = Path("test_results")
    output_dir.mkdir(exist_ok=True)
    
    filepath = output_dir / filename
    
    with open(filepath, 'w') as f:
        f.write(f"# {tool_name} Detailed Test Results\n\n")
        f.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        
        # Add tool usage instructions
        f.write("## How to Use This Tool\n\n")
        
        if "field_relationships" in tool_name:
            f.write("### Python Usage\n\n")
            f.write("```python\n")
            f.write("from healthie_mcp.tools.field_relationships import FieldRelationshipTool, FieldRelationshipInput\n")
            f.write("from healthie_mcp.schema_manager import SchemaManager\n\n")
            f.write("# Initialize the tool\n")
            f.write("schema_manager = SchemaManager(api_endpoint='https://api.gethealthie.com/graphql')\n")
            f.write("tool = FieldRelationshipTool(schema_manager)\n\n")
            f.write("# Execute with parameters\n")
            f.write("input_data = FieldRelationshipInput(\n")
            f.write("    field_name='patient',  # Field to explore\n")
            f.write("    max_depth=3,          # How deep to traverse relationships\n")
            f.write("    include_scalars=True  # Include scalar fields\n")
            f.write(")\n")
            f.write("result = tool.execute(input_data)\n")
            f.write("```\n\n")
            
        elif "workflow_sequence" in tool_name:
            f.write("### Python Usage\n\n")
            f.write("```python\n")
            f.write("from healthie_mcp.tools.workflow_sequences import WorkflowSequencesTool\n")
            f.write("from healthie_mcp.schema_manager import SchemaManager\n\n")
            f.write("# Initialize the tool\n")
            f.write("schema_manager = SchemaManager(api_endpoint='https://api.gethealthie.com/graphql')\n")
            f.write("tool = WorkflowSequencesTool(schema_manager)\n\n")
            f.write("# Get all workflows\n")
            f.write("result = tool.execute()\n\n")
            f.write("# Or filter by workflow name\n")
            f.write("result = tool.execute(workflow_name='appointment')\n\n")
            f.write("# Or filter by category\n")
            f.write("result = tool.execute(category='patient_management')\n")
            f.write("```\n\n")
            
        elif "compliance_checker" in tool_name:
            f.write("### Python Usage\n\n")
            f.write("```python\n")
            f.write("from healthie_mcp.tools.compliance_checker import ComplianceCheckerTool, ComplianceCheckerInput\n")
            f.write("from healthie_mcp.models.compliance_checker import RegulatoryFramework\n")
            f.write("from healthie_mcp.schema_manager import SchemaManager\n\n")
            f.write("# Initialize the tool\n")
            f.write("schema_manager = SchemaManager(api_endpoint='https://api.gethealthie.com/graphql')\n")
            f.write("tool = ComplianceCheckerTool(schema_manager)\n\n")
            f.write("# Check a GraphQL query for compliance\n")
            f.write("input_data = ComplianceCheckerInput(\n")
            f.write("    query='query GetPatient($id: ID!) { patient(id: $id) { firstName ssn } }',\n")
            f.write("    operation_type='query',\n")
            f.write("    frameworks=[RegulatoryFramework.HIPAA],\n")
            f.write("    check_phi_exposure=True,\n")
            f.write("    check_audit_requirements=True,\n")
            f.write("    data_handling_context='Provider viewing patient record'\n")
            f.write(")\n")
            f.write("result = tool.execute(input_data)\n")
            f.write("```\n\n")
        
        # Summary
        success_count = sum(1 for r in results if r.get('success', False))
        f.write(f"## Summary\n\n")
        f.write(f"- Total tests: {len(results)}\n")
        f.write(f"- Successful: {success_count}\n")
        f.write(f"- Failed: {len(results) - success_count}\n")
        f.write(f"- Success rate: {(success_count/len(results)*100):.1f}%\n\n")
        
        # Detailed results
        f.write("## Detailed Test Results\n\n")
        for i, result in enumerate(results, 1):
            f.write(f"### Test {i}: {result['test']}\n\n")
            f.write(f"**Status**: {'✅ Success' if result['success'] else '❌ Failed'}\n\n")
            
            # Always show input if available
            if 'input' in result:
                f.write("#### Input Parameters\n\n")
                f.write("```json\n")
                f.write(format_json(result['input']))
                f.write("\n```\n\n")
            
            # Show how the tool was called
            if 'input_query' in result:
                f.write("#### Input Query\n\n")
                f.write("```graphql\n")
                f.write(result['input_query'])
                f.write("\n```\n\n")
            
            if result['success']:
                # Format based on tool type
                if 'full_result' in result:
                    # Compliance checker format
                    f.write("#### Full Analysis Results\n\n")
                    f.write("```json\n")
                    f.write(format_json(result['full_result']))
                    f.write("\n```\n\n")
                    
                elif 'workflows' in result:
                    # Workflow sequences format
                    f.write(f"**Workflows Found**: {result.get('workflows_found', 0)}\n\n")
                    if result.get('workflows'):
                        for workflow in result['workflows']:
                            f.write(f"#### Workflow: {workflow['workflow_name']}\n\n")
                            f.write(f"- **Category**: {workflow['category']}\n")
                            f.write(f"- **Description**: {workflow['description']}\n")
                            f.write(f"- **Steps**: {workflow['total_steps']}\n")
                            f.write(f"- **Duration**: {workflow.get('estimated_duration', 'N/A')}\n\n")
                            
                            if workflow.get('steps'):
                                f.write("**Step Details**:\n\n")
                                for step in workflow['steps']:
                                    f.write(f"{step['step_number']}. **{step['description']}**\n")
                                    f.write(f"   - Operation: `{step['operation_type']} {step['operation_name']}`\n")
                                    f.write(f"   - Required: {step.get('required_inputs', [])}\n")
                                    if step.get('notes'):
                                        f.write(f"   - Notes: {step['notes']}\n")
                                    f.write("\n")
                                
                elif 'output' in result:
                    # Field relationships format
                    f.write("#### Output\n\n")
                    f.write("```json\n")
                    f.write(format_json(result['output']))
                    f.write("\n```\n\n")
                    
                    if 'analysis' in result:
                        f.write("#### Analysis\n\n")
                        for key, value in result['analysis'].items():
                            f.write(f"- **{key}**: {value}\n")
                        f.write("\n")
                        
            else:
                f.write(f"**Error**: {result.get('error', 'Unknown error')}\n\n")
                if 'traceback' in result:
                    f.write("**Traceback**:\n```\n")
                    f.write(result['traceback'])
                    f.write("\n```\n")
            
            f.write("\n---\n\n")
    
    print(f"\n📄 Detailed results saved to: {filepath}")

def main():
    """Run detailed tests for the 3 additional tools"""
    print("="*80)
    print("Detailed Testing of 3 Additional MCP Tools")
    print("="*80)
    
    # Test each tool with detailed output
    field_results = test_field_relationships_detailed()
    save_detailed_results("field_relationships Tool", field_results, "06_field_relationships_detailed.md")
    
    workflow_results = test_workflow_sequences_detailed()
    save_detailed_results("build_workflow_sequence Tool", workflow_results, "07_workflow_sequences_detailed.md")
    
    compliance_results = test_compliance_checker_detailed()
    save_detailed_results("compliance_checker Tool", compliance_results, "08_compliance_checker_detailed.md")
    
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
    
    return 0 if total_success == len(all_results) else 1

if __name__ == "__main__":
    sys.exit(main())