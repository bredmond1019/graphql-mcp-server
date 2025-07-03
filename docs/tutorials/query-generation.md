# Query Generation with MCP Tools

Learn how to instantly generate production-ready GraphQL queries and implementation code using the `query_templates` and `code_examples` tools.

## Overview

These two powerful tools work together to:
- **query_templates**: Provide tested GraphQL query templates for common workflows
- **code_examples**: Generate complete, working implementations in multiple languages

Together, they reduce query development time from hours to minutes.

## Query Templates Tool

### Basic Usage

Get templates for specific workflows:

```python
# Get all available templates
all_templates = query_templates(workflow="all")

# Get patient management templates
patient_templates = query_templates(
    workflow="patient_management",
    include_variables=True
)

# Get appointment templates
appointment_templates = query_templates(workflow="appointments")
```

### Available Workflows

Based on testing, the tool provides templates for:

1. **patient_management** - Patient CRUD operations
2. **appointments** - Scheduling and availability
3. **clinical_data** - Clinical notes and documentation
4. **billing** - Insurance and payment processing
5. **provider_management** - Provider operations
6. **all** - Get templates across all workflows

### Real Template Examples

#### Patient Management Templates

```graphql
# Create Patient Template
mutation CreatePatient($input: CreatePatientInput!) {
  createPatient(input: $input) {
    patient {
      id
      firstName
      lastName
      email
      dateOfBirth
      phoneNumber
      addresses {
        id
        line1
        city
        state
        zipCode
      }
    }
    errors {
      field
      message
    }
  }
}

# Variables template included:
{
  "input": {
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "dateOfBirth": "1990-01-01",
    "phoneNumber": "+1234567890"
  }
}
```

#### Appointment Templates

```graphql
# Book Appointment Template
mutation BookAppointment($input: CreateAppointmentInput!) {
  createAppointment(input: $input) {
    appointment {
      id
      date
      time
      endTime
      status
      provider {
        id
        firstName
        lastName
      }
      patient {
        id
        firstName
        lastName
      }
      appointmentType {
        name
        duration
      }
    }
    errors {
      field
      message
    }
  }
}

# Check Availability Template
query CheckAvailability(
  $providerId: ID!
  $startDate: String!
  $endDate: String!
) {
  provider(id: $providerId) {
    availabilities(
      startDate: $startDate
      endDate: $endDate
    ) {
      date
      slots {
        time
        available
        duration
      }
    }
  }
}
```

#### Clinical Data Templates

```graphql
# Create Clinical Note Template
mutation CreateClinicalNote($input: CreateClinicalNoteInput!) {
  createClinicalNote(input: $input) {
    clinicalNote {
      id
      noteType
      content
      patient {
        id
        firstName
        lastName
      }
      provider {
        id
        firstName
        lastName
      }
      createdAt
      signedAt
    }
    errors {
      field
      message
    }
  }
}
```

## Code Examples Tool

### Basic Usage

Generate working code in your preferred language:

```python
# JavaScript/React example
js_code = code_examples(
    operation="create_patient",
    language="javascript"
)

# Python example
py_code = code_examples(
    operation="book_appointment", 
    language="python"
)

# cURL example
curl_code = code_examples(
    operation="get_patient",
    language="curl"
)
```

### Generated Code Examples

#### JavaScript Implementation

```javascript
// Generated Create Patient Function
import { gql, useMutation } from '@apollo/client';

const CREATE_PATIENT = gql`
  mutation CreatePatient($input: CreatePatientInput!) {
    createPatient(input: $input) {
      patient {
        id
        firstName
        lastName
        email
      }
      errors {
        field
        message
      }
    }
  }
`;

function CreatePatientForm() {
  const [createPatient, { loading, error }] = useMutation(CREATE_PATIENT);
  
  const handleSubmit = async (formData) => {
    try {
      const { data } = await createPatient({
        variables: {
          input: {
            firstName: formData.firstName,
            lastName: formData.lastName,
            email: formData.email,
            dateOfBirth: formData.dateOfBirth,
            phoneNumber: formData.phoneNumber
          }
        }
      });
      
      if (data.createPatient.errors?.length > 0) {
        // Handle validation errors
        console.error('Validation errors:', data.createPatient.errors);
        return;
      }
      
      // Success!
      console.log('Patient created:', data.createPatient.patient);
      
    } catch (error) {
      console.error('Error creating patient:', error);
    }
  };
  
  return (
    // Your form JSX here
  );
}
```

#### Python Implementation

```python
# Generated Book Appointment Function
import requests
from datetime import datetime

def book_appointment(
    patient_id: str,
    provider_id: str,
    appointment_date: str,
    appointment_time: str,
    appointment_type_id: str,
    api_key: str
):
    """
    Book an appointment in Healthie
    
    Args:
        patient_id: ID of the patient
        provider_id: ID of the provider
        appointment_date: Date in YYYY-MM-DD format
        appointment_time: Time in HH:MM format
        appointment_type_id: ID of appointment type
        api_key: Your Healthie API key
    
    Returns:
        dict: Created appointment data
    """
    
    query = """
    mutation BookAppointment($input: CreateAppointmentInput!) {
      createAppointment(input: $input) {
        appointment {
          id
          date
          time
          endTime
          status
        }
        errors {
          field
          message
        }
      }
    }
    """
    
    variables = {
        "input": {
            "patientId": patient_id,
            "providerId": provider_id,
            "date": appointment_date,
            "time": appointment_time,
            "appointmentTypeId": appointment_type_id,
            "contactType": "video_call"
        }
    }
    
    response = requests.post(
        'https://api.gethealthie.com/graphql',
        json={
            'query': query,
            'variables': variables
        },
        headers={
            'Authorization': f'Basic {api_key}',
            'AuthorizationSource': 'API',
            'Content-Type': 'application/json'
        }
    )
    
    data = response.json()
    
    if 'errors' in data:
        raise Exception(f"GraphQL errors: {data['errors']}")
    
    return data['data']['createAppointment']['appointment']

# Usage example
appointment = book_appointment(
    patient_id="123",
    provider_id="456",
    appointment_date="2024-01-15",
    appointment_time="14:00",
    appointment_type_id="789",
    api_key="your_api_key"
)
```

#### cURL Implementation

```bash
# Generated Get Patient cURL command
curl -X POST https://api.gethealthie.com/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic YOUR_API_KEY" \
  -H "AuthorizationSource: API" \
  -d '{
    "query": "query GetPatient($id: ID!) { patient(id: $id) { id firstName lastName email dateOfBirth phoneNumber addresses { line1 city state zipCode } } }",
    "variables": {
      "id": "PATIENT_ID"
    }
  }'
```

## Combining Templates and Examples

### Workflow: Complete Feature Implementation

1. **Get the template:**
```python
# Get appointment booking template
template = query_templates(
    workflow="appointments",
    include_variables=True
)
```

2. **Generate implementation code:**
```python
# Generate React component
react_code = code_examples(
    operation="book_appointment",
    language="javascript"
)
```

3. **Create error handling:**
```python
# Get error handling patterns
error_examples = code_examples(
    operation="handle_errors",
    language="javascript"
)
```

### Workflow: Multi-Language SDK

Generate consistent implementations across languages:

```python
operations = [
    "create_patient",
    "update_patient", 
    "get_patient",
    "search_patients"
]

languages = ["javascript", "python", "curl"]

# Generate SDK for each language
for lang in languages:
    print(f"\n=== {lang.upper()} SDK ===\n")
    
    for op in operations:
        code = code_examples(
            operation=op,
            language=lang
        )
        
        # Save to file
        filename = f"sdk/{lang}/{op}.{lang}"
        save_code(filename, code)
```

## Advanced Template Usage

### 1. Customizing Templates

Templates are starting points - customize for your needs:

```python
# Get base template
template = query_templates(workflow="patient_management")

# Customize fields
customized = template.replace(
    "firstName\n      lastName", 
    "firstName\n      middleName\n      lastName\n      suffix"
)

# Add custom fields
customized = add_field_to_query(customized, "customField1")
```

### 2. Building Complex Queries

Combine multiple templates:

```python
# Get patient and appointments in one query
patient_template = query_templates(workflow="patient_management")
appointment_template = query_templates(workflow="appointments")

# Combine into single query
combined_query = f"""
query GetPatientWithAppointments($patientId: ID!) {{
  {extract_query_body(patient_template)}
  
  appointments(patientId: $patientId) {{
    {extract_query_body(appointment_template)}
  }}
}}
"""
```

### 3. Template Variables

Work with template variables effectively:

```python
# Get template with variables
template_data = query_templates(
    workflow="clinical_data",
    include_variables=True
)

# Extract query and variables separately
query = template_data["query"]
variables = template_data["variables"]

# Modify variables for your use case
variables["input"]["noteType"] = "SOAP"
variables["input"]["templateId"] = "soap-template-1"
```

## Code Generation Patterns

### 1. Error-First Design

Generated code includes comprehensive error handling:

```javascript
// Pattern from code_examples
try {
  const result = await operation();
  
  // Check for GraphQL errors
  if (result.errors) {
    handleGraphQLErrors(result.errors);
    return;
  }
  
  // Check for mutation errors
  if (result.data.mutation.errors?.length > 0) {
    handleValidationErrors(result.data.mutation.errors);
    return;
  }
  
  // Success path
  handleSuccess(result.data);
  
} catch (networkError) {
  // Network/transport errors
  handleNetworkError(networkError);
}
```

### 2. Authentication Patterns

All generated code includes proper authentication:

```python
# Python pattern
headers = {
    'Authorization': f'Basic {api_key}',
    'AuthorizationSource': 'API',
    'Content-Type': 'application/json'
}

# JavaScript pattern
const client = new ApolloClient({
  uri: 'https://api.gethealthie.com/graphql',
  headers: {
    'Authorization': `Basic ${apiKey}`,
    'AuthorizationSource': 'API'
  }
});
```

### 3. Type Safety

Generated TypeScript includes type definitions:

```typescript
// Generated types
interface CreatePatientInput {
  firstName: string;
  lastName: string;
  email: string;
  dateOfBirth: string;
  phoneNumber?: string;
}

interface Patient {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
}

// Type-safe function
async function createPatient(
  input: CreatePatientInput
): Promise<Patient> {
  // Implementation
}
```

## Workflow-Specific Examples

### Patient Registration Flow

```python
# 1. Get registration template
reg_template = query_templates(
    workflow="patient_management",
    operation="create_patient"
)

# 2. Get validation rules
validation_code = code_examples(
    operation="validate_patient",
    language="javascript"
)

# 3. Get complete form component
form_code = code_examples(
    operation="patient_registration_form",
    language="javascript"
)
```

### Appointment Booking Flow

```python
# 1. Check availability template
avail_template = query_templates(
    workflow="appointments",
    operation="check_availability"
)

# 2. Get booking mutation
book_template = query_templates(
    workflow="appointments",
    operation="book_appointment"
)

# 3. Generate booking widget
widget_code = code_examples(
    operation="appointment_booking_widget",
    language="javascript"
)
```

### Clinical Documentation Flow

```python
# 1. Get note templates
note_templates = query_templates(
    workflow="clinical_data",
    include_variables=True
)

# 2. Generate SOAP note form
soap_code = code_examples(
    operation="soap_note_form",
    language="javascript"
)

# 3. Get signing/locking code
sign_code = code_examples(
    operation="sign_clinical_note",
    language="python"
)
```

## Best Practices

### 1. Always Include Error Handling

```python
# Good: Use generated error handling
code = code_examples(
    operation="create_patient",
    language="javascript"
)
# Includes try/catch and error states

# Not ideal: Basic query without error handling
basic_query = "mutation { createPatient(...) { id } }"
```

### 2. Use Variables for Dynamic Values

```python
# Good: Template with variables
template = query_templates(
    workflow="patient_management",
    include_variables=True
)

# Not ideal: Hardcoded values
query = 'mutation { createPatient(firstName: "John") { id } }'
```

### 3. Start with Templates, Customize After

```python
# Good: Start with tested template
base = query_templates(workflow="appointments")
customized = customize_for_your_needs(base)

# Not ideal: Write from scratch
custom_query = "mutation { ... }"
```

### 4. Generate for Your Stack

```python
# Good: Generate for your exact setup
if using_react:
    code = code_examples(operation="patient_form", language="javascript")
elif using_django:
    code = code_examples(operation="patient_form", language="python")
```

## Performance Optimization

Templates and generated code include performance best practices:

### 1. Minimal Field Selection

```graphql
# Templates only request needed fields
mutation CreatePatient($input: CreatePatientInput!) {
  createPatient(input: $input) {
    patient {
      id          # Only essential fields
      firstName
      lastName
    }
  }
}
```

### 2. Efficient Pagination

```graphql
# Templates include pagination
query GetPatients($first: Int!, $after: String) {
  patients(first: $first, after: $after) {
    edges {
      node {
        id
        firstName
        lastName
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

### 3. Batch Operations

```python
# Generated code supports batching
appointments = code_examples(
    operation="bulk_create_appointments",
    language="python"
)
```

## Next Steps

Now that you can generate queries and code:

1. **[Type Exploration](./type-exploration.md)** - Understand the types in your queries
2. **[Debugging with MCP](./debugging-with-mcp.md)** - Handle errors in generated code
3. **[Using MCP Tools](./using-mcp-tools.md)** - Back to overview

Remember: Templates and examples are tested and production-ready. Use them as your foundation!