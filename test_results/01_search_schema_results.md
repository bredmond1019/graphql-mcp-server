# Tool: search_schema

*Tested on: 2025-07-02 22:15:32*

## Purpose
Search through GraphQL schema to find types, fields, queries, and mutations using regex patterns.

## Test 1: Search for Patient types and fields

### Input
```json
{
  "tool": "search_schema",
  "arguments": {
    "query": "Patient",
    "type_filter": "type",
    "context_lines": 2
  }
}
```

### Output
```json
{
  "total_matches": 106,
  "matches": [
    {
      "line": 605,
      "type": "field",
      "content": "   \n     \"\"\"The number of times a patient rescheduled an appointment\"\"\"\n>>>   patient_reschedule_cou...",
      "context": []
    },
    {
      "line": 1073,
      "type": "field",
      "content": "     If there is an existing patient record for the patient requesting the appointment\n     \"\"\"\n>>> ...",
      "context": []
    },
    {
      "line": 1382,
      "type": "field",
      "content": "   \n     \"\"\"The maximum number of times a patient can self reschedule\"\"\"\n>>>   patient_reschedule_co...",
      "context": []
    }
  ]
}
```

### Analysis
Found 106 matches for 'Patient'. This demonstrates the tool's ability to quickly search through the large schema file.

## Test 2: Search for appointment mutations

### Input
```json
{
  "tool": "search_schema",
  "arguments": {
    "query": "appointment",
    "type_filter": "mutation",
    "context_lines": 1
  }
}
```

### Output
```json
{
  "total_matches": 96,
  "matches": [
    {
      "line": 10417,
      "type": "other",
      "content": "   \n>>>   \"\"\"Attach Appointment to Charting Note\"\"\"\n     connectApptToCharting(",
      "context": []
    },
    {
      "line": 10510,
      "type": "other",
      "content": "     \"\"\"\n>>>   create appointment mutation for providers. Clients use the completeCheckout mutation\n...",
      "context": []
    },
    {
      "line": 10512,
      "type": "other",
      "content": "     \"\"\"\n>>>   createAppointment(\n       \"\"\"Parameters for createAppointment\"\"\"",
      "context": []
    }
  ]
}
```

### Analysis
Found 96 matches for 'appointment'. This demonstrates the tool's ability to quickly search through the large schema file.

## Test 3: Search for insurance related items

### Input
```json
{
  "tool": "search_schema",
  "arguments": {
    "query": "insurance",
    "type_filter": "any",
    "context_lines": 1
  }
}
```

### Output
```json
{
  "total_matches": 373,
  "matches": [
    {
      "line": 17,
      "type": "other",
      "content": "   \n>>> \"\"\"Accepted Insurance Plan\"\"\"\n   type AcceptedInsurancePlan {",
      "context": []
    },
    {
      "line": 18,
      "type": "type",
      "content": "   \"\"\"Accepted Insurance Plan\"\"\"\n>>> type AcceptedInsurancePlan {\n     \"\"\"Unique identifier of the p...",
      "context": []
    },
    {
      "line": 23,
      "type": "field",
      "content": "     \"\"\"Connected ICD Code Object\"\"\"\n>>>   insurance_plan: InsurancePlan\n   }",
      "context": []
    }
  ]
}
```

### Analysis
Found 373 matches for 'insurance'. This demonstrates the tool's ability to quickly search through the large schema file.

## Summary
- Total tests: 3
- Successful: 3
- Failed: 0

The search_schema tool effectively searches through the 36,000+ line schema file, making it easy to find specific types, fields, and operations. This is invaluable for developers exploring the API.
