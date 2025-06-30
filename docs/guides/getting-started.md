# Getting Started with Healthie MCP Server

This guide will help you understand what the Healthie MCP server is, why you'd use it, and how to get started with your first queries.

## 🤔 What is this?

The Healthie MCP Server is an AI-powered development assistant that helps you work with Healthie's GraphQL API more effectively. Instead of manually browsing through documentation or guessing query structures, you can ask the AI directly:

- "Show me how to create a patient"
- "What fields are available for appointments?"
- "Help me build a query for clinical notes"
- "How do I validate a medical record number?"

## 🎯 Why would I use this?

### Before (Traditional Development)
```bash
# Manual process:
1. Open GraphQL schema documentation
2. Search through hundreds of types manually
3. Figure out field relationships
4. Write queries from scratch
5. Debug validation errors
6. Repeat for each new feature
```

### After (With MCP Server)
```bash
# AI-assisted process:
1. Ask: "How do I create a patient?"
2. Get pre-built query templates
3. See example variables and validation rules
4. Get healthcare-specific guidance
5. Build features faster with less errors
```

## 🏥 Perfect for Healthcare Apps

This server is specifically designed for healthcare applications using Healthie:

- **Patient Management Systems** - Registration, demographics, medical history
- **Appointment Scheduling** - Booking, availability, reminders
- **Clinical Documentation** - Notes, assessments, care plans
- **Billing & Insurance** - Claims, payments, authorizations
- **Provider Portals** - Credentials, schedules, patient management

## 🚀 Your First 5 Minutes

### 1. Install and Setup (2 minutes)
```bash
# Clone and setup
cd python-mcp-server
uv sync

# Set your API endpoint
export HEALTHIE_API_URL="https://staging-api.gethealthie.com/graphql"
```

### 2. Start the Server (30 seconds)
```bash
# Development mode with inspector
uv run mcp dev src/healthie_mcp/server.py:mcp

# Or install in Claude Desktop
uv run mcp install src/healthie_mcp/server.py:mcp --name "Healthie Assistant"
```

### 3. Try Your First Queries (2.5 minutes)

**Find patient-related fields:**
```
search_schema query="patient" type_filter="type"
```

**Get pre-built query templates:**
```
query_templates workflow="patient_management"
```

**Understand a specific type:**
```
introspect_type type_name="Patient"
```

**Get code examples:**
```
code_examples category="patient_management" language="javascript"
```

## 🔍 Real-World Examples

### Building a Patient Registration Form

**Ask the MCP server:**
```
query_templates workflow="patient_management"
```

**Get response with ready-to-use queries:**
```graphql
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

**Plus validation guidance:**
```json
{
  "variables": {
    "input": {
      "email": "patient@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "dateOfBirth": "1990-01-01",
      "phoneNumber": "+1234567890"
    }
  },
  "validation_notes": [
    "Email must be unique across the system",
    "Phone number should include country code",
    "Date of birth must be in YYYY-MM-DD format"
  ]
}
```

### Finding Available Appointment Slots

**Ask for appointment workflows:**
```
workflow_sequences category="appointments"
```

**Get step-by-step guidance:**
```yaml
name: "Book Patient Appointment"
steps:
  1. "Query provider availability"
  2. "Check patient eligibility" 
  3. "Create appointment"
  4. "Send confirmation"
queries:
  - name: "Get Available Slots"
    query: |
      query GetAvailability($providerId: ID!, $date: String!) {
        availabilitySlots(providerId: $providerId, date: $date) {
          startTime
          endTime
          available
        }
      }
```

### Validating Healthcare Data

**Check medical identifier formats:**
```
input_validation field_type="medical_identifiers"
```

**Get validation rules:**
```json
{
  "npi": {
    "pattern": "^\\d{10}$",
    "description": "National Provider Identifier - 10 digits",
    "example": "1234567890"
  },
  "medical_record_number": {
    "pattern": "^[A-Z]{2}\\d{6}$", 
    "description": "Format: 2 letters + 6 digits",
    "example": "MR123456"
  }
}
```

## 🛠️ Available Tools Overview

| Tool | What it does | When to use |
|------|-------------|-------------|
| **search_schema** | Find types, fields, queries in the schema | "Where is patient data defined?" |
| **introspect_type** | Get detailed info about a specific type | "What fields does Patient have?" |
| **query_templates** | Pre-built queries for common operations | "How do I create an appointment?" |
| **code_examples** | JavaScript/Python/cURL examples | "Show me working code" |
| **healthcare_patterns** | Find healthcare-specific patterns | "What FHIR resources are supported?" |
| **workflow_sequences** | Multi-step process guidance | "How do I complete patient intake?" |
| **field_relationships** | Understand how types connect | "How are patients linked to appointments?" |
| **input_validation** | Validation rules and patterns | "How do I validate a phone number?" |
| **error_decoder** | Understand and fix API errors | "Why did my mutation fail?" |
| **performance_analyzer** | Optimize query performance | "How can I make this faster?" |
| **field_usage** | Field usage recommendations | "Which patient fields should I include?" |

## 🎯 Next Steps

### For Frontend Developers
1. Try the [Patient Dashboard Tutorial](../tutorials/patient-dashboard.md)
2. Explore [JavaScript examples](../../examples/integrations/javascript/)
3. Review [healthcare workflow patterns](./healthcare-workflows.md)

### For Backend Developers  
1. Check out [API integration examples](../../examples/integrations/python/)
2. Learn about [error handling patterns](../api/error-handling.md)
3. See [performance optimization guide](../api/configuration.md)

### For Healthcare Teams
1. Review [healthcare-specific workflows](./healthcare-workflows.md)
2. Understand [compliance considerations](../api/configuration.md#security)
3. Explore [clinical data patterns](../tutorials/clinical-integration.md)

## 💡 Pro Tips

- **Start with templates** - Use `query_templates` to get working queries quickly
- **Validate early** - Use `input_validation` to catch errors before API calls
- **Search efficiently** - Use type filters in `search_schema` to narrow results
- **Learn patterns** - Use `healthcare_patterns` to understand FHIR mappings
- **Debug systematically** - Use `error_decoder` when things go wrong

Ready to dive deeper? Check out the [Tool Overview](./tool-overview.md) for detailed examples of each tool!