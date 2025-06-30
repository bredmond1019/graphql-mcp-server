# Configuration Guide

Complete guide to configuring the Healthie MCP Server for different environments and use cases.

## 🔧 Configuration Overview

The Healthie MCP Server uses a two-tier configuration system:
1. **Application Settings** - Runtime configuration via environment variables
2. **Tool Configuration** - Behavior configuration via YAML files

## 🌍 Environment Variables

### Required Settings

```bash
# Healthie API endpoint (required)
export HEALTHIE_API_URL="https://staging-api.gethealthie.com/graphql"
```

### Optional Settings

```bash
# Authentication
export HEALTHIE_API_KEY="your-api-key-here"

# Schema caching
export SCHEMA_DIR="./schemas"
export CACHE_ENABLED="true"
export CACHE_DURATION_HOURS="24"

# Logging
export LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
export DEBUG_MODE="false"

# Network settings
export REQUEST_TIMEOUT="30"
export MAX_RETRIES="3"
```

### Environment-Specific Configurations

#### Development Environment
```bash
# .env.development
HEALTHIE_API_URL="https://staging-api.gethealthie.com/graphql"
HEALTHIE_API_KEY=""  # Optional for development
CACHE_ENABLED="true"
CACHE_DURATION_HOURS="1"  # Shorter cache for development
LOG_LEVEL="DEBUG"
DEBUG_MODE="true"
```

#### Staging Environment
```bash
# .env.staging
HEALTHIE_API_URL="https://staging-api.gethealthie.com/graphql"
HEALTHIE_API_KEY="staging-api-key"
CACHE_ENABLED="true"
CACHE_DURATION_HOURS="6"
LOG_LEVEL="INFO"
DEBUG_MODE="false"
```

#### Production Environment
```bash
# .env.production
HEALTHIE_API_URL="https://api.gethealthie.com/graphql"
HEALTHIE_API_KEY="production-api-key"
CACHE_ENABLED="true"
CACHE_DURATION_HOURS="24"
LOG_LEVEL="WARNING"
DEBUG_MODE="false"
REQUEST_TIMEOUT="60"
MAX_RETRIES="5"
```

## 📁 YAML Configuration Files

Tool behavior is configured via YAML files in `src/healthie_mcp/config/data/`:

### `queries.yaml` - Query Templates
```yaml
patient_management:
  - name: "Get Patient Details"
    description: "Retrieve comprehensive patient information"
    query: |
      query GetPatient($id: ID!) {
        patient(id: $id) {
          id
          firstName
          lastName
          email
          dateOfBirth
        }
      }
    variables:
      id: "patient-123"
    required_variables: ["id"]
    optional_variables: []
    notes: "Include only necessary fields for HIPAA compliance"
```

### `patterns.yaml` - Healthcare Patterns
```yaml
patient_workflows:
  - name: "Patient Registration"
    fhir_mapping: "Patient"
    healthie_types: ["Patient", "PatientProfile"]
    description: "Standard patient onboarding workflow"
    compliance_notes:
      - "HIPAA: Minimum necessary principle"
      - "Require explicit consent for data collection"
    workflow_steps:
      - "Identity verification"
      - "Demographics collection"
      - "Insurance verification"
      - "Consent management"
```

### `validation.yaml` - Validation Rules
```yaml
contact_information:
  email:
    pattern: "^[^@]+@[^@]+\\.[^@]+$"
    required: true
    description: "Valid email address format"
    example: "patient@example.com"
    error_message: "Please enter a valid email address"
  
  phone:
    pattern: "^\\+?1?[0-9]{10}$"
    required: false
    description: "US phone number format"
    example: "+1234567890"
    error_message: "Phone number must be 10 digits"

medical_identifiers:
  npi:
    pattern: "^\\d{10}$"
    description: "National Provider Identifier"
    example: "1234567890"
    validation_notes: "10-digit numeric identifier for healthcare providers"
```

### `errors.yaml` - Error Solutions
```yaml
authentication_errors:
  - pattern: "401 Unauthorized"
    explanation: "Invalid or missing API key"
    common_causes:
      - "API key not set in environment"
      - "Invalid API key format"
      - "Expired API key"
    solutions:
      - "Check HEALTHIE_API_KEY environment variable"
      - "Verify API key with Healthie support"
      - "Regenerate API key if expired"
    code_examples:
      - "export HEALTHIE_API_KEY='your-valid-key'"
```

### `workflows.yaml` - Workflow Sequences
```yaml
patient_intake:
  - name: "Complete Patient Intake"
    description: "End-to-end patient onboarding process"
    estimated_duration: "10-15 minutes"
    steps:
      - step_number: 1
        name: "Identity Verification"
        description: "Verify patient identity and check for existing records"
        queries: ["searchPatients"]
        validation_required: ["email", "dateOfBirth"]
        next_step_conditions:
          - "if_exists: update_existing"
          - "if_new: create_patient"
```

### `performance.yaml` - Performance Rules
```yaml
query_optimization:
  complexity_thresholds:
    low: 10
    medium: 25
    high: 50
    critical: 100
  
  depth_limits:
    recommended: 5
    maximum: 10
  
  field_count_guidelines:
    list_queries: 10
    detail_queries: 25
    dashboard_queries: 15

healthcare_specific:
  patient_queries:
    recommended_fields:
      - "id"
      - "firstName" 
      - "lastName"
      - "email"
    avoid_in_lists:
      - "medicalHistory"
      - "clinicalNotes"
      - "prescriptions"
```

## 🛠️ Customization Examples

### Adding Custom Query Templates

1. **Edit `queries.yaml`:**
```yaml
custom_workflows:
  - name: "Custom Patient Search"
    description: "Search patients with custom criteria"
    query: |
      query CustomPatientSearch($criteria: MyCustomInput!) {
        customPatientSearch(criteria: $criteria) {
          id
          name
          customField
        }
      }
    variables:
      criteria:
        customField: "value"
```

2. **Test the new template:**
```bash
uv run python -c "
from src.healthie_mcp.tools.query_templates import QueryTemplatesTool
from src.healthie_mcp.schema_manager import SchemaManager
tool = QueryTemplatesTool(SchemaManager('', '.'))
result = tool.execute(workflow='custom_workflows')
print(result.templates[0].name)
"
```

### Adding Custom Validation Rules

1. **Edit `validation.yaml`:**
```yaml
custom_healthcare:
  medical_record_number:
    pattern: "^MRN\\d{8}$"
    description: "Medical record number with MRN prefix"
    example: "MRN12345678"
    validation_notes: "Must start with 'MRN' followed by 8 digits"
```

2. **Test the validation:**
```bash
uv run python -c "
from src.healthie_mcp.config.loader import get_config_loader
loader = get_config_loader()
validation = loader.load_validation()
print(validation['custom_healthcare']['medical_record_number'])
"
```

### Creating Environment-Specific Configs

For different environments, you can override YAML configs:

```bash
# Development - use local overrides
cp src/healthie_mcp/config/data/queries.yaml src/healthie_mcp/config/data/queries.dev.yaml
# Edit queries.dev.yaml with development-specific queries

# Update config loader to use environment-specific files
export CONFIG_ENVIRONMENT="dev"
```

## 🔒 Security Configuration

### API Key Management

**Development:**
```bash
# Use environment file (not committed to git)
echo "HEALTHIE_API_KEY=dev-key" >> .env.local
source .env.local
```

**Production:**
```bash
# Use secure secret management
# Example with AWS Secrets Manager
export HEALTHIE_API_KEY=$(aws secretsmanager get-secret-value --secret-id healthie-api-key --query SecretString --output text)
```

### HIPAA Compliance Settings

```bash
# Enable audit logging
export ENABLE_AUDIT_LOGGING="true"
export AUDIT_LOG_FILE="/secure/logs/healthie-mcp-audit.log"

# Disable debug logging in production
export LOG_LEVEL="WARNING"
export DEBUG_MODE="false"

# Secure cache directory
export SCHEMA_DIR="/secure/cache/schemas"
```

### Access Control

Configure field-level access in your application:

```yaml
# Add to patterns.yaml
access_control:
  patient_data:
    public_fields: ["id", "firstName", "lastName"]
    protected_fields: ["ssn", "medicalHistory", "clinicalNotes"]
    admin_only_fields: ["internalNotes", "billingInfo"]
```

## 🚀 Performance Configuration

### Caching Strategy

```bash
# Aggressive caching for production
export CACHE_ENABLED="true"
export CACHE_DURATION_HOURS="24"

# Conservative caching for development  
export CACHE_DURATION_HOURS="1"

# Disable caching for testing
export CACHE_ENABLED="false"
```

### Network Optimization

```bash
# High-latency environments
export REQUEST_TIMEOUT="120"
export MAX_RETRIES="5"

# Low-latency environments
export REQUEST_TIMEOUT="10"
export MAX_RETRIES="2"
```

### Memory Management

```bash
# Large healthcare organizations
export MAX_SCHEMA_SIZE="10MB"
export CACHE_MAX_ENTRIES="1000"

# Small clinics
export MAX_SCHEMA_SIZE="1MB"
export CACHE_MAX_ENTRIES="100"
```

## 📊 Monitoring Configuration

### Logging Configuration

```bash
# Structured logging for production
export LOG_FORMAT="json"
export LOG_FILE="/var/log/healthie-mcp.log"

# Human-readable logging for development
export LOG_FORMAT="text"
export LOG_FILE=""  # stdout
```

### Metrics Collection

```bash
# Enable metrics collection
export ENABLE_METRICS="true"
export METRICS_ENDPOINT="http://prometheus:9090"

# Health check configuration
export HEALTH_CHECK_INTERVAL="30"
export HEALTH_CHECK_TIMEOUT="5"
```

## 🧪 Testing Configuration

### Test Environment Setup

```bash
# Test-specific settings
export HEALTHIE_API_URL="http://localhost:4000/graphql"  # Mock server
export CACHE_ENABLED="false"  # Always fresh data in tests
export LOG_LEVEL="CRITICAL"  # Minimal logging in tests
export DEBUG_MODE="false"
```

### Mock Configuration

For testing without real API access:

```yaml
# Add to queries.yaml
test_data:
  - name: "Mock Patient Query"
    description: "Test query with mock data"
    query: "{ mockPatient { id name } }"
    mock_response:
      mockPatient:
        id: "test-123"
        name: "Test Patient"
```

## 📋 Configuration Validation

### Validate Current Configuration

```bash
# Test all configuration
uv run python examples/scripts/development-tools/test-basic-imports.py

# Test specific configuration
uv run python -c "
from src.healthie_mcp.config.settings import get_settings
settings = get_settings()
print('✅ Configuration valid')
print(f'API URL: {settings.healthie_api_url}')
print(f'Cache: {settings.cache_enabled}')
"
```

### Required vs Optional Settings

| Setting | Required | Default | Impact if Missing |
|---------|----------|---------|-------------------|
| `HEALTHIE_API_URL` | ✅ | staging URL | Server won't start |
| `HEALTHIE_API_KEY` | ❌ | None | Schema tools limited |
| `SCHEMA_DIR` | ❌ | `schemas` | Uses default directory |
| `CACHE_ENABLED` | ❌ | `true` | Performance impact |
| `LOG_LEVEL` | ❌ | `INFO` | Default logging |

## 🔄 Configuration Hot-Reloading

YAML configurations are cached but can be reloaded:

```python
# Force reload configuration
from src.healthie_mcp.config.loader import get_config_loader
loader = get_config_loader()
loader.clear_cache()  # Reload from files
```

This allows updating tool behavior without restarting the server, useful for:
- Adding new query templates
- Updating validation rules
- Modifying workflow sequences
- Adjusting performance thresholds