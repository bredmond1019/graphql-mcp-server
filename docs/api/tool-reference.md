# Tool Reference

Complete API reference for all 11 tools in the Healthie MCP Server.

## 🔍 Schema Tools

### `search_schema`

**Purpose:** Search the GraphQL schema for types, fields, queries, or mutations.

**Parameters:**
- `query` (string, required): Search query (supports regex)
- `type_filter` (string, optional): Filter by type (`query`, `mutation`, `type`, `input`, `enum`, `interface`, `union`, `scalar`, `any`)
- `context_lines` (integer, optional): Number of context lines around matches (default: 3)

**Returns:** `SchemaSearchResult`
```json
{
  "matches": [
    {
      "line_number": 42,
      "content": ">>> type Patient {\n    id: ID!\n    firstName: String",
      "match_type": "type", 
      "location": "Patient"
    }
  ],
  "total_matches": 1,
  "search_query": "patient",
  "type_filter": "type"
}
```

**Example:**
```bash
search_schema query="patient" type_filter="type" context_lines=2
```

---

### `introspect_type`

**Purpose:** Get detailed information about a specific GraphQL type.

**Parameters:**
- `type_name` (string, required): Name of the type to introspect

**Returns:** `TypeIntrospectionResult`
```json
{
  "type_name": "Patient",
  "kind": "OBJECT",
  "description": "Patient information",
  "fields": [
    {
      "name": "id",
      "type": "ID!",
      "description": "Unique identifier",
      "is_deprecated": false
    }
  ],
  "interfaces": [],
  "possible_types": []
}
```

**Example:**
```bash
introspect_type type_name="Patient"
```

---

## 🏥 Healthcare Tools

### `healthcare_patterns`

**Purpose:** Find healthcare-specific patterns and FHIR mappings.

**Parameters:**
- `category` (string, optional): Pattern category (`patient_workflows`, `fhir_resources`, `billing_patterns`, `compliance`)

**Returns:** `HealthcarePatternsResult`
```json
{
  "patterns": [
    {
      "name": "Patient Demographics",
      "category": "patient_workflows",
      "fhir_mapping": "Patient",
      "healthie_types": ["Patient", "PatientProfile"],
      "description": "Standard patient demographic information"
    }
  ],
  "total_patterns": 1,
  "categories_available": ["patient_workflows", "fhir_resources"]
}
```

**Example:**
```bash
healthcare_patterns category="patient_workflows"
```

---

## 🚀 Developer Tools

### `query_templates`

**Purpose:** Get pre-built GraphQL queries and mutations.

**Parameters:**
- `workflow` (string, optional): Workflow filter (`patient_management`, `appointments`, `clinical_data`, `billing`)
- `include_variables` (boolean, optional): Include example variables (default: true)

**Returns:** `QueryTemplatesResult`
```json
{
  "templates": [
    {
      "name": "Create Patient",
      "description": "Register a new patient",
      "category": "patient_management",
      "query": "mutation CreatePatient($input: CreatePatientInput!) { ... }",
      "variables": {"input": {"firstName": "John"}},
      "required_variables": ["input.firstName", "input.lastName"],
      "optional_variables": ["input.phoneNumber"],
      "notes": "Requires patient consent"
    }
  ],
  "total_count": 1
}
```

**Example:**
```bash
query_templates workflow="patient_management" include_variables=true
```

---

### `code_examples`

**Purpose:** Get implementation examples in different programming languages.

**Parameters:**
- `category` (string, optional): Example category (`patient_management`, `appointments`, `clinical_data`, `billing`)
- `language` (string, optional): Programming language (`javascript`, `python`, `curl`)

**Returns:** `CodeExamplesResult`
```json
{
  "examples": [
    {
      "title": "Patient Registration with Apollo Client",
      "category": "patient_management",
      "language": "javascript",
      "code": "import { gql, useMutation } from '@apollo/client';...",
      "description": "Complete patient registration form",
      "dependencies": ["@apollo/client", "react"],
      "setup_notes": "Requires Apollo Client configuration"
    }
  ],
  "total_examples": 1
}
```

**Example:**
```bash
code_examples category="patient_management" language="javascript"
```

---

### `workflow_sequences`

**Purpose:** Get multi-step workflow guidance.

**Parameters:**
- `category` (string, optional): Workflow category (`patient_intake`, `appointment_booking`, `clinical_documentation`)

**Returns:** `WorkflowSequencesResult`
```json
{
  "workflows": [
    {
      "name": "Patient Intake Process",
      "category": "patient_intake",
      "steps": [
        {
          "step_number": 1,
          "name": "Verify Identity",
          "description": "Check patient exists or create new",
          "queries": ["searchPatients", "createPatient"],
          "validation_required": ["email", "dateOfBirth"]
        }
      ],
      "estimated_duration": "5-10 minutes"
    }
  ]
}
```

**Example:**
```bash
workflow_sequences category="patient_intake"
```

---

### `field_relationships`

**Purpose:** Understand how GraphQL types connect to each other.

**Parameters:**
- `source_type` (string, optional): Starting type name
- `target_type` (string, optional): Target type name

**Returns:** `FieldRelationshipsResult`
```json
{
  "relationships": [
    {
      "source_type": "Patient",
      "target_type": "Appointment",
      "relationship_type": "one_to_many",
      "field_path": "appointments",
      "description": "Patient can have multiple appointments"
    }
  ],
  "total_relationships": 1
}
```

**Example:**
```bash
field_relationships source_type="Patient" target_type="Appointment"
```

---

### `input_validation`

**Purpose:** Get validation rules and patterns for healthcare data.

**Parameters:**
- `field_type` (string, optional): Field type (`contact_information`, `medical_identifiers`, `date_fields`, `healthcare_data`)

**Returns:** `InputValidationResult`
```json
{
  "validation_rules": [
    {
      "field_name": "email",
      "pattern": "^[^@]+@[^@]+\\.[^@]+$",
      "required": true,
      "description": "Valid email address",
      "example": "patient@example.com",
      "error_message": "Please enter a valid email address"
    }
  ],
  "field_type": "contact_information"
}
```

**Example:**
```bash
input_validation field_type="contact_information"
```

---

### `error_decoder`

**Purpose:** Understand and resolve API errors.

**Parameters:**
- `error_message` (string, optional): Specific error message to decode
- `error_type` (string, optional): Error category (`authentication`, `validation`, `graphql_validation`)

**Returns:** `ErrorDecoderResult`
```json
{
  "error_explanations": [
    {
      "error_pattern": "Email already exists",
      "explanation": "A patient with this email is already registered",
      "common_causes": ["Duplicate registration", "Case sensitivity"],
      "solutions": ["Search for existing patient", "Use different email"],
      "code_examples": ["searchPatients(criteria: { email: 'existing@email.com' })"]
    }
  ]
}
```

**Example:**
```bash
error_decoder error_message="Validation failed: Email already exists"
```

---

### `performance_analyzer`

**Purpose:** Analyze and optimize query performance.

**Parameters:**
- `query` (string, optional): GraphQL query to analyze
- `category` (string, optional): Analysis category (`best_practices`, `healthcare_queries`)

**Returns:** `PerformanceAnalysisResult`
```json
{
  "analysis": {
    "complexity_score": 15,
    "depth": 3,
    "field_count": 5,
    "estimated_cost": "medium"
  },
  "recommendations": [
    "Consider using pagination for large result sets",
    "Add field limits to reduce payload size"
  ],
  "optimizations": [
    {
      "issue": "Deep nesting detected",
      "suggestion": "Break into multiple queries",
      "example": "query GetPatient { patient(id: $id) { id name } }"
    }
  ]
}
```

**Example:**
```bash
performance_analyzer query="{ patients { appointments { provider { organization } } } }"
```

---

### `field_usage`

**Purpose:** Get field usage recommendations for different contexts.

**Parameters:**
- `type_name` (string, required): GraphQL type name
- `context` (string, optional): Usage context (`dashboard`, `list_view`, `form`, `api_response`)

**Returns:** `FieldUsageResult`
```json
{
  "recommended_fields": [
    {
      "field_name": "id",
      "importance": "required",
      "description": "Always include for object identification",
      "performance_impact": "minimal"
    },
    {
      "field_name": "firstName",
      "importance": "recommended",
      "description": "Essential for patient identification",
      "performance_impact": "minimal"
    }
  ],
  "context": "dashboard",
  "performance_notes": ["Avoid deeply nested fields in list views"]
}
```

**Example:**
```bash
field_usage type_name="Patient" context="dashboard"
```

---

## 📚 Response Format Standards

### Common Response Fields

All tool responses follow these patterns:

**Success Response:**
```json
{
  "data": { /* tool-specific data */ },
  "metadata": {
    "tool_name": "search_schema",
    "execution_time_ms": 150,
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

**Error Response:**
```json
{
  "error": {
    "type": "ValidationError",
    "message": "Invalid parameter: type_filter must be one of...",
    "details": {
      "parameter": "type_filter",
      "provided_value": "invalid_type",
      "valid_values": ["query", "mutation", "type"]
    }
  }
}
```

### Healthcare-Specific Fields

Many responses include healthcare context:

```json
{
  "healthcare_context": {
    "fhir_mapping": "Patient",
    "compliance_notes": ["HIPAA: Minimum necessary principle applies"],
    "medical_terminology": ["Uses SNOMED CT codes"]
  }
}
```

## 🔧 Tool Categories

### Core Schema Tools
- `search_schema` - Find anything in the schema
- `introspect_type` - Deep dive into specific types
- `healthcare_patterns` - Healthcare-specific schema patterns

### Developer Productivity Tools  
- `query_templates` - Ready-to-use queries
- `code_examples` - Implementation examples
- `workflow_sequences` - Multi-step processes
- `field_relationships` - Type connections

### Validation & Debugging Tools
- `input_validation` - Data validation rules
- `error_decoder` - Error resolution
- `performance_analyzer` - Query optimization
- `field_usage` - Field selection guidance

## 💡 Usage Patterns

### Discovery Workflow
1. `healthcare_patterns` - Understand domain patterns
2. `search_schema` - Find relevant types
3. `introspect_type` - Understand type details
4. `field_relationships` - Map connections

### Implementation Workflow  
1. `query_templates` - Get base queries
2. `field_usage` - Choose optimal fields
3. `input_validation` - Validate data
4. `code_examples` - Implement in your language

### Debugging Workflow
1. `error_decoder` - Understand errors
2. `performance_analyzer` - Optimize queries
3. `input_validation` - Check data format
4. `field_relationships` - Verify connections

Each tool is designed to work independently but provides maximum value when used together in these common workflows.