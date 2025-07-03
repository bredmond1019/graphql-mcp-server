# Error Handling Guide

Comprehensive guide to understanding, handling, and resolving errors in the Healthie MCP Server.

## 🚨 Error Categories

### 1. Configuration Errors

**`ConfigurationError`** - Issues with server configuration

```json
{
  "error": {
    "type": "ConfigurationError",
    "message": "Invalid API URL format",
    "details": {
      "field": "healthie_api_url",
      "value": "invalid-url",
      "expected": "Valid HTTP/HTTPS URL"
    }
  }
}
```

**Common causes:**
- Invalid environment variables
- Missing required configuration
- Malformed YAML files

**Resolution:**
```bash
# Check configuration
uv run python -c "from src.healthie_mcp.config.settings import get_settings; print(get_settings())"

# Validate YAML files
uv run python -c "from src.healthie_mcp.config.loader import get_config_loader; get_config_loader().load_queries()"
```

### 2. Tool Execution Errors

**`ToolError`** - Issues during tool execution

```json
{
  "error": {
    "type": "ToolError", 
    "message": "Failed to execute search_schema",
    "details": {
      "tool_name": "search_schema",
      "parameters": {"query": "invalid[regex"},
      "cause": "Invalid regex pattern"
    }
  }
}
```

**Common causes:**
- Invalid tool parameters
- Regex syntax errors
- Missing required fields

**Resolution:**
```bash
# Test tool parameters
search_schema query="patient" type_filter="type"

# Validate regex patterns
python -c "import re; re.compile('your-pattern')"
```

### 3. Schema Errors

**`SchemaError`** - GraphQL schema related issues

```json
{
  "error": {
    "type": "SchemaError",
    "message": "Schema not available",
    "details": {
      "endpoint": "https://staging-api.gethealthie.com/graphql",
      "http_status": 404,
      "suggestion": "Check API endpoint and authentication"
    }
  }
}
```

**Common causes:**
- Invalid API endpoint
- Network connectivity issues  
- Missing authentication

**Resolution:**
```bash
# Test connectivity
curl -I https://staging-api.gethealthie.com/graphql

# Check authentication
export HEALTHIE_API_KEY="<your-api-key>"

# Use cached schema if available
export CACHE_ENABLED="true"
```

### 4. Validation Errors

**`ValidationError`** - Data validation failures

```json
{
  "error": {
    "type": "ValidationError",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "value": "invalid-email",
      "expected": "Valid email format",
      "pattern": "^[^@]+@[^@]+\\.[^@]+$"
    }
  }
}
```

**Common causes:**
- Invalid data formats
- Missing required fields
- Pattern mismatches

**Resolution:**
```bash
# Check validation rules
input_validation field_type="contact_information"

# Test specific patterns
python -c "import re; print(re.match(r'^[^@]+@[^@]+\.[^@]+$', 'test@example.com'))"
```

## 🔧 Error Resolution Patterns

### Network Error Recovery

```python
import time
import requests
from typing import Optional

def retry_with_backoff(func, max_retries: int = 3, backoff_factor: float = 1.0):
    """Retry function with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise
            wait_time = backoff_factor * (2 ** attempt)
            time.sleep(wait_time)

# Usage
def fetch_schema():
    response = requests.get("https://staging-api.gethealthie.com/graphql")
    response.raise_for_status()
    return response.text

schema = retry_with_backoff(fetch_schema)
```

### Graceful Degradation

```python
def search_with_fallback(query: str, type_filter: str = "any"):
    """Search with graceful degradation"""
    try:
        # Try full schema search
        return search_schema(query=query, type_filter=type_filter)
    except SchemaError:
        # Fallback to cached schema
        try:
            return search_cached_schema(query=query)
        except Exception:
            # Fallback to basic search
            return basic_pattern_search(query=query)
```

### Input Sanitization

```python
import re
from typing import Dict, Any

def sanitize_tool_input(tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize and validate tool input parameters"""
    sanitized = {}
    
    for key, value in params.items():
        if key == "query" and isinstance(value, str):
            # Sanitize regex patterns
            try:
                re.compile(value)
                sanitized[key] = value
            except re.error:
                raise ValidationError(f"Invalid regex pattern: {value}")
        elif key == "type_filter":
            # Validate type filter
            valid_filters = {"query", "mutation", "type", "input", "enum", "any"}
            if value not in valid_filters:
                raise ValidationError(f"Invalid type_filter: {value}")
            sanitized[key] = value
        else:
            sanitized[key] = value
    
    return sanitized
```

## 🏥 Healthcare-Specific Error Handling

### HIPAA Compliance Errors

```json
{
  "error": {
    "type": "ComplianceError",
    "message": "Access to protected health information denied",
    "details": {
      "field": "medicalHistory",
      "user_role": "basic_user",
      "required_role": "healthcare_provider",
      "compliance_note": "HIPAA minimum necessary principle"
    }
  }
}
```

**Resolution:**
- Verify user permissions
- Request only necessary fields
- Implement role-based access control

### Medical Data Validation Errors

```json
{
  "error": {
    "type": "MedicalValidationError",
    "message": "Invalid medical identifier",
    "details": {
      "field": "npi",
      "value": "invalid123",
      "expected": "10-digit numeric identifier",
      "regulation": "CMS National Provider Identifier standard"
    }
  }
}
```

**Resolution:**
```bash
# Check medical validation rules
input_validation field_type="medical_identifiers"

# Validate specific formats
python -c "
import re
npi_pattern = r'^\d{10}$'
print(re.match(npi_pattern, '1234567890'))
"
```

### Clinical Data Access Errors

```json
{
  "error": {
    "type": "ClinicalAccessError",
    "message": "Clinical data requires explicit consent",
    "details": {
      "patient_id": "patient-123",
      "data_type": "clinical_notes",
      "consent_status": "not_provided",
      "required_consent": "clinical_data_access"
    }
  }
}
```

## 📊 Error Monitoring & Logging

### Structured Error Logging

```python
import json
import logging
from datetime import datetime

class HealthcareErrorLogger:
    def __init__(self):
        self.logger = logging.getLogger('healthie.errors')
        handler = logging.FileHandler('healthie_errors.log')
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_error(self, error: Exception, context: dict = None):
        """Log errors with healthcare context"""
        error_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'error_type': error.__class__.__name__,
            'message': str(error),
            'context': context or {},
            # Remove PHI from logs
            'sanitized': True
        }
        
        # Remove potential PHI
        if 'patient_id' in error_data['context']:
            error_data['context']['patient_id'] = 'REDACTED'
        
        self.logger.error(json.dumps(error_data))

# Usage
error_logger = HealthcareErrorLogger()
try:
    result = search_schema(query="patient")
except Exception as e:
    error_logger.log_error(e, {'tool': 'search_schema', 'user': 'admin'})
```

### Error Metrics Collection

```python
from collections import defaultdict
from typing import Dict

class ErrorMetrics:
    def __init__(self):
        self.error_counts = defaultdict(int)
        self.error_patterns = defaultdict(list)
    
    def record_error(self, error_type: str, message: str, tool_name: str = None):
        """Record error for metrics"""
        self.error_counts[error_type] += 1
        
        if tool_name:
            self.error_patterns[tool_name].append(error_type)
    
    def get_error_summary(self) -> Dict:
        """Get error summary for monitoring"""
        return {
            'total_errors': sum(self.error_counts.values()),
            'error_types': dict(self.error_counts),
            'tools_with_errors': dict(self.error_patterns)
        }

# Usage
metrics = ErrorMetrics()
metrics.record_error('ValidationError', 'Invalid email', 'input_validation')
print(metrics.get_error_summary())
```

## 🛠️ Debugging Tools

### Error Reproduction Script

```python
#!/usr/bin/env python3
"""
Error reproduction script for debugging
"""

def reproduce_error(tool_name: str, params: dict):
    """Reproduce specific error conditions"""
    print(f"Reproducing error for {tool_name} with params: {params}")
    
    try:
        # Import and execute tool
        module = __import__(f'healthie_mcp.tools.{tool_name}', fromlist=[tool_name])
        # Execute with problematic parameters
        result = getattr(module, 'execute')(**params)
        print("No error occurred - issue may be resolved")
        return result
    except Exception as e:
        print(f"Error reproduced: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None

# Example usage
reproduce_error('search_schema', {'query': 'invalid[regex', 'type_filter': 'invalid'})
```

### Error Analysis Tool

```bash
# Create error analysis script
cat > analyze_errors.py << 'EOF'
import json
import re
from collections import Counter

def analyze_error_log(log_file: str):
    """Analyze error patterns from log file"""
    error_types = Counter()
    error_messages = []
    
    with open(log_file, 'r') as f:
        for line in f:
            try:
                error_data = json.loads(line.split(' - ', 1)[1])
                error_types[error_data['error_type']] += 1
                error_messages.append(error_data['message'])
            except:
                continue
    
    print("Error Type Distribution:")
    for error_type, count in error_types.most_common():
        print(f"  {error_type}: {count}")
    
    print("\nCommon Error Patterns:")
    message_patterns = Counter()
    for msg in error_messages:
        # Extract common patterns
        if 'invalid' in msg.lower():
            message_patterns['Invalid input'] += 1
        elif 'not found' in msg.lower():
            message_patterns['Resource not found'] += 1
        elif 'timeout' in msg.lower():
            message_patterns['Network timeout'] += 1
    
    for pattern, count in message_patterns.most_common():
        print(f"  {pattern}: {count}")

if __name__ == "__main__":
    analyze_error_log('healthie_errors.log')
EOF

python analyze_errors.py
```

## 🔍 Common Error Scenarios

### Tool Parameter Validation

```python
def validate_search_parameters(query: str, type_filter: str = "any", context_lines: int = 3):
    """Validate search_schema parameters"""
    errors = []
    
    # Validate query
    if not query or not query.strip():
        errors.append("Query cannot be empty")
    
    try:
        re.compile(query)
    except re.error as e:
        errors.append(f"Invalid regex pattern: {e}")
    
    # Validate type_filter
    valid_filters = {"any", "query", "mutation", "type", "input", "enum", "interface", "union", "scalar"}
    if type_filter not in valid_filters:
        errors.append(f"Invalid type_filter: {type_filter}")
    
    # Validate context_lines
    if not isinstance(context_lines, int) or context_lines < 0 or context_lines > 10:
        errors.append("Context lines must be an integer between 0 and 10")
    
    if errors:
        raise ValidationError("; ".join(errors))
    
    return {"query": query, "type_filter": type_filter, "context_lines": context_lines}
```

### Schema Access Patterns

```python
def safe_schema_access(schema_manager, operation_name: str):
    """Safely access schema with error handling"""
    try:
        schema_content = schema_manager.get_schema_content()
        if not schema_content:
            raise SchemaError("Schema content is empty")
        return schema_content
    except Exception as e:
        # Log the error
        print(f"Schema access failed for {operation_name}: {e}")
        
        # Try fallback options
        try:
            # Try cached schema
            cached_path = schema_manager.cache_file
            if cached_path.exists():
                return cached_path.read_text()
        except Exception:
            pass
        
        # Return empty schema with warning
        return ""
```

### Healthcare Data Validation

```python
def validate_healthcare_data(data: dict, field_type: str):
    """Validate healthcare-specific data formats"""
    validation_rules = {
        'npi': r'^\d{10}$',
        'medical_record_number': r'^[A-Z]{2}\d{6}$',
        'phone_number': r'^\+?1?[0-9]{10}$',
        'email': r'^[^@]+@[^@]+\.[^@]+$'
    }
    
    errors = []
    
    for field_name, field_value in data.items():
        if field_name in validation_rules:
            pattern = validation_rules[field_name]
            if not re.match(pattern, str(field_value)):
                errors.append(f"Invalid {field_name}: {field_value}")
    
    if errors:
        raise MedicalValidationError("; ".join(errors))
    
    return True
```

## 📈 Error Prevention Best Practices

### 1. Input Validation
- Always validate user input before processing
- Use type hints and Pydantic models
- Implement regex pattern validation for healthcare data

### 2. Error Recovery
- Implement retry logic for network operations
- Provide fallback options for failed operations
- Cache successful results for offline access

### 3. Monitoring
- Log all errors with sufficient context
- Monitor error rates and patterns
- Set up alerts for critical error types

### 4. Documentation
- Document all possible error conditions
- Provide clear resolution steps
- Include example error scenarios

### 5. Testing
- Test error conditions explicitly
- Validate error messages and codes
- Test recovery mechanisms

This comprehensive error handling approach ensures robust, reliable operation of the Healthie MCP Server while maintaining healthcare compliance and providing clear guidance for issue resolution.