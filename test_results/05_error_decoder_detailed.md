# Tool 5: error_decoder - Detailed Test Results

*Generated on: 2025-07-02 23:42:56*

## Tool Overview

The Error Decoder tool analyzes GraphQL error responses and provides clear explanations, solutions, and corrected queries when possible.
## How to Use This Tool

### Python Usage

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

## Test Summary

- **Total tests**: 2
- **Successful**: 2
- **Failed**: 0
- **Success rate**: 100.0%

## Detailed Test Results

### Test 1: GraphQL validation error

**Status**: ✅ Success

#### Input Parameters

```json
{
  "error_response": {
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
  },
  "query": "query GetPatient($id: ID!) {\n    patient(id: $id) {\n        id\n        firstName\n        invalidField\n    }\n}",
  "variables": {
    "id": "123"
  }
}
```

#### Output

```json
{
  "error_category": "VALIDATION_ERROR",
  "primary_cause": "The field 'invalidField' does not exist on type 'Patient'",
  "solutions": [
    "Remove the 'invalidField' from your query",
    "Check available fields on Patient type using introspection",
    "Common patient fields include: id, firstName, lastName, email, dateOfBirth",
    "Use the introspect_type tool to see all available fields on Patient"
  ],
  "corrected_query": "query GetPatient($id: ID!) {\n    patient(id: $id) {\n        id\n        firstName\n        # invalidField removed - field doesn't exist\n    }\n}",
  "additional_context": {
    "available_fields": [
      "id",
      "firstName",
      "lastName",
      "email",
      "phoneNumber",
      "dateOfBirth"
    ],
    "error_location": "Line 4, Column 9"
  }
}
```


---

### Test 2: Authentication error

**Status**: ✅ Success

#### Input Parameters

```json
{
  "error_response": {
    "errors": [
      {
        "message": "Unauthorized",
        "extensions": {
          "code": "UNAUTHENTICATED"
        }
      }
    ]
  },
  "query": "query { currentUser { id } }"
}
```

#### Output

```json
{
  "error_category": "AUTHENTICATION_ERROR",
  "primary_cause": "Missing or invalid authentication token",
  "solutions": [
    "Ensure you're including the Authorization header with a valid API key",
    "Format: 'Authorization: Bearer YOUR_API_KEY'",
    "Check if your API key has expired",
    "Verify the API key has the necessary permissions for this query"
  ],
  "corrected_query": null,
  "additional_context": {
    "required_headers": {
      "Authorization": "Bearer YOUR_API_KEY",
      "Content-Type": "application/json"
    },
    "authentication_docs": "https://docs.gethealthie.com/authentication"
  }
}
```


---

