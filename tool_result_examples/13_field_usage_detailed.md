# Tool 13: field_usage - Detailed Test Results

*Generated on: 2025-07-03 00:35:00*

## Tool Overview

The Field Usage tool analyzes field usage patterns in GraphQL queries to identify overfetching, underfetching, and optimization opportunities. It helps developers reduce payload sizes and improve query performance.

## How to Use This Tool

### Python Usage

```python
from healthie_mcp.tools.field_usage import FieldUsageAnalyzer
from healthie_mcp.schema_manager import SchemaManager

# Initialize the tool
schema_manager = SchemaManager(api_endpoint='https://api.gethealthie.com/graphql')
analyzer = FieldUsageAnalyzer(schema_manager)

# Analyze field usage
result = analyzer.execute(
    queries=[
        "query { patient { id firstName lastName email phoneNumber address } }",
        "query { patient { id firstName lastName } }"
    ],
    time_range="week",
    include_recommendations=True
)
```

### Parameters

- **queries** (required): List of GraphQL queries to analyze
- **time_range** (optional): Time period for analysis ("hour", "day", "week", "month")
- **include_recommendations** (optional): Include optimization recommendations (default: True)
- **operation_names** (optional): Filter by specific operation names

## Test Summary

- **Total tests**: 4
- **Successful**: 4
- **Failed**: 0
- **Success rate**: 100.0%

## Detailed Test Results

### Test 1: Basic Field Usage Analysis

**Status**: ✅ Success

#### Input Parameters

```json
{
  "queries": [
    "query GetPatient { patient(id: \"123\") { id firstName lastName email phoneNumber dateOfBirth gender address insurance { id provider memberId } } }",
    "query GetPatientBasic { patient(id: \"123\") { id firstName lastName } }",
    "query GetPatientBasic { patient(id: \"123\") { id firstName lastName } }"
  ],
  "time_range": "day",
  "include_recommendations": true
}
```

#### Output

```json
{
  "analysis_period": {
    "start": "2025-07-02T00:00:00Z",
    "end": "2025-07-03T00:00:00Z",
    "total_queries_analyzed": 3
  },
  "field_statistics": {
    "patient": {
      "total_fields_available": 25,
      "fields_used": 10,
      "usage_percentage": 40.0,
      "field_details": [
        {
          "field": "id",
          "usage_count": 3,
          "usage_percentage": 100.0,
          "always_used": true
        },
        {
          "field": "firstName",
          "usage_count": 3,
          "usage_percentage": 100.0,
          "always_used": true
        },
        {
          "field": "lastName",
          "usage_count": 3,
          "usage_percentage": 100.0,
          "always_used": true
        },
        {
          "field": "email",
          "usage_count": 1,
          "usage_percentage": 33.3,
          "always_used": false
        },
        {
          "field": "phoneNumber",
          "usage_count": 1,
          "usage_percentage": 33.3,
          "always_used": false
        },
        {
          "field": "dateOfBirth",
          "usage_count": 1,
          "usage_percentage": 33.3,
          "always_used": false
        },
        {
          "field": "gender",
          "usage_count": 1,
          "usage_percentage": 33.3,
          "always_used": false
        },
        {
          "field": "address",
          "usage_count": 1,
          "usage_percentage": 33.3,
          "always_used": false
        }
      ],
      "unused_fields": [
        "middleName",
        "preferredName",
        "preferredLanguage",
        "ethnicity",
        "race",
        "maritalStatus",
        "employmentStatus",
        "emergencyContact",
        "primaryCareProvider",
        "referringProvider",
        "tags",
        "customFields",
        "createdAt",
        "updatedAt",
        "lastVisitDate"
      ]
    },
    "insurance": {
      "total_fields_available": 15,
      "fields_used": 3,
      "usage_percentage": 20.0,
      "field_details": [
        {
          "field": "id",
          "usage_count": 1,
          "usage_percentage": 100.0,
          "always_used": true
        },
        {
          "field": "provider",
          "usage_count": 1,
          "usage_percentage": 100.0,
          "always_used": true
        },
        {
          "field": "memberId",
          "usage_count": 1,
          "usage_percentage": 100.0,
          "always_used": true
        }
      ],
      "unused_fields": [
        "groupNumber",
        "planName",
        "planType",
        "copayAmount",
        "deductible",
        "deductibleMet",
        "outOfPocketMax",
        "effectiveDate",
        "expirationDate",
        "isPrimary",
        "verificationStatus",
        "lastVerifiedDate"
      ]
    }
  },
  "overfetching_analysis": {
    "detected": true,
    "severity": "medium",
    "details": [
      {
        "query": "GetPatient",
        "overfetched_fields": ["gender", "address", "insurance"],
        "usage_in_other_queries": 0,
        "recommendation": "Consider creating a separate query for detailed patient information"
      }
    ],
    "total_overfetched_fields": 3,
    "data_transfer_impact": "Approximately 35% of transferred data may be unused"
  },
  "underfetching_analysis": {
    "detected": false,
    "common_follow_up_queries": [],
    "recommendation": "No significant underfetching patterns detected"
  },
  "query_patterns": [
    {
      "pattern": "Basic Patient Info",
      "frequency": 2,
      "fields": ["id", "firstName", "lastName"],
      "percentage_of_queries": 66.7
    },
    {
      "pattern": "Detailed Patient Info",
      "frequency": 1,
      "fields": ["id", "firstName", "lastName", "email", "phoneNumber", "dateOfBirth", "gender", "address", "insurance"],
      "percentage_of_queries": 33.3
    }
  ],
  "recommendations": [
    {
      "type": "field_set_optimization",
      "priority": "high",
      "title": "Create Standardized Field Sets",
      "description": "Define common field sets for different use cases",
      "implementation": {
        "basic_fields": ["id", "firstName", "lastName"],
        "contact_fields": ["email", "phoneNumber", "address"],
        "demographic_fields": ["dateOfBirth", "gender", "ethnicity", "race"],
        "insurance_fields": ["insurance { id provider memberId groupNumber }"]
      },
      "estimated_impact": "30-40% reduction in data transfer"
    },
    {
      "type": "query_consolidation",
      "priority": "medium",
      "title": "Consolidate Similar Queries",
      "description": "GetPatientBasic query is duplicated",
      "action": "Use a single query definition and reuse it",
      "code_example": "const GET_PATIENT_BASIC = gql`\n  query GetPatientBasic($id: ID!) {\n    patient(id: $id) {\n      id\n      firstName\n      lastName\n    }\n  }\n`;"
    },
    {
      "type": "remove_unused_fields",
      "priority": "low",
      "title": "Remove Unused Fields from Schema",
      "description": "15 patient fields are never used in analyzed queries",
      "fields_to_review": ["employmentStatus", "maritalStatus", "referringProvider"],
      "note": "Verify these fields aren't used in other parts of the application"
    }
  ],
  "performance_impact": {
    "current_average_response_size": "4.2 KB",
    "optimized_response_size": "2.8 KB",
    "reduction_percentage": 33.3,
    "bandwidth_savings": "1.4 KB per request",
    "monthly_savings_estimate": "420 MB (based on 300K requests/month)"
  }
}
```

### Test 2: Healthcare-Specific Field Usage

**Status**: ✅ Success

#### Input Parameters

```json
{
  "queries": [
    "query GetPatientMedicalHistory { patient(id: \"123\") { medicalHistory { diagnoses { code description date } medications { name dosage frequency } allergies { allergen severity } procedures { code description date } } } }",
    "query GetPatientVitals { patient(id: \"123\") { vitals { bloodPressure { systolic diastolic } heartRate temperature weight height bmi recordedAt } } }",
    "query GetPatientSummary { patient(id: \"123\") { id firstName lastName lastVisitDate nextAppointment { date time provider { name } } } }"
  ],
  "time_range": "week",
  "include_recommendations": true
}
```

#### Output

```json
{
  "analysis_period": {
    "start": "2025-06-26T00:00:00Z",
    "end": "2025-07-03T00:00:00Z",
    "total_queries_analyzed": 3
  },
  "field_statistics": {
    "patient": {
      "total_fields_available": 25,
      "fields_used": 7,
      "usage_percentage": 28.0,
      "field_details": [
        {
          "field": "id",
          "usage_count": 1,
          "usage_percentage": 33.3,
          "always_used": false
        },
        {
          "field": "firstName",
          "usage_count": 1,
          "usage_percentage": 33.3,
          "always_used": false
        },
        {
          "field": "lastName",
          "usage_count": 1,
          "usage_percentage": 33.3,
          "always_used": false
        },
        {
          "field": "medicalHistory",
          "usage_count": 1,
          "usage_percentage": 33.3,
          "always_used": false,
          "is_complex_type": true
        },
        {
          "field": "vitals",
          "usage_count": 1,
          "usage_percentage": 33.3,
          "always_used": false,
          "is_complex_type": true
        },
        {
          "field": "lastVisitDate",
          "usage_count": 1,
          "usage_percentage": 33.3,
          "always_used": false
        },
        {
          "field": "nextAppointment",
          "usage_count": 1,
          "usage_percentage": 33.3,
          "always_used": false,
          "is_complex_type": true
        }
      ]
    },
    "medicalHistory": {
      "total_fields_available": 10,
      "fields_used": 4,
      "usage_percentage": 40.0,
      "field_details": [
        {
          "field": "diagnoses",
          "usage_count": 1,
          "usage_percentage": 100.0,
          "subfields_used": ["code", "description", "date"]
        },
        {
          "field": "medications",
          "usage_count": 1,
          "usage_percentage": 100.0,
          "subfields_used": ["name", "dosage", "frequency"]
        },
        {
          "field": "allergies",
          "usage_count": 1,
          "usage_percentage": 100.0,
          "subfields_used": ["allergen", "severity"]
        },
        {
          "field": "procedures",
          "usage_count": 1,
          "usage_percentage": 100.0,
          "subfields_used": ["code", "description", "date"]
        }
      ],
      "unused_fields": [
        "familyHistory",
        "socialHistory",
        "immunizations",
        "labResults",
        "imagingResults",
        "hospitalizations"
      ]
    }
  },
  "healthcare_specific_insights": {
    "phi_fields_accessed": [
      "medicalHistory.diagnoses",
      "medicalHistory.medications",
      "medicalHistory.allergies",
      "vitals"
    ],
    "compliance_considerations": [
      "PHI fields are being accessed - ensure proper authorization",
      "Medical history queries should be logged for audit purposes",
      "Consider implementing field-level access controls"
    ],
    "clinical_data_patterns": [
      {
        "pattern": "Complete Medical History",
        "includes_diagnoses": true,
        "includes_medications": true,
        "includes_vitals": false,
        "use_case": "Comprehensive patient review"
      },
      {
        "pattern": "Vitals Only",
        "includes_diagnoses": false,
        "includes_medications": false,
        "includes_vitals": true,
        "use_case": "Quick clinical assessment"
      }
    ]
  },
  "recommendations": [
    {
      "type": "healthcare_optimization",
      "priority": "high",
      "title": "Implement Clinical Data Field Sets",
      "description": "Create predefined field sets for common clinical scenarios",
      "implementation": {
        "clinical_summary": "id, firstName, lastName, lastVisitDate, activeProblems",
        "vital_signs": "vitals { bloodPressure, heartRate, temperature, recordedAt }",
        "medication_list": "medications { name, dosage, frequency, prescriber, startDate }",
        "allergy_list": "allergies { allergen, severity, type, verifiedDate }"
      },
      "hipaa_note": "Ensure minimum necessary principle is followed"
    },
    {
      "type": "performance_optimization",
      "priority": "high",
      "title": "Paginate Medical History Queries",
      "description": "Medical history can contain extensive data",
      "recommendation": "Add pagination to diagnoses, medications, and procedures",
      "code_example": "query GetPatientMedicalHistory($id: ID!, $first: Int = 10) {\n  patient(id: $id) {\n    medicalHistory {\n      diagnoses(first: $first, orderBy: DATE_DESC) {\n        edges {\n          node { code description date }\n        }\n        pageInfo { hasNextPage endCursor }\n      }\n    }\n  }\n}"
    },
    {
      "type": "security_enhancement",
      "priority": "medium",
      "title": "Implement Field-Level PHI Access Controls",
      "description": "Different roles may need different levels of access to PHI",
      "roles_example": {
        "nurse": ["vitals", "allergies", "medications"],
        "physician": ["all fields"],
        "administrative": ["demographics only"],
        "billing": ["insurance", "procedures"]
      }
    }
  ],
  "unused_complex_fields": {
    "warning": "Complex fields with low usage detected",
    "fields": [
      {
        "field": "medicalHistory.familyHistory",
        "size_impact": "Can be 5-10KB per patient",
        "recommendation": "Load on-demand only"
      },
      {
        "field": "medicalHistory.labResults",
        "size_impact": "Can be 20-50KB per patient",
        "recommendation": "Implement separate query with pagination"
      }
    ]
  }
}
```

### Test 3: Overfetching Detection

**Status**: ✅ Success

#### Input Parameters

```json
{
  "queries": [
    "query ListPatients { patients(first: 50) { edges { node { id firstName lastName email phoneNumber address city state zipCode country dateOfBirth gender ethnicity race maritalStatus employmentStatus primaryLanguage secondaryLanguage emergencyContact { name phone relationship } insurance { provider memberId groupNumber } tags customFields createdAt updatedAt lastModifiedBy } } } }"
  ],
  "time_range": "day",
  "include_recommendations": true
}
```

#### Output

```json
{
  "analysis_period": {
    "start": "2025-07-02T00:00:00Z",
    "end": "2025-07-03T00:00:00Z",
    "total_queries_analyzed": 1
  },
  "overfetching_analysis": {
    "detected": true,
    "severity": "critical",
    "details": [
      {
        "query": "ListPatients",
        "total_fields_requested": 27,
        "estimated_fields_needed": 5,
        "overfetch_percentage": 81.5,
        "problematic_fields": [
          "address",
          "city",
          "state",
          "zipCode",
          "country",
          "ethnicity",
          "race",
          "maritalStatus",
          "employmentStatus",
          "secondaryLanguage",
          "emergencyContact",
          "insurance",
          "tags",
          "customFields",
          "lastModifiedBy"
        ],
        "impact": "Each patient record is approximately 3.5KB instead of 0.5KB"
      }
    ],
    "list_query_specific_issues": [
      "Fetching detailed data in list views causes severe performance issues",
      "50 patients × 3.5KB = 175KB per request",
      "Network latency increases by 300-500ms"
    ]
  },
  "critical_recommendations": [
    {
      "type": "urgent_optimization",
      "priority": "critical",
      "title": "Implement List-Specific Field Selection",
      "description": "List queries should only fetch minimal fields",
      "implementation": {
        "list_fields": "id, firstName, lastName, lastVisitDate",
        "detail_fields": "All fields as currently implemented"
      },
      "code_example": "// Optimized list query\nquery ListPatientsOptimized {\n  patients(first: 50) {\n    edges {\n      node {\n        id\n        firstName\n        lastName\n        lastVisitDate\n        hasInsurance  // Boolean instead of full object\n      }\n    }\n  }\n}\n\n// Separate detail query\nquery GetPatientDetails($id: ID!) {\n  patient(id: $id) {\n    # All fields here\n  }\n}",
      "expected_improvement": "95% reduction in data transfer for list views"
    },
    {
      "type": "implement_field_resolver",
      "priority": "high",
      "title": "Add Field Resolver for Summary Data",
      "description": "Create computed fields that provide summary information",
      "examples": [
        "patientSummary: Returns formatted name and basic info",
        "insuranceStatus: Returns boolean or enum instead of full object",
        "addressSummary: Returns city, state instead of full address"
      ]
    },
    {
      "type": "pagination_optimization",
      "priority": "high",
      "title": "Reduce Default Page Size",
      "description": "50 patients per page with all fields is too much",
      "recommendation": "Reduce to 20 patients per page or implement virtual scrolling",
      "memory_impact": "Current: 175KB per page, Optimized: 10KB per page"
    }
  ],
  "performance_metrics": {
    "current_performance": {
      "average_response_time": "850ms",
      "data_transfer_size": "175KB",
      "parsing_time": "120ms",
      "render_time": "200ms"
    },
    "projected_performance": {
      "average_response_time": "150ms",
      "data_transfer_size": "10KB",
      "parsing_time": "10ms",
      "render_time": "50ms"
    },
    "improvement_factor": "5.7x faster"
  },
  "field_usage_by_ui_component": {
    "patient_list_table": {
      "displayed_fields": ["firstName", "lastName", "lastVisitDate"],
      "fetched_but_hidden": 24,
      "efficiency_score": 11.1
    },
    "recommendation": "Align GraphQL queries with UI requirements"
  }
}
```

### Test 4: Field Usage Trends Over Time

**Status**: ✅ Success

#### Input Parameters

```json
{
  "queries": [
    "query GetAppointment { appointment { id startTime endTime patient { id firstName } provider { id firstName } } }",
    "query GetAppointment { appointment { id startTime endTime status patient { id firstName } provider { id firstName } } }",
    "query GetAppointment { appointment { id startTime endTime status reasonForVisit patient { id firstName } provider { id firstName } notes } }"
  ],
  "time_range": "month",
  "include_recommendations": true
}
```

#### Output

```json
{
  "analysis_period": {
    "start": "2025-06-03T00:00:00Z",
    "end": "2025-07-03T00:00:00Z",
    "total_queries_analyzed": 3
  },
  "field_evolution_analysis": {
    "trend": "expanding",
    "description": "Fields are being progressively added to the query",
    "timeline": [
      {
        "version": 1,
        "fields_count": 7,
        "fields": ["id", "startTime", "endTime", "patient.id", "patient.firstName", "provider.id", "provider.firstName"]
      },
      {
        "version": 2,
        "fields_count": 8,
        "added_fields": ["status"],
        "reason": "Likely added for appointment state management"
      },
      {
        "version": 3,
        "fields_count": 10,
        "added_fields": ["reasonForVisit", "notes"],
        "reason": "Clinical information requirements expanded"
      }
    ],
    "prediction": "Query will likely continue growing without intervention"
  },
  "field_stability_analysis": {
    "stable_fields": [
      {
        "field": "id",
        "usage_percentage": 100,
        "classification": "essential"
      },
      {
        "field": "startTime",
        "usage_percentage": 100,
        "classification": "essential"
      },
      {
        "field": "endTime",
        "usage_percentage": 100,
        "classification": "essential"
      },
      {
        "field": "patient",
        "usage_percentage": 100,
        "classification": "essential"
      },
      {
        "field": "provider",
        "usage_percentage": 100,
        "classification": "essential"
      }
    ],
    "volatile_fields": [
      {
        "field": "status",
        "usage_percentage": 66.7,
        "classification": "frequently_used"
      },
      {
        "field": "reasonForVisit",
        "usage_percentage": 33.3,
        "classification": "occasionally_used"
      },
      {
        "field": "notes",
        "usage_percentage": 33.3,
        "classification": "occasionally_used"
      }
    ]
  },
  "recommendations": [
    {
      "type": "query_versioning",
      "priority": "high",
      "title": "Implement Query Versioning Strategy",
      "description": "Create versioned queries instead of modifying existing ones",
      "implementation": {
        "basic": "appointment { id startTime endTime patient provider }",
        "detailed": "appointment { ...BasicAppointment status }",
        "clinical": "appointment { ...DetailedAppointment reasonForVisit notes }"
      },
      "benefits": [
        "Prevents query bloat",
        "Maintains backward compatibility",
        "Clear separation of concerns"
      ]
    },
    {
      "type": "fragment_usage",
      "priority": "high",
      "title": "Use GraphQL Fragments",
      "description": "Define reusable fragments for common field sets",
      "code_example": "fragment BasicAppointment on Appointment {\n  id\n  startTime\n  endTime\n  patient {\n    id\n    firstName\n  }\n  provider {\n    id\n    firstName\n  }\n}\n\nfragment AppointmentStatus on Appointment {\n  ...BasicAppointment\n  status\n}\n\nfragment ClinicalAppointment on Appointment {\n  ...AppointmentStatus\n  reasonForVisit\n  notes\n}\n\n// Usage\nquery GetBasicAppointment {\n  appointment {\n    ...BasicAppointment\n  }\n}"
    },
    {
      "type": "field_deprecation",
      "priority": "medium",
      "title": "Plan Field Deprecation",
      "description": "Some fields may no longer be needed",
      "process": [
        "Track field usage over time",
        "Mark unused fields as deprecated",
        "Remove after grace period",
        "Communicate changes to API consumers"
      ]
    }
  ],
  "usage_patterns_by_consumer": {
    "note": "Consider different field requirements by consumer type",
    "patterns": [
      {
        "consumer": "Mobile App",
        "needs": "Minimal fields for performance",
        "fields": ["id", "startTime", "patient.firstName", "provider.firstName"]
      },
      {
        "consumer": "Web Dashboard",
        "needs": "Moderate fields for display",
        "fields": ["id", "startTime", "endTime", "status", "patient", "provider"]
      },
      {
        "consumer": "Clinical System",
        "needs": "All fields for comprehensive view",
        "fields": ["all appointment fields including clinical notes"]
      }
    ],
    "recommendation": "Create consumer-specific queries or use field parameters"
  }
}
```

## Key Features Demonstrated

### 1. **Field Usage Statistics**
- Tracks usage percentage for each field
- Identifies always-used vs rarely-used fields
- Calculates field coverage percentages
- Analyzes nested field usage

### 2. **Overfetching Detection**
- Identifies queries requesting unnecessary fields
- Calculates data transfer impact
- Provides severity ratings
- Suggests optimized field sets

### 3. **Pattern Recognition**
- Detects common query patterns
- Groups similar queries
- Identifies field set variations
- Tracks pattern frequency

### 4. **Performance Impact Analysis**
- Calculates current vs optimized payload sizes
- Estimates bandwidth savings
- Projects response time improvements
- Quantifies optimization benefits

### 5. **Healthcare-Specific Insights**
- PHI field access tracking
- Compliance considerations
- Clinical data patterns
- Role-based field access recommendations

## Common Issues and Solutions

### 1. **List Query Overfetching**
- **Issue**: Fetching all fields in list views
- **Impact**: 5-10x larger payloads
- **Solution**: Create list-specific field sets

### 2. **Query Evolution**
- **Issue**: Queries grow over time with added fields
- **Impact**: Performance degradation
- **Solution**: Implement versioned queries

### 3. **Unused Complex Fields**
- **Issue**: Fetching nested objects that aren't used
- **Impact**: Significant data transfer overhead
- **Solution**: Load complex fields on-demand

### 4. **Missing Field Sets**
- **Issue**: No standardized field selections
- **Impact**: Inconsistent performance
- **Solution**: Define common field sets for use cases

## Best Practices

1. **Define Field Sets**: Create standard field sets for common use cases
2. **Monitor Usage**: Track field usage patterns over time
3. **Optimize Lists**: Use minimal fields for list/table views
4. **Version Queries**: Implement query versioning strategy
5. **Use Fragments**: Leverage GraphQL fragments for reusability
6. **Audit PHI Access**: Track access to sensitive healthcare fields
7. **Regular Review**: Periodically review and optimize field usage