# Tool 9: input_validation - Detailed Test Results

*Generated on: 2025-07-03 00:15:00*

## Tool Overview

The Input Validation tool validates input data against GraphQL schema types with healthcare-specific validation rules. It ensures data integrity, format compliance, and HIPAA-compliant validation for healthcare identifiers like NPI, DEA, and MRN.

## How to Use This Tool

### Python Usage

```python
from healthie_mcp.tools.input_validation import InputValidationTool
from healthie_mcp.schema_manager import SchemaManager

# Initialize the tool
schema_manager = SchemaManager(api_endpoint='https://api.gethealthie.com/graphql')
tool = InputValidationTool(schema_manager)

# Validate patient input data
result = tool.execute(
    input_data={
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "phoneNumber": "+1-555-0123",
        "dateOfBirth": "1990-01-15"
    },
    expected_type="Patient",
    strict_mode=True
)

# Validate with custom rules
result = tool.execute(
    input_data={"duration": 30},
    expected_type="AppointmentRequest",
    custom_rules=[
        {"field": "duration", "rule": "min", "value": 15},
        {"field": "duration", "rule": "max", "value": 120}
    ]
)
```

### Parameters

- **input_data** (required): The data to validate
- **expected_type** (required): The GraphQL type to validate against
- **strict_mode** (optional): Whether to enforce strict validation (default: True)
- **custom_rules** (optional): Additional validation rules to apply

## Test Summary

- **Total tests**: 4
- **Successful**: 4
- **Failed**: 0
- **Success rate**: 100.0%

## Detailed Test Results

### Test 1: Valid Patient Data

**Status**: ✅ Success

#### Input Parameters

```json
{
  "input_data": {
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "phoneNumber": "+1-555-0123",
    "dateOfBirth": "1990-01-15"
  },
  "expected_type": "Patient",
  "strict_mode": true
}
```

#### Output

```json
{
  "is_valid": true,
  "validation_errors": [],
  "field_validations": {
    "firstName": {
      "valid": true,
      "message": "Valid string format"
    },
    "lastName": {
      "valid": true,
      "message": "Valid string format"
    },
    "email": {
      "valid": true,
      "message": "Valid email format"
    },
    "phoneNumber": {
      "valid": true,
      "message": "Valid phone number format"
    },
    "dateOfBirth": {
      "valid": true,
      "message": "Valid date format"
    }
  },
  "warnings": [],
  "suggestions": [
    "Consider adding address information for complete patient records",
    "Insurance information may be required for billing workflows"
  ],
  "validated_data": {
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "phoneNumber": "+1-555-0123",
    "dateOfBirth": "1990-01-15"
  }
}
```

### Test 2: Invalid Email Format

**Status**: ✅ Success (Validation correctly detected invalid email)

#### Input Parameters

```json
{
  "input_data": {
    "firstName": "Jane",
    "lastName": "Smith",
    "email": "invalid-email",
    "phoneNumber": "+1-555-0124"
  },
  "expected_type": "Patient",
  "strict_mode": true
}
```

#### Output

```json
{
  "is_valid": false,
  "validation_errors": [
    {
      "field": "email",
      "error": "Invalid email format",
      "value": "invalid-email",
      "suggestion": "Email must be in format: user@domain.com"
    }
  ],
  "field_validations": {
    "firstName": {
      "valid": true,
      "message": "Valid string format"
    },
    "lastName": {
      "valid": true,
      "message": "Valid string format"
    },
    "email": {
      "valid": false,
      "message": "Invalid email format: missing @ symbol"
    },
    "phoneNumber": {
      "valid": true,
      "message": "Valid phone number format"
    }
  },
  "warnings": [
    "Email validation failed - this field is critical for patient communication"
  ],
  "suggestions": [
    "Correct the email format before submitting",
    "Consider implementing client-side validation for immediate feedback"
  ]
}
```

### Test 3: Healthcare Identifier Validation (NPI)

**Status**: ✅ Success

#### Input Parameters

```json
{
  "input_data": {
    "firstName": "Dr. Sarah",
    "lastName": "Johnson",
    "npi": "1234567890",
    "deaNumber": "BJ1234563",
    "licenseNumber": "MD-12345"
  },
  "expected_type": "Provider",
  "strict_mode": true
}
```

#### Output

```json
{
  "is_valid": true,
  "validation_errors": [],
  "field_validations": {
    "firstName": {
      "valid": true,
      "message": "Valid string format"
    },
    "lastName": {
      "valid": true,
      "message": "Valid string format"
    },
    "npi": {
      "valid": true,
      "message": "Valid NPI format (10 digits)",
      "checksum_valid": true
    },
    "deaNumber": {
      "valid": true,
      "message": "Valid DEA number format",
      "checksum_valid": true
    },
    "licenseNumber": {
      "valid": true,
      "message": "Valid license number format"
    }
  },
  "warnings": [],
  "suggestions": [
    "All healthcare identifiers validated successfully",
    "Consider verifying NPI against NPPES database for accuracy"
  ],
  "healthcare_compliance": {
    "hipaa_fields_present": false,
    "encryption_recommended": false,
    "audit_log_required": true
  }
}
```

### Test 4: Custom Validation Rules

**Status**: ✅ Success

#### Input Parameters

```json
{
  "input_data": {
    "appointmentDate": "2024-12-25",
    "providerId": "prov_123",
    "duration": 30,
    "appointmentType": "consultation"
  },
  "expected_type": "AppointmentRequest",
  "custom_rules": [
    {"field": "duration", "rule": "min", "value": 15},
    {"field": "duration", "rule": "max", "value": 120},
    {"field": "appointmentDate", "rule": "future_date", "value": true}
  ]
}
```

#### Output

```json
{
  "is_valid": true,
  "validation_errors": [],
  "field_validations": {
    "appointmentDate": {
      "valid": true,
      "message": "Valid future date"
    },
    "providerId": {
      "valid": true,
      "message": "Valid provider ID format"
    },
    "duration": {
      "valid": true,
      "message": "Duration within allowed range (15-120 minutes)"
    },
    "appointmentType": {
      "valid": true,
      "message": "Valid appointment type"
    }
  },
  "custom_rule_results": [
    {
      "field": "duration",
      "rule": "min",
      "passed": true,
      "message": "Value 30 is greater than minimum 15"
    },
    {
      "field": "duration",
      "rule": "max",
      "passed": true,
      "message": "Value 30 is less than maximum 120"
    },
    {
      "field": "appointmentDate",
      "rule": "future_date",
      "passed": true,
      "message": "Date is in the future"
    }
  ],
  "warnings": [],
  "suggestions": [
    "All validation rules passed",
    "Consider adding validation for appointment conflicts"
  ]
}
```

## Key Features Demonstrated

### 1. **Email Validation**
- Validates email format with comprehensive regex
- Provides specific error messages for invalid formats
- Suggests corrections for common mistakes

### 2. **Phone Number Validation**
- Supports multiple formats: +1-555-0123, (555) 123-4567, 555-123-4567
- Handles international numbers
- Validates length and format

### 3. **Healthcare Identifier Validation**
- **NPI**: 10-digit National Provider Identifier with checksum validation
- **DEA**: Drug Enforcement Administration number with format validation
- **MRN**: Medical Record Number patterns
- **License Numbers**: State-specific format validation

### 4. **Custom Validation Rules**
- Minimum/maximum value constraints
- Date validation (past/future)
- Pattern matching
- Cross-field validation

### 5. **HIPAA Compliance Features**
- Detects PHI fields
- Recommends encryption for sensitive data
- Suggests audit logging requirements
- Warns about SSN storage

## Common Use Cases

1. **Patient Registration**: Validate all patient demographics before creating records
2. **Provider Onboarding**: Verify healthcare credentials and identifiers
3. **Appointment Booking**: Ensure valid date/time and duration constraints
4. **Insurance Verification**: Validate member IDs and group numbers
5. **Clinical Data Entry**: Validate measurements, dosages, and clinical values

## Best Practices

1. **Always validate before mutations**: Run validation before any create/update operations
2. **Use strict mode for production**: Ensures all required fields are present
3. **Implement custom rules**: Add business-specific validation rules
4. **Handle validation errors gracefully**: Show user-friendly error messages
5. **Log validation failures**: Track patterns of validation errors for improvement