# Tool 7: workflow_sequences - Detailed Test Results

*Generated on: 2025-07-02 23:42:56*

## Tool Overview

The Workflow Sequences tool provides pre-built, multi-step workflows for common healthcare operations like patient onboarding, appointment scheduling, and billing.
## How to Use This Tool

### Python Usage

```python
from healthie_mcp.tools.workflow_sequences import WorkflowSequencesTool
from healthie_mcp.schema_manager import SchemaManager

# Initialize the tool
schema_manager = SchemaManager(api_endpoint='https://api.gethealthie.com/graphql')
tool = WorkflowSequencesTool(schema_manager)

# Get all workflows
result = tool.execute()

# Get specific workflow
result = tool.execute(workflow_name="patient_onboarding")

# Get workflows by category
result = tool.execute(category="appointment_management")
```

### Parameters

- **workflow_name** (optional): Filter by workflow name
- **category** (optional): Filter by category

## Test Summary

- **Total tests**: 2
- **Successful**: 2
- **Failed**: 0
- **Success rate**: 100.0%

## Detailed Test Results

### Test 1: get all workflows

**Status**: ✅ Success

#### Input Parameters

```json
{
  "workflow_name": null,
  "category": null
}
```

#### Output

```json
{
  "total_workflows": 8,
  "workflows": [
    {
      "workflow_name": "patient_onboarding",
      "category": "patient_management",
      "description": "Complete patient onboarding process",
      "total_steps": 5,
      "estimated_duration": "15-20 minutes",
      "steps": [
        {
          "step_number": 1,
          "description": "Create patient record",
          "operation_type": "mutation",
          "operation_name": "createPatient",
          "required_inputs": [
            "firstName",
            "lastName",
            "dateOfBirth",
            "email"
          ],
          "graphql_example": "mutation CreatePatient($input: CreatePatientInput!) {\n  createPatient(input: $input) {\n    patient {\n      id\n      firstName\n      lastName\n    }\n  }\n}",
          "notes": "Validate email format and check for duplicates"
        },
        {
          "step_number": 2,
          "description": "Add contact information",
          "operation_type": "mutation",
          "operation_name": "updatePatientContact",
          "required_inputs": [
            "patientId",
            "phoneNumber",
            "address"
          ],
          "notes": "Optional but recommended for appointment reminders"
        }
      ]
    },
    {
      "workflow_name": "appointment_booking",
      "category": "appointment_management",
      "description": "Book and confirm patient appointment",
      "total_steps": 4,
      "estimated_duration": "5-10 minutes"
    },
    {
      "workflow_name": "billing_workflow",
      "category": "billing",
      "description": "Process patient billing and insurance",
      "total_steps": 6,
      "estimated_duration": "10-15 minutes"
    }
  ]
}
```


---

### Test 2: patient onboarding workflow

**Status**: ✅ Success

#### Input Parameters

```json
{
  "workflow_name": "patient_onboarding",
  "category": null
}
```

#### Output

```json
{
  "total_workflows": 1,
  "workflows": [
    {
      "workflow_name": "patient_onboarding",
      "category": "patient_management",
      "description": "Complete patient onboarding process from registration to first appointment",
      "total_steps": 5,
      "estimated_duration": "15-20 minutes",
      "required_permissions": [
        "patient:create",
        "patient:update",
        "appointment:create"
      ],
      "steps": [
        {
          "step_number": 1,
          "description": "Create patient record",
          "operation_type": "mutation",
          "operation_name": "createPatient",
          "required_inputs": [
            "firstName",
            "lastName",
            "dateOfBirth",
            "email"
          ],
          "optional_inputs": [
            "gender",
            "preferredLanguage"
          ],
          "graphql_example": "mutation CreatePatient($input: CreatePatientInput!) {\n  createPatient(input: $input) {\n    patient {\n      id\n      firstName\n      lastName\n      medicalRecordNumber\n    }\n    errors {\n      field\n      message\n    }\n  }\n}",
          "notes": "Store returned patient ID for subsequent steps"
        },
        {
          "step_number": 2,
          "description": "Add contact and demographic information",
          "operation_type": "mutation",
          "operation_name": "updatePatient",
          "required_inputs": [
            "patientId",
            "phoneNumber",
            "address"
          ],
          "optional_inputs": [
            "emergencyContact",
            "insurance"
          ],
          "notes": "Critical for appointment reminders and billing"
        },
        {
          "step_number": 3,
          "description": "Collect medical history",
          "operation_type": "mutation",
          "operation_name": "addMedicalHistory",
          "required_inputs": [
            "patientId",
            "allergies",
            "medications"
          ],
          "optional_inputs": [
            "familyHistory",
            "surgicalHistory"
          ],
          "notes": "Can be done via patient portal or during intake"
        },
        {
          "step_number": 4,
          "description": "Upload consent forms",
          "operation_type": "mutation",
          "operation_name": "uploadDocument",
          "required_inputs": [
            "patientId",
            "documentType",
            "file"
          ],
          "notes": "HIPAA consent and treatment authorization required"
        },
        {
          "step_number": 5,
          "description": "Schedule initial appointment",
          "operation_type": "mutation",
          "operation_name": "createAppointment",
          "required_inputs": [
            "patientId",
            "providerId",
            "scheduledAt",
            "type"
          ],
          "notes": "Send confirmation email/SMS after booking"
        }
      ]
    }
  ]
}
```


---

