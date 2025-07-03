# Tool 6: compliance_checker - Detailed Test Results

*Generated on: 2025-07-02 23:42:56*

## Tool Overview

The Compliance Checker tool validates GraphQL queries against healthcare regulatory frameworks (HIPAA, HITECH, GDPR) to ensure proper PHI handling and audit compliance.
## How to Use This Tool

### Python Usage

```python
from healthie_mcp.tools.compliance_checker import ComplianceCheckerTool, ComplianceCheckerInput
from healthie_mcp.models.compliance_checker import RegulatoryFramework
from healthie_mcp.schema_manager import SchemaManager

# Initialize the tool
schema_manager = SchemaManager(api_endpoint='https://api.gethealthie.com/graphql')
tool = ComplianceCheckerTool(schema_manager)

# Check compliance
input_data = ComplianceCheckerInput(
    query='query { patient(id: "123") { firstName ssn } }',
    operation_type='query',
    frameworks=[RegulatoryFramework.HIPAA],
    check_phi_exposure=True,
    check_audit_requirements=True,
    data_handling_context='Provider viewing patient record'
)
result = tool.execute(input_data)
```

### Parameters

- **query** (required): The GraphQL query to check
- **operation_type** (required): Either "query" or "mutation"
- **frameworks** (required): List of frameworks (HIPAA, HITECH, GDPR)
- **check_phi_exposure** (optional): Check for PHI exposure (default: True)
- **check_audit_requirements** (optional): Check audit needs (default: True)
- **data_handling_context** (optional): Context description

## Test Summary

- **Total tests**: 2
- **Successful**: 2
- **Failed**: 0
- **Success rate**: 100.0%

## Detailed Test Results

### Test 1: HIPAA patient query compliance

**Status**: ✅ Success

#### Input Parameters

```json
{
  "query": "query GetPatientInfo($id: ID!) {\n    patient(id: $id) {\n        id\n        firstName\n        lastName\n        dateOfBirth\n        ssn\n        email\n        phoneNumber\n        diagnoses {\n            icdCode\n            description\n        }\n    }\n}",
  "operation_type": "query",
  "frameworks": [
    "HIPAA"
  ],
  "check_phi_exposure": true,
  "check_audit_requirements": true,
  "data_handling_context": "Provider viewing patient record"
}
```

#### Output

```json
{
  "overall_compliance": "PARTIAL",
  "summary": "Query exposes sensitive PHI fields. Implement proper access controls and audit logging.",
  "violations": [
    {
      "severity": "HIGH",
      "field": "ssn",
      "message": "Social Security Number is highly sensitive PHI",
      "recommendation": "Only query SSN when absolutely necessary and ensure proper encryption",
      "regulation_reference": "HIPAA \u00a7164.514(b)"
    }
  ],
  "phi_risks": [
    {
      "category": "Identifiers",
      "fields": [
        "ssn",
        "dateOfBirth"
      ],
      "risk_level": "HIGH",
      "description": "Query includes direct identifiers that could be used to identify the patient",
      "mitigation": "Implement field-level access controls and consider data minimization"
    },
    {
      "category": "Medical Information",
      "fields": [
        "diagnoses"
      ],
      "risk_level": "MEDIUM",
      "description": "Medical diagnoses are sensitive health information",
      "mitigation": "Ensure access is limited to authorized healthcare providers"
    }
  ],
  "audit_requirements": [
    {
      "requirement": "Access Logging",
      "met": false,
      "description": "Log all access to patient PHI including user, timestamp, and data accessed",
      "implementation_guide": "Implement middleware to capture GraphQL query details and user context"
    },
    {
      "requirement": "User Authentication",
      "met": true,
      "description": "Verify user identity before granting access",
      "implementation_guide": "Current authentication mechanism appears adequate"
    }
  ],
  "recommendations": [
    "Consider removing SSN from routine queries",
    "Implement field-level permissions based on user role",
    "Add audit logging for all PHI access",
    "Use data minimization - only query necessary fields",
    "Implement automatic session timeout for PHI access"
  ]
}
```


---

### Test 2: Multi-framework mutation compliance

**Status**: ✅ Success

#### Input Parameters

```json
{
  "query": "mutation UpdatePatientRecord($id: ID!, $input: UpdatePatientInput!) {\n    updatePatient(id: $id, input: $input) {\n        patient {\n            id\n            medicalRecordNumber\n            lastUpdated\n        }\n    }\n}",
  "operation_type": "mutation",
  "frameworks": [
    "HIPAA",
    "HITECH"
  ],
  "check_phi_exposure": true,
  "check_audit_requirements": true,
  "data_handling_context": "Updating patient medical information"
}
```

#### Output

```json
{
  "overall_compliance": "COMPLIANT",
  "summary": "Mutation follows best practices for PHI updates with minimal data exposure",
  "violations": [],
  "phi_risks": [
    {
      "category": "Identifiers",
      "fields": [
        "medicalRecordNumber"
      ],
      "risk_level": "LOW",
      "description": "Medical record number is included but is necessary for record identification",
      "mitigation": "Ensure MRN is not exposed in logs or error messages"
    }
  ],
  "audit_requirements": [
    {
      "requirement": "Modification Tracking",
      "met": true,
      "description": "Track all modifications to patient records",
      "implementation_guide": "lastUpdated field provides timestamp tracking"
    },
    {
      "requirement": "Data Integrity",
      "met": true,
      "description": "Ensure data modifications are tracked and reversible",
      "implementation_guide": "Implement versioning or audit tables for patient data changes"
    }
  ],
  "recommendations": [
    "Log the specific fields being updated in audit trail",
    "Implement before/after comparison for sensitive field changes",
    "Consider adding user context to the mutation for audit purposes"
  ]
}
```


---

