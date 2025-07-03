# Phase 3 Tools Documentation

This document provides comprehensive documentation for the 9 tools in Phase 3 that were tested and fixed.

## Table of Contents

1. [Input Validation Tool](#1-input-validation-tool)
2. [Performance Analyzer Tool](#2-performance-analyzer-tool)
3. [Healthcare Patterns Tool](#3-healthcare-patterns-tool)
4. [Rate Limit Advisor Tool](#4-rate-limit-advisor-tool)
5. [Field Usage Tool](#5-field-usage-tool)
6. [Integration Testing Tool](#6-integration-testing-tool)
7. [Webhook Configurator Tool](#7-webhook-configurator-tool)
8. [API Usage Analytics Tool](#8-api-usage-analytics-tool)
9. [Environment Manager Tool](#9-environment-manager-tool)

---

## 1. Input Validation Tool

### Purpose
Validates input data against GraphQL schema types with healthcare-specific validation rules.

### Key Features
- GraphQL type validation
- Healthcare identifier validation (NPI, DEA, MRN)
- Email and phone number validation
- Custom validation rules
- HIPAA-compliant field validation
- Strict and flexible validation modes

### Usage Example
```python
# Validate patient input data
result = validate_input(
    input_data={
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "phoneNumber": "+1-555-0123",
        "dateOfBirth": "1990-01-15",
        "npi": "1234567890"  # Healthcare provider NPI
    },
    expected_type="Patient",
    strict_mode=True,
    custom_rules=[
        {"field": "dateOfBirth", "rule": "date_format", "value": "YYYY-MM-DD"}
    ]
)
```

### Response Structure
```json
{
    "is_valid": true,
    "validation_errors": [],
    "field_validations": {
        "email": {"valid": true, "message": "Valid email format"},
        "phoneNumber": {"valid": true, "message": "Valid phone number"},
        "npi": {"valid": true, "message": "Valid NPI format"}
    },
    "warnings": [],
    "suggestions": [
        "Consider adding address validation for complete patient records"
    ]
}
```

### Healthcare-Specific Validations
- **NPI**: 10-digit National Provider Identifier
- **DEA**: DEA registration number format
- **MRN**: Medical Record Number patterns
- **SSN**: Social Security Number (with HIPAA warnings)
- **Insurance ID**: Various insurance identifier formats

---

## 2. Performance Analyzer Tool

### Purpose
Analyzes GraphQL queries for potential performance issues and provides optimization recommendations.

### Key Features
- N+1 query detection
- Nesting depth analysis
- Query complexity scoring
- Field usage analysis
- Execution time estimation
- Healthcare-specific optimizations

### Usage Example
```python
# Analyze a complex healthcare query
result = analyze_query_performance(
    query="""
    query GetPatientWithHistory {
        patient(id: "123") {
            id
            demographics {
                firstName
                lastName
                dateOfBirth
            }
            appointments(last: 100) {
                edges {
                    node {
                        id
                        provider {
                            name
                            specialty
                        }
                        notes {
                            content
                            attachments {
                                url
                            }
                        }
                    }
                }
            }
        }
    }
    """,
    include_suggestions=True
)
```

### Response Structure
```json
{
    "overall_score": 65,
    "complexity_score": 78,
    "issues": [
        {
            "issue_type": "n_plus_one",
            "severity": "high",
            "description": "Potential N+1 query on field 'appointments'",
            "location": "Field: appointments",
            "suggestion": "Use DataLoader or batch loading",
            "estimated_impact": "Could cause 1 + N database queries"
        }
    ],
    "total_issues": 3,
    "suggestions": [
        "Implement DataLoader pattern for related data",
        "Add pagination to limit result sets",
        "Cache frequently accessed provider data"
    ],
    "estimated_execution_time": "Moderate (500ms-2s)"
}
```

### Performance Metrics
- **Score 80-100**: Excellent performance
- **Score 60-79**: Good, minor optimizations possible
- **Score 40-59**: Moderate issues, optimization recommended
- **Score 0-39**: Significant issues, optimization required

---

## 3. Healthcare Patterns Tool

### Purpose
Provides comprehensive healthcare workflow patterns, implementation guides, and FHIR compatibility mappings.

### Key Features
- Pre-built healthcare workflows
- FHIR resource mappings
- Compliance considerations
- Multi-step implementation guides
- Best practices for healthcare data

### Usage Example
```python
# Get patient registration workflow
result = get_healthcare_patterns(
    pattern_type="patient_registration",
    include_examples=True,
    include_compliance=True,
    include_fhir_mappings=True
)
```

### Available Patterns
1. **Patient Registration**: Complete onboarding workflow
2. **Appointment Scheduling**: Booking and management
3. **Clinical Documentation**: Notes and forms
4. **Billing Workflow**: Claims and payments
5. **Prescription Management**: Medication workflows
6. **Lab Results**: Order and result handling
7. **Referral Management**: Provider referrals
8. **Telehealth**: Virtual visit workflows

### Response Structure
```json
{
    "pattern_name": "Patient Registration",
    "description": "Complete patient onboarding workflow",
    "category": "patient_management",
    "implementation_steps": [
        {
            "step": 1,
            "name": "Collect Demographics",
            "description": "Gather patient personal information",
            "required_fields": ["firstName", "lastName", "dateOfBirth"],
            "graphql_example": "mutation CreatePatient { ... }",
            "validation_rules": ["Email format", "Phone validation"]
        }
    ],
    "compliance_considerations": [
        "HIPAA: Ensure minimum necessary information",
        "Obtain consent before processing PHI"
    ],
    "fhir_mappings": {
        "patient": "Patient",
        "insurance": "Coverage",
        "provider": "Practitioner"
    }
}
```

---

## 4. Rate Limit Advisor Tool

### Purpose
Analyzes API usage patterns and provides recommendations for avoiding rate limits and optimizing costs.

### Key Features
- Usage pattern analysis
- Rate limit risk assessment
- Tier recommendations
- Cost projections
- Caching strategies
- Optimization suggestions

### Usage Example
```python
# Analyze API usage patterns
result = analyze_rate_limits(
    query_patterns=[
        "get_patient",
        "list_appointments", 
        "search_patients",
        "bulk_export"
    ],
    expected_requests_per_day=25000,
    peak_hour_percentage=25.0,
    concurrent_users=50,
    average_response_size_kb=10.0,
    include_cost_analysis=True
)
```

### Response Structure
```json
{
    "usage_patterns": [
        {
            "pattern_name": "Patient Management",
            "requests_per_minute": 17.36,
            "peak_requests_per_minute": 52.08,
            "complexity": "medium",
            "time_distribution": {...}
        }
    ],
    "forecast": {
        "daily_requests": 25000,
        "monthly_requests": 750000,
        "peak_hour_requests": 6250,
        "rate_limit_risk": "medium",
        "recommended_tier": "pro"
    },
    "optimization_tips": [
        {
            "title": "Implement Batch Operations",
            "description": "Replace individual API calls with batch operations",
            "impact": "Reduce API calls by up to 90%",
            "implementation_effort": "medium",
            "example_code": "..."
        }
    ],
    "cost_projections": [
        {
            "tier": "pro",
            "monthly_cost": 999,
            "annual_cost": 11988,
            "included_requests": 2000000,
            "overage_rate": 0.00006
        }
    ],
    "caching_strategies": [
        {
            "strategy_name": "Patient Demographics Caching",
            "cache_duration": "4 hours",
            "expected_reduction": "85% reduction",
            "considerations": ["HIPAA compliance required"]
        }
    ]
}
```

---

## 5. Field Usage Tool

### Purpose
Analyzes field usage patterns in GraphQL queries and provides optimization recommendations.

### Key Features
- Field usage statistics
- Overfetching detection
- Underfetching analysis
- Schema coverage reports
- Performance impact assessment

### Usage Example
```python
# Analyze field usage patterns
result = analyze_field_usage(
    queries=[
        "query GetPatient { patient { id firstName lastName email } }",
        "query GetPatientFull { patient { ...AllFields } }"
    ],
    time_range="week",
    include_recommendations=True
)
```

### Response Structure
```json
{
    "total_fields_available": 45,
    "fields_used": 12,
    "usage_percentage": 26.7,
    "most_used_fields": [
        {"field": "id", "usage_count": 1000, "percentage": 100},
        {"field": "firstName", "usage_count": 950, "percentage": 95}
    ],
    "unused_fields": ["middleName", "suffix", "preferredLanguage"],
    "overfetching_detected": true,
    "recommendations": [
        "Create specific field sets for common use cases",
        "Remove unused fields from queries",
        "Consider implementing field-level permissions"
    ],
    "performance_impact": "Reducing fields could save 60% bandwidth"
}
```

---

## 6. Integration Testing Tool

### Purpose
Generates comprehensive test scenarios and code for API integrations.

### Key Features
- Test scenario generation
- Multi-language test code
- Edge case coverage
- Healthcare-specific scenarios
- Mock data generation

### Usage Example
```python
# Generate integration tests
result = generate_integration_tests(
    operation_type="mutation",
    operation_name="createAppointment",
    test_framework="jest",
    include_edge_cases=True,
    include_mock_data=True
)
```

### Response Structure
```json
{
    "test_scenarios": [
        {
            "name": "Valid appointment creation",
            "description": "Test successful appointment booking",
            "type": "positive",
            "input": {...},
            "expected_output": {...},
            "test_code": "test('Valid appointment creation', async () => { ... })"
        },
        {
            "name": "Double booking prevention",
            "description": "Test conflict detection",
            "type": "negative",
            "input": {...},
            "expected_error": "TIME_SLOT_UNAVAILABLE"
        }
    ],
    "mock_data": {
        "patients": [...],
        "providers": [...],
        "availableSlots": [...]
    },
    "coverage_report": {
        "scenarios_generated": 8,
        "positive_tests": 3,
        "negative_tests": 5,
        "edge_cases": 2
    }
}
```

---

## 7. Webhook Configurator Tool

### Purpose
Helps configure secure webhooks for real-time event notifications from the Healthie platform.

### Key Features
- Webhook endpoint validation
- Security configuration
- Event mapping
- Retry policies
- Signature verification
- HIPAA-compliant setup

### Usage Example
```python
# Configure webhooks
result = webhook_configurator(
    action="configure",
    endpoint_url="https://api.example.com/webhooks/healthie",
    events=["patient.created", "appointment.updated", "payment.completed"],
    security_level="hipaa_compliant",
    custom_headers={"X-API-Key": "your-api-key"}
)
```

### Response Structure
```json
{
    "configuration": {
        "name": "Webhook for Patient Management Events",
        "endpoint_url": "https://api.example.com/webhooks/healthie",
        "security": {
            "signing_secret": "whsec_1234567890abcdef",
            "signature_header": "X-Healthie-Signature",
            "timestamp_tolerance_seconds": 120,
            "required_headers": ["X-Healthie-Event", "X-Healthie-Delivery"],
            "ip_whitelist": ["198.51.100.0/24"]
        },
        "event_filter": {
            "events": ["patient.created", "appointment.updated"],
            "patient_tags": ["vip", "chronic-care"],
            "provider_ids": ["prov_123", "prov_456"]
        },
        "retry_config": {
            "max_retries": 3,
            "retry_delay_seconds": 5,
            "exponential_backoff": true
        }
    },
    "validation_result": {
        "is_valid": true,
        "ssl_valid": true,
        "response_time_ms": 245
    },
    "recommendations": [
        "Implement request queuing for high-volume events",
        "Store webhook payloads for replay capability",
        "Monitor webhook delivery success rates"
    ]
}
```

### Security Levels
- **basic**: Simple signature verification
- **standard**: Signature + timestamp validation
- **enhanced**: Additional headers and user agent validation
- **hipaa_compliant**: Full security with audit logging

---

## 8. API Usage Analytics Tool

### Purpose
Provides comprehensive analytics for API usage patterns, performance metrics, and optimization insights.

### Key Features
- Usage pattern detection
- Performance metrics
- Cost analysis
- Trend identification
- Healthcare compliance tracking
- Optimization recommendations

### Usage Example
```python
# Analyze API usage
result = api_usage_analytics(
    time_range="month",
    operations=["getPatient", "listAppointments", "createNote"],
    metric_types=["response_time", "error_rate", "data_volume"],
    include_patterns=True,
    include_insights=True,
    include_healthcare_analysis=True
)
```

### Response Structure
```json
{
    "report": {
        "report_id": "rpt_123456",
        "time_range": "month",
        "total_requests": 750000,
        "unique_operations": 45,
        "average_response_time": 285,
        "error_rate": 0.02,
        "top_operations": [
            {"name": "getPatient", "count": 250000, "percentage": 33.3}
        ],
        "usage_patterns": [
            {
                "pattern_type": "peak_hours",
                "description": "High usage 10am-2pm weekdays",
                "frequency": 20,
                "impact": "high"
            }
        ],
        "performance_insights": [
            {
                "category": "performance",
                "title": "Slow queries detected",
                "impact_score": 8.5,
                "affected_operations": ["searchPatients"],
                "recommended_actions": ["Add pagination", "Optimize filters"]
            }
        ],
        "healthcare_compliance": {
            "phi_access_count": 500000,
            "encryption_compliance": 100,
            "audit_log_coverage": 99.8
        }
    },
    "quick_stats": {
        "requests_per_day": 25000,
        "peak_hour_load": 3500,
        "p95_response_time": 450
    },
    "critical_findings": [
        "High error rate on bulk operations",
        "PHI access patterns require review"
    ],
    "next_steps": [
        "Implement caching for top 3 operations",
        "Review and optimize slow queries",
        "Enable request batching"
    ]
}
```

---

## 9. Environment Manager Tool

### Purpose
Manages environment configurations, deployment processes, and security validations for healthcare applications.

### Key Features
- Environment configuration validation
- Deployment checklists
- Secret management
- Security validation
- Transition guides
- Compliance verification

### Usage Example
```python
# Validate production configuration
result = environment_manager(
    action="validate_config",
    environment="production",
    config={
        "api_url": "https://api.healthie.com/graphql",
        "api_key": "prod_key_encrypted",
        "ssl_cert": "/certs/production.pem",
        "log_level": "ERROR",
        "monitoring": True,
        "hipaa_mode": True
    }
)
```

### Response Structure
```json
{
    "validation_result": {
        "is_valid": true,
        "environment": "production",
        "validation_details": [
            {"field": "api_url", "status": "valid", "message": "HTTPS protocol verified"},
            {"field": "ssl_cert", "status": "valid", "message": "Certificate valid until 2025-12-31"},
            {"field": "hipaa_mode", "status": "valid", "message": "HIPAA compliance enabled"}
        ],
        "security_score": 95,
        "compliance_status": "compliant"
    },
    "deployment_checklist": [
        {"task": "Run all tests", "status": "pending", "required": true, "automated": true},
        {"task": "Backup database", "status": "pending", "required": true, "automated": true},
        {"task": "Update SSL certificates", "status": "completed", "required": true},
        {"task": "Verify HIPAA compliance", "status": "completed", "required": true}
    ],
    "recommendations": [
        "Enable database encryption at rest",
        "Configure automated security scanning",
        "Set up compliance audit logging"
    ],
    "warnings": [
        "Ensure PHI data is encrypted in transit and at rest",
        "Production deployments require approval from security team"
    ]
}
```

### Environment Types
- **development**: Local development with relaxed security
- **staging**: Pre-production testing environment
- **production**: Full security and compliance requirements
- **test**: Automated testing environment

---

## Integration Guide

### Adding Tools to MCP Server

To integrate these tools into the main MCP server:

1. Move tool files from `todo/` to main `tools/` directory
2. Update imports in each tool file
3. Register in `server.py`:

```python
# In server.py
from .tools.input_validation import setup_input_validation_tool
from .tools.performance_analyzer import setup_query_performance_tool
# ... import other tools

# Register tools
setup_input_validation_tool(mcp, schema_manager)
setup_query_performance_tool(mcp, schema_manager)
# ... register other tools
```

### Configuration Files

Each tool uses configuration from `config/data/`:
- `validation.yaml`: Validation rules and patterns
- `performance.yaml`: Performance thresholds
- `patterns.yaml`: Healthcare workflow patterns
- `webhooks.yaml`: Webhook event definitions
- `environments.yaml`: Environment configurations

### Best Practices

1. **Healthcare Compliance**: Always consider HIPAA when handling PHI
2. **Performance**: Use caching and batching for high-volume operations
3. **Security**: Implement proper authentication and encryption
4. **Testing**: Generate comprehensive test coverage
5. **Monitoring**: Track API usage and performance metrics