"""Code example generator tool for external developers."""

from typing import Optional, List
from mcp.server.fastmcp import FastMCP
from ..models.external_dev_tools import (
    CodeExampleResult, CodeExample, CodeLanguage
)


def setup_code_example_tool(mcp: FastMCP, schema_manager) -> None:
    """Setup the code example generator tool with the MCP server."""
    
    @mcp.tool()
    def generate_code_examples(
        operation_name: str,
        language: Optional[str] = None
    ) -> CodeExampleResult:
        """Generate working code examples for GraphQL operations in multiple languages.
        
        This tool provides ready-to-use code examples for common GraphQL operations,
        helping external developers integrate quickly with the Healthie API.
        
        Args:
            operation_name: Name of the GraphQL operation or workflow
            language: Specific language to generate (javascript, typescript, python, curl)
                     
        Returns:
            CodeExampleResult with code examples in requested languages
        """
        try:
            # Generate examples based on operation
            examples = _generate_examples(operation_name, language)
            
            return CodeExampleResult(
                operation_name=operation_name,
                examples=examples,
                total_examples=len(examples),
                languages=[example.language for example in examples]
            )
            
        except Exception as e:
            return CodeExampleResult(
                operation_name=operation_name,
                examples=[],
                total_examples=0,
                languages=[],
                error=f"Error generating code examples: {str(e)}"
            )


def _generate_examples(operation_name: str, language_filter: Optional[str]) -> List[CodeExample]:
    """Generate code examples for the specified operation."""
    examples = []
    operation_lower = operation_name.lower()
    
    # Define which languages to generate
    languages = []
    if language_filter:
        languages = [CodeLanguage(language_filter)]
    else:
        languages = [CodeLanguage.JAVASCRIPT, CodeLanguage.PYTHON, CodeLanguage.CURL]
    
    # Patient-related operations
    if 'patient' in operation_lower or 'client' in operation_lower:
        if 'create' in operation_lower:
            examples.extend(_generate_create_patient_examples(languages))
        elif 'get' in operation_lower or 'fetch' in operation_lower:
            examples.extend(_generate_get_patient_examples(languages))
    
    # Appointment operations
    elif 'appointment' in operation_lower:
        if 'book' in operation_lower or 'create' in operation_lower:
            examples.extend(_generate_book_appointment_examples(languages))
        elif 'get' in operation_lower or 'list' in operation_lower:
            examples.extend(_generate_get_appointments_examples(languages))
    
    # Generic query/mutation examples
    elif 'query' in operation_lower:
        examples.extend(_generate_generic_query_examples(languages))
    elif 'mutation' in operation_lower:
        examples.extend(_generate_generic_mutation_examples(languages))
    
    return examples


def _generate_create_patient_examples(languages: List[CodeLanguage]) -> List[CodeExample]:
    """Generate examples for creating a patient."""
    examples = []
    
    for lang in languages:
        if lang == CodeLanguage.JAVASCRIPT:
            examples.append(CodeExample(
                language=lang,
                title="Create Patient - JavaScript",
                code="""// Using fetch API
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

  const response = await fetch('https://api.gethealthie.com/graphql', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.HEALTHIE_API_KEY}`
    },
    body: JSON.stringify({
      query: mutation,
      variables: {
        input: patientData
      }
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
});""",
                dependencies=["fetch API or axios"],
                notes="Remember to set HEALTHIE_API_KEY environment variable"
            ))
        
        elif lang == CodeLanguage.PYTHON:
            examples.append(CodeExample(
                language=lang,
                title="Create Patient - Python",
                code="""import requests
import os

def create_patient(patient_data):
    mutation = '''
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
    '''
    
    response = requests.post(
        'https://api.gethealthie.com/graphql',
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
})""",
                dependencies=["requests"],
                notes="Install with: pip install requests"
            ))
        
        elif lang == CodeLanguage.CURL:
            examples.append(CodeExample(
                language=lang,
                title="Create Patient - cURL",
                code="""curl -X POST https://api.gethealthie.com/graphql \\
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
  }'""",
                notes="Set HEALTHIE_API_KEY environment variable before running"
            ))
    
    return examples


def _generate_get_patient_examples(languages: List[CodeLanguage]) -> List[CodeExample]:
    """Generate examples for getting patient data."""
    examples = []
    
    for lang in languages:
        if lang == CodeLanguage.JAVASCRIPT:
            examples.append(CodeExample(
                language=lang,
                title="Get Patient Details - JavaScript",
                code="""const getPatient = async (clientId) => {
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

  const response = await fetch('https://api.gethealthie.com/graphql', {
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
};""",
                dependencies=["fetch API"]
            ))
    
    return examples


def _generate_book_appointment_examples(languages: List[CodeLanguage]) -> List[CodeExample]:
    """Generate examples for booking appointments."""
    examples = []
    
    for lang in languages:
        if lang == CodeLanguage.PYTHON:
            examples.append(CodeExample(
                language=lang,
                title="Book Appointment - Python",
                code="""def book_appointment(client_id, provider_id, start_time, end_time):
    mutation = '''
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
    '''
    
    response = requests.post(
        'https://api.gethealthie.com/graphql',
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
    
    return response.json()['data']['createAppointment']""",
                dependencies=["requests"],
                notes="Times should be in ISO 8601 format"
            ))
    
    return examples


def _generate_get_appointments_examples(languages: List[CodeLanguage]) -> List[CodeExample]:
    """Generate examples for getting appointments."""
    return []  # Simplified for space


def _generate_generic_query_examples(languages: List[CodeLanguage]) -> List[CodeExample]:
    """Generate generic query examples."""
    return []  # Simplified for space


def _generate_generic_mutation_examples(languages: List[CodeLanguage]) -> List[CodeExample]:
    """Generate generic mutation examples."""
    return []  # Simplified for space