# Debugging with MCP Tools

Master the `error_decoder` tool to transform cryptic GraphQL errors into actionable solutions and learn debugging strategies using all MCP tools together.

## Overview

The `error_decoder` tool provides:
- Plain English explanations of errors
- Specific solutions for common problems
- Code examples to fix issues
- Related documentation links

Combined with other MCP tools, you can debug any API integration issue quickly.

## Common Error Types

### 1. Field Errors

**Error:**
```
Cannot query field 'patient_name' on type 'Patient'
```

**Using error_decoder:**
```python
solution = error_decoder(
    error_message="Cannot query field 'patient_name' on type 'Patient'"
)

# Returns:
{
    "error_type": "FIELD_NOT_FOUND",
    "plain_english": "The field 'patient_name' does not exist on the Patient type. GraphQL fields are case-sensitive and must match exactly.",
    "possible_solutions": [
        "Use 'firstName' and 'lastName' instead of 'patient_name'",
        "Check the exact field name using introspection",
        "The correct fields might be camelCase: firstName, lastName"
    ],
    "example_fix": """
    # Instead of:
    query { patient(id: "123") { patient_name } }
    
    # Use:
    query { patient(id: "123") { firstName lastName } }
    """
}
```

### 2. Authentication Errors

**Error:**
```
Not authorized
```

**Using error_decoder:**
```python
solution = error_decoder(error_message="Not authorized")

# Returns:
{
    "error_type": "AUTHENTICATION_ERROR",
    "plain_english": "Your request lacks proper authentication or you don't have permission for this operation.",
    "possible_solutions": [
        "Ensure you're sending the Authorization header: 'Basic YOUR_API_KEY'",
        "Include the AuthorizationSource header: 'API'",
        "Verify your API key is active and has necessary permissions",
        "Check if this operation requires specific user roles"
    ],
    "example_fix": """
    headers = {
        'Authorization': 'Basic YOUR_API_KEY',
        'AuthorizationSource': 'API',
        'Content-Type': 'application/json'
    }
    """
}
```

### 3. Validation Errors

**Error:**
```
date_of_birth must be a valid date
```

**Using error_decoder:**
```python
solution = error_decoder(
    error_message="date_of_birth must be a valid date"
)

# Returns:
{
    "error_type": "VALIDATION_ERROR", 
    "plain_english": "The date_of_birth field expects a date in YYYY-MM-DD format.",
    "possible_solutions": [
        "Use ISO 8601 date format: YYYY-MM-DD",
        "Example: '1990-01-15' instead of '01/15/1990'",
        "Ensure the date is not in the future",
        "Check for timezone issues"
    ],
    "example_fix": """
    # Correct format:
    {
        "dateOfBirth": "1990-01-15"
    }
    
    # Common mistakes:
    # "01/15/1990" - Wrong format
    # "1990-1-15" - Missing leading zeros
    # "15-01-1990" - Wrong order
    """
}
```

## Debugging Workflows

### Workflow 1: Field Not Found

When you get a field error, use this debugging flow:

```python
# 1. Decode the error
error = "Cannot query field 'patient_email' on type 'Patient'"
solution = error_decoder(error_message=error)

# 2. Search for the correct field
search_results = search_schema(
    search_term="email",
    type_filter="field"
)

# 3. Introspect the type
patient_type = introspect_type(type_name="Patient")

# 4. Find the correct field name
email_field = next(
    (f for f in patient_type.fields if "email" in f.name.lower()),
    None
)
# Result: field is actually called 'email', not 'patient_email'
```

### Workflow 2: Invalid Input

Debug input validation errors:

```python
# 1. Decode the validation error
error = "Input validation failed"
solution = error_decoder(error_message=error)

# 2. Introspect the input type
input_type = introspect_type(type_name="CreatePatientInput")

# 3. Check required fields
required_fields = [
    f.name for f in input_type.fields 
    if f.type.kind == "NON_NULL"
]

# 4. Get a working example
example = code_examples(
    operation="create_patient",
    language="javascript"
)
```

### Workflow 3: Permission Errors

Debug authorization issues:

```python
# 1. Decode the auth error
error = "Forbidden: Insufficient permissions"
solution = error_decoder(error_message=error)

# 2. Check operation requirements
operation_info = search_schema(
    search_term="createProvider",
    type_filter="mutation"
)

# 3. Review auth examples
auth_example = code_examples(
    operation="authentication",
    language="python"
)

# 4. Verify headers
headers_template = query_templates(
    workflow="authentication",
    include_variables=True
)
```

## Complex Debugging Scenarios

### Scenario 1: Nested Field Errors

**Error:**
```
Cannot query field 'address' on type 'Patient'. Did you mean 'addresses'?
```

**Debugging approach:**
```python
# 1. Decode error
solution = error_decoder(error_message=error)

# 2. Explore nested structure
patient = introspect_type("Patient")
address_field = next(f for f in patient.fields if "address" in f.name.lower())

# 3. Check if it's a list
if address_field.type.kind == "LIST":
    # It's 'addresses' (plural), not 'address'
    
# 4. Introspect the Address type
address_type = introspect_type("Address")

# 5. Build correct query
correct_query = """
query {
  patient(id: "123") {
    addresses {  # Note: plural
      line1
      city
      state
    }
  }
}
"""
```

### Scenario 2: Missing Required Fields

**Error:**
```
Field 'phoneNumber' of required type 'String!' was not provided
```

**Debugging approach:**
```python
# 1. Understand the error
solution = error_decoder(error_message=error)

# 2. Get all required fields
input_type = introspect_type("CreatePatientInput")
required = [
    f.name for f in input_type.fields 
    if f.type.kind == "NON_NULL"
]

# 3. Get a complete example
template = query_templates(
    workflow="patient_management",
    include_variables=True
)

# 4. Build complete input
complete_input = {
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com",
    "phoneNumber": "+1234567890",  # This was missing
    "dateOfBirth": "1990-01-01"
}
```

### Scenario 3: Type Mismatches

**Error:**
```
Expected type 'Int', found "twenty"
```

**Debugging approach:**
```python
# 1. Decode type error
solution = error_decoder(error_message=error)

# 2. Check field type
type_info = introspect_type("Appointment")
duration_field = next(f for f in type_info.fields if f.name == "duration")
# Shows: duration: Int (expects number, not string)

# 3. Get proper usage example
example = code_examples(
    operation="create_appointment",
    language="javascript"
)

# 4. Fix the type
correct_value = 20  # Not "twenty"
```

## Error Patterns and Solutions

### Pattern 1: Casing Issues

GraphQL is case-sensitive. Common mistakes:

```python
# Wrong casing examples
errors = [
    "Cannot query field 'firstname'",  # Should be firstName
    "Cannot query field 'DateOfBirth'", # Should be dateOfBirth
    "Unknown type 'patient'"            # Should be Patient
]

for error in errors:
    solution = error_decoder(error_message=error)
    # Each returns specific casing guidance
```

### Pattern 2: Plural vs Singular

Many relationships are plural:

```python
# Common plural mistakes
plural_errors = {
    "address": "addresses",
    "phoneNumber": "phoneNumbers", 
    "provider": "providers",
    "appointment": "appointments"
}

# Debug approach
for singular, plural in plural_errors.items():
    # Search for both
    singular_results = search_schema(singular)
    plural_results = search_schema(plural)
    
    # Compare match counts
    # Usually plural has more matches for lists
```

### Pattern 3: Deprecated Fields

```python
# When using deprecated fields
error = "Field 'phone' is deprecated. Use 'phoneNumber' instead"

# Debug approach
solution = error_decoder(error_message=error)

# Find all deprecated fields
type_info = introspect_type(
    type_name="Patient",
    include_deprecated=True
)

deprecated = [
    f for f in type_info.fields 
    if f.isDeprecated
]
```

## Advanced Debugging Techniques

### 1. Query Complexity Errors

```python
# Error: Query too complex
error = "Query complexity of 1500 exceeds maximum of 1000"

# Debug approach
# 1. Decode error
solution = error_decoder(error_message=error)

# 2. Simplify query
# - Remove unnecessary nested fields
# - Use pagination
# - Split into multiple queries

# 3. Get optimization tips
performance_tips = query_templates(
    workflow="performance_optimization"
)
```

### 2. Rate Limiting Errors

```python
# Error: Rate limit exceeded
error = "API rate limit exceeded. Try again in 60 seconds"

# Debug approach
solution = error_decoder(error_message=error)

# Solutions:
# - Implement exponential backoff
# - Batch operations
# - Cache responses
# - Use webhooks for real-time updates
```

### 3. Timeout Errors

```python
# Error: Query timeout
error = "Query exceeded 30 second timeout"

# Debug approach
# 1. Decode error
solution = error_decoder(error_message=error)

# 2. Optimize query
# - Reduce field selection
# - Add pagination limits
# - Remove deep nesting

# 3. Get efficient query patterns
efficient_queries = query_templates(
    workflow="performance"
)
```

## Debugging Best Practices

### 1. Always Start with error_decoder

```python
# Good practice
def handle_graphql_error(error):
    # First, decode the error
    solution = error_decoder(error_message=str(error))
    
    # Then take action based on error type
    if solution["error_type"] == "FIELD_NOT_FOUND":
        # Use search_schema to find correct field
        pass
    elif solution["error_type"] == "AUTHENTICATION_ERROR":
        # Check auth setup
        pass
    elif solution["error_type"] == "VALIDATION_ERROR":
        # Fix input format
        pass
```

### 2. Use Multiple Tools Together

```python
def comprehensive_debug(error_message):
    """Use all MCP tools for thorough debugging"""
    
    # 1. Decode error
    decoded = error_decoder(error_message=error_message)
    
    # 2. Search for related elements
    search_term = extract_search_term(error_message)
    search_results = search_schema(search_term)
    
    # 3. Introspect mentioned types
    type_name = extract_type_name(error_message)
    if type_name:
        type_info = introspect_type(type_name)
    
    # 4. Get working examples
    operation = extract_operation(error_message)
    if operation:
        example = code_examples(
            operation=operation,
            language="javascript"
        )
    
    return {
        "error_analysis": decoded,
        "related_schema": search_results,
        "type_details": type_info,
        "working_example": example
    }
```

### 3. Build Error Recovery

```python
def with_error_recovery(operation):
    """Wrap operations with smart error recovery"""
    
    try:
        result = operation()
        return result
        
    except GraphQLError as e:
        # Decode error
        solution = error_decoder(error_message=str(e))
        
        # Attempt automatic recovery
        if solution["error_type"] == "FIELD_NOT_FOUND":
            # Try with corrected field name
            corrected_operation = apply_field_correction(
                operation, 
                solution["example_fix"]
            )
            return corrected_operation()
            
        elif solution["error_type"] == "VALIDATION_ERROR":
            # Try with fixed format
            fixed_input = apply_validation_fix(
                operation,
                solution["example_fix"]
            )
            return operation(fixed_input)
            
        else:
            # Can't auto-recover, provide guidance
            raise EnhancedError(e, solution)
```

## Common Error Reference

### Authentication/Authorization

| Error | Cause | Solution |
|-------|-------|----------|
| "Not authorized" | Missing auth headers | Add Authorization and AuthorizationSource headers |
| "Invalid API key" | Wrong or expired key | Verify API key is active |
| "Insufficient permissions" | Role-based access | Check user role requirements |

### Field Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Cannot query field X" | Field doesn't exist | Use search_schema to find correct name |
| "Field X is deprecated" | Using old field | Check deprecation message for alternative |
| "Unknown argument X" | Invalid parameter | Introspect type for valid arguments |

### Validation Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Invalid date format" | Wrong date format | Use YYYY-MM-DD format |
| "Invalid email" | Email validation | Ensure valid email format |
| "Required field missing" | Missing input | Check all non-null fields |

### Type Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Expected type X, found Y" | Type mismatch | Convert to expected type |
| "Unknown type X" | Type doesn't exist | Types are capitalized in GraphQL |
| "Cannot return null" | Non-null violation | Ensure field has value |

## Next Steps

Now that you can debug effectively:

1. **[Using MCP Tools](./using-mcp-tools.md)** - Back to overview
2. **[Search and Discover](./search-and-discover.md)** - Find what you need
3. **[Query Generation](./query-generation.md)** - Build correct queries

Remember: Good debugging starts with understanding the error. The error_decoder tool gives you that understanding instantly!