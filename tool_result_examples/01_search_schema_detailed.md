# Tool 1: search_schema - Detailed Test Results

*Generated on: 2025-07-02 23:42:56*

## Tool Overview

The Schema Search tool allows you to search through the Healthie GraphQL schema to find types, fields, arguments, and enums. It's essential for discovering available operations and understanding the API structure.
## How to Use This Tool

### Python Usage

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

## Test Summary

- **Total tests**: 2
- **Successful**: 2
- **Failed**: 0
- **Success rate**: 100.0%

## Detailed Test Results

### Test 1: search for patient

**Status**: ✅ Success

#### Input Parameters

```json
{
  "query": "patient",
  "search_type": "all"
}
```

#### Output

```json
{
  "total_results": 47,
  "types": [
    {
      "name": "Patient",
      "kind": "OBJECT",
      "description": "Represents a patient in the system"
    },
    {
      "name": "PatientInput",
      "kind": "INPUT_OBJECT",
      "description": "Input type for patient creation"
    },
    {
      "name": "PatientConnection",
      "kind": "OBJECT",
      "description": "Paginated patient results"
    }
  ],
  "fields": [
    {
      "name": "patient",
      "type": "Patient",
      "parent_type": "Query",
      "description": "Get a single patient by ID"
    },
    {
      "name": "patients",
      "type": "PatientConnection",
      "parent_type": "Query",
      "description": "List all patients"
    },
    {
      "name": "createPatient",
      "type": "Patient",
      "parent_type": "Mutation",
      "description": "Create a new patient"
    }
  ],
  "arguments": [
    {
      "name": "patientId",
      "type": "ID!",
      "field": "appointment",
      "parent_type": "Query"
    },
    {
      "name": "patientFilter",
      "type": "PatientFilterInput",
      "field": "appointments",
      "parent_type": "Query"
    }
  ],
  "enums": []
}
```

#### Analysis

- **Total Results**: 47
- **Result Breakdown**: {'types': 3, 'fields': 3, 'arguments': 2, 'enums': 0}


---

### Test 2: search mutations

**Status**: ✅ Success

#### Input Parameters

```json
{
  "query": "mutation",
  "search_type": "types"
}
```

#### Output

```json
{
  "total_results": 15,
  "types": [
    {
      "name": "Mutation",
      "kind": "OBJECT",
      "description": "Root mutation type"
    },
    {
      "name": "CreatePatientMutation",
      "kind": "OBJECT",
      "description": "Create patient mutation payload"
    },
    {
      "name": "UpdatePatientMutation",
      "kind": "OBJECT",
      "description": "Update patient mutation payload"
    },
    {
      "name": "CreateAppointmentMutation",
      "kind": "OBJECT",
      "description": "Create appointment mutation payload"
    },
    {
      "name": "CancelAppointmentMutation",
      "kind": "OBJECT",
      "description": "Cancel appointment mutation payload"
    }
  ],
  "fields": [],
  "arguments": [],
  "enums": []
}
```


---

