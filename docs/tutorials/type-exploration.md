# Type Exploration with MCP Tools

Master the `introspect_type` tool to understand GraphQL types in depth, explore relationships, and build type-safe applications.

## Overview

The `introspect_type` tool provides comprehensive information about any GraphQL type in the Healthie schema, including:
- All fields with their types and descriptions
- Nullability constraints
- Relationships to other types
- Available arguments
- Deprecation status

## Why Type Introspection Matters

Understanding types thoroughly helps you:
- Write correct queries without trial and error
- Understand data relationships
- Build proper validation
- Avoid using deprecated fields
- Create accurate TypeScript/Flow types

## Basic Usage

### Simple Type Introspection

```python
# Get basic type information
patient_type = introspect_type(type_name="Patient")

# Returns information about:
# - Type kind (OBJECT, INTERFACE, ENUM, etc.)
# - All fields with their types
# - Field descriptions
# - Which fields are required (non-null)
```

### Detailed Introspection

```python
# Get comprehensive type details
appointment_type = introspect_type(
    type_name="Appointment",
    include_relationships=True,
    include_deprecated=True
)

# Additional information:
# - Related types (Patient, Provider, etc.)
# - Deprecated fields with reasons
# - Field arguments and their types
```

## Real-World Examples

### Example 1: Understanding the Patient Type

```python
result = introspect_type(type_name="Patient")
```

**Result Overview:**
- **Total Fields**: ~100+
- **Core Fields**: id, firstName, lastName, email, dateOfBirth
- **Relationships**: appointments, providers, insurancePolicies, documents
- **Nested Types**: addresses, phoneNumbers, emergencyContacts

**Key Fields Discovered:**
```graphql
type Patient {
  # Identity fields
  id: ID!
  firstName: String
  lastName: String
  email: String
  
  # Demographics
  dateOfBirth: String
  gender: Gender
  ethnicity: String
  primaryLanguage: String
  
  # Contact
  phoneNumbers: [PhoneNumber!]
  addresses: [Address!]
  
  # Medical
  medicalRecordNumber: String
  allergies: [Allergy!]
  medications: [Medication!]
  
  # Relationships
  primaryProvider: Provider
  careTeam: [Provider!]
  appointments: [Appointment!]
  
  # Insurance
  insurancePolicies: [InsurancePolicy!]
  primaryInsurance: InsurancePolicy
}
```

### Example 2: Complex Type - Appointment

```python
result = introspect_type(type_name="Appointment")
```

**Result Overview:**
- **Total Fields**: 98
- **Status Fields**: status, confirmedAt, cancelledAt, completedAt
- **Relationship Fields**: patient, provider, appointmentType, location
- **Telehealth Fields**: videoRoomUrl, contactType

**Important Fields:**
```graphql
type Appointment {
  # Core fields
  id: ID!
  date: String!
  time: String!
  endTime: String!
  duration: Int
  
  # Status management
  status: AppointmentStatus!
  confirmedAt: DateTime
  checkedInAt: DateTime
  cancelledAt: DateTime
  cancellationReason: String
  
  # Participants
  patient: Patient!
  provider: Provider!
  attendees: [User!]
  
  # Type and location
  appointmentType: AppointmentType!
  location: Location
  contactType: ContactType!
  
  # Telehealth
  videoRoomUrl: String
  videoRoomStatus: VideoRoomStatus
  
  # Clinical
  chartingNote: ChartingNote
  formAnswerGroups: [FormAnswerGroup!]
}
```

### Example 3: The User Type (Most Complex)

```python
result = introspect_type(type_name="User")
```

**Result Overview:**
- **Total Fields**: 453 (!!)
- **Categories**: Personal info, professional details, settings, permissions
- **Provider Fields**: npi, dea, licenses, specialties
- **Patient Fields**: medicalRecordNumber, insurances, careTeam

This demonstrates that User is a polymorphic type serving multiple roles.

## Understanding Field Types

### Scalar Types

Basic data types in GraphQL:

```python
# Common scalars found via introspection
String     # Text data
Int        # Whole numbers
Float      # Decimal numbers
Boolean    # true/false
ID         # Unique identifiers
DateTime   # ISO 8601 timestamps
Date       # YYYY-MM-DD
JSON       # Arbitrary JSON data
```

### Nullability

Understanding `!` (non-null) markers:

```graphql
# From introspection results
firstName: String        # Can be null
id: ID!                 # Cannot be null
addresses: [Address!]   # List can be null, but items cannot
emails: [String!]!      # Neither list nor items can be null
```

### List Types

Arrays of values:

```graphql
# Single item
provider: Provider

# List of items
providers: [Provider]

# Non-null list of non-null items
appointments: [Appointment!]!
```

## Exploring Relationships

### Finding Related Types

When introspecting a type, pay attention to:

1. **Direct relationships**:
```python
# In Patient type
provider: Provider           # Direct link to Provider
appointments: [Appointment]  # List of related Appointments
```

2. **Reverse relationships**:
```python
# In Appointment type
patient: Patient   # Links back to Patient
```

3. **Junction types**:
```python
# PatientProvider type links Patients and Providers
type PatientProvider {
  patient: Patient!
  provider: Provider!
  isPrimary: Boolean
  startDate: Date
}
```

### Relationship Mapping Example

```python
# Map patient relationships
patient = introspect_type("Patient")
relationships = {}

for field in patient.fields:
    if field.type.kind == "OBJECT":
        relationships[field.name] = field.type.name
    elif field.type.kind == "LIST" and field.type.ofType.kind == "OBJECT":
        relationships[field.name] = f"[{field.type.ofType.name}]"

# Results in:
# {
#   "primaryProvider": "Provider",
#   "appointments": "[Appointment]",
#   "insurancePolicies": "[InsurancePolicy]",
#   "documents": "[Document]",
#   ...
# }
```

## Enum Types

Discovering valid values:

```python
# Introspect an enum
status_enum = introspect_type(type_name="AppointmentStatus")

# Returns values:
# - scheduled
# - confirmed
# - checked_in
# - in_progress
# - completed
# - cancelled
# - no_show
```

Common Healthcare Enums:
```python
# Gender
gender = introspect_type("Gender")
# Values: male, female, other, unknown

# Contact Type
contact_type = introspect_type("ContactType")
# Values: in_person, video_call, phone_call, chat

# Document Type
doc_type = introspect_type("DocumentType")
# Values: lab_result, imaging, clinical_note, consent_form
```

## Input Types

Understanding mutation inputs:

```python
# Introspect input type
create_input = introspect_type(type_name="CreatePatientInput")

# Reveals required vs optional fields:
type CreatePatientInput {
  firstName: String!      # Required
  lastName: String!       # Required
  email: String!         # Required
  dateOfBirth: Date!     # Required
  phoneNumber: String    # Optional
  gender: Gender         # Optional
  addressInput: AddressInput  # Optional nested input
}
```

## Advanced Introspection Patterns

### 1. Building Type Maps

Create a complete map of your domain:

```python
def build_type_map(domain):
    """Build complete type map for a domain"""
    
    # Start with core type
    core_type = introspect_type(domain)
    type_map = {domain: core_type}
    
    # Find related types
    for field in core_type.fields:
        field_type = extract_base_type(field.type)
        if field_type not in type_map:
            type_map[field_type] = introspect_type(field_type)
    
    return type_map

# Usage
patient_types = build_type_map("Patient")
# Returns: Patient, Address, PhoneNumber, Provider, etc.
```

### 2. Finding Optional vs Required

Analyze which fields are commonly required:

```python
def analyze_nullability(type_name):
    """Analyze field nullability patterns"""
    
    type_info = introspect_type(type_name)
    
    required = []
    optional = []
    
    for field in type_info.fields:
        if field.type.kind == "NON_NULL":
            required.append(field.name)
        else:
            optional.append(field.name)
    
    return {
        "required": required,
        "optional": optional,
        "required_percentage": len(required) / len(type_info.fields) * 100
    }
```

### 3. Deprecation Checking

Find deprecated fields before using them:

```python
def find_deprecated_fields(type_name):
    """Find all deprecated fields in a type"""
    
    type_info = introspect_type(
        type_name=type_name,
        include_deprecated=True
    )
    
    deprecated = []
    for field in type_info.fields:
        if field.isDeprecated:
            deprecated.append({
                "field": field.name,
                "reason": field.deprecationReason,
                "suggested_alternative": extract_alternative(field.deprecationReason)
            })
    
    return deprecated
```

## Type-Driven Development

### 1. Generate TypeScript Interfaces

```python
def generate_typescript_interface(type_name):
    """Generate TypeScript interface from GraphQL type"""
    
    type_info = introspect_type(type_name)
    
    interface = f"interface {type_name} {{\n"
    
    for field in type_info.fields:
        ts_type = graphql_to_typescript(field.type)
        optional = "?" if not field.type.kind == "NON_NULL" else ""
        interface += f"  {field.name}{optional}: {ts_type};\n"
    
    interface += "}"
    
    return interface

# Usage
patient_interface = generate_typescript_interface("Patient")
```

### 2. Build Validation Rules

```python
def generate_validation_rules(input_type_name):
    """Generate validation rules from input type"""
    
    type_info = introspect_type(input_type_name)
    
    rules = {}
    
    for field in type_info.fields:
        rules[field.name] = {
            "required": field.type.kind == "NON_NULL",
            "type": extract_base_type(field.type),
            "validation": infer_validation(field.name, field.type)
        }
    
    return rules

# Usage
patient_rules = generate_validation_rules("CreatePatientInput")
```

### 3. Documentation Generation

```python
def generate_type_documentation(type_name):
    """Generate markdown documentation for a type"""
    
    type_info = introspect_type(type_name)
    
    doc = f"# {type_name} Type\n\n"
    doc += f"Total fields: {len(type_info.fields)}\n\n"
    
    doc += "## Fields\n\n"
    doc += "| Field | Type | Required | Description |\n"
    doc += "|-------|------|----------|-------------|\n"
    
    for field in type_info.fields:
        required = "Yes" if field.type.kind == "NON_NULL" else "No"
        doc += f"| {field.name} | {field.type} | {required} | {field.description or 'N/A'} |\n"
    
    return doc
```

## Common Introspection Patterns

### Healthcare-Specific Types

Key types to introspect for healthcare apps:

```python
healthcare_types = [
    "Patient",           # Core patient data
    "Provider",          # Healthcare providers
    "Appointment",       # Scheduling
    "ClinicalNote",      # Documentation
    "Medication",        # Prescriptions
    "Allergy",          # Allergies
    "InsurancePolicy",   # Insurance
    "Claim",            # Billing
    "FormTemplate",      # Custom forms
    "Organization"       # Healthcare facilities
]

for type_name in healthcare_types:
    info = introspect_type(type_name)
    print(f"{type_name}: {len(info.fields)} fields")
```

### Finding Audit Fields

Most types have audit fields:

```python
def find_audit_fields(type_name):
    """Find common audit fields in a type"""
    
    type_info = introspect_type(type_name)
    
    audit_patterns = ["createdAt", "updatedAt", "createdBy", "updatedBy", "deletedAt"]
    audit_fields = []
    
    for field in type_info.fields:
        if field.name in audit_patterns:
            audit_fields.append(field.name)
    
    return audit_fields

# Most types have: createdAt, updatedAt, sometimes deletedAt
```

### Identifying Relationships

```python
def find_relationships(type_name):
    """Find all relationships from a type"""
    
    type_info = introspect_type(type_name)
    relationships = {
        "belongs_to": [],    # Single object references
        "has_many": [],      # List references
        "has_one": []        # Single optional references
    }
    
    for field in type_info.fields:
        if field.type.kind == "OBJECT":
            if field.type.kind == "NON_NULL":
                relationships["belongs_to"].append(field.name)
            else:
                relationships["has_one"].append(field.name)
        elif field.type.kind == "LIST":
            relationships["has_many"].append(field.name)
    
    return relationships
```

## Troubleshooting

### Type Not Found

```python
try:
    result = introspect_type("InvalidType")
except Exception as e:
    # Type doesn't exist
    # Use search_schema to find correct name
    suggestions = search_schema("Invalid", type_filter="type")
```

### Handling Large Types

For types with many fields (like User with 453 fields):

```python
# Filter to specific field categories
def introspect_category(type_name, category):
    type_info = introspect_type(type_name)
    
    # Filter fields by category patterns
    if category == "medical":
        patterns = ["medical", "health", "clinical", "diagnosis"]
    elif category == "insurance":
        patterns = ["insurance", "policy", "claim", "coverage"]
    
    filtered_fields = [
        field for field in type_info.fields
        if any(pattern in field.name.lower() for pattern in patterns)
    ]
    
    return filtered_fields
```

## Best Practices

### 1. Cache Introspection Results

```python
# Types don't change often - cache results
TYPE_CACHE = {}

def cached_introspect(type_name):
    if type_name not in TYPE_CACHE:
        TYPE_CACHE[type_name] = introspect_type(type_name)
    return TYPE_CACHE[type_name]
```

### 2. Validate Before Using

```python
# Always check if fields exist before using
def safe_query_builder(type_name, requested_fields):
    type_info = introspect_type(type_name)
    available_fields = [f.name for f in type_info.fields]
    
    valid_fields = [
        field for field in requested_fields 
        if field in available_fields
    ]
    
    return build_query(type_name, valid_fields)
```

### 3. Use for Code Generation

```python
# Generate from introspection, not assumptions
def generate_fragment(type_name, field_set="basic"):
    type_info = introspect_type(type_name)
    
    if field_set == "basic":
        fields = ["id", "createdAt", "updatedAt"]
    elif field_set == "full":
        fields = [f.name for f in type_info.fields]
    
    return f"""
    fragment {type_name}Fields on {type_name} {{
        {' '.join(fields)}
    }}
    """
```

## Next Steps

Now that you can explore types in depth:

1. **[Debugging with MCP](./debugging-with-mcp.md)** - Use type knowledge to debug effectively
2. **[Query Generation](./query-generation.md)** - Build queries with correct types
3. **[Using MCP Tools](./using-mcp-tools.md)** - Back to overview

Remember: Understanding types deeply prevents errors and enables you to build robust, type-safe applications!