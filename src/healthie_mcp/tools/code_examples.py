"""Code example generator tool for external developers."""

from typing import Optional, List, Dict, Any
from ..models.external_dev_tools import (
    CodeExampleInput, CodeExampleResult, CodeExample, CodeLanguage
)
from ..base import BaseTool, SchemaManagerProtocol
from ..config.loader import ConfigLoader
from ..exceptions import ToolError


class CodeExampleConstants:
    """Constants for code example generation."""
    
    # Default languages to generate when none specified
    DEFAULT_LANGUAGES = [CodeLanguage.JAVASCRIPT, CodeLanguage.PYTHON, CodeLanguage.CURL]
    
    # Operation categories for code generation
    OPERATION_CATEGORIES = {
        'patient': ['create', 'get', 'update', 'list'],
        'appointment': ['book', 'create', 'get', 'list', 'cancel', 'update'],
        'provider': ['get', 'list', 'create', 'update'],
        'billing': ['create_charge', 'get_invoices', 'process_payment'],
        'clinical': ['create_note', 'get_assessments', 'update_care_plan']
    }
    
    # Common GraphQL endpoints
    GRAPHQL_ENDPOINTS = {
        'production': 'https://api.gethealthie.com/graphql',
        'staging': 'https://staging-api.gethealthie.com/graphql'
    }
    
    # Common dependencies by language
    LANGUAGE_DEPENDENCIES = {
        CodeLanguage.JAVASCRIPT: ["fetch API", "axios (optional)", "node.js"],
        CodeLanguage.TYPESCRIPT: ["fetch API", "@types/node", "typescript"],
        CodeLanguage.PYTHON: ["requests", "python 3.7+"],
        CodeLanguage.CURL: ["curl", "jq (optional for JSON parsing)"]
    }
    
    # Authentication notes
    AUTH_NOTES = {
        'api_key': "Set HEALTHIE_API_KEY environment variable with your API key",
        'bearer_token': "Use Bearer token authentication in Authorization header",
        'environment': "Use staging environment for testing, production for live data"
    }


class CodeExampleTool(BaseTool[CodeExampleResult]):
    """Tool for generating code examples for external developers."""
    
    def __init__(self, schema_manager: SchemaManagerProtocol):
        """Initialize the code example tool."""
        super().__init__(schema_manager)
        self.config_loader = ConfigLoader()
        self._examples_cache: Optional[Dict[str, Any]] = None
    
    def get_tool_name(self) -> str:
        """Get the tool name."""
        return "code_examples"
    
    def get_tool_description(self) -> str:
        """Get the tool description."""
        return (
            "Generate working code examples for GraphQL operations in multiple languages "
            "to help external developers integrate with the Healthie API"
        )
    
    def execute(self, input_data: CodeExampleInput) -> CodeExampleResult:
        """Generate code examples for the specified operation.
        
        Args:
            input_data: Input parameters for code generation
            
        Returns:
            CodeExampleResult with generated examples
        """
        try:
            # Load configuration
            self._ensure_config_loaded()
            
            # Validate and parse languages
            target_languages = self._parse_languages(input_data.language)
            
            # Generate examples
            examples = self._generate_examples(input_data.operation_name, target_languages)
            
            # Build result
            return self._build_result(input_data.operation_name, examples)
            
        except Exception as e:
            return CodeExampleResult(
                operation_name=input_data.operation_name,
                examples=[],
                total_examples=0,
                languages=[],
                error=f"Error generating code examples: {str(e)}"
            )
    
    def _ensure_config_loaded(self) -> None:
        """Ensure configuration is loaded."""
        if self._examples_cache is None:
            try:
                self._examples_cache = self.config_loader.load_examples()
            except Exception:
                # Use default configuration if loading fails
                self._examples_cache = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration when config loading fails."""
        return {
            "examples": {},
            "templates": {},
            "endpoints": CodeExampleConstants.GRAPHQL_ENDPOINTS,
            "dependencies": CodeExampleConstants.LANGUAGE_DEPENDENCIES
        }
    
    def _parse_languages(self, language_filter: Optional[str]) -> List[CodeLanguage]:
        """Parse and validate language filter.
        
        Args:
            language_filter: Optional language filter string
            
        Returns:
            List of CodeLanguage enums to target
        """
        if not language_filter:
            return CodeExampleConstants.DEFAULT_LANGUAGES
        
        try:
            return [CodeLanguage(language_filter.lower())]
        except ValueError:
            # Return default if invalid language specified
            return CodeExampleConstants.DEFAULT_LANGUAGES
    
    def _generate_examples(self, operation_name: str, languages: List[CodeLanguage]) -> List[CodeExample]:
        """Generate code examples for the operation.
        
        Args:
            operation_name: Name of the operation
            languages: Languages to generate examples for
            
        Returns:
            List of CodeExample objects
        """
        examples = []
        operation_lower = operation_name.lower()
        
        # Try to find examples in configuration first
        config_examples = self._get_config_examples(operation_name, languages)
        if config_examples:
            examples.extend(config_examples)
        
        # Generate examples based on operation patterns
        pattern_examples = self._generate_pattern_examples(operation_lower, languages)
        examples.extend(pattern_examples)
        
        return examples
    
    def _get_config_examples(self, operation_name: str, languages: List[CodeLanguage]) -> List[CodeExample]:
        """Get examples from configuration.
        
        Args:
            operation_name: Operation name
            languages: Target languages
            
        Returns:
            List of examples from configuration
        """
        examples = []
        config_examples = self._examples_cache.get("examples", {})
        
        for operation_key, operation_examples in config_examples.items():
            if operation_key.lower() in operation_name.lower():
                for example_data in operation_examples:
                    if self._should_include_example(example_data, languages):
                        example = self._create_example_from_config(example_data)
                        examples.append(example)
        
        return examples
    
    def _should_include_example(self, example_data: Dict[str, Any], languages: List[CodeLanguage]) -> bool:
        """Check if example should be included based on language filter.
        
        Args:
            example_data: Example configuration data
            languages: Target languages
            
        Returns:
            True if example should be included
        """
        if not isinstance(example_data, dict):
            return False
            
        example_lang = example_data.get("language")
        if not example_lang:
            return False
            
        try:
            lang_enum = CodeLanguage(example_lang.lower())
            return lang_enum in languages
        except ValueError:
            return False
    
    def _create_example_from_config(self, example_data: Dict[str, Any]) -> CodeExample:
        """Create CodeExample from configuration data.
        
        Args:
            example_data: Configuration data for example
            
        Returns:
            CodeExample object
        """
        return CodeExample(
            language=CodeLanguage(example_data["language"].lower()),
            title=example_data.get("title", "Code Example"),
            code=example_data.get("code", ""),
            dependencies=example_data.get("dependencies", []),
            notes=example_data.get("notes", "")
        )
    
    def _generate_pattern_examples(self, operation_lower: str, languages: List[CodeLanguage]) -> List[CodeExample]:
        """Generate examples based on operation patterns.
        
        Args:
            operation_lower: Operation name in lowercase
            languages: Target languages
            
        Returns:
            List of generated examples
        """
        examples = []
        
        # Generate examples for different operation patterns
        for category, operations in CodeExampleConstants.OPERATION_CATEGORIES.items():
            if category in operation_lower:
                for operation in operations:
                    if operation in operation_lower:
                        examples.extend(self._generate_category_examples(category, operation, languages))
                        break
        
        # If no specific pattern matched, generate generic examples
        if not examples:
            examples.extend(self._generate_generic_examples(operation_lower, languages))
        
        return examples
    
    def _generate_category_examples(
        self, 
        category: str, 
        operation: str, 
        languages: List[CodeLanguage]
    ) -> List[CodeExample]:
        """Generate examples for a specific category and operation.
        
        Args:
            category: Operation category (e.g., 'patient', 'appointment')
            operation: Specific operation (e.g., 'create', 'get')
            languages: Target languages
            
        Returns:
            List of generated examples
        """
        examples = []
        
        for language in languages:
            example = self._create_category_example(category, operation, language)
            if example:
                examples.append(example)
        
        return examples
    
    def _create_category_example(
        self, 
        category: str, 
        operation: str, 
        language: CodeLanguage
    ) -> Optional[CodeExample]:
        """Create a specific category example.
        
        Args:
            category: Operation category
            operation: Specific operation
            language: Target language
            
        Returns:
            CodeExample or None if not supported
        """
        # This is a simplified implementation - in practice, this would
        # generate more sophisticated examples based on the category and operation
        
        if category == 'patient' and operation == 'create':
            return self._create_create_patient_example(language)
        elif category == 'patient' and operation == 'get':
            return self._create_get_patient_example(language)
        elif category == 'appointment' and operation == 'book':
            return self._create_book_appointment_example(language)
        
        return None
    
    def _create_create_patient_example(self, language: CodeLanguage) -> Optional[CodeExample]:
        """Create patient creation example."""
        if language == CodeLanguage.JAVASCRIPT:
            return CodeExample(
                language=language,
                title="Create Patient - JavaScript",
                code=self._get_javascript_create_patient_code(),
                dependencies=CodeExampleConstants.LANGUAGE_DEPENDENCIES[language],
                notes=CodeExampleConstants.AUTH_NOTES['api_key']
            )
        elif language == CodeLanguage.PYTHON:
            return CodeExample(
                language=language,
                title="Create Patient - Python",
                code=self._get_python_create_patient_code(),
                dependencies=CodeExampleConstants.LANGUAGE_DEPENDENCIES[language],
                notes=CodeExampleConstants.AUTH_NOTES['api_key']
            )
        elif language == CodeLanguage.CURL:
            return CodeExample(
                language=language,
                title="Create Patient - cURL",
                code=self._get_curl_create_patient_code(),
                dependencies=CodeExampleConstants.LANGUAGE_DEPENDENCIES[language],
                notes=CodeExampleConstants.AUTH_NOTES['api_key']
            )
        
        return None
    
    def _create_get_patient_example(self, language: CodeLanguage) -> Optional[CodeExample]:
        """Create get patient example."""
        if language == CodeLanguage.JAVASCRIPT:
            return CodeExample(
                language=language,
                title="Get Patient - JavaScript",
                code=self._get_javascript_get_patient_code(),
                dependencies=CodeExampleConstants.LANGUAGE_DEPENDENCIES[language],
                notes=CodeExampleConstants.AUTH_NOTES['api_key']
            )
        
        return None
    
    def _create_book_appointment_example(self, language: CodeLanguage) -> Optional[CodeExample]:
        """Create book appointment example."""
        if language == CodeLanguage.PYTHON:
            return CodeExample(
                language=language,
                title="Book Appointment - Python",
                code=self._get_python_book_appointment_code(),
                dependencies=CodeExampleConstants.LANGUAGE_DEPENDENCIES[language],
                notes=CodeExampleConstants.AUTH_NOTES['api_key']
            )
        
        return None
    
    def _generate_generic_examples(self, operation_lower: str, languages: List[CodeLanguage]) -> List[CodeExample]:
        """Generate generic examples when no specific pattern matches.
        
        Args:
            operation_lower: Operation name in lowercase
            languages: Target languages
            
        Returns:
            List of generic examples
        """
        examples = []
        
        for language in languages:
            if language == CodeLanguage.JAVASCRIPT:
                examples.append(CodeExample(
                    language=language,
                    title=f"Generic GraphQL Query - JavaScript",
                    code=self._get_generic_javascript_code(),
                    dependencies=CodeExampleConstants.LANGUAGE_DEPENDENCIES[language],
                    notes="Generic example for GraphQL operations"
                ))
        
        return examples
    
    def _build_result(self, operation_name: str, examples: List[CodeExample]) -> CodeExampleResult:
        """Build the final result.
        
        Args:
            operation_name: Original operation name
            examples: Generated examples
            
        Returns:
            CodeExampleResult object
        """
        return CodeExampleResult(
            operation_name=operation_name,
            examples=examples,
            total_examples=len(examples),
            languages=[example.language for example in examples]
        )
    
    # Code generation methods
    def _get_javascript_create_patient_code(self) -> str:
        """Get JavaScript code for creating a patient."""
        return '''// Using fetch API
const createPatient = async (patientData) => {
  const mutation = `
    mutation CreatePatient($input: CreateClientInput!) {
      createClient(input: $input) {
        client {
          id
          firstName
          lastName
          email
        }
        errors {
          field
          message
        }
      }
    }
  `;

  const response = await fetch('https://staging-api.gethealthie.com/graphql', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.HEALTHIE_API_KEY}`
    },
    body: JSON.stringify({
      query: mutation,
      variables: { input: patientData }
    })
  });

  const result = await response.json();
  
  if (result.errors) {
    throw new Error(result.errors[0].message);
  }
  
  return result.data.createClient;
};

// Usage
const newPatient = await createPatient({
  firstName: "John",
  lastName: "Doe",
  email: "john.doe@example.com",
  phone: "+1234567890"
});'''
    
    def _get_python_create_patient_code(self) -> str:
        """Get Python code for creating a patient."""
        return '''import requests
import os

def create_patient(patient_data):
    mutation = """
    mutation CreatePatient($input: CreateClientInput!) {
      createClient(input: $input) {
        client {
          id
          firstName
          lastName
          email
        }
        errors {
          field
          message
        }
      }
    }
    """
    
    response = requests.post(
        'https://staging-api.gethealthie.com/graphql',
        json={
            'query': mutation,
            'variables': {'input': patient_data}
        },
        headers={
            'Authorization': f'Bearer {os.getenv("HEALTHIE_API_KEY")}',
            'Content-Type': 'application/json'
        }
    )
    
    response.raise_for_status()
    result = response.json()
    
    if 'errors' in result:
        raise Exception(result['errors'][0]['message'])
    
    return result['data']['createClient']

# Usage
new_patient = create_patient({
    'firstName': 'John',
    'lastName': 'Doe',
    'email': 'john.doe@example.com',
    'phone': '+1234567890'
})'''
    
    def _get_curl_create_patient_code(self) -> str:
        """Get cURL code for creating a patient."""
        return '''curl -X POST https://staging-api.gethealthie.com/graphql \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer $HEALTHIE_API_KEY" \\
  -d '{
    "query": "mutation CreatePatient($input: CreateClientInput!) { createClient(input: $input) { client { id firstName lastName email } errors { field message } } }",
    "variables": {
      "input": {
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890"
      }
    }
  }' '''
    
    def _get_javascript_get_patient_code(self) -> str:
        """Get JavaScript code for getting a patient."""
        return '''const getPatient = async (clientId) => {
  const query = `
    query GetPatient($id: ID!) {
      client(id: $id) {
        id
        firstName
        lastName
        email
        phone
        dateOfBirth
        appointments {
          id
          startTime
          status
        }
      }
    }
  `;

  const response = await fetch('https://staging-api.gethealthie.com/graphql', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.HEALTHIE_API_KEY}`
    },
    body: JSON.stringify({
      query: query,
      variables: { id: clientId }
    })
  });

  const result = await response.json();
  return result.data.client;
};'''
    
    def _get_python_book_appointment_code(self) -> str:
        """Get Python code for booking an appointment."""
        return '''def book_appointment(client_id, provider_id, start_time, end_time):
    mutation = """
    mutation BookAppointment($input: CreateAppointmentInput!) {
      createAppointment(input: $input) {
        appointment {
          id
          startTime
          endTime  
          status
        }
        errors {
          field
          message
        }
      }
    }
    """
    
    response = requests.post(
        'https://staging-api.gethealthie.com/graphql',
        json={
            'query': mutation,
            'variables': {
                'input': {
                    'clientId': client_id,
                    'providerId': provider_id,
                    'startTime': start_time,
                    'endTime': end_time
                }
            }
        },
        headers={
            'Authorization': f'Bearer {os.getenv("HEALTHIE_API_KEY")}',
            'Content-Type': 'application/json'
        }
    )
    
    return response.json()['data']['createAppointment']'''
    
    def _get_generic_javascript_code(self) -> str:
        """Get generic JavaScript code."""
        return '''// Generic GraphQL request function
const makeGraphQLRequest = async (query, variables = {}) => {
  const response = await fetch('https://staging-api.gethealthie.com/graphql', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.HEALTHIE_API_KEY}`
    },
    body: JSON.stringify({
      query: query,
      variables: variables
    })
  });

  const result = await response.json();
  
  if (result.errors) {
    throw new Error(result.errors[0].message);
  }
  
  return result.data;
};'''


def setup_code_example_tool(mcp, schema_manager: SchemaManagerProtocol):
    """Setup the code example tool."""
    tool = CodeExampleTool(schema_manager)

    @mcp.tool(name=tool.get_tool_name())
    def code_examples(
        operation_name: str,
        language: Optional[str] = None
    ) -> dict:
        """Generate working code examples for GraphQL operations in multiple languages.
        
        This tool provides ready-to-use code examples for common GraphQL operations,
        helping external developers integrate quickly with the Healthie API.
        
        Args:
            operation_name: Name of the GraphQL operation or workflow
            language: Specific language to generate (javascript, typescript, python, curl)
                     
        Returns:
            CodeExampleResult with code examples in requested languages
        """
        input_data = CodeExampleInput(
            operation_name=operation_name,
            language=language
        )

        result = tool.execute(input_data)
        return result.model_dump()

