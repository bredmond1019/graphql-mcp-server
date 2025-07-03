# Tool: query_templates

*Tested on: 2025-07-02 22:15:32*

## Purpose
Get pre-built GraphQL query templates for common healthcare workflows.

## Test 1: All workflows (no filter)

### Input
```json
{
  "tool": "query_templates",
  "arguments": {
    "workflow": null,
    "include_variables": true
  }
}
```

### Output
```json
{
  "template_count": 10,
  "templates": [
    {
      "name": "Get Patient Details",
      "description": "Retrieve comprehensive patient information including demographics and medical history",
      "query": "query GetPatientDetails($clientId: ID!) {\n  client(id: $clientId) {\n    id\n    first_name\n    last_name\n    email\n    phone_number\n    date_of_birth\n    gender\n    addresses {\n      line1\n      line2\n...",
      "variables": {
        "clientId": "patient-id-here"
      }
    },
    {
      "name": "Create New Patient",
      "description": "Register a new patient with required demographic information",
      "query": "mutation CreatePatient($input: signUpInput!) {\n  signUp(input: $input) {\n    user {\n      id\n      first_name\n      last_name\n      email\n      phone_number\n    }\n    errors {\n      field\n      messag...",
      "variables": {
        "input": {
          "first_name": "John",
          "last_name": "Doe",
          "email": "john.doe@example.com",
          "phone_number": "+1234567890",
          "role": "patient",
          "dietitian_id": "provider-id-here"
        }
      }
    }
  ]
}
```

### Analysis
Retrieved 10 templates for the None workflow. These templates provide ready-to-use GraphQL queries.

## Test 2: Patient management workflow

### Input
```json
{
  "tool": "query_templates",
  "arguments": {
    "workflow": "patient_management",
    "include_variables": true
  }
}
```

### Output
```json
{
  "template_count": 3,
  "templates": [
    {
      "name": "Get Patient Details",
      "description": "Retrieve comprehensive patient information including demographics and medical history",
      "query": "query GetPatientDetails($clientId: ID!) {\n  client(id: $clientId) {\n    id\n    first_name\n    last_name\n    email\n    phone_number\n    date_of_birth\n    gender\n    addresses {\n      line1\n      line2\n...",
      "variables": {
        "clientId": "patient-id-here"
      }
    },
    {
      "name": "Create New Patient",
      "description": "Register a new patient with required demographic information",
      "query": "mutation CreatePatient($input: signUpInput!) {\n  signUp(input: $input) {\n    user {\n      id\n      first_name\n      last_name\n      email\n      phone_number\n    }\n    errors {\n      field\n      messag...",
      "variables": {
        "input": {
          "first_name": "John",
          "last_name": "Doe",
          "email": "john.doe@example.com",
          "phone_number": "+1234567890",
          "role": "patient",
          "dietitian_id": "provider-id-here"
        }
      }
    }
  ]
}
```

### Analysis
Retrieved 3 templates for the patient_management workflow. These templates provide ready-to-use GraphQL queries.

## Test 3: Clinical data workflow

### Input
```json
{
  "tool": "query_templates",
  "arguments": {
    "workflow": "clinical_data",
    "include_variables": false
  }
}
```

### Output
```json
{
  "template_count": 2,
  "templates": [
    {
      "name": "Get Patient Forms",
      "description": "Retrieve forms and assessments for a patient",
      "query": "query GetPatientForms($clientId: ID!, $formType: String) {\n  client(id: $clientId) {\n    id\n    forms(type: $formType) {\n      id\n      name\n      formType\n      status\n      submittedAt\n      respons...",
      "variables": {}
    },
    {
      "name": "Create Clinical Note",
      "description": "Create a clinical note or progress note for a patient",
      "query": "mutation CreateClinicalNote($input: CreateNoteInput!) {\n  createNote(input: $input) {\n    note {\n      id\n      title\n      content\n      noteType\n      createdAt\n      client {\n        id\n        fir...",
      "variables": {}
    }
  ]
}
```

### Analysis
Retrieved 2 templates for the clinical_data workflow. These templates provide ready-to-use GraphQL queries.

## Summary
- Total tests: 3
- Successful: 3
- Failed: 0

The query_templates tool provides pre-built, working GraphQL queries for common healthcare workflows. This significantly accelerates development by providing tested query patterns.
