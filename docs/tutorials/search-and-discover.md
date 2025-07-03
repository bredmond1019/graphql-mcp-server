# Search and Discover with MCP Tools

Master the art of finding exactly what you need in the Healthie GraphQL schema using the powerful `search_schema` tool.

## Overview

The `search_schema` tool searches through 925,260 characters (36,023 lines) of GraphQL schema instantly, helping you find types, fields, mutations, and queries with surgical precision.

## Why Schema Search Matters

Without proper search tools, developers often:
- Spend hours reading through schema documentation
- Make incorrect assumptions about field names
- Miss important related types and fields
- Write queries that fail due to typos or wrong field names

The `search_schema` tool eliminates these problems entirely.

## Basic Usage

### Simple Search

Find anything related to a term:

```python
# Search for patient-related items
result = search_schema(search_term="patient")

# Result includes:
# - Types: Patient, PatientDemographics, PatientInsurance
# - Fields: patient_id, patient_name, patient_email
# - Mutations: createPatient, updatePatient, archivePatient
# - Queries: patient, patients, patientSearch
```

### Filtered Search

Target specific schema elements:

```python
# Find only patient-related types
types = search_schema(search_term="patient", type_filter="type")

# Find only mutations
mutations = search_schema(search_term="appointment", type_filter="mutation")

# Find only queries
queries = search_schema(search_term="provider", type_filter="query")

# Find only fields
fields = search_schema(search_term="email", type_filter="field")
```

## Real-World Search Examples

### Example 1: Finding Patient Operations

**Scenario**: You need to implement patient management features.

```python
# Step 1: Find all patient types
patient_types = search_schema(search_term="patient", type_filter="type")
# Found: Patient, PatientDemographics, PatientInsurance, PatientContact

# Step 2: Find patient mutations
patient_mutations = search_schema(search_term="patient", type_filter="mutation")
# Found: createPatient, updatePatient, archivePatient, bulkUpdatePatients

# Step 3: Find patient queries
patient_queries = search_schema(search_term="patient", type_filter="query")
# Found: patient, patients, patientSearch, patientByEmail
```

**Result**: In 3 searches, you have a complete map of patient operations.

### Example 2: Implementing Insurance Features

**Scenario**: Building insurance verification and claims processing.

```python
# Comprehensive insurance search
insurance_results = search_schema(search_term="insurance")

# Returns 373 matches including:
# Types:
#   - InsurancePlan
#   - InsurancePolicy  
#   - InsuranceClaim
#   - InsuranceVerification
#
# Fields:
#   - insurance_member_id
#   - insurance_group_number
#   - insurance_copay
#   - insurance_deductible
#
# Mutations:
#   - createInsurancePolicy
#   - verifyInsurance
#   - submitInsuranceClaim
#   - updateInsurancePolicy
```

### Example 3: Appointment System Discovery

**Scenario**: Building a complete appointment booking system.

```python
# Find appointment mutations
apt_mutations = search_schema(
    search_term="appointment", 
    type_filter="mutation"
)
# Found 96 appointment-related mutations!

# Key mutations discovered:
# - createAppointment
# - updateAppointment
# - cancelAppointment
# - rescheduleAppointment
# - createRecurringAppointment
# - bulkCreateAppointments
# - confirmAppointment
# - checkInAppointment
```

## Advanced Search Patterns

### 1. Partial Term Matching

Use partial terms for broader results:

```python
# Instead of "appointment"
search_schema(search_term="appoint")
# Also finds: appointing, appointed, appointments

# Instead of "medication"
search_schema(search_term="medic")
# Also finds: medical, medicine, medications, medicate
```

### 2. Discovering Field Relationships

Find related fields across types:

```python
# Find all ID fields
id_fields = search_schema(search_term="_id", type_filter="field")
# Reveals: patient_id, provider_id, appointment_id, organization_id

# Find all timestamp fields
timestamps = search_schema(search_term="_at", type_filter="field")
# Reveals: created_at, updated_at, deleted_at, signed_at
```

### 3. Healthcare Pattern Discovery

Find healthcare-specific patterns:

```python
# Medical identifiers
search_schema(search_term="npi")  # National Provider Identifier
search_schema(search_term="dea")  # DEA number
search_schema(search_term="tin")  # Tax ID

# Clinical terms
search_schema(search_term="diagnosis")
search_schema(search_term="icd")     # ICD codes
search_schema(search_term="cpt")     # CPT codes
search_schema(search_term="vitals")  # Vital signs
```

### 4. Finding Enum Values

Discover valid values for enums:

```python
# Find status-related enums
status_search = search_schema(search_term="status")

# Reveals enums like:
# - AppointmentStatus: scheduled, confirmed, completed, cancelled
# - ClaimStatus: pending, submitted, approved, denied
# - TaskStatus: open, in_progress, completed, archived
```

## Search Strategies

### Strategy 1: Top-Down Discovery

Start broad, then narrow:

```python
# 1. Start with domain
billing_all = search_schema("billing")
# 300+ results

# 2. Focus on types
billing_types = search_schema("billing", type_filter="type")
# 15 types

# 3. Explore specific type
billing_item = introspect_type("BillingItem")
# All fields and relationships
```

### Strategy 2: Bottom-Up Construction

Start specific, then expand:

```python
# 1. Find specific operation
create_claim = search_schema("createInsuranceClaim", type_filter="mutation")

# 2. Find input type
claim_input = search_schema("InsuranceClaimInput", type_filter="type")

# 3. Find related types
claim_types = search_schema("Claim", type_filter="type")
```

### Strategy 3: Relationship Mapping

Trace connections between types:

```python
# 1. Start with core type
search_schema("Patient", type_filter="type")

# 2. Find foreign keys
search_schema("patient_id", type_filter="field")
# Shows: Appointments, Claims, Documents with patient_id

# 3. Map relationships
search_schema("PatientProvider", type_filter="type")
search_schema("PatientInsurance", type_filter="type")
```

## Common Search Scenarios

### Finding Authentication Fields

```python
# Authentication and authorization
auth_search = search_schema("auth")

# Finds:
# - authenticateUser mutation
# - authorization field
# - auth_token type
# - authenticated_at timestamp
```

### Discovering Webhooks

```python
# Webhook configuration
webhook_search = search_schema("webhook")

# Finds:
# - WebhookConfig type
# - createWebhook mutation
# - webhook_url field
# - webhook_events enum
```

### Locating File Uploads

```python
# File and document handling
file_search = search_schema("file")
document_search = search_schema("document")

# Finds:
# - FileUpload type
# - uploadDocument mutation
# - file_url field
# - document_type enum
```

## Search Tips and Tricks

### 1. Use Context Clues

GraphQL schemas often follow naming patterns:

```python
# Mutations typically start with:
search_schema("create")  # createPatient, createAppointment
search_schema("update")  # updatePatient, updateClaim
search_schema("delete")  # deleteDocument, deleteTask
search_schema("archive") # archivePatient, archiveNote
```

### 2. Look for Plurals

```python
# Singular usually = single record query
search_schema("patient", type_filter="query")    # patient(id: ID!)

# Plural usually = list query
search_schema("patients", type_filter="query")   # patients(filters: ...)
```

### 3. Check for Variations

```python
# Different naming conventions
search_schema("phone")       # phone, phoneNumber, phone_number
search_schema("dob")         # dob, dateOfBirth, date_of_birth
search_schema("mrn")         # mrn, medicalRecordNumber
```

### 4. Find Hidden Features

```python
# Bulk operations
search_schema("bulk")        # bulkCreateAppointments, bulkUpdatePatients

# Batch processing
search_schema("batch")       # batchProcessClaims, batchUpload

# Advanced features
search_schema("recurring")   # recurringAppointment, recurringPayment
```

## Interpreting Search Results

### Understanding Match Context

Each search result includes context:

```python
result = search_schema("appointment")

# Each match shows:
{
    "line_number": 1234,
    "content": "type Appointment implements Node {",
    "match_type": "type_definition",
    "context": [
        "# Previous line",
        "type Appointment implements Node {",  # <-- matched line
        "  id: ID!"
    ]
}
```

### Analyzing Match Patterns

Look for patterns in results:

```python
# High match count = core concept
patient_matches = search_schema("patient")
# 500+ matches = Patient is central to the schema

# Low match count = specialized feature
telemetry_matches = search_schema("telemetry")
# 5 matches = Telemetry is a specific feature
```

## Performance Optimization

### 1. Cache Common Searches

```python
# Cache frequently used searches
COMMON_SEARCHES = {
    "patient_ops": search_schema("patient", type_filter="mutation"),
    "appointment_types": search_schema("appointment", type_filter="type"),
    "billing_queries": search_schema("billing", type_filter="query")
}
```

### 2. Use Specific Filters

```python
# Faster: Filtered search
mutations = search_schema("create", type_filter="mutation")

# Slower: Unfiltered search then filter
all_results = search_schema("create")
mutations = [r for r in all_results if r.match_type == "mutation"]
```

### 3. Combine Searches Intelligently

```python
# Find complete feature set efficiently
def discover_feature(domain):
    return {
        "types": search_schema(domain, type_filter="type"),
        "queries": search_schema(domain, type_filter="query"),
        "mutations": search_schema(domain, type_filter="mutation"),
        "core_fields": search_schema(f"{domain}_id", type_filter="field")
    }

insurance_feature = discover_feature("insurance")
```

## Next Steps

Now that you've mastered schema searching:

1. **[Query Generation](./query-generation.md)** - Turn search results into working queries
2. **[Type Exploration](./type-exploration.md)** - Deep dive into discovered types
3. **[Using MCP Tools](./using-mcp-tools.md)** - Back to overview

Remember: Effective searching saves hours of development time. Always search before you code!