#!/usr/bin/env python3
"""
Comprehensive test script for all 8 working MCP tools with detailed output capture
Phase 2: Full detailed testing with real examples and comprehensive analysis
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from pprint import pformat
import traceback

# Add the project root to the path
sys.path.insert(0, '.')

# Set environment variables if needed
if "HEALTHIE_API_URL" not in os.environ:
    os.environ["HEALTHIE_API_URL"] = "http://localhost:3000/graphql"

try:
    # First try to import without MCP
    import sys
    sys.path.insert(0, 'src')
    
    from healthie_mcp.config import get_settings
    from healthie_mcp.schema_manager import SchemaManager
    
    # Import all 8 working tools
    from healthie_mcp.tools.schema_search import SchemaSearchTool
    from healthie_mcp.tools.query_templates import QueryTemplatesTool
    from healthie_mcp.tools.code_examples import CodeExamplesTool, CodeExamplesInput
    from healthie_mcp.tools.type_introspection import TypeIntrospectionTool
    from healthie_mcp.tools.error_decoder import ErrorDecoderTool, ErrorDecoderInput
    from healthie_mcp.tools.compliance_checker import ComplianceCheckerTool, ComplianceCheckerInput
    from healthie_mcp.tools.workflow_sequences import WorkflowSequencesTool
    from healthie_mcp.tools.field_relationships import FieldRelationshipTool, FieldRelationshipInput
    from healthie_mcp.models.compliance_checker import RegulatoryFramework
    
    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("Trying alternative import...")
    try:
        from src.healthie_mcp.config import get_settings
        from src.healthie_mcp.schema_manager import SchemaManager
        
        # Import all 8 working tools
        from src.healthie_mcp.tools.schema_search import SchemaSearchTool
        from src.healthie_mcp.tools.query_templates import QueryTemplatesTool
        from src.healthie_mcp.tools.code_examples import CodeExamplesTool, CodeExamplesInput
        from src.healthie_mcp.tools.type_introspection import TypeIntrospectionTool
        from src.healthie_mcp.tools.error_decoder import ErrorDecoderTool, ErrorDecoderInput
        from src.healthie_mcp.tools.compliance_checker import ComplianceCheckerTool, ComplianceCheckerInput
        from src.healthie_mcp.tools.workflow_sequences import WorkflowSequencesTool
        from src.healthie_mcp.tools.field_relationships import FieldRelationshipTool, FieldRelationshipInput
        from src.healthie_mcp.models.compliance_checker import RegulatoryFramework
        
        print("✅ Alternative imports successful!")
    except ImportError as e2:
        print(f"❌ Alternative import also failed: {e2}")
        sys.exit(1)

def format_json(obj):
    """Format JSON for pretty printing"""
    return json.dumps(obj, indent=2, default=str)

def test_schema_search_detailed():
    """Test 1: Schema Search Tool"""
    print("\n" + "="*80)
    print("Testing search_schema tool - DETAILED")
    print("="*80)
    
    results = []
    
    # Initialize tool
    settings = get_settings()
    schema_manager = SchemaManager(
        api_endpoint=str(settings.healthie_api_url),
        cache_dir=Path(settings.schema_dir)
    )
    tool = SchemaSearchTool(schema_manager)
    
    # Test 1: Search for patient-related types
    print("\n📝 Test 1: Searching for 'patient' in schema")
    try:
        result = tool.execute(query="patient", search_type="all")
        result_dict = result.model_dump()
        
        print(f"\n✅ Found {result_dict['total_results']} results")
        print(f"\nResult breakdown:")
        print(f"- Types found: {len(result_dict.get('types', []))}")
        print(f"- Fields found: {len(result_dict.get('fields', []))}")
        print(f"- Arguments found: {len(result_dict.get('arguments', []))}")
        print(f"- Enums found: {len(result_dict.get('enums', []))}")
        
        test_result = {
            "test": "search for patient",
            "success": True,
            "input": {
                "query": "patient",
                "search_type": "all"
            },
            "output": result_dict,
            "analysis": {
                "total_results": result_dict['total_results'],
                "result_breakdown": {
                    "types": len(result_dict.get('types', [])),
                    "fields": len(result_dict.get('fields', [])),
                    "arguments": len(result_dict.get('arguments', [])),
                    "enums": len(result_dict.get('enums', []))
                }
            }
        }
        results.append(test_result)
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "search for patient",
            "success": False,
            "input": {"query": "patient", "search_type": "all"},
            "error": str(e),
            "traceback": traceback.format_exc()
        })
    
    # Test 2: Search for mutation types only
    print("\n📝 Test 2: Searching for mutations (types only)")
    try:
        result = tool.execute(query="mutation", search_type="types")
        result_dict = result.model_dump()
        
        print(f"\n✅ Found {len(result_dict.get('types', []))} mutation types")
        if result_dict.get('types'):
            print("\nSample mutation types:")
            for type_info in result_dict['types'][:5]:
                print(f"- {type_info['name']}: {type_info.get('description', 'No description')}")
        
        results.append({
            "test": "search mutations",
            "success": True,
            "input": {"query": "mutation", "search_type": "types"},
            "output": result_dict
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "search mutations",
            "success": False,
            "input": {"query": "mutation", "search_type": "types"},
            "error": str(e)
        })
    
    return results

def test_query_templates_detailed():
    """Test 2: Query Templates Tool"""
    print("\n" + "="*80)
    print("Testing query_templates tool - DETAILED")
    print("="*80)
    
    results = []
    
    # Initialize tool
    settings = get_settings()
    schema_manager = SchemaManager(
        api_endpoint=str(settings.healthie_api_url),
        cache_dir=Path(settings.schema_dir)
    )
    tool = QueryTemplatesTool(schema_manager)
    
    # Test 1: Get appointment query template
    print("\n📝 Test 1: Getting appointment query template")
    try:
        result = tool.execute(operation_name="appointment", operation_type="query")
        result_dict = result.model_dump()
        
        print(f"\n✅ Template generated successfully!")
        print(f"Template type: {result_dict['template_type']}")
        print(f"Has variables: {result_dict['has_variables']}")
        print(f"Variable count: {len(result_dict.get('variables', {}))}")
        
        print("\nGenerated Query:")
        print(result_dict['template'])
        
        results.append({
            "test": "appointment query template",
            "success": True,
            "input": {
                "operation_name": "appointment",
                "operation_type": "query"
            },
            "output": result_dict
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "appointment query template",
            "success": False,
            "input": {"operation_name": "appointment", "operation_type": "query"},
            "error": str(e)
        })
    
    # Test 2: Get createPatient mutation template
    print("\n📝 Test 2: Getting createPatient mutation template")
    try:
        result = tool.execute(operation_name="createPatient", operation_type="mutation")
        result_dict = result.model_dump()
        
        print(f"\n✅ Mutation template generated!")
        print(f"\nVariables required:")
        for var_name, var_info in result_dict.get('variables', {}).items():
            print(f"- ${var_name}: {var_info}")
        
        results.append({
            "test": "createPatient mutation template",
            "success": True,
            "input": {
                "operation_name": "createPatient",
                "operation_type": "mutation"
            },
            "output": result_dict
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "createPatient mutation template",
            "success": False,
            "input": {"operation_name": "createPatient", "operation_type": "mutation"},
            "error": str(e)
        })
    
    return results

def test_code_examples_detailed():
    """Test 3: Code Examples Tool"""
    print("\n" + "="*80)
    print("Testing code_examples tool - DETAILED")
    print("="*80)
    
    results = []
    
    # Initialize tool
    settings = get_settings()
    schema_manager = SchemaManager(
        api_endpoint=str(settings.healthie_api_url),
        cache_dir=Path(settings.schema_dir)
    )
    tool = CodeExamplesTool(schema_manager)
    
    # Test 1: Get Python examples for patient queries
    print("\n📝 Test 1: Python examples for patient queries")
    try:
        input_data = CodeExamplesInput(
            operation_name="patient",
            language="python",
            include_authentication=True,
            include_error_handling=True
        )
        
        result = tool.execute(input_data)
        result_dict = result.model_dump()
        
        print(f"\n✅ Generated {len(result_dict['examples'])} Python examples")
        print(f"Authentication included: {result_dict['authentication_included']}")
        print(f"Error handling included: {result_dict['error_handling_included']}")
        
        results.append({
            "test": "Python patient examples",
            "success": True,
            "input": input_data.model_dump(),
            "output": result_dict
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "Python patient examples",
            "success": False,
            "input": {
                "operation_name": "patient",
                "language": "python",
                "include_authentication": True,
                "include_error_handling": True
            },
            "error": str(e)
        })
    
    # Test 2: Get TypeScript examples for mutations
    print("\n📝 Test 2: TypeScript examples for createAppointment")
    try:
        input_data = CodeExamplesInput(
            operation_name="createAppointment",
            language="typescript",
            include_authentication=True,
            include_error_handling=True
        )
        
        result = tool.execute(input_data)
        result_dict = result.model_dump()
        
        print(f"\n✅ Generated TypeScript examples")
        for i, example in enumerate(result_dict['examples'], 1):
            print(f"\nExample {i}: {example['title']}")
            print(f"Description: {example['description']}")
        
        results.append({
            "test": "TypeScript createAppointment examples",
            "success": True,
            "input": input_data.model_dump(),
            "output": result_dict
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "TypeScript createAppointment examples",
            "success": False,
            "input": {
                "operation_name": "createAppointment",
                "language": "typescript",
                "include_authentication": True,
                "include_error_handling": True
            },
            "error": str(e)
        })
    
    return results

def test_type_introspection_detailed():
    """Test 4: Type Introspection Tool"""
    print("\n" + "="*80)
    print("Testing introspect_type tool - DETAILED")
    print("="*80)
    
    results = []
    
    # Initialize tool
    settings = get_settings()
    schema_manager = SchemaManager(
        api_endpoint=str(settings.healthie_api_url),
        cache_dir=Path(settings.schema_dir)
    )
    tool = TypeIntrospectionTool(schema_manager)
    
    # Test 1: Introspect Patient type
    print("\n📝 Test 1: Introspecting Patient type")
    try:
        result = tool.execute(type_name="Patient", include_deprecated=True)
        result_dict = result.model_dump()
        
        print(f"\n✅ Type introspection successful!")
        print(f"Type: {result_dict['type_info']['name']}")
        print(f"Kind: {result_dict['type_info']['kind']}")
        print(f"Total fields: {len(result_dict.get('fields', []))}")
        print(f"Deprecated fields: {sum(1 for f in result_dict.get('fields', []) if f.get('is_deprecated'))}")
        
        # Show some field examples
        if result_dict.get('fields'):
            print("\nSample fields:")
            for field in result_dict['fields'][:5]:
                print(f"- {field['name']}: {field['type']}")
        
        results.append({
            "test": "Patient type introspection",
            "success": True,
            "input": {
                "type_name": "Patient",
                "include_deprecated": True
            },
            "output": result_dict
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "Patient type introspection",
            "success": False,
            "input": {"type_name": "Patient", "include_deprecated": True},
            "error": str(e)
        })
    
    # Test 2: Introspect an enum type
    print("\n📝 Test 2: Introspecting enum type")
    try:
        result = tool.execute(type_name="AppointmentStatus", include_deprecated=False)
        result_dict = result.model_dump()
        
        print(f"\n✅ Enum introspection successful!")
        if result_dict.get('enum_values'):
            print(f"Enum values ({len(result_dict['enum_values'])}):")
            for value in result_dict['enum_values']:
                print(f"- {value['name']}: {value.get('description', 'No description')}")
        
        results.append({
            "test": "AppointmentStatus enum introspection",
            "success": True,
            "input": {
                "type_name": "AppointmentStatus",
                "include_deprecated": False
            },
            "output": result_dict
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "AppointmentStatus enum introspection",
            "success": False,
            "input": {"type_name": "AppointmentStatus", "include_deprecated": False},
            "error": str(e)
        })
    
    return results

def test_error_decoder_detailed():
    """Test 5: Error Decoder Tool"""
    print("\n" + "="*80)
    print("Testing error_decoder tool - DETAILED")
    print("="*80)
    
    results = []
    
    # Initialize tool
    settings = get_settings()
    schema_manager = SchemaManager(
        api_endpoint=str(settings.healthie_api_url),
        cache_dir=Path(settings.schema_dir)
    )
    tool = ErrorDecoderTool(schema_manager)
    
    # Test 1: GraphQL validation error
    print("\n📝 Test 1: Decoding GraphQL validation error")
    
    error_response = {
        "errors": [
            {
                "message": "Field 'invalidField' doesn't exist on type 'Patient'",
                "extensions": {
                    "code": "GRAPHQL_VALIDATION_FAILED",
                    "field": "invalidField",
                    "type": "Patient"
                }
            }
        ]
    }
    
    query = """
    query GetPatient($id: ID!) {
        patient(id: $id) {
            id
            firstName
            invalidField
        }
    }
    """
    
    try:
        input_data = ErrorDecoderInput(
            error_response=error_response,
            query=query,
            variables={"id": "123"}
        )
        
        result = tool.execute(input_data)
        result_dict = result.model_dump()
        
        print(f"\n✅ Error decoded successfully!")
        print(f"Error category: {result_dict['error_category']}")
        print(f"Primary cause: {result_dict['primary_cause']}")
        print(f"Solution count: {len(result_dict.get('solutions', []))}")
        
        print("\nSolutions:")
        for i, solution in enumerate(result_dict.get('solutions', []), 1):
            print(f"{i}. {solution}")
        
        results.append({
            "test": "GraphQL validation error",
            "success": True,
            "input": {
                "error_response": error_response,
                "query": query,
                "variables": {"id": "123"}
            },
            "output": result_dict
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "GraphQL validation error",
            "success": False,
            "error": str(e)
        })
    
    # Test 2: Authentication error
    print("\n📝 Test 2: Decoding authentication error")
    
    auth_error = {
        "errors": [
            {
                "message": "Unauthorized",
                "extensions": {
                    "code": "UNAUTHENTICATED"
                }
            }
        ]
    }
    
    try:
        input_data = ErrorDecoderInput(
            error_response=auth_error,
            query="query { currentUser { id } }"
        )
        
        result = tool.execute(input_data)
        result_dict = result.model_dump()
        
        print(f"\n✅ Authentication error decoded!")
        print(f"Corrected query provided: {result_dict.get('corrected_query') is not None}")
        
        results.append({
            "test": "Authentication error",
            "success": True,
            "input": {
                "error_response": auth_error,
                "query": "query { currentUser { id } }"
            },
            "output": result_dict
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "Authentication error",
            "success": False,
            "error": str(e)
        })
    
    return results

def test_compliance_checker_detailed():
    """Test 6: Compliance Checker Tool"""
    print("\n" + "="*80)
    print("Testing compliance_checker tool - DETAILED")
    print("="*80)
    
    results = []
    
    # Initialize tool
    settings = get_settings()
    schema_manager = SchemaManager(
        api_endpoint=str(settings.healthie_api_url),
        cache_dir=Path(settings.schema_dir)
    )
    tool = ComplianceCheckerTool(schema_manager)
    
    # Test 1: HIPAA compliance check
    print("\n📝 Test 1: HIPAA compliance check for patient query")
    
    test_query = """
    query GetPatientInfo($id: ID!) {
        patient(id: $id) {
            id
            firstName
            lastName
            dateOfBirth
            ssn
            email
            phoneNumber
            diagnoses {
                icdCode
                description
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
            data_handling_context="Provider viewing patient record"
        )
        
        result = tool.execute(input_data)
        result_dict = result.model_dump()
        
        print(f"\n✅ Compliance check complete!")
        print(f"Overall compliance: {result_dict['overall_compliance']}")
        print(f"Violations found: {len(result_dict.get('violations', []))}")
        print(f"PHI risks identified: {len(result_dict.get('phi_risks', []))}")
        print(f"Recommendations: {len(result_dict.get('recommendations', []))}")
        
        results.append({
            "test": "HIPAA patient query compliance",
            "success": True,
            "input": input_data.model_dump(),
            "output": result_dict
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "HIPAA patient query compliance",
            "success": False,
            "input": {
                "query": test_query,
                "operation_type": "query",
                "frameworks": ["HIPAA"]
            },
            "error": str(e)
        })
    
    # Test 2: Multi-framework compliance
    print("\n📝 Test 2: Multi-framework compliance (HIPAA + HITECH)")
    
    mutation_query = """
    mutation UpdatePatientRecord($id: ID!, $input: UpdatePatientInput!) {
        updatePatient(id: $id, input: $input) {
            patient {
                id
                medicalRecordNumber
                lastUpdated
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
            data_handling_context="Updating patient medical information"
        )
        
        result = tool.execute(input_data)
        result_dict = result.model_dump()
        
        print(f"\n✅ Multi-framework check complete!")
        print(f"Audit requirements: {len(result_dict.get('audit_requirements', []))}")
        
        results.append({
            "test": "Multi-framework mutation compliance",
            "success": True,
            "input": input_data.model_dump(),
            "output": result_dict
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "Multi-framework mutation compliance",
            "success": False,
            "error": str(e)
        })
    
    return results

def test_workflow_sequences_detailed():
    """Test 7: Workflow Sequences Tool"""
    print("\n" + "="*80)
    print("Testing workflow_sequences tool - DETAILED")
    print("="*80)
    
    results = []
    
    # Initialize tool
    settings = get_settings()
    schema_manager = SchemaManager(
        api_endpoint=str(settings.healthie_api_url),
        cache_dir=Path(settings.schema_dir)
    )
    tool = WorkflowSequencesTool(schema_manager)
    
    # Test 1: Get all workflows
    print("\n📝 Test 1: Getting all available workflows")
    try:
        result = tool.execute()  # No filters
        result_dict = result.model_dump()
        
        print(f"\n✅ Found {result_dict['total_workflows']} workflows")
        print("\nWorkflow categories:")
        categories = set()
        for workflow in result_dict.get('workflows', []):
            categories.add(workflow['category'])
        for category in sorted(categories):
            print(f"- {category}")
        
        results.append({
            "test": "get all workflows",
            "success": True,
            "input": {
                "workflow_name": None,
                "category": None
            },
            "output": result_dict
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "get all workflows",
            "success": False,
            "error": str(e)
        })
    
    # Test 2: Get specific workflow
    print("\n📝 Test 2: Getting patient onboarding workflow")
    try:
        result = tool.execute(workflow_name="patient_onboarding")
        result_dict = result.model_dump()
        
        if result_dict['workflows']:
            workflow = result_dict['workflows'][0]
            print(f"\n✅ Found workflow: {workflow['workflow_name']}")
            print(f"Steps: {workflow['total_steps']}")
            print(f"Duration: {workflow.get('estimated_duration', 'N/A')}")
            
            print("\nWorkflow steps:")
            for step in workflow.get('steps', [])[:5]:
                print(f"{step['step_number']}. {step['description']}")
        
        results.append({
            "test": "patient onboarding workflow",
            "success": True,
            "input": {
                "workflow_name": "patient_onboarding",
                "category": None
            },
            "output": result_dict
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "patient onboarding workflow",
            "success": False,
            "error": str(e)
        })
    
    return results

def test_field_relationships_detailed():
    """Test 8: Field Relationships Tool"""
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
    
    # Test 1: Explore patient field relationships
    print("\n📝 Test 1: Exploring 'patient' field relationships")
    try:
        input_data = FieldRelationshipInput(
            field_name="patient",
            max_depth=3,
            include_scalars=True
        )
        
        result = tool.execute(input_data)
        result_dict = result.model_dump()
        
        print(f"\n✅ Found {result_dict['total_relationships']} relationships")
        print(f"Related fields: {len(result_dict.get('related_fields', []))}")
        print(f"Suggestions: {len(result_dict.get('suggestions', []))}")
        
        if result_dict.get('relationship_tree'):
            print("\nRelationship tree depth:", 
                  max(len(path.split('.')) for path in result_dict.get('related_fields', [''])))
        
        results.append({
            "test": "patient field relationships",
            "success": True,
            "input": input_data.model_dump(),
            "output": result_dict
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "patient field relationships",
            "success": False,
            "input": {
                "field_name": "patient",
                "max_depth": 3,
                "include_scalars": True
            },
            "error": str(e)
        })
    
    # Test 2: Explore appointment relationships without scalars
    print("\n📝 Test 2: Exploring 'appointment' relationships (no scalars)")
    try:
        input_data = FieldRelationshipInput(
            field_name="appointment",
            max_depth=2,
            include_scalars=False
        )
        
        result = tool.execute(input_data)
        result_dict = result.model_dump()
        
        print(f"\n✅ Relationships mapped successfully")
        print(f"Complex types only: {result_dict.get('include_scalars', True) == False}")
        
        results.append({
            "test": "appointment relationships no scalars",
            "success": True,
            "input": input_data.model_dump(),
            "output": result_dict
        })
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        results.append({
            "test": "appointment relationships no scalars",
            "success": False,
            "error": str(e)
        })
    
    return results

def save_detailed_results(tool_name, tool_number, results, filename):
    """Save detailed test results for a specific tool"""
    output_dir = Path("test_results/phase_2")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = output_dir / filename
    
    with open(filepath, 'w') as f:
        f.write(f"# Tool {tool_number}: {tool_name} - Detailed Test Results\n\n")
        f.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        
        # Tool overview
        f.write("## Tool Overview\n\n")
        f.write(get_tool_overview(tool_name))
        
        # How to use
        f.write("\n## How to Use This Tool\n\n")
        f.write(get_tool_usage(tool_name))
        
        # Test summary
        success_count = sum(1 for r in results if r.get('success', False))
        f.write(f"\n## Test Summary\n\n")
        f.write(f"- **Total tests**: {len(results)}\n")
        f.write(f"- **Successful**: {success_count}\n")
        f.write(f"- **Failed**: {len(results) - success_count}\n")
        f.write(f"- **Success rate**: {(success_count/len(results)*100):.1f}%\n\n")
        
        # Detailed results
        f.write("## Detailed Test Results\n\n")
        for i, result in enumerate(results, 1):
            f.write(f"### Test {i}: {result['test']}\n\n")
            f.write(f"**Status**: {'✅ Success' if result['success'] else '❌ Failed'}\n\n")
            
            # Input parameters
            if 'input' in result:
                f.write("#### Input Parameters\n\n")
                f.write("```json\n")
                f.write(format_json(result['input']))
                f.write("\n```\n\n")
            
            # Show query if present
            if 'input_query' in result:
                f.write("#### Input Query\n\n")
                f.write("```graphql\n")
                f.write(result['input_query'])
                f.write("\n```\n\n")
            
            if result['success']:
                # Output
                if 'output' in result:
                    f.write("#### Output\n\n")
                    f.write("```json\n")
                    f.write(format_json(result['output']))
                    f.write("\n```\n\n")
                
                # Analysis
                if 'analysis' in result:
                    f.write("#### Analysis\n\n")
                    for key, value in result['analysis'].items():
                        f.write(f"- **{key.replace('_', ' ').title()}**: {value}\n")
                    f.write("\n")
                    
            else:
                f.write(f"**Error**: {result.get('error', 'Unknown error')}\n\n")
                if 'traceback' in result:
                    f.write("**Traceback**:\n```\n")
                    f.write(result['traceback'])
                    f.write("\n```\n")
            
            f.write("\n---\n\n")
    
    print(f"📄 Results saved to: {filepath}")

def get_tool_overview(tool_name):
    """Get overview description for each tool"""
    overviews = {
        "search_schema": "The Schema Search tool allows you to search through the Healthie GraphQL schema to find types, fields, arguments, and enums. It's essential for discovering available operations and understanding the API structure.",
        "query_templates": "The Query Templates tool generates ready-to-use GraphQL query and mutation templates for specific operations. It automatically includes all available fields and proper variable definitions.",
        "code_examples": "The Code Examples tool generates complete, runnable code examples in Python, TypeScript, or cURL for interacting with the Healthie API. Examples include authentication and error handling.",
        "introspect_type": "The Type Introspection tool provides detailed information about specific GraphQL types, including all fields, their types, descriptions, and deprecation status.",
        "error_decoder": "The Error Decoder tool analyzes GraphQL error responses and provides clear explanations, solutions, and corrected queries when possible.",
        "compliance_checker": "The Compliance Checker tool validates GraphQL queries against healthcare regulatory frameworks (HIPAA, HITECH, GDPR) to ensure proper PHI handling and audit compliance.",
        "workflow_sequences": "The Workflow Sequences tool provides pre-built, multi-step workflows for common healthcare operations like patient onboarding, appointment scheduling, and billing.",
        "field_relationships": "The Field Relationships tool maps and visualizes the relationships between GraphQL fields, helping understand data structure and navigation paths."
    }
    return overviews.get(tool_name, "Tool for working with Healthie GraphQL API.")

def get_tool_usage(tool_name):
    """Get usage instructions for each tool"""
    usage_templates = {
        "search_schema": """### Python Usage

```python
from healthie_mcp.tools.schema_search import SchemaSearchTool
from healthie_mcp.schema_manager import SchemaManager

# Initialize the tool
schema_manager = SchemaManager(api_endpoint='https://api.gethealthie.com/graphql')
tool = SchemaSearchTool(schema_manager)

# Search for patient-related items
result = tool.execute(query="patient", search_type="all")

# Search only for types
result = tool.execute(query="appointment", search_type="types")

# Search for fields
result = tool.execute(query="email", search_type="fields")
```

### Parameters

- **query** (required): The search term to look for in the schema
- **search_type** (optional): One of "all", "types", "fields", "arguments", "enums" (default: "all")
""",

        "query_templates": """### Python Usage

```python
from healthie_mcp.tools.query_templates import QueryTemplatesTool
from healthie_mcp.schema_manager import SchemaManager

# Initialize the tool
schema_manager = SchemaManager(api_endpoint='https://api.gethealthie.com/graphql')
tool = QueryTemplatesTool(schema_manager)

# Get a query template
result = tool.execute(operation_name="patient", operation_type="query")

# Get a mutation template
result = tool.execute(operation_name="createAppointment", operation_type="mutation")
```

### Parameters

- **operation_name** (required): The name of the operation (e.g., "patient", "createAppointment")
- **operation_type** (required): Either "query" or "mutation"
""",

        "code_examples": """### Python Usage

```python
from healthie_mcp.tools.code_examples import CodeExamplesTool, CodeExamplesInput
from healthie_mcp.schema_manager import SchemaManager

# Initialize the tool
schema_manager = SchemaManager(api_endpoint='https://api.gethealthie.com/graphql')
tool = CodeExamplesTool(schema_manager)

# Get Python examples
input_data = CodeExamplesInput(
    operation_name="patient",
    language="python",
    include_authentication=True,
    include_error_handling=True
)
result = tool.execute(input_data)

# Get TypeScript examples
input_data = CodeExamplesInput(
    operation_name="createAppointment",
    language="typescript",
    include_authentication=True,
    include_error_handling=True
)
result = tool.execute(input_data)
```

### Parameters

- **operation_name** (required): The GraphQL operation name
- **language** (required): One of "python", "typescript", or "curl"
- **include_authentication** (optional): Include auth code (default: True)
- **include_error_handling** (optional): Include error handling (default: True)
""",

        "introspect_type": """### Python Usage

```python
from healthie_mcp.tools.type_introspection import TypeIntrospectionTool
from healthie_mcp.schema_manager import SchemaManager

# Initialize the tool
schema_manager = SchemaManager(api_endpoint='https://api.gethealthie.com/graphql')
tool = TypeIntrospectionTool(schema_manager)

# Introspect a type
result = tool.execute(type_name="Patient", include_deprecated=True)

# Introspect an enum
result = tool.execute(type_name="AppointmentStatus", include_deprecated=False)
```

### Parameters

- **type_name** (required): The name of the type to introspect
- **include_deprecated** (optional): Include deprecated fields (default: False)
""",

        "error_decoder": """### Python Usage

```python
from healthie_mcp.tools.error_decoder import ErrorDecoderTool, ErrorDecoderInput
from healthie_mcp.schema_manager import SchemaManager

# Initialize the tool
schema_manager = SchemaManager(api_endpoint='https://api.gethealthie.com/graphql')
tool = ErrorDecoderTool(schema_manager)

# Decode an error
error_response = {
    "errors": [{
        "message": "Field 'invalidField' doesn't exist on type 'Patient'",
        "extensions": {"code": "GRAPHQL_VALIDATION_FAILED"}
    }]
}

input_data = ErrorDecoderInput(
    error_response=error_response,
    query="query { patient(id: 123) { invalidField } }",
    variables={}
)
result = tool.execute(input_data)
```

### Parameters

- **error_response** (required): The error response from GraphQL
- **query** (optional): The query that caused the error
- **variables** (optional): Variables used in the query
""",

        "compliance_checker": """### Python Usage

```python
from healthie_mcp.tools.compliance_checker import ComplianceCheckerTool, ComplianceCheckerInput
from healthie_mcp.models.compliance_checker import RegulatoryFramework
from healthie_mcp.schema_manager import SchemaManager

# Initialize the tool
schema_manager = SchemaManager(api_endpoint='https://api.gethealthie.com/graphql')
tool = ComplianceCheckerTool(schema_manager)

# Check compliance
input_data = ComplianceCheckerInput(
    query='query { patient(id: "123") { firstName ssn } }',
    operation_type='query',
    frameworks=[RegulatoryFramework.HIPAA],
    check_phi_exposure=True,
    check_audit_requirements=True,
    data_handling_context='Provider viewing patient record'
)
result = tool.execute(input_data)
```

### Parameters

- **query** (required): The GraphQL query to check
- **operation_type** (required): Either "query" or "mutation"
- **frameworks** (required): List of frameworks (HIPAA, HITECH, GDPR)
- **check_phi_exposure** (optional): Check for PHI exposure (default: True)
- **check_audit_requirements** (optional): Check audit needs (default: True)
- **data_handling_context** (optional): Context description
""",

        "workflow_sequences": """### Python Usage

```python
from healthie_mcp.tools.workflow_sequences import WorkflowSequencesTool
from healthie_mcp.schema_manager import SchemaManager

# Initialize the tool
schema_manager = SchemaManager(api_endpoint='https://api.gethealthie.com/graphql')
tool = WorkflowSequencesTool(schema_manager)

# Get all workflows
result = tool.execute()

# Get specific workflow
result = tool.execute(workflow_name="patient_onboarding")

# Get workflows by category
result = tool.execute(category="appointment_management")
```

### Parameters

- **workflow_name** (optional): Filter by workflow name
- **category** (optional): Filter by category
""",

        "field_relationships": """### Python Usage

```python
from healthie_mcp.tools.field_relationships import FieldRelationshipTool, FieldRelationshipInput
from healthie_mcp.schema_manager import SchemaManager

# Initialize the tool
schema_manager = SchemaManager(api_endpoint='https://api.gethealthie.com/graphql')
tool = FieldRelationshipTool(schema_manager)

# Explore field relationships
input_data = FieldRelationshipInput(
    field_name='patient',
    max_depth=3,
    include_scalars=True
)
result = tool.execute(input_data)
```

### Parameters

- **field_name** (required): The field to explore relationships for
- **max_depth** (optional): Maximum traversal depth (default: 2)
- **include_scalars** (optional): Include scalar fields (default: True)
"""
    }
    return usage_templates.get(tool_name, "See tool documentation for usage details.")

def main():
    """Run comprehensive tests for all 8 working tools"""
    print("="*80)
    print("Phase 2: Comprehensive Testing of All 8 Working MCP Tools")
    print("="*80)
    
    all_results = []
    
    # Test all 8 tools
    tools = [
        ("search_schema", test_schema_search_detailed, "01_search_schema_detailed.md"),
        ("query_templates", test_query_templates_detailed, "02_query_templates_detailed.md"),
        ("code_examples", test_code_examples_detailed, "03_code_examples_detailed.md"),
        ("introspect_type", test_type_introspection_detailed, "04_introspect_type_detailed.md"),
        ("error_decoder", test_error_decoder_detailed, "05_error_decoder_detailed.md"),
        ("compliance_checker", test_compliance_checker_detailed, "06_compliance_checker_detailed.md"),
        ("workflow_sequences", test_workflow_sequences_detailed, "07_workflow_sequences_detailed.md"),
        ("field_relationships", test_field_relationships_detailed, "08_field_relationships_detailed.md")
    ]
    
    for i, (tool_name, test_func, output_file) in enumerate(tools, 1):
        print(f"\n{'='*80}")
        print(f"Testing Tool {i}/8: {tool_name}")
        print(f"{'='*80}")
        
        try:
            results = test_func()
            all_results.extend(results)
            save_detailed_results(tool_name, i, results, output_file)
        except Exception as e:
            print(f"❌ Tool {tool_name} testing failed: {str(e)}")
            traceback.print_exc()
    
    # Overall summary
    total_tests = len(all_results)
    total_success = sum(1 for r in all_results if r.get('success', False))
    
    print("\n" + "="*80)
    print("PHASE 2 TESTING COMPLETE - OVERALL SUMMARY")
    print("="*80)
    print(f"Total tests run: {total_tests}")
    print(f"Successful tests: {total_success}")
    print(f"Failed tests: {total_tests - total_success}")
    print(f"Overall success rate: {(total_success/total_tests*100):.1f}%")
    print(f"\nDetailed results saved to: test_results/phase_2/")
    
    return 0 if total_success == total_tests else 1

if __name__ == "__main__":
    sys.exit(main())