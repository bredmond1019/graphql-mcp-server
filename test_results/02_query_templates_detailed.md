# Tool 2: query_templates - Detailed Test Results

*Generated on: 2025-07-02 23:42:56*

## Tool Overview

The Query Templates tool generates ready-to-use GraphQL query and mutation templates for specific operations. It automatically includes all available fields and proper variable definitions.
## How to Use This Tool

### Python Usage

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

## Test Summary

- **Total tests**: 2
- **Successful**: 2
- **Failed**: 0
- **Success rate**: 100.0%

## Detailed Test Results

### Test 1: appointment query template

**Status**: ✅ Success

#### Input Parameters

```json
{
  "operation_name": "appointment",
  "operation_type": "query"
}
```

#### Output

```json
{
  "operation_name": "appointment",
  "template_type": "query",
  "has_variables": true,
  "variables": {
    "id": "ID!"
  },
  "template": "query GetAppointment($id: ID!) {\n  appointment(id: $id) {\n    id\n    scheduledAt\n    duration\n    status\n    type\n    provider {\n      id\n      firstName\n      lastName\n      title\n    }\n    patient {\n      id\n      firstName\n      lastName\n      dateOfBirth\n    }\n    location {\n      id\n      name\n      address\n    }\n    notes\n    createdAt\n    updatedAt\n  }\n}",
  "description": "Fetches a single appointment by ID with all available fields"
}
```


---

### Test 2: createPatient mutation template

**Status**: ✅ Success

#### Input Parameters

```json
{
  "operation_name": "createPatient",
  "operation_type": "mutation"
}
```

#### Output

```json
{
  "operation_name": "createPatient",
  "template_type": "mutation",
  "has_variables": true,
  "variables": {
    "input": "CreatePatientInput!"
  },
  "template": "mutation CreatePatient($input: CreatePatientInput!) {\n  createPatient(input: $input) {\n    patient {\n      id\n      firstName\n      lastName\n      email\n      phoneNumber\n      dateOfBirth\n      gender\n      medicalRecordNumber\n      createdAt\n    }\n    errors {\n      field\n      message\n    }\n  }\n}",
  "description": "Creates a new patient record"
}
```


---

