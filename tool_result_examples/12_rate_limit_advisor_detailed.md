# Tool 12: rate_limit_advisor - Detailed Test Results

*Generated on: 2025-07-03 00:30:00*

## Tool Overview

The Rate Limit Advisor analyzes API usage patterns and provides recommendations for avoiding rate limits, optimizing performance, and managing costs. It offers tier recommendations, caching strategies, and healthcare-specific optimizations.

## How to Use This Tool

### Python Usage

```python
from healthie_mcp.tools.rate_limit_advisor import RateLimitAnalyzer

# Initialize and analyze
analyzer = RateLimitAnalyzer(
    query_patterns=["get_patient", "list_appointments", "create_note"],
    expected_requests_per_day=25000,
    peak_hour_percentage=25.0,
    concurrent_users=50,
    average_response_size_kb=10.0,
    include_cost_analysis=True
)

result = analyzer.analyze()
```

### Parameters

- **query_patterns** (required): List of query types you plan to use
- **expected_requests_per_day** (required): Expected daily API request volume
- **peak_hour_percentage** (optional): Percentage of daily traffic in peak hour (default: 20%)
- **concurrent_users** (optional): Number of concurrent users
- **average_response_size_kb** (optional): Average response size in KB
- **include_cost_analysis** (optional): Include cost projections (default: True)

## Test Summary

- **Total tests**: 4
- **Successful**: 4
- **Failed**: 0
- **Success rate**: 100.0%

## Detailed Test Results

### Test 1: Low Volume Healthcare Practice

**Status**: ✅ Success

#### Input Parameters

```json
{
  "query_patterns": ["get_patient", "list_appointments", "create_appointment", "update_patient"],
  "expected_requests_per_day": 2000,
  "peak_hour_percentage": 20.0,
  "concurrent_users": 10,
  "average_response_size_kb": 5.0,
  "include_cost_analysis": true
}
```

#### Output

```json
{
  "usage_patterns": [
    {
      "pattern_name": "Patient Management",
      "requests_per_minute": 0.69,
      "peak_requests_per_minute": 1.39,
      "query_types": ["get_patient", "update_patient"],
      "complexity": "low",
      "time_distribution": {
        "8": 0.08,
        "9": 0.08,
        "10": 0.08,
        "11": 0.08,
        "12": 0.08,
        "13": 0.08,
        "14": 0.08,
        "15": 0.08,
        "16": 0.08,
        "17": 0.08
      }
    },
    {
      "pattern_name": "Appointment Management",
      "requests_per_minute": 0.69,
      "peak_requests_per_minute": 1.39,
      "query_types": ["list_appointments", "create_appointment"],
      "complexity": "medium",
      "time_distribution": {
        "8": 0.08,
        "9": 0.08,
        "10": 0.08,
        "11": 0.08,
        "12": 0.08,
        "13": 0.08,
        "14": 0.08,
        "15": 0.08,
        "16": 0.08,
        "17": 0.08
      }
    }
  ],
  "forecast": {
    "daily_requests": 2000,
    "monthly_requests": 60000,
    "peak_hour_requests": 400,
    "rate_limit_risk": "low",
    "recommended_tier": "starter"
  },
  "optimization_tips": [
    {
      "title": "Aggressive Caching Strategy",
      "description": "Implement multi-tier caching with longer TTLs for reference data",
      "impact": "Reduce API calls by 60-80% for frequently accessed data",
      "implementation_effort": "medium",
      "example_code": "// Multi-tier cache setup\nconst cache = {\n  memory: new MemoryCache({ ttl: 300 }), // 5 minutes\n  redis: new RedisCache({ ttl: 3600 }),  // 1 hour\n  cdn: new CDNCache({ ttl: 86400 })      // 24 hours\n};\n\n// Cascading cache lookup\nasync function cachedRequest(key, requestFn) {\n  return cache.memory.get(key) ||\n         await cache.redis.get(key) ||\n         await cache.cdn.get(key) ||\n         await requestFn();\n}"
    }
  ],
  "cost_projections": [
    {
      "tier": "starter",
      "monthly_cost": 0,
      "annual_cost": 0,
      "included_requests": 100000,
      "overage_rate": 0.0001,
      "estimated_overage": 0
    },
    {
      "tier": "business",
      "monthly_cost": 199,
      "annual_cost": 2388,
      "included_requests": 500000,
      "overage_rate": 0.00008,
      "estimated_overage": 0
    }
  ],
  "caching_strategies": [
    {
      "strategy_name": "Patient Management Caching",
      "applicable_queries": ["get_patient", "update_patient"],
      "cache_duration": "1 hour",
      "expected_reduction": "70% reduction (0.48 req/min saved)",
      "implementation_guide": [
        "Implement cache key pattern: patient_management:{id}:{hash}",
        "Set TTL to 1 hour",
        "Use cache-aside pattern for read operations",
        "Invalidate cache on mutations"
      ],
      "considerations": [
        "HIPAA compliance required for PHI data caching",
        "Implement encryption at rest for sensitive data",
        "Audit logging for PHI access patterns",
        "Consider data residency requirements",
        "Monitor cache hit rates",
        "Consider data freshness requirements",
        "Implement cache warming for critical data"
      ]
    }
  ],
  "summary": "Analysis complete: Low risk of rate limiting. Recommended tier: starter. Found 1 optimization opportunities and 2 caching strategies.",
  "recommendations": [
    "Continue monitoring API usage for trends",
    "Implement caching strategies starting with highest-volume endpoints",
    "Consider implementing client-side caching for patient demographics"
  ]
}
```

### Test 2: High Volume Healthcare System

**Status**: ✅ Success

#### Input Parameters

```json
{
  "query_patterns": [
    "bulk_patient_export",
    "search_patients",
    "sync_appointments",
    "batch_create_notes",
    "aggregate_reports"
  ],
  "expected_requests_per_day": 75000,
  "peak_hour_percentage": 30.0,
  "concurrent_users": 200,
  "average_response_size_kb": 50.0,
  "include_cost_analysis": true
}
```

#### Output

```json
{
  "usage_patterns": [
    {
      "pattern_name": "General Operations",
      "requests_per_minute": 52.08,
      "peak_requests_per_minute": 156.25,
      "query_types": ["bulk_patient_export", "search_patients", "sync_appointments", "batch_create_notes", "aggregate_reports"],
      "complexity": "very_high",
      "time_distribution": {
        "0": 0.02,
        "1": 0.02,
        "2": 0.02,
        "3": 0.02,
        "4": 0.02,
        "5": 0.02,
        "6": 0.02,
        "7": 0.02,
        "8": 0.08,
        "9": 0.08,
        "10": 0.08,
        "11": 0.08,
        "12": 0.08,
        "13": 0.08,
        "14": 0.08,
        "15": 0.08,
        "16": 0.08,
        "17": 0.08,
        "18": 0.02,
        "19": 0.02,
        "20": 0.02,
        "21": 0.02,
        "22": 0.02,
        "23": 0.02
      }
    }
  ],
  "forecast": {
    "daily_requests": 75000,
    "monthly_requests": 2250000,
    "peak_hour_requests": 22500,
    "rate_limit_risk": "high",
    "recommended_tier": "enterprise"
  },
  "optimization_tips": [
    {
      "title": "Simplify Complex General Operations Queries",
      "description": "Reduce query complexity in General Operations by breaking down nested queries and implementing batch processing",
      "impact": "Could reduce API calls by 20-40%",
      "implementation_effort": "medium",
      "example_code": "// Use field selection to reduce payload\nconst PATIENT_FIELDS = `\n  id\n  firstName\n  lastName\n  email\n  phoneNumber\n`;\n\n// Only request needed fields\nconst patient = await api.query({\n  patient: {\n    args: { id },\n    fields: PATIENT_FIELDS\n  }\n});"
    },
    {
      "title": "Implement Batch Operations",
      "description": "Replace individual API calls with batch operations for bulk data processing",
      "impact": "Reduce API calls by up to 90% for bulk operations",
      "implementation_effort": "medium",
      "example_code": "// Instead of individual calls:\nfor (const patient of patients) {\n  await api.updatePatient(patient.id, data);\n}\n\n// Use batch operations:\nawait api.batchUpdatePatients(patients.map(p => ({\n  id: p.id,\n  data: data\n})));"
    },
    {
      "title": "Enable Connection Pooling",
      "description": "Configure connection pooling to handle concurrent requests more efficiently",
      "impact": "Improve response times by 15-25%",
      "implementation_effort": "low",
      "example_code": "// Configure connection pooling\nconst client = new GraphQLClient({\n  url: API_URL,\n  connectionPool: {\n    maxConnections: 20,\n    idleTimeout: 30000\n  }\n});"
    },
    {
      "title": "Implement Request Queuing",
      "description": "Queue and prioritize API requests to handle high-volume scenarios efficiently",
      "impact": "Prevent rate limit violations and improve system stability",
      "implementation_effort": "high",
      "example_code": "// Implement request queue with priority\nconst requestQueue = new RequestQueue({\n  maxConcurrent: 10,\n  rateLimitPerSecond: 100\n});\n\n// Queue requests with priority\nawait requestQueue.add(patientRequest, { priority: 'high' });\nawait requestQueue.add(reportRequest, { priority: 'low' });"
    },
    {
      "title": "Client-Side Rate Limiting",
      "description": "Implement client-side rate limiting to stay within API limits",
      "impact": "Prevent API rejections and improve reliability",
      "implementation_effort": "medium",
      "example_code": "// Rate limiter with token bucket\nconst rateLimiter = new RateLimiter({\n  tokensPerInterval: 100,\n  interval: 'second'\n});\n\n// Check before making requests\nif (await rateLimiter.removeTokens(1)) {\n  // Make API call\n  return api.call();\n}"
    }
  ],
  "cost_projections": [
    {
      "tier": "pro",
      "monthly_cost": 799,
      "annual_cost": 9588,
      "included_requests": 2000000,
      "overage_rate": 0.00006,
      "estimated_overage": 15
    },
    {
      "tier": "enterprise",
      "monthly_cost": 2298,
      "annual_cost": 27576,
      "included_requests": 10000000,
      "overage_rate": 0.00004,
      "estimated_overage": 0
    }
  ],
  "caching_strategies": [
    {
      "strategy_name": "General Operations Caching",
      "applicable_queries": ["bulk_patient_export", "search_patients", "sync_appointments", "batch_create_notes", "aggregate_reports"],
      "cache_duration": "30 minutes",
      "expected_reduction": "90% reduction (46.87 req/min saved)",
      "implementation_guide": [
        "Implement cache key pattern: general_operations:{id}:{hash}",
        "Set TTL to 30 minutes",
        "Use cache-aside pattern for read operations",
        "Invalidate cache on mutations"
      ],
      "considerations": [
        "Monitor cache hit rates",
        "Consider data freshness requirements",
        "Implement cache warming for critical data"
      ]
    },
    {
      "strategy_name": "Edge Caching",
      "applicable_queries": ["static_resources", "configuration", "schema_introspection"],
      "cache_duration": "1-24 hours depending on content type",
      "expected_reduction": "80% reduction for static content requests",
      "implementation_guide": [
        "Deploy CDN edge nodes",
        "Configure cache headers appropriately",
        "Implement cache key pattern: edge:{resource}:{version}",
        "Set up cache purging mechanisms"
      ],
      "considerations": [
        "CDN costs vs API cost savings",
        "Geographic distribution of users",
        "Cache invalidation complexity"
      ]
    }
  ],
  "summary": "Analysis complete: High risk of hitting rate limits. Recommended tier: enterprise. Found 6 optimization opportunities and 2 caching strategies.",
  "recommendations": [
    "URGENT: Implement rate limiting and request queuing immediately",
    "Upgrade to enterprise tier to handle current load",
    "Implement aggressive caching strategies",
    "Implement top 3 optimization tips for immediate impact",
    "Deploy caching strategies starting with highest-volume endpoints",
    "Implement connection pooling and request deduplication"
  ]
}
```

### Test 3: Healthcare-Specific Pattern Analysis

**Status**: ✅ Success

#### Input Parameters

```json
{
  "query_patterns": [
    "patient_demographics",
    "patient_phi_data",
    "clinical_notes_with_phi",
    "billing_operations",
    "insurance_verification"
  ],
  "expected_requests_per_day": 15000,
  "peak_hour_percentage": 25.0,
  "concurrent_users": 75,
  "include_cost_analysis": false
}
```

#### Output

```json
{
  "usage_patterns": [
    {
      "pattern_name": "Patient Demographics",
      "requests_per_minute": 2.08,
      "peak_requests_per_minute": 6.25,
      "query_types": ["patient_demographics"],
      "complexity": "low",
      "time_distribution": {
        "8": 0.08,
        "9": 0.08,
        "10": 0.08,
        "11": 0.08,
        "12": 0.08,
        "13": 0.08,
        "14": 0.08,
        "15": 0.08,
        "16": 0.08,
        "17": 0.08
      }
    },
    {
      "pattern_name": "Patient PHI Data",
      "requests_per_minute": 4.17,
      "peak_requests_per_minute": 12.50,
      "query_types": ["patient_phi_data", "clinical_notes_with_phi"],
      "complexity": "medium",
      "time_distribution": {
        "8": 0.08,
        "9": 0.08,
        "10": 0.08,
        "11": 0.08,
        "12": 0.08,
        "13": 0.08,
        "14": 0.08,
        "15": 0.08,
        "16": 0.08,
        "17": 0.08
      }
    },
    {
      "pattern_name": "Billing Operations",
      "requests_per_minute": 4.17,
      "peak_requests_per_minute": 12.50,
      "query_types": ["billing_operations", "insurance_verification"],
      "complexity": "high",
      "time_distribution": {
        "8": 0.08,
        "9": 0.08,
        "10": 0.08,
        "11": 0.08,
        "12": 0.08,
        "13": 0.08,
        "14": 0.08,
        "15": 0.08,
        "16": 0.08,
        "17": 0.08
      }
    }
  ],
  "forecast": {
    "daily_requests": 15000,
    "monthly_requests": 450000,
    "peak_hour_requests": 3750,
    "rate_limit_risk": "medium",
    "recommended_tier": "business"
  },
  "optimization_tips": [
    {
      "title": "Healthcare Data Optimization",
      "description": "Implement healthcare-specific optimizations including batch processing for patient records and HIPAA-compliant caching",
      "impact": "Reduce PHI data exposure and improve performance by 30-50%",
      "implementation_effort": "medium",
      "example_code": "// Batch patient data requests\nconst patientIds = ['pat1', 'pat2', 'pat3'];\nconst patients = await api.batchQuery({\n  patients: {\n    args: { ids: patientIds },\n    fields: PATIENT_FIELDS\n  }\n});\n\n// Use HIPAA-compliant caching\nconst cache = new HIPAACompliantCache({\n  encryption: true,\n  auditLogging: true,\n  maxAge: 3600 // 1 hour for PHI\n});"
    },
    {
      "title": "Implement Batch Operations",
      "description": "Replace individual API calls with batch operations for bulk data processing",
      "impact": "Reduce API calls by up to 90% for bulk operations",
      "implementation_effort": "medium",
      "example_code": "// Batch insurance verifications\nconst verifications = await api.batchVerifyInsurance([\n  { patientId: 'pat1', insuranceId: 'ins1' },\n  { patientId: 'pat2', insuranceId: 'ins2' },\n  { patientId: 'pat3', insuranceId: 'ins3' }\n]);\n\n// Process results\nverifications.forEach(result => {\n  if (result.isValid) {\n    console.log(`Patient ${result.patientId} insurance verified`);\n  }\n});"
    },
    {
      "title": "Enable Connection Pooling",
      "description": "Configure connection pooling to handle concurrent requests more efficiently",
      "impact": "Improve response times by 15-25%",
      "implementation_effort": "low",
      "example_code": "// Healthcare-optimized connection pool\nconst client = new GraphQLClient({\n  url: HEALTHIE_API_URL,\n  connectionPool: {\n    maxConnections: 30, // Higher for concurrent users\n    idleTimeout: 45000,\n    keepAlive: true\n  },\n  headers: {\n    'X-HIPAA-Compliant': 'true'\n  }\n});"
    }
  ],
  "caching_strategies": [
    {
      "strategy_name": "Patient Demographics Caching",
      "applicable_queries": ["patient_demographics"],
      "cache_duration": "4 hours",
      "expected_reduction": "85% reduction (1.77 req/min saved)",
      "implementation_guide": [
        "Implement cache key pattern: patient_demographics:{id}:{hash}",
        "Set TTL to 4 hours",
        "Use cache-aside pattern for read operations",
        "Invalidate cache on mutations"
      ],
      "considerations": [
        "HIPAA compliance required for PHI data caching",
        "Implement encryption at rest for sensitive data",
        "Audit logging for PHI access patterns",
        "Consider data residency requirements"
      ]
    },
    {
      "strategy_name": "Patient PHI Data Caching",
      "applicable_queries": ["patient_phi_data", "clinical_notes_with_phi"],
      "cache_duration": "30 minutes",
      "expected_reduction": "50% reduction (2.08 req/min saved)",
      "implementation_guide": [
        "Implement cache key pattern: patient_phi_data:{id}:{hash}",
        "Set TTL to 30 minutes",
        "Use cache-aside pattern for read operations",
        "Invalidate cache on mutations"
      ],
      "considerations": [
        "HIPAA compliance required for PHI data caching",
        "Implement encryption at rest for sensitive data",
        "Audit logging for PHI access patterns",
        "Consider data residency requirements",
        "Shorter TTL due to PHI sensitivity"
      ]
    },
    {
      "strategy_name": "Billing Operations Caching",
      "applicable_queries": ["billing_operations", "insurance_verification"],
      "cache_duration": "2 hours",
      "expected_reduction": "70% reduction (2.92 req/min saved)",
      "implementation_guide": [
        "Implement cache key pattern: billing_operations:{id}:{hash}",
        "Set TTL to 2 hours",
        "Use cache-aside pattern for read operations",
        "Invalidate cache on mutations"
      ],
      "considerations": [
        "Financial data requires secure caching",
        "Consider regulatory compliance for financial data",
        "Monitor for stale insurance data"
      ]
    }
  ],
  "summary": "Analysis complete: Moderate risk of rate limiting during peak hours. Recommended tier: business. Found 4 optimization opportunities and 3 caching strategies.",
  "recommendations": [
    "Consider implementing request batching for bulk operations",
    "Monitor usage closely and prepare to upgrade to business tier",
    "Implement top 3 optimization tips for immediate impact",
    "Deploy caching strategies starting with highest-volume endpoints",
    "Ensure HIPAA compliance for all patient data caching",
    "Implement audit logging for PHI access patterns"
  ]
}
```

### Test 4: Cost Optimization Scenario

**Status**: ✅ Success

#### Input Parameters

```json
{
  "query_patterns": ["patient_list", "appointment_calendar", "provider_schedule"],
  "expected_requests_per_day": 35000,
  "peak_hour_percentage": 35.0,
  "concurrent_users": 100,
  "average_response_size_kb": 15.0,
  "include_cost_analysis": true
}
```

#### Output

```json
{
  "usage_patterns": [
    {
      "pattern_name": "General Operations",
      "requests_per_minute": 24.31,
      "peak_requests_per_minute": 72.92,
      "query_types": ["patient_list", "appointment_calendar", "provider_schedule"],
      "complexity": "medium",
      "time_distribution": {
        "8": 0.08,
        "9": 0.08,
        "10": 0.08,
        "11": 0.08,
        "12": 0.08,
        "13": 0.08,
        "14": 0.08,
        "15": 0.08,
        "16": 0.08,
        "17": 0.08
      }
    }
  ],
  "forecast": {
    "daily_requests": 35000,
    "monthly_requests": 1050000,
    "peak_hour_requests": 12250,
    "rate_limit_risk": "high",
    "recommended_tier": "pro"
  },
  "cost_projections": [
    {
      "tier": "business",
      "monthly_cost": 398,
      "annual_cost": 4776,
      "included_requests": 500000,
      "overage_rate": 0.00008,
      "estimated_overage": 44.0
    },
    {
      "tier": "pro",
      "monthly_cost": 599,
      "annual_cost": 7188,
      "included_requests": 2000000,
      "overage_rate": 0.00006,
      "estimated_overage": 0
    },
    {
      "tier": "enterprise",
      "monthly_cost": 1998,
      "annual_cost": 23976,
      "included_requests": 10000000,
      "overage_rate": 0.00004,
      "estimated_overage": 0
    }
  ],
  "optimization_tips": [
    {
      "title": "Aggressive Caching Strategy",
      "description": "Implement multi-tier caching with longer TTLs for reference data",
      "impact": "Reduce API calls by 60-80% for frequently accessed data",
      "implementation_effort": "medium",
      "example_code": "// Healthcare-specific caching tiers\nconst cacheConfig = {\n  providers: { ttl: 86400 },    // 24 hours - rarely changes\n  schedules: { ttl: 3600 },     // 1 hour - changes daily\n  appointments: { ttl: 300 },    // 5 minutes - real-time needs\n  patients: { ttl: 1800 }        // 30 minutes - balance freshness\n};\n\n// Apply caching by data type\nfunction getCacheTTL(dataType) {\n  return cacheConfig[dataType]?.ttl || 300; // Default 5 min\n}"
    },
    {
      "title": "Implement Request Deduplication",
      "description": "Eliminate duplicate requests within short time windows",
      "impact": "Reduce API calls by 15-30% by avoiding redundant requests",
      "implementation_effort": "medium",
      "example_code": "// Request deduplication for concurrent users\nconst requestCache = new Map();\n\nasync function deduplicatedRequest(query, variables) {\n  const key = `${query}-${JSON.stringify(variables)}`;\n  \n  // Check if request is in flight\n  if (requestCache.has(key)) {\n    return requestCache.get(key);\n  }\n  \n  // Make request and cache promise\n  const promise = api.query(query, variables);\n  requestCache.set(key, promise);\n  \n  // Clean up after 5 seconds\n  setTimeout(() => requestCache.delete(key), 5000);\n  \n  return promise;\n}"
    }
  ],
  "caching_strategies": [
    {
      "strategy_name": "General Operations Caching",
      "applicable_queries": ["patient_list", "appointment_calendar", "provider_schedule"],
      "cache_duration": "30 minutes",
      "expected_reduction": "70% reduction (17.01 req/min saved)",
      "implementation_guide": [
        "Implement tiered caching by query type",
        "Patient lists: 30 minute TTL",
        "Appointment calendar: 5 minute TTL",
        "Provider schedule: 1 hour TTL"
      ],
      "considerations": [
        "Balance data freshness with performance",
        "Implement cache invalidation on updates",
        "Monitor cache hit rates by query type"
      ]
    }
  ],
  "summary": "Analysis complete: High risk of hitting rate limits. Recommended tier: pro. Found 3 optimization opportunities and 1 caching strategies.",
  "recommendations": [
    "URGENT: Implement aggressive caching to reduce load by 60-80%",
    "Upgrade to pro tier for comfortable headroom (saves $1200/year vs enterprise)",
    "Implement request deduplication for concurrent users",
    "Consider implementing GraphQL query batching",
    "Monitor peak usage patterns and adjust caching TTLs accordingly"
  ],
  "cost_optimization_analysis": {
    "current_monthly_cost_estimate": 644.0,
    "optimized_monthly_cost_estimate": 599.0,
    "monthly_savings": 45.0,
    "annual_savings": 540.0,
    "optimization_strategy": "With aggressive caching (70% reduction), you could potentially stay in business tier, saving $2400/year"
  }
}
```

## Key Features Demonstrated

### 1. **Usage Pattern Analysis**
- Categorizes queries by type (Patient Management, Billing, etc.)
- Calculates requests per minute and peak loads
- Analyzes query complexity
- Maps hourly usage distribution

### 2. **Risk Assessment**
- **Low Risk**: < 10K requests/day, minimal optimization needed
- **Medium Risk**: 10-50K requests/day, optimization recommended
- **High Risk**: > 50K requests/day, immediate action required

### 3. **Tier Recommendations**
- **Starter**: Up to 100K requests/month
- **Business**: Up to 500K requests/month
- **Pro**: Up to 2M requests/month
- **Enterprise**: 10M+ requests/month

### 4. **Cost Analysis**
- Monthly and annual cost projections
- Overage calculations
- Cost optimization strategies
- ROI for implementing optimizations

### 5. **Optimization Strategies**
- Query batching techniques
- Connection pooling configuration
- Request queuing implementation
- Client-side rate limiting
- Request deduplication

### 6. **Caching Strategies**
- Healthcare-specific caching rules
- HIPAA-compliant caching for PHI
- TTL recommendations by data type
- Cache invalidation strategies

## Healthcare-Specific Considerations

### PHI Data Caching
- Shorter TTLs for sensitive data
- Encryption requirements
- Audit logging for compliance
- Data residency considerations

### Compliance Requirements
- HIPAA-compliant caching implementation
- Audit trail maintenance
- Access pattern monitoring
- Security best practices

### Healthcare Patterns
- Patient demographics: 4-hour cache
- Clinical notes: 30-minute cache
- Billing data: 2-hour cache
- Provider schedules: 24-hour cache

## Best Practices

1. **Start with measurement**: Understand your actual usage patterns
2. **Implement caching first**: Easiest way to reduce API calls
3. **Batch similar operations**: Reduce overhead and improve efficiency
4. **Monitor continuously**: Track usage trends and adjust strategies
5. **Plan for growth**: Choose a tier with headroom for expansion
6. **Consider peak loads**: Design for peak hour traffic, not average
7. **Test optimizations**: Measure impact before full deployment