# Complete Tool Overview

This guide provides detailed examples and use cases for all 11 tools in the Healthie MCP server. Each tool is designed to solve specific development challenges when working with Healthie's GraphQL API.

## 🔍 Schema Exploration Tools

### `search_schema` - Find Anything in the Schema

**When to use:** You know what you're looking for but don't know where it is.

**Real examples:**
```bash
# Find all patient-related types
search_schema query="patient" type_filter="type"

# Find appointment queries
search_schema query="appointment" type_filter="query" 

# Find all mutation operations
search_schema query="create|update|delete" type_filter="mutation"

# Find fields with specific patterns
search_schema query="email|phone" type_filter="field"
```

**What you get:**
- Exact line numbers in the schema
- Context lines around matches
- Type information (query/mutation/type/field)
- Location within parent types

**Pro tip:** Use regex patterns like `"create.*patient"` to find specific mutations.

---

### `introspect_type` - Deep Dive into Types

**When to use:** You found a type and want to understand it completely.

**Real examples:**
```bash
# Understand the Patient type
introspect_type type_name="Patient"

# Learn about appointment structure  
introspect_type type_name="Appointment"

# Explore input types for mutations
introspect_type type_name="CreatePatientInput"
```

**What you get:**
- All fields with descriptions
- Field types and nullability
- Interface implementations
- Enum values (if applicable)
- Deprecation warnings

**Example output structure:**
```json
{
  "type_name": "Patient",
  "kind": "OBJECT",
  "fields": [
    {
      "name": "id",
      "type": "ID!",
      "description": "Unique identifier",
      "is_deprecated": false
    },
    {
      "name": "email", 
      "type": "String",
      "description": "Patient email address",
      "is_deprecated": false
    }
  ]
}
```

---

## 🏥 Healthcare-Specific Tools

### `healthcare_patterns` - Find Healthcare Workflows

**When to use:** You're building healthcare features and want to follow best practices.

**Real examples:**
```bash
# Find FHIR-compatible patterns
healthcare_patterns category="fhir_resources"

# Explore patient management workflows
healthcare_patterns category="patient_workflows"

# Discover billing and insurance patterns
healthcare_patterns category="billing_patterns"

# Find compliance-related fields
healthcare_patterns category="compliance"
```

**What you get:**
- FHIR resource mappings
- Healthcare workflow patterns
- Compliance considerations
- Medical terminology guidance

**Example use case - Patient Demographics:**
```json
{
  "pattern": "Patient Demographics",
  "fhir_mapping": "Patient",
  "healthie_types": ["Patient", "PatientProfile"],
  "required_fields": ["firstName", "lastName", "dateOfBirth"],
  "compliance_notes": [
    "HIPAA: Minimum necessary principle applies",
    "Consider consent for optional fields"
  ]
}
```

---

## 🚀 Developer Productivity Tools

### `query_templates` - Ready-to-Use Queries

**When to use:** You need working GraphQL queries quickly.

**Real examples:**
```bash
# Get all patient management queries
query_templates workflow="patient_management"

# Find appointment-related templates
query_templates workflow="appointments"

# Get billing and payment queries
query_templates workflow="billing"

# Get all templates with examples
query_templates include_variables=true
```

**What you get:**
- Complete GraphQL queries and mutations
- Example variables
- Required vs optional parameters
- Usage notes and tips

**Example template:**
```graphql
# Create Patient Template
mutation CreatePatient($input: CreatePatientInput!) {
  createPatient(input: $input) {
    patient {
      id
      email
      firstName
      lastName
      dateOfBirth
      phoneNumber
    }
    errors
  }
}
```

**With example variables:**
```json
{
  "variables": {
    "input": {
      "email": "patient@example.com",
      "firstName": "John",
      "lastName": "Doe", 
      "dateOfBirth": "1990-01-01"
    }
  }
}
```

---

### `code_examples` - Implementation Examples

**When to use:** You have the query but need implementation code.

**Real examples:**
```bash
# JavaScript/React examples
code_examples category="patient_management" language="javascript"

# Python examples
code_examples category="appointments" language="python"

# cURL examples for testing
code_examples category="billing" language="curl"

# Get all available examples
code_examples
```

**What you get:**
- Complete code examples in your preferred language
- Authentication setup
- Error handling patterns
- Best practices

**JavaScript example:**
```javascript
// Patient Registration with Apollo Client
import { gql, useMutation } from '@apollo/client';

const CREATE_PATIENT = gql`
  mutation CreatePatient($input: CreatePatientInput!) {
    createPatient(input: $input) {
      patient { id email firstName lastName }
      errors
    }
  }
`;

function PatientRegistration() {
  const [createPatient, { loading, error }] = useMutation(CREATE_PATIENT);
  
  const handleSubmit = async (formData) => {
    try {
      const { data } = await createPatient({
        variables: { input: formData }
      });
      // Handle success
    } catch (err) {
      // Handle error
    }
  };
}
```

---

### `workflow_sequences` - Multi-Step Processes

**When to use:** You're implementing complex healthcare workflows.

**Real examples:**
```bash
# Complete patient intake process
workflow_sequences category="patient_intake"

# Appointment booking workflow
workflow_sequences category="appointment_booking"

# Clinical documentation workflow
workflow_sequences category="clinical_documentation"
```

**What you get:**
- Step-by-step workflow guidance
- Required queries for each step
- Error handling at each stage
- Best practices and tips

**Example workflow:**
```yaml
workflow: "Patient Intake Process"
steps:
  1:
    name: "Verify Patient Identity"
    queries: ["searchPatients", "getPatientByEmail"]
    validation: ["email format", "duplicate check"]
  2:
    name: "Collect Demographics" 
    queries: ["createPatient", "updatePatientProfile"]
    required_fields: ["firstName", "lastName", "dateOfBirth"]
  3:
    name: "Insurance Verification"
    queries: ["createInsuranceInfo", "verifyInsurance"]
    compliance: ["HIPAA authorization required"]
```

---

## 🔧 Development Support Tools

### `field_relationships` - Understand Connections

**When to use:** You need to understand how different types relate to each other.

**Real examples:**
```bash
# How are patients connected to appointments?
field_relationships source_type="Patient" target_type="Appointment"

# What connects to billing information?
field_relationships target_type="PaymentInfo"

# Find all relationships for a type
field_relationships source_type="Provider"
```

**What you get:**
- Direct field connections
- Relationship types (one-to-one, one-to-many)
- Nested relationship paths
- Query examples for each relationship

---

### `input_validation` - Validate Before Sending

**When to use:** You want to validate data before making API calls.

**Real examples:**
```bash
# Validate healthcare-specific fields
input_validation field_type="medical_identifiers"

# Check email and phone patterns
input_validation field_type="contact_information"

# Validate date formats
input_validation field_type="date_fields"

# Get all validation rules
input_validation
```

**What you get:**
- Regex patterns for validation
- Healthcare-specific rules (NPI, medical record numbers)
- Format examples
- Error messages

**Example validation rules:**
```json
{
  "email": {
    "pattern": "^[^@]+@[^@]+\\.[^@]+$",
    "required": true,
    "example": "patient@example.com"
  },
  "npi": {
    "pattern": "^\\d{10}$",
    "description": "National Provider Identifier",
    "example": "1234567890"
  },
  "phone": {
    "pattern": "^\\+?1?[0-9]{10}$",
    "format": "US phone number",
    "example": "+1234567890"
  }
}
```

---

### `error_decoder` - Understand and Fix Errors

**When to use:** Your API calls are failing and you need to understand why.

**Real examples:**
```bash
# Decode a specific error
error_decoder error_message="Validation failed: Email already exists"

# Get help with authentication errors
error_decoder error_type="authentication"

# Understand GraphQL errors
error_decoder error_type="graphql_validation"
```

**What you get:**
- Plain English explanation of errors
- Common causes and solutions
- Code examples for fixes
- Prevention strategies

---

### `performance_analyzer` - Optimize Your Queries

**When to use:** Your queries are slow or you want to optimize performance.

**Real examples:**
```bash
# Analyze a complex query
performance_analyzer query="{ patients { appointments { provider { organization } } } }"

# Get general performance tips
performance_analyzer category="best_practices"

# Healthcare-specific optimizations
performance_analyzer category="healthcare_queries"
```

**What you get:**
- Performance bottleneck identification
- Optimization suggestions
- Alternative query patterns
- Caching recommendations

---

### `field_usage` - Choose the Right Fields

**When to use:** You're not sure which fields to include in your queries.

**Real examples:**
```bash
# Essential patient fields for a dashboard
field_usage type_name="Patient" context="dashboard"

# Appointment fields for scheduling
field_usage type_name="Appointment" context="scheduling"

# Provider information for directories
field_usage type_name="Provider" context="directory"
```

**What you get:**
- Recommended fields for different use cases
- Performance impact of each field
- Healthcare-specific considerations
- Common patterns and anti-patterns

## 🎯 Tool Combinations for Common Tasks

### Building a Patient Dashboard
1. `healthcare_patterns category="patient_workflows"` - Understand the domain
2. `query_templates workflow="patient_management"` - Get base queries
3. `field_usage type_name="Patient" context="dashboard"` - Choose fields
4. `code_examples category="patient_management" language="javascript"` - Get implementation

### Implementing Appointment Booking
1. `workflow_sequences category="appointment_booking"` - Understand the process
2. `field_relationships source_type="Patient" target_type="Appointment"` - Understand connections
3. `input_validation field_type="date_fields"` - Validate inputs
4. `performance_analyzer category="healthcare_queries"` - Optimize

### Debugging API Issues
1. `error_decoder error_message="Your error here"` - Understand the error
2. `input_validation` - Check your data format
3. `query_templates` - Compare with working examples
4. `field_usage` - Verify field selection

Each tool is designed to work independently but they're most powerful when used together. Start with the healthcare patterns and workflow guidance, then drill down into specific implementation details with the other tools.