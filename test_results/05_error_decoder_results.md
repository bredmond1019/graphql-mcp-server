# Tool: error_decoder

*Tested on: 2025-07-02 22:15:32*

## Purpose
Decode GraphQL error messages and get actionable solutions.

## Test 1: Field doesn't exist error

### Input
```json
{
  "tool": "error_decoder",
  "arguments": {
    "error_message": "Field 'role' doesn't exist on type 'User'",
    "include_compliance_notes": true
  }
}
```

### Output
```json
{
  "error_type": "unknown",
  "plain_english": "An unexpected error occurred that doesn't match common patterns.",
  "solution_count": 1,
  "solutions": [
    {
      "problem": "General error",
      "solution": "Check the Healthie API documentation for more details about this error"
    }
  ],
  "is_healthcare_specific": false
}
```

### Analysis
Decoded error as 'unknown' and provided 1 solutions. This helps developers quickly resolve common API errors.

## Test 2: Unauthorized error

### Input
```json
{
  "tool": "error_decoder",
  "arguments": {
    "error_message": "Unauthorized: Must be logged in",
    "include_compliance_notes": true
  }
}
```

### Output
```json
{
  "error_type": "authentication",
  "plain_english": "Your API key is missing, invalid, or expired. The server cannot verify your identity.",
  "solution_count": 2,
  "solutions": [
    {
      "problem": "Invalid or missing API key",
      "solution": "Check that your HEALTHIE_API_KEY environment variable is set correctly"
    },
    {
      "problem": "Expired API key",
      "solution": "Generate a new API key from your Healthie dashboard"
    }
  ],
  "is_healthcare_specific": false
}
```

### Analysis
Decoded error as 'authentication' and provided 2 solutions. This helps developers quickly resolve common API errors.

## Test 3: Validation failed error

### Input
```json
{
  "tool": "error_decoder",
  "arguments": {
    "error_message": "Validation failed: Email already exists",
    "include_compliance_notes": true
  }
}
```

### Output
```json
{
  "error_type": "validation",
  "plain_english": "The data you provided doesn't meet the required format or business rules. Some fields may be missing, invalid, or contain incorrect values. The issue seems to be related to email validation or formatting.",
  "solution_count": 1,
  "solutions": [
    {
      "problem": "General error",
      "solution": "Check the Healthie API documentation for more details about this error"
    }
  ],
  "is_healthcare_specific": false
}
```

### Analysis
Decoded error as 'validation' and provided 1 solutions. This helps developers quickly resolve common API errors.

## Summary
- Total tests: 3
- Successful: 3
- Failed: 0

The error_decoder tool translates cryptic error messages into understandable explanations with actionable solutions. This reduces debugging time and improves developer experience.
