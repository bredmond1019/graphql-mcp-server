# Tool 11: healthcare_patterns - Detailed Test Results

*Generated on: 2025-07-03 00:25:00*

## Tool Overview

The Healthcare Patterns tool provides comprehensive healthcare workflow patterns, implementation guides, and FHIR compatibility mappings. It helps developers implement common healthcare workflows correctly with built-in compliance considerations.

## How to Use This Tool

### Python Usage

```python
from healthie_mcp.tools.healthcare_patterns import HealthcarePatternsTool
from healthie_mcp.schema_manager import SchemaManager

# Initialize the tool
schema_manager = SchemaManager(api_endpoint='https://api.gethealthie.com/graphql')
tool = HealthcarePatternsTool(schema_manager)

# Get a specific pattern
result = tool.execute(
    pattern_type="patient_registration",
    include_examples=True,
    include_compliance=True,
    include_fhir_mappings=True
)

# List all available patterns
result = tool.execute(pattern_type=None)
```

### Parameters

- **pattern_type** (optional): Specific pattern to retrieve (e.g., "patient_registration")
- **include_examples** (optional): Include code examples (default: True)
- **include_compliance** (optional): Include compliance considerations (default: True)
- **include_fhir_mappings** (optional): Include FHIR resource mappings (default: False)

## Test Summary

- **Total tests**: 4
- **Successful**: 4
- **Failed**: 0
- **Success rate**: 100.0%

## Detailed Test Results

### Test 1: Patient Registration Pattern

**Status**: ✅ Success

#### Input Parameters

```json
{
  "pattern_type": "patient_registration",
  "include_examples": true,
  "include_compliance": true,
  "include_fhir_mappings": true
}
```

#### Output

```json
{
  "pattern_name": "Patient Registration",
  "description": "Complete workflow for registering new patients in the healthcare system",
  "category": "patient_management",
  "complexity": "medium",
  "estimated_time": "15-20 minutes",
  "implementation_steps": [
    {
      "step": 1,
      "name": "Collect Patient Demographics",
      "description": "Gather essential patient information including name, DOB, contact details",
      "required_fields": [
        "firstName",
        "lastName",
        "dateOfBirth",
        "gender",
        "email",
        "phoneNumber"
      ],
      "optional_fields": [
        "middleName",
        "preferredName",
        "preferredLanguage",
        "ethnicity",
        "race"
      ],
      "validation_rules": [
        "Email must be valid format",
        "Phone must be 10 digits",
        "Date of birth must be in the past",
        "Age must be 0-120 years"
      ],
      "graphql_example": "mutation CreatePatient($input: CreatePatientInput!) {\n  createPatient(input: $input) {\n    patient {\n      id\n      firstName\n      lastName\n      email\n    }\n    errors {\n      field\n      message\n    }\n  }\n}"
    },
    {
      "step": 2,
      "name": "Verify Insurance Information",
      "description": "Collect and verify patient insurance details",
      "required_fields": [
        "insuranceProvider",
        "memberId",
        "groupNumber"
      ],
      "optional_fields": [
        "copayAmount",
        "deductible",
        "effectiveDate",
        "expirationDate"
      ],
      "validation_rules": [
        "Member ID format validation",
        "Insurance provider must be active",
        "Verify coverage dates"
      ],
      "api_calls": [
        "verifyInsuranceEligibility",
        "getInsurancePlanDetails"
      ]
    },
    {
      "step": 3,
      "name": "Capture Consent and Agreements",
      "description": "Obtain necessary consents for treatment and data sharing",
      "required_fields": [
        "hipaaConsent",
        "treatmentConsent",
        "consentDate"
      ],
      "optional_fields": [
        "researchConsent",
        "marketingConsent",
        "teleHealthConsent"
      ],
      "compliance_notes": [
        "Must retain consent records for 7 years",
        "Consent must be obtained before any PHI sharing",
        "Minor patients require guardian consent"
      ]
    },
    {
      "step": 4,
      "name": "Create Patient Record",
      "description": "Create the patient record in the system with all collected information",
      "actions": [
        "Validate all required data",
        "Create patient record",
        "Link insurance information",
        "Store consent records",
        "Generate patient ID/MRN"
      ],
      "success_criteria": [
        "Patient record created successfully",
        "Unique ID generated",
        "All consents stored",
        "Welcome email sent"
      ]
    }
  ],
  "compliance_considerations": [
    {
      "framework": "HIPAA",
      "requirements": [
        "Minimum necessary information principle",
        "Encrypt PHI in transit and at rest",
        "Implement access controls",
        "Maintain audit logs for all access"
      ]
    },
    {
      "framework": "HITECH",
      "requirements": [
        "Provide patients with electronic access to health information",
        "Implement breach notification procedures"
      ]
    }
  ],
  "fhir_mappings": {
    "patient": {
      "resource": "Patient",
      "fields": {
        "firstName": "name[0].given[0]",
        "lastName": "name[0].family",
        "dateOfBirth": "birthDate",
        "gender": "gender",
        "email": "telecom[?(@.system=='email')].value",
        "phoneNumber": "telecom[?(@.system=='phone')].value"
      }
    },
    "insurance": {
      "resource": "Coverage",
      "fields": {
        "memberId": "identifier[0].value",
        "insuranceProvider": "payor[0].reference"
      }
    },
    "consent": {
      "resource": "Consent",
      "fields": {
        "consentDate": "dateTime",
        "status": "status"
      }
    }
  },
  "code_examples": {
    "javascript": "// Complete patient registration flow\nconst registerPatient = async (patientData) => {\n  try {\n    // Step 1: Create patient\n    const { data } = await client.mutate({\n      mutation: CREATE_PATIENT,\n      variables: {\n        input: {\n          firstName: patientData.firstName,\n          lastName: patientData.lastName,\n          dateOfBirth: patientData.dateOfBirth,\n          email: patientData.email,\n          phoneNumber: patientData.phoneNumber\n        }\n      }\n    });\n    \n    const patientId = data.createPatient.patient.id;\n    \n    // Step 2: Add insurance\n    await client.mutate({\n      mutation: ADD_INSURANCE,\n      variables: {\n        patientId,\n        insurance: patientData.insurance\n      }\n    });\n    \n    // Step 3: Record consent\n    await client.mutate({\n      mutation: RECORD_CONSENT,\n      variables: {\n        patientId,\n        consentType: 'HIPAA',\n        granted: true\n      }\n    });\n    \n    return { success: true, patientId };\n  } catch (error) {\n    console.error('Registration failed:', error);\n    throw error;\n  }\n};",
    "python": "# Complete patient registration flow\nimport asyncio\nfrom datetime import datetime\n\nasync def register_patient(patient_data):\n    try:\n        # Step 1: Create patient\n        create_result = await client.execute(\n            CREATE_PATIENT_MUTATION,\n            variable_values={\n                'input': {\n                    'firstName': patient_data['firstName'],\n                    'lastName': patient_data['lastName'],\n                    'dateOfBirth': patient_data['dateOfBirth'],\n                    'email': patient_data['email'],\n                    'phoneNumber': patient_data['phoneNumber']\n                }\n            }\n        )\n        \n        patient_id = create_result['createPatient']['patient']['id']\n        \n        # Step 2: Add insurance\n        await client.execute(\n            ADD_INSURANCE_MUTATION,\n            variable_values={\n                'patientId': patient_id,\n                'insurance': patient_data['insurance']\n            }\n        )\n        \n        # Step 3: Record consent\n        await client.execute(\n            RECORD_CONSENT_MUTATION,\n            variable_values={\n                'patientId': patient_id,\n                'consentType': 'HIPAA',\n                'granted': True,\n                'grantedAt': datetime.now().isoformat()\n            }\n        )\n        \n        return {'success': True, 'patientId': patient_id}\n    except Exception as error:\n        print(f'Registration failed: {error}')\n        raise"
  },
  "common_errors": [
    {
      "error": "Duplicate patient detected",
      "cause": "Patient with same name and DOB already exists",
      "solution": "Check for existing patients before creating"
    },
    {
      "error": "Invalid insurance information",
      "cause": "Insurance verification failed",
      "solution": "Verify insurance details with provider"
    }
  ],
  "best_practices": [
    "Always validate data on both client and server side",
    "Implement duplicate patient detection logic",
    "Send confirmation emails after successful registration",
    "Log all registration attempts for audit purposes",
    "Handle partial registration failures gracefully"
  ],
  "related_patterns": [
    "patient_matching",
    "insurance_verification",
    "consent_management"
  ]
}
```

### Test 2: Appointment Scheduling Pattern

**Status**: ✅ Success

#### Input Parameters

```json
{
  "pattern_type": "appointment_scheduling",
  "include_examples": true,
  "include_compliance": false
}
```

#### Output

```json
{
  "pattern_name": "Appointment Scheduling",
  "description": "Workflow for scheduling patient appointments with providers",
  "category": "scheduling",
  "complexity": "medium",
  "estimated_time": "5-10 minutes",
  "implementation_steps": [
    {
      "step": 1,
      "name": "Check Provider Availability",
      "description": "Query available time slots for the selected provider",
      "required_fields": [
        "providerId",
        "startDate",
        "endDate"
      ],
      "graphql_example": "query GetAvailableSlots($providerId: ID!, $startDate: DateTime!, $endDate: DateTime!) {\n  availableSlots(\n    providerId: $providerId\n    startDate: $startDate\n    endDate: $endDate\n  ) {\n    id\n    startTime\n    endTime\n    duration\n    appointmentTypeIds\n  }\n}"
    },
    {
      "step": 2,
      "name": "Validate Appointment Request",
      "description": "Ensure the requested slot is still available and valid",
      "validation_rules": [
        "Slot must be in the future",
        "Patient must not have conflicting appointments",
        "Provider must be available",
        "Appointment type must match provider specialties"
      ]
    },
    {
      "step": 3,
      "name": "Create Appointment",
      "description": "Book the appointment and update calendars",
      "required_fields": [
        "patientId",
        "providerId",
        "appointmentTypeId",
        "startTime",
        "duration"
      ],
      "optional_fields": [
        "reason",
        "notes",
        "isVirtual",
        "recurringRule"
      ],
      "graphql_example": "mutation CreateAppointment($input: CreateAppointmentInput!) {\n  createAppointment(input: $input) {\n    appointment {\n      id\n      startTime\n      endTime\n      patient {\n        id\n        firstName\n        lastName\n      }\n      provider {\n        id\n        firstName\n        lastName\n      }\n    }\n    errors {\n      field\n      message\n    }\n  }\n}"
    },
    {
      "step": 4,
      "name": "Send Confirmations",
      "description": "Send appointment confirmations and reminders",
      "actions": [
        "Send email confirmation to patient",
        "Send SMS reminder if enabled",
        "Add to provider calendar",
        "Schedule reminder notifications"
      ]
    }
  ],
  "code_examples": {
    "javascript": "// Appointment scheduling flow\nconst scheduleAppointment = async ({\n  patientId,\n  providerId,\n  appointmentTypeId,\n  startTime,\n  duration,\n  reason\n}) => {\n  // Step 1: Check availability\n  const { data: slots } = await client.query({\n    query: GET_AVAILABLE_SLOTS,\n    variables: {\n      providerId,\n      startDate: startTime,\n      endDate: new Date(startTime.getTime() + 86400000) // +1 day\n    }\n  });\n  \n  // Step 2: Validate slot is available\n  const requestedSlot = slots.availableSlots.find(\n    slot => new Date(slot.startTime).getTime() === startTime.getTime()\n  );\n  \n  if (!requestedSlot) {\n    throw new Error('Requested time slot is not available');\n  }\n  \n  // Step 3: Create appointment\n  const { data } = await client.mutate({\n    mutation: CREATE_APPOINTMENT,\n    variables: {\n      input: {\n        patientId,\n        providerId,\n        appointmentTypeId,\n        startTime: startTime.toISOString(),\n        duration,\n        reason\n      }\n    }\n  });\n  \n  if (data.createAppointment.errors?.length > 0) {\n    throw new Error(data.createAppointment.errors[0].message);\n  }\n  \n  // Step 4: Send confirmations\n  await sendAppointmentConfirmation(data.createAppointment.appointment);\n  \n  return data.createAppointment.appointment;\n};"
  },
  "common_errors": [
    {
      "error": "Time slot no longer available",
      "cause": "Another user booked the slot",
      "solution": "Refresh availability and let user select again"
    },
    {
      "error": "Provider not available",
      "cause": "Provider schedule changed",
      "solution": "Re-query provider availability"
    }
  ],
  "best_practices": [
    "Implement optimistic locking for slot booking",
    "Show real-time availability updates",
    "Allow buffer time between appointments",
    "Support recurring appointments",
    "Implement waitlist functionality"
  ]
}
```

### Test 3: Clinical Documentation Pattern

**Status**: ✅ Success

#### Input Parameters

```json
{
  "pattern_type": "clinical_documentation",
  "include_examples": true,
  "include_compliance": true
}
```

#### Output

```json
{
  "pattern_name": "Clinical Documentation",
  "description": "Workflow for creating and managing clinical notes and documentation",
  "category": "clinical",
  "complexity": "high",
  "estimated_time": "10-30 minutes",
  "implementation_steps": [
    {
      "step": 1,
      "name": "Create Clinical Note",
      "description": "Initialize a new clinical note for the patient encounter",
      "required_fields": [
        "patientId",
        "providerId",
        "appointmentId",
        "noteType",
        "chiefComplaint"
      ],
      "note_types": [
        "progress_note",
        "initial_consultation",
        "follow_up",
        "procedure_note",
        "discharge_summary"
      ]
    },
    {
      "step": 2,
      "name": "Document Clinical Findings",
      "description": "Record examination findings, diagnoses, and treatment plans",
      "sections": [
        {
          "name": "History of Present Illness",
          "required": true,
          "fields": ["narrative", "duration", "severity"]
        },
        {
          "name": "Review of Systems",
          "required": true,
          "fields": ["constitutional", "cardiovascular", "respiratory"]
        },
        {
          "name": "Physical Examination",
          "required": true,
          "fields": ["vitals", "generalAppearance", "systemsExam"]
        },
        {
          "name": "Assessment and Plan",
          "required": true,
          "fields": ["diagnoses", "treatmentPlan", "followUp"]
        }
      ]
    },
    {
      "step": 3,
      "name": "Add Diagnoses and Procedures",
      "description": "Link ICD-10 codes for diagnoses and CPT codes for procedures",
      "required_fields": [
        "icd10Codes",
        "cptCodes"
      ],
      "validation_rules": [
        "ICD-10 codes must be valid and active",
        "CPT codes must match performed procedures",
        "Primary diagnosis must be specified"
      ]
    },
    {
      "step": 4,
      "name": "Sign and Lock Note",
      "description": "Electronically sign the note to make it part of the legal medical record",
      "requirements": [
        "Provider must authenticate",
        "Note must be complete",
        "All required sections filled",
        "Timestamp must be recorded"
      ],
      "graphql_example": "mutation SignClinicalNote($noteId: ID!) {\n  signClinicalNote(noteId: $noteId) {\n    note {\n      id\n      status\n      signedAt\n      signedBy {\n        id\n        name\n        credentials\n      }\n    }\n  }\n}"
    }
  ],
  "compliance_considerations": [
    {
      "framework": "HIPAA",
      "requirements": [
        "Notes must be signed within 24-48 hours",
        "Amendments must be tracked",
        "Access logs must be maintained",
        "Notes cannot be deleted, only amended"
      ]
    },
    {
      "framework": "Medicare",
      "requirements": [
        "Documentation must support medical necessity",
        "Time-based billing must include duration",
        "Teaching physician rules for residents"
      ]
    }
  ],
  "code_examples": {
    "javascript": "// Clinical documentation workflow\nconst createClinicalNote = async (encounterData) => {\n  // Step 1: Create note\n  const { data: noteData } = await client.mutate({\n    mutation: CREATE_CLINICAL_NOTE,\n    variables: {\n      input: {\n        patientId: encounterData.patientId,\n        appointmentId: encounterData.appointmentId,\n        noteType: 'progress_note',\n        chiefComplaint: encounterData.chiefComplaint\n      }\n    }\n  });\n  \n  const noteId = noteData.createClinicalNote.note.id;\n  \n  // Step 2: Add clinical content\n  await client.mutate({\n    mutation: UPDATE_NOTE_CONTENT,\n    variables: {\n      noteId,\n      sections: {\n        hpi: encounterData.historyOfPresentIllness,\n        ros: encounterData.reviewOfSystems,\n        physicalExam: encounterData.physicalExam,\n        assessment: encounterData.assessment,\n        plan: encounterData.plan\n      }\n    }\n  });\n  \n  // Step 3: Add diagnoses\n  await client.mutate({\n    mutation: ADD_DIAGNOSES,\n    variables: {\n      noteId,\n      diagnoses: encounterData.diagnoses.map(d => ({\n        icd10Code: d.code,\n        description: d.description,\n        isPrimary: d.isPrimary\n      }))\n    }\n  });\n  \n  // Step 4: Sign note\n  await client.mutate({\n    mutation: SIGN_CLINICAL_NOTE,\n    variables: { noteId }\n  });\n  \n  return noteId;\n};"
  },
  "templates": {
    "progress_note": "Chief Complaint: {{chiefComplaint}}\n\nHistory of Present Illness:\n{{hpi}}\n\nReview of Systems:\n{{ros}}\n\nPhysical Examination:\n{{physicalExam}}\n\nAssessment and Plan:\n{{assessment}}\n{{plan}}\n\nFollow-up: {{followUp}}"
  },
  "best_practices": [
    "Use templates to ensure consistency",
    "Implement auto-save functionality",
    "Support voice-to-text dictation",
    "Enable collaborative documentation",
    "Maintain version history"
  ]
}
```

### Test 4: List All Available Patterns

**Status**: ✅ Success

#### Input Parameters

```json
{
  "pattern_type": null,
  "include_examples": false,
  "include_compliance": false
}
```

#### Output

```json
{
  "available_patterns": [
    {
      "name": "patient_registration",
      "display_name": "Patient Registration",
      "category": "patient_management",
      "description": "Complete workflow for registering new patients",
      "complexity": "medium",
      "typical_duration": "15-20 minutes"
    },
    {
      "name": "appointment_scheduling",
      "display_name": "Appointment Scheduling",
      "category": "scheduling",
      "description": "Schedule and manage patient appointments",
      "complexity": "medium",
      "typical_duration": "5-10 minutes"
    },
    {
      "name": "clinical_documentation",
      "display_name": "Clinical Documentation",
      "category": "clinical",
      "description": "Create and manage clinical notes",
      "complexity": "high",
      "typical_duration": "10-30 minutes"
    },
    {
      "name": "billing_workflow",
      "display_name": "Billing and Claims",
      "category": "financial",
      "description": "Process billing and insurance claims",
      "complexity": "high",
      "typical_duration": "20-30 minutes"
    },
    {
      "name": "prescription_management",
      "display_name": "Prescription Management",
      "category": "clinical",
      "description": "Create and manage prescriptions",
      "complexity": "medium",
      "typical_duration": "5-10 minutes"
    },
    {
      "name": "lab_results",
      "display_name": "Lab Results Management",
      "category": "clinical",
      "description": "Order labs and process results",
      "complexity": "medium",
      "typical_duration": "10-15 minutes"
    },
    {
      "name": "referral_management",
      "display_name": "Referral Management",
      "category": "care_coordination",
      "description": "Create and track patient referrals",
      "complexity": "medium",
      "typical_duration": "10-15 minutes"
    },
    {
      "name": "telehealth",
      "display_name": "Telehealth Visits",
      "category": "virtual_care",
      "description": "Conduct virtual appointments",
      "complexity": "medium",
      "typical_duration": "30-60 minutes"
    },
    {
      "name": "patient_portal",
      "display_name": "Patient Portal Access",
      "category": "patient_engagement",
      "description": "Enable patient self-service features",
      "complexity": "low",
      "typical_duration": "5-10 minutes"
    },
    {
      "name": "care_team_collaboration",
      "display_name": "Care Team Collaboration",
      "category": "care_coordination",
      "description": "Coordinate care among multiple providers",
      "complexity": "high",
      "typical_duration": "ongoing"
    }
  ],
  "categories": {
    "patient_management": {
      "name": "Patient Management",
      "description": "Patterns for managing patient records and demographics",
      "pattern_count": 1
    },
    "scheduling": {
      "name": "Scheduling",
      "description": "Appointment and calendar management patterns",
      "pattern_count": 1
    },
    "clinical": {
      "name": "Clinical",
      "description": "Clinical documentation and treatment patterns",
      "pattern_count": 3
    },
    "financial": {
      "name": "Financial",
      "description": "Billing, claims, and payment patterns",
      "pattern_count": 1
    },
    "care_coordination": {
      "name": "Care Coordination",
      "description": "Patterns for coordinating care across providers",
      "pattern_count": 2
    },
    "virtual_care": {
      "name": "Virtual Care",
      "description": "Telehealth and remote care patterns",
      "pattern_count": 1
    },
    "patient_engagement": {
      "name": "Patient Engagement",
      "description": "Patient portal and self-service patterns",
      "pattern_count": 1
    }
  },
  "total_patterns": 10,
  "implementation_notes": [
    "Each pattern includes step-by-step implementation guides",
    "Code examples available in JavaScript, Python, and cURL",
    "All patterns include HIPAA compliance considerations",
    "FHIR mappings available for interoperability"
  ]
}
```

## Key Features Demonstrated

### 1. **Comprehensive Workflow Patterns**
- Step-by-step implementation guides
- Required and optional fields for each step
- Validation rules and requirements
- Success criteria and checkpoints

### 2. **Code Examples**
- Working code in multiple languages (JavaScript, Python)
- Complete flow implementations
- Error handling examples
- Best practices demonstrated

### 3. **Compliance Integration**
- HIPAA requirements built into workflows
- HITECH and Medicare considerations
- Audit and security requirements
- Data retention policies

### 4. **FHIR Compatibility**
- Resource mappings for interoperability
- Field-level FHIR path mappings
- Standard terminology usage
- HL7 compliance guidance

### 5. **Healthcare-Specific Features**
- Medical coding (ICD-10, CPT)
- Clinical documentation standards
- Insurance verification workflows
- Consent management

## Common Use Cases

1. **New System Implementation**: Use patterns as blueprints for building features
2. **Integration Projects**: Follow patterns for consistent implementations
3. **Compliance Audits**: Reference patterns for regulatory requirements
4. **Developer Training**: Learn healthcare workflows and best practices
5. **API Migration**: Map existing workflows to Healthie API

## Best Practices

1. **Follow patterns closely**: They encode healthcare domain expertise
2. **Customize for your needs**: Patterns are starting points, not rigid rules
3. **Maintain compliance**: Always consider regulatory requirements
4. **Test thoroughly**: Healthcare workflows have edge cases
5. **Document variations**: Record any deviations from standard patterns
6. **Update regularly**: Healthcare regulations and standards evolve