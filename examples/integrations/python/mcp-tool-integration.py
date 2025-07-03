"""
MCP Tool Integration for Python

This example shows how to integrate the 5 core MCP tools
into your Python application for faster Healthie API development.

Prerequisites:
- MCP server running locally or accessible
- requests library for HTTP calls
- python-graphql-client or similar
"""

import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import re


class MCPClient:
    """Client for interacting with MCP tools"""
    
    def __init__(self, server_url: str = "http://localhost:5000"):
        self.server_url = server_url
        self.session = requests.Session()
    
    def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool with parameters"""
        response = self.session.post(
            f"{self.server_url}/tools/{tool_name}",
            json=params,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    def search_schema(self, search_term: str, type_filter: Optional[str] = None) -> Dict:
        """Search the GraphQL schema"""
        params = {"search_term": search_term}
        if type_filter:
            params["type_filter"] = type_filter
        return self.call_tool("search_schema", params)
    
    def query_templates(self, workflow: str = "all", include_variables: bool = False) -> Dict:
        """Get GraphQL query templates"""
        return self.call_tool("query_templates", {
            "workflow": workflow,
            "include_variables": include_variables
        })
    
    def code_examples(self, operation: str, language: str = "python") -> Dict:
        """Generate code examples"""
        return self.call_tool("code_examples", {
            "operation": operation,
            "language": language
        })
    
    def introspect_type(self, type_name: str, include_deprecated: bool = False) -> Dict:
        """Introspect a GraphQL type"""
        return self.call_tool("introspect_type", {
            "type_name": type_name,
            "include_deprecated": include_deprecated
        })
    
    def error_decoder(self, error_message: str) -> Dict:
        """Decode GraphQL errors"""
        return self.call_tool("error_decoder", {
            "error_message": error_message
        })


class HealthieAPIClient:
    """Enhanced Healthie API client with MCP integration"""
    
    def __init__(self, api_key: str, mcp_client: MCPClient):
        self.api_key = api_key
        self.mcp = mcp_client
        self.base_url = "https://api.gethealthie.com/graphql"
        self.headers = {
            "Authorization": f"Basic {api_key}",
            "AuthorizationSource": "API",
            "Content-Type": "application/json"
        }
        self._query_cache = {}
    
    def execute_query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Execute a GraphQL query with automatic error handling"""
        try:
            response = requests.post(
                self.base_url,
                json={
                    "query": query,
                    "variables": variables or {}
                },
                headers=self.headers
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Check for GraphQL errors
            if "errors" in data:
                return self._handle_graphql_errors(data["errors"], query, variables)
            
            return data["data"]
            
        except Exception as e:
            # Decode the error
            decoded = self.mcp.error_decoder(str(e))
            
            # Enhance the exception
            e.decoded = decoded
            e.solutions = decoded.get("possible_solutions", [])
            e.example_fix = decoded.get("example_fix", "")
            
            raise e
    
    def _handle_graphql_errors(self, errors: List[Dict], query: str, variables: Dict) -> Dict:
        """Handle GraphQL errors with MCP error decoder"""
        decoded_errors = []
        
        for error in errors:
            decoded = self.mcp.error_decoder(error["message"])
            decoded_errors.append({
                "original": error,
                "decoded": decoded,
                "type": decoded.get("error_type"),
                "solutions": decoded.get("possible_solutions", [])
            })
        
        # Attempt automatic correction for field errors
        if decoded_errors[0]["type"] == "FIELD_NOT_FOUND":
            corrected_query = self._correct_field_error(query, decoded_errors[0])
            if corrected_query:
                print(f"Attempting auto-correction: {corrected_query}")
                return self.execute_query(corrected_query, variables)
        
        # Raise enhanced exception
        raise GraphQLError(decoded_errors)
    
    def _correct_field_error(self, query: str, error_info: Dict) -> Optional[str]:
        """Attempt to correct field errors automatically"""
        match = re.search(r"field '(\w+)'", error_info["original"]["message"])
        if not match:
            return None
        
        incorrect_field = match.group(1)
        
        # Search for correct field
        search_results = self.mcp.search_schema(incorrect_field, "field")
        
        if search_results["matches"]:
            correct_field = search_results["matches"][0]["field_name"]
            return query.replace(incorrect_field, correct_field)
        
        return None


class GraphQLError(Exception):
    """Enhanced GraphQL error with decoded information"""
    
    def __init__(self, decoded_errors: List[Dict]):
        self.errors = decoded_errors
        message = "\n".join([
            f"{e['original']['message']} -> {e['decoded']['plain_english']}"
            for e in decoded_errors
        ])
        super().__init__(message)


class SmartQueryBuilder:
    """Build GraphQL queries using MCP tools"""
    
    def __init__(self, mcp_client: MCPClient):
        self.mcp = mcp_client
        self._template_cache = {}
    
    def build_query(self, operation: str, workflow: str = "all") -> Dict[str, Any]:
        """Build a query from templates and schema search"""
        cache_key = f"{operation}:{workflow}"
        
        if cache_key in self._template_cache:
            return self._template_cache[cache_key]
        
        # Search for the operation
        search_results = self.mcp.search_schema(operation)
        
        if not search_results["total_matches"]:
            raise ValueError(f"Operation '{operation}' not found in schema")
        
        # Get templates
        templates = self.mcp.query_templates(workflow, include_variables=True)
        
        # Find matching template
        template = None
        for t in templates["templates"]:
            if operation.lower() in t["name"].lower():
                template = t
                break
        
        result = {
            "operation": operation,
            "search_matches": search_results["matches"],
            "template": template,
            "query": template["query"] if template else self._generate_basic_query(operation)
        }
        
        self._template_cache[cache_key] = result
        return result
    
    def _generate_basic_query(self, operation: str) -> str:
        """Generate a basic query structure"""
        return f"""
query {operation}($id: ID!) {{
  {operation}(id: $id) {{
    id
    # Add fields as needed
  }}
}}
"""


class TypeSafeFormBuilder:
    """Build forms and validation from GraphQL types"""
    
    def __init__(self, mcp_client: MCPClient):
        self.mcp = mcp_client
    
    def build_form(self, type_name: str) -> Dict[str, Any]:
        """Build form configuration from type introspection"""
        # Introspect the type
        type_info = self.mcp.introspect_type(type_name)
        
        # Build form fields
        form_fields = []
        validation_rules = {}
        
        for field in type_info["fields"]:
            field_config = {
                "name": field["name"],
                "label": self._humanize(field["name"]),
                "type": self._map_to_form_type(field["type"]),
                "required": field["type"]["kind"] == "NON_NULL"
            }
            
            # Build validation
            rules = self._build_validation_rules(field)
            if rules:
                validation_rules[field["name"]] = rules
            
            form_fields.append(field_config)
        
        return {
            "type_name": type_name,
            "fields": form_fields,
            "validation": validation_rules,
            "submit_function": self._generate_submit_function(type_name, form_fields)
        }
    
    def _humanize(self, field_name: str) -> str:
        """Convert field name to human-readable label"""
        # Convert camelCase to Title Case
        result = re.sub('([A-Z])', r' \1', field_name)
        return result.strip().title()
    
    def _map_to_form_type(self, graphql_type: Dict) -> str:
        """Map GraphQL type to form input type"""
        type_name = graphql_type.get("name") or graphql_type.get("ofType", {}).get("name")
        
        type_mapping = {
            "String": "text",
            "Int": "number",
            "Float": "number",
            "Boolean": "checkbox",
            "Date": "date",
            "DateTime": "datetime",
            "Email": "email"
        }
        
        return type_mapping.get(type_name, "text")
    
    def _build_validation_rules(self, field: Dict) -> Dict[str, Any]:
        """Build validation rules for a field"""
        rules = {}
        
        # Required validation
        if field["type"]["kind"] == "NON_NULL":
            rules["required"] = True
        
        # Field-specific validation
        field_name = field["name"].lower()
        
        if "email" in field_name:
            rules["pattern"] = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
            rules["message"] = "Please enter a valid email address"
        
        elif "phone" in field_name:
            rules["pattern"] = r"^[\d\s\-\(\)\+]+$"
            rules["message"] = "Please enter a valid phone number"
        
        elif "date" in field_name:
            rules["format"] = "date"
            if "birth" in field_name:
                rules["max"] = datetime.now().date().isoformat()
                rules["message"] = "Date of birth cannot be in the future"
        
        return rules
    
    def _generate_submit_function(self, type_name: str, fields: List[Dict]) -> str:
        """Generate a submit function for the form"""
        required_fields = [f for f in fields if f["required"]]
        
        return f"""
def submit_{type_name.lower()}(form_data):
    # Validate required fields
    errors = {{}}
    
    required_fields = {[f["name"] for f in required_fields]}
    for field in required_fields:
        if not form_data.get(field):
            errors[field] = f"{{field}} is required"
    
    if errors:
        raise ValueError(f"Validation errors: {{errors}}")
    
    # Submit to API
    return api_client.execute_query(
        mutation_query,
        {{"input": form_data}}
    )
"""


class DevelopmentWorkflow:
    """Complete development workflow using all MCP tools"""
    
    def __init__(self, api_key: str, mcp_server_url: str = "http://localhost:5000"):
        self.mcp = MCPClient(mcp_server_url)
        self.api_client = HealthieAPIClient(api_key, self.mcp)
        self.query_builder = SmartQueryBuilder(self.mcp)
        self.form_builder = TypeSafeFormBuilder(self.mcp)
    
    def implement_feature(self, feature_name: str) -> Dict[str, Any]:
        """Implement a complete feature using MCP tools"""
        print(f"🚀 Implementing {feature_name} feature...")
        
        # 1. Discovery
        discovery = self._discover_feature(feature_name)
        print(f"✅ Discovered {len(discovery['types'])} types, "
              f"{len(discovery['queries'])} queries, "
              f"{len(discovery['mutations'])} mutations")
        
        # 2. Generate code
        code = self._generate_code(feature_name, discovery)
        print("✅ Generated code templates")
        
        # 3. Build forms
        forms = self._build_forms(discovery)
        print(f"✅ Built {len(forms)} forms")
        
        # 4. Prepare error handling
        error_handlers = self._prepare_error_handling(feature_name)
        print("✅ Prepared error handlers")
        
        return {
            "discovery": discovery,
            "code": code,
            "forms": forms,
            "error_handlers": error_handlers
        }
    
    def _discover_feature(self, feature_name: str) -> Dict[str, List]:
        """Discover all schema elements for a feature"""
        results = {}
        
        for element_type in ["type", "query", "mutation"]:
            search_results = self.mcp.search_schema(feature_name, element_type)
            results[f"{element_type}s"] = search_results["matches"]
        
        return results
    
    def _generate_code(self, feature_name: str, discovery: Dict) -> Dict[str, Any]:
        """Generate code for the feature"""
        code = {}
        
        # Generate query code
        if discovery["queries"]:
            main_query = discovery["queries"][0]["content"]
            code["query"] = self.mcp.code_examples(
                self._guess_operation(main_query),
                "python"
            )
        
        # Generate mutation code
        if discovery["mutations"]:
            main_mutation = discovery["mutations"][0]["content"]
            code["mutation"] = self.mcp.code_examples(
                self._guess_operation(main_mutation),
                "python"
            )
        
        return code
    
    def _build_forms(self, discovery: Dict) -> List[Dict]:
        """Build forms for discovered types"""
        forms = []
        
        for type_match in discovery["types"][:3]:  # Limit to first 3 types
            try:
                form = self.form_builder.build_form(type_match["type_name"])
                forms.append(form)
            except Exception as e:
                print(f"Warning: Could not build form for {type_match['type_name']}: {e}")
        
        return forms
    
    def _prepare_error_handling(self, feature_name: str) -> Dict[str, Dict]:
        """Prepare error handlers for common errors"""
        common_errors = [
            f"{feature_name} not found",
            f"Invalid {feature_name}",
            f"{feature_name} already exists",
            "Not authorized",
            "Validation failed"
        ]
        
        handlers = {}
        
        for error_msg in common_errors:
            decoded = self.mcp.error_decoder(error_msg)
            handlers[error_msg] = decoded
        
        return handlers
    
    def _guess_operation(self, schema_element: str) -> str:
        """Guess operation name from schema element"""
        element_lower = schema_element.lower()
        
        if "create" in element_lower:
            if "patient" in element_lower:
                return "create_patient"
            elif "appointment" in element_lower:
                return "book_appointment"
        elif "update" in element_lower:
            return "update_patient"
        elif "get" in element_lower or "query" in element_lower:
            return "get_patient"
        
        return "create_patient"  # Default


# Example usage functions

def example_basic_usage():
    """Basic example of using MCP tools"""
    # Initialize MCP client
    mcp = MCPClient()
    
    # Search schema
    print("🔍 Searching for patient operations...")
    results = mcp.search_schema("patient", "mutation")
    print(f"Found {results['total_matches']} patient mutations")
    
    # Get templates
    print("\n📝 Getting patient templates...")
    templates = mcp.query_templates("patient_management", include_variables=True)
    print(f"Found {len(templates['templates'])} templates")
    
    # Generate code
    print("\n⚡ Generating Python code...")
    code = mcp.code_examples("create_patient", "python")
    print("Generated code ready!")
    
    # Introspect type
    print("\n🔎 Exploring Patient type...")
    patient_type = mcp.introspect_type("Patient")
    print(f"Patient type has {len(patient_type['fields'])} fields")
    
    # Decode error
    print("\n🐛 Decoding sample error...")
    error = mcp.error_decoder("Cannot query field 'patient_name' on type 'Patient'")
    print(f"Error type: {error['error_type']}")
    print(f"Solution: {error['possible_solutions'][0]}")


def example_complete_workflow():
    """Complete workflow example"""
    # Initialize workflow
    workflow = DevelopmentWorkflow(
        api_key="your_api_key_here",
        mcp_server_url="http://localhost:5000"
    )
    
    # Implement patient management feature
    patient_feature = workflow.implement_feature("patient")
    
    print("\n📊 Feature Implementation Summary:")
    print(f"Types discovered: {len(patient_feature['discovery']['types'])}")
    print(f"Queries found: {len(patient_feature['discovery']['queries'])}")
    print(f"Mutations found: {len(patient_feature['discovery']['mutations'])}")
    print(f"Forms generated: {len(patient_feature['forms'])}")
    print(f"Error handlers: {len(patient_feature['error_handlers'])}")
    
    # Use the generated code
    if patient_feature['code'].get('query'):
        print("\n📋 Generated Query Code:")
        print(patient_feature['code']['query']['code'][:500] + "...")
    
    # Show form configuration
    if patient_feature['forms']:
        print("\n📝 First Form Configuration:")
        form = patient_feature['forms'][0]
        print(f"Type: {form['type_name']}")
        print(f"Fields: {len(form['fields'])}")
        print(f"Required fields: {sum(1 for f in form['fields'] if f['required'])}")


def example_error_handling():
    """Example of advanced error handling"""
    # Initialize clients
    mcp = MCPClient()
    api_client = HealthieAPIClient("your_api_key", mcp)
    
    # Try a query that might fail
    try:
        result = api_client.execute_query("""
            query GetPatient($id: ID!) {
                patient(id: $id) {
                    id
                    patient_name  # This field doesn't exist!
                    email
                }
            }
        """, {"id": "123"})
        
    except GraphQLError as e:
        print("❌ GraphQL Error occurred:")
        for error in e.errors:
            print(f"\nOriginal: {error['original']['message']}")
            print(f"Decoded: {error['decoded']['plain_english']}")
            print(f"Solutions:")
            for solution in error['solutions']:
                print(f"  - {solution}")
    
    except Exception as e:
        if hasattr(e, 'decoded'):
            print(f"❌ Error: {e}")
            print(f"Solutions: {e.solutions}")
            print(f"Example fix: {e.example_fix}")


if __name__ == "__main__":
    print("Healthie MCP Tools - Python Integration Examples\n")
    
    # Run basic example
    print("1. Basic Usage Example")
    print("-" * 50)
    example_basic_usage()
    
    # Uncomment to run complete workflow
    # print("\n\n2. Complete Workflow Example")
    # print("-" * 50)
    # example_complete_workflow()
    
    # Uncomment to run error handling example
    # print("\n\n3. Error Handling Example")
    # print("-" * 50)
    # example_error_handling()