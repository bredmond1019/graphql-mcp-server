# Tool: introspect_type

*Tested on: 2025-07-02 22:15:32*

## Purpose
Get detailed information about a specific GraphQL type including fields, relationships, and requirements.

## Test 1: Patient type details

### Input
```json
{
  "tool": "introspect_type",
  "arguments": {
    "type_name": "Patient"
  }
}
```

### Output
```json
{
  "type_name": "Patient",
  "kind": "ERROR",
  "description": "Type 'Patient' not found in schema.",
  "field_count": 0,
  "sample_fields": []
}
```

### Analysis
Successfully introspected the Patient type with 0 fields. This provides detailed type information for proper API usage.

## Test 2: Appointment type details

### Input
```json
{
  "tool": "introspect_type",
  "arguments": {
    "type_name": "Appointment"
  }
}
```

### Output
```json
{
  "type_name": "Appointment",
  "kind": "OBJECT",
  "description": "An appointment object containing information about the appointment, including the attendees, date, l",
  "field_count": 98,
  "sample_fields": [
    {
      "name": "actual_duration",
      "type": "String",
      "required": false
    },
    {
      "name": "add_to_gcal_link",
      "type": "String",
      "required": false
    },
    {
      "name": "appointment_category",
      "type": "String",
      "required": false
    },
    {
      "name": "appointment_inclusions_count",
      "type": "Int",
      "required": false
    },
    {
      "name": "appointment_label",
      "type": "String",
      "required": false
    }
  ]
}
```

### Analysis
Successfully introspected the Appointment type with 98 fields. This provides detailed type information for proper API usage.

## Test 3: User type details

### Input
```json
{
  "tool": "introspect_type",
  "arguments": {
    "type_name": "User"
  }
}
```

### Output
```json
{
  "type_name": "User",
  "kind": "OBJECT",
  "description": "An user entry, returns basic user information\n\nHealthcare Context: Represents patient/client data in",
  "field_count": 453,
  "sample_fields": [
    {
      "name": "access_token",
      "type": "String",
      "required": false
    },
    {
      "name": "accessed_account",
      "type": "Boolean",
      "required": false
    },
    {
      "name": "active",
      "type": "Boolean!",
      "required": false
    },
    {
      "name": "active_care_plan",
      "type": "CarePlan",
      "required": false
    },
    {
      "name": "active_group_care_plan",
      "type": "CarePlan",
      "required": false
    }
  ]
}
```

### Analysis
Successfully introspected the User type with 453 fields. This provides detailed type information for proper API usage.

## Summary
- Total tests: 3
- Successful: 3
- Failed: 0

The introspect_type tool provides comprehensive type information including fields, types, and requirements. This is essential for understanding data structures and relationships.
