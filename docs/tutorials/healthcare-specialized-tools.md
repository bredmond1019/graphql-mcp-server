# Healthcare Specialized MCP Tools

Learn how to use the 3 healthcare-specialized tools that provide domain-specific guidance for building compliant, efficient healthcare applications.

## Overview

These tools complement the 5 primary development tools with healthcare expertise:

1. **compliance_checker** - Validate HIPAA compliance and identify PHI exposure risks
2. **build_workflow_sequence** - Get step-by-step guidance for healthcare workflows
3. **field_relationships** - Understand how healthcare data models connect

## Compliance Checker Tool

The most critical tool for healthcare developers - prevents costly compliance violations.

### Why It Matters

- HIPAA violations can cost $100 - $2M per incident
- State regulations add additional requirements
- PHI exposure risks are not always obvious
- Audit requirements are complex

### Basic Usage

```python
# Check a query for compliance issues
result = compliance_checker(
    query="""
    query GetPatient($id: ID!) {
        patient(id: $id) {
            id
            firstName
            lastName
            ssn              # Violation!
            dateOfBirth      # PHI risk
            medicalRecordNumber  # PHI risk
        }
    }
    """,
    frameworks=["hipaa"],
    check_phi_exposure=True,
    check_audit_requirements=True
)

# Result shows:
# - Overall compliance: VIOLATION
# - 4 violations found
# - 3 PHI exposure risks
# - 18 recommendations provided
```

### Real-World Examples

#### Example 1: Checking Mutations for Audit Requirements

```python
# Mutations require stricter controls
result = compliance_checker(
    query="""
    mutation UpdatePatient($id: ID!, $input: UpdatePatientInput!) {
        updatePatient(id: $id, input: $input) {
            patient {
                id
                email
                phoneNumber
            }
        }
    }
    """,
    operation_type="mutation",
    check_audit_requirements=True,
    data_handling_context="Updating patient contact information"
)

# Returns 6 audit requirements:
# - Access logging required
# - User authorization verification
# - Data integrity checks
# - Encryption requirements
# - Retention policies
# - Breach detection mechanisms
```

#### Example 2: State-Specific Compliance

```python
# California has additional privacy laws
result = compliance_checker(
    query=patient_query,
    frameworks=["hipaa"],
    state="CA",
    check_phi_exposure=True
)

# Returns:
# - 2 California-specific regulations
# - CCPA requirements
# - Additional consent requirements
```

### Best Practices

1. **Always check mutations** - They modify data and need audit trails
2. **Include state parameter** - Many states have additional requirements
3. **Review all recommendations** - Even if compliant, improvements suggested
4. **Check before production** - Catch issues early

## Build Workflow Sequence Tool

Provides step-by-step guidance for complex healthcare operations.

### Why It Matters

- Healthcare workflows have specific sequences
- Missing steps can cause compliance issues
- Helps new developers understand healthcare processes
- Prevents common implementation mistakes

### Basic Usage

```python
# Get patient onboarding workflow
workflows = build_workflow_sequence(
    workflow_name="patient_onboarding"
)

# Returns complete workflow with:
# - 4 steps with descriptions
# - Required inputs for each step
# - Expected outputs
# - GraphQL examples
# - Dependencies between steps
```

### Real-World Examples

#### Example 1: Appointment Booking Workflow

```python
# Get appointment booking sequence
result = build_workflow_sequence(
    workflow_name="appointment"
)

# Returns 3-step workflow:
# 1. Check provider availability
#    - Required: providerId, startDate, endDate
#    - Returns: availableSlots
#
# 2. Create appointment
#    - Required: patientId, providerId, startTime, endTime
#    - Returns: appointment.id, status
#
# 3. Send confirmation
#    - Required: appointmentId
#    - Returns: confirmation.sent
```

#### Example 2: Filter by Category

```python
# Get all patient management workflows
workflows = build_workflow_sequence(
    category="patient_management"
)

# Returns workflows for:
# - Patient registration
# - Insurance verification
# - Document collection
# - Initial assessment
```

### Workflow Structure

Each workflow includes:

```python
{
    "workflow_name": "Complete Patient Onboarding",
    "category": "patient_management",
    "description": "Full patient registration process",
    "total_steps": 4,
    "estimated_duration": "5-10 minutes",
    "prerequisites": [
        "Valid API key",
        "Organization setup"
    ],
    "steps": [
        {
            "step_number": 1,
            "operation_type": "mutation",
            "operation_name": "createClient",
            "description": "Create patient record",
            "required_inputs": ["firstName", "lastName", "email"],
            "expected_outputs": ["client.id"],
            "graphql_example": "...",
            "notes": "Save client.id for next steps"
        }
    ]
}
```

### Best Practices

1. **Follow step order** - Dependencies matter
2. **Save outputs** - Later steps need earlier IDs
3. **Check prerequisites** - Ensure setup is complete
4. **Use provided examples** - They're tested and working

## Field Relationships Tool

Maps connections between GraphQL fields to build efficient queries.

### Why It Matters

- Healthcare data is highly interconnected
- Prevents N+1 query problems
- Helps understand data model
- Optimizes query performance

### Basic Usage

```python
# Explore patient relationships
relationships = field_relationships(
    field_name="patient",
    max_depth=2,
    include_scalars=False
)

# When schema is available, returns:
# - Related types (Appointment, Provider, Insurance)
# - Connection paths
# - Required vs optional relationships
# - Healthcare-specific categorization
```

### Expected Features (When Fully Functional)

#### Healthcare Field Categorization

The tool categorizes relationships by healthcare context:

- **Patient data**: Demographics, medical history
- **Clinical data**: Notes, assessments, vitals
- **Administrative**: Scheduling, billing, insurance
- **Provider data**: Credentials, specialties, availability

#### Relationship Mapping

```python
# Example output structure
{
    "source_field": "patient",
    "related_fields": [
        {
            "field_name": "appointments",
            "field_type": "[Appointment]",
            "path": "patient.appointments",
            "is_list": true,
            "description": "Patient's appointments"
        },
        {
            "field_name": "primaryProvider",
            "field_type": "Provider",
            "path": "patient.primaryProvider",
            "is_required": false,
            "description": "Primary care provider"
        }
    ],
    "suggestions": [
        "Include demographic fields: firstName, lastName, dateOfBirth",
        "Consider pagination for list fields: appointments, documents"
    ]
}
```

### Current Limitations

- Requires loaded GraphQL schema
- Returns empty results without schema
- Has healthcare logic ready but needs data

## Using Tools Together

### Compliant Patient Query Building

```python
# 1. Search for patient fields
fields = search_schema("patient", type_filter="type")

# 2. Check relationships (when available)
relationships = field_relationships("patient", max_depth=2)

# 3. Build query
query = """
query GetPatient($id: ID!) {
    patient(id: $id) {
        id
        firstName
        lastName
        # Include related data
    }
}
"""

# 4. Validate compliance
compliance = compliance_checker(
    query=query,
    frameworks=["hipaa"],
    check_phi_exposure=True
)

# 5. Fix any violations before using
```

### Implementing Healthcare Workflows

```python
# 1. Get workflow guidance
workflow = build_workflow_sequence("patient_onboarding")

# 2. For each step, generate code
for step in workflow.steps:
    code = code_examples(
        operation=step.operation_name,
        language="javascript"
    )
    
# 3. Check compliance for each mutation
for step in workflow.steps:
    if step.operation_type == "mutation":
        compliance_checker(
            query=step.graphql_example,
            operation_type="mutation"
        )
```

## Key Takeaways

### compliance_checker
- **Always use** for any PHI-handling queries
- **Essential** for mutations that modify data
- **Provides** specific regulatory references
- **Saves** from costly violations

### build_workflow_sequence
- **Guides** multi-step implementations
- **Prevents** missing critical steps
- **Includes** working GraphQL examples
- **Follows** healthcare best practices

### field_relationships
- **Maps** data connections (when schema available)
- **Optimizes** query efficiency
- **Categorizes** by healthcare context
- **Suggests** query improvements

## Next Steps

1. **Always validate** - Run compliance_checker on all queries
2. **Follow workflows** - Use build_workflow_sequence for complex operations
3. **Understand relationships** - Use field_relationships when planning queries
4. **Combine with primary tools** - Use all 8 tools together for best results

These healthcare-specialized tools transform the MCP server from a development aid into a compliance and best practices enforcement system, essential for any healthcare API integration.