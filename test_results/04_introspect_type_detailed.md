# Tool 4: introspect_type - Detailed Test Results

*Generated on: 2025-07-02 23:42:56*

## Tool Overview

The Type Introspection tool provides detailed information about specific GraphQL types, including all fields, their types, descriptions, and deprecation status.
## How to Use This Tool

### Python Usage

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

## Test Summary

- **Total tests**: 2
- **Successful**: 2
- **Failed**: 0
- **Success rate**: 100.0%

## Detailed Test Results

### Test 1: Patient type introspection

**Status**: ✅ Success

#### Input Parameters

```json
{
  "type_name": "Patient",
  "include_deprecated": true
}
```

#### Output

```json
{
  "type_info": {
    "name": "Patient",
    "kind": "OBJECT",
    "description": "Represents a patient in the healthcare system"
  },
  "fields": [
    {
      "name": "id",
      "type": "ID!",
      "description": "Unique identifier for the patient",
      "is_deprecated": false
    },
    {
      "name": "firstName",
      "type": "String!",
      "description": "Patient's first name",
      "is_deprecated": false
    },
    {
      "name": "lastName",
      "type": "String!",
      "description": "Patient's last name",
      "is_deprecated": false
    },
    {
      "name": "email",
      "type": "String",
      "description": "Patient's email address",
      "is_deprecated": false
    },
    {
      "name": "phoneNumber",
      "type": "String",
      "description": "Patient's phone number",
      "is_deprecated": false
    },
    {
      "name": "dateOfBirth",
      "type": "Date",
      "description": "Patient's date of birth",
      "is_deprecated": false
    },
    {
      "name": "gender",
      "type": "Gender",
      "description": "Patient's gender",
      "is_deprecated": false
    },
    {
      "name": "medicalRecordNumber",
      "type": "String",
      "description": "Medical record number",
      "is_deprecated": false
    },
    {
      "name": "ssn",
      "type": "String",
      "description": "Social Security Number (deprecated)",
      "is_deprecated": true,
      "deprecation_reason": "Use encrypted SSN field instead"
    },
    {
      "name": "appointments",
      "type": "[Appointment!]",
      "description": "List of patient's appointments",
      "is_deprecated": false
    },
    {
      "name": "diagnoses",
      "type": "[Diagnosis!]",
      "description": "Patient's diagnoses",
      "is_deprecated": false
    },
    {
      "name": "medications",
      "type": "[Medication!]",
      "description": "Patient's current medications",
      "is_deprecated": false
    }
  ],
  "interfaces": [],
  "enum_values": null
}
```


---

### Test 2: AppointmentStatus enum introspection

**Status**: ✅ Success

#### Input Parameters

```json
{
  "type_name": "AppointmentStatus",
  "include_deprecated": false
}
```

#### Output

```json
{
  "type_info": {
    "name": "AppointmentStatus",
    "kind": "ENUM",
    "description": "Possible statuses for an appointment"
  },
  "fields": null,
  "interfaces": null,
  "enum_values": [
    {
      "name": "SCHEDULED",
      "description": "Appointment is scheduled",
      "is_deprecated": false
    },
    {
      "name": "CONFIRMED",
      "description": "Appointment is confirmed by patient",
      "is_deprecated": false
    },
    {
      "name": "IN_PROGRESS",
      "description": "Appointment is currently in progress",
      "is_deprecated": false
    },
    {
      "name": "COMPLETED",
      "description": "Appointment has been completed",
      "is_deprecated": false
    },
    {
      "name": "CANCELLED",
      "description": "Appointment was cancelled",
      "is_deprecated": false
    },
    {
      "name": "NO_SHOW",
      "description": "Patient did not show up",
      "is_deprecated": false
    }
  ]
}
```


---

