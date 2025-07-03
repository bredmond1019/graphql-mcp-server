# Tool 8: field_relationships - Detailed Test Results

*Generated on: 2025-07-02 23:42:56*

## Tool Overview

The Field Relationships tool maps and visualizes the relationships between GraphQL fields, helping understand data structure and navigation paths.
## How to Use This Tool

### Python Usage

```python
from healthie_mcp.tools.field_relationships import FieldRelationshipTool, FieldRelationshipInput
from healthie_mcp.schema_manager import SchemaManager

# Initialize the tool
schema_manager = SchemaManager(api_endpoint='https://api.gethealthie.com/graphql')
tool = FieldRelationshipTool(schema_manager)

# Explore field relationships
input_data = FieldRelationshipInput(
    field_name='patient',
    max_depth=3,
    include_scalars=True
)
result = tool.execute(input_data)
```

### Parameters

- **field_name** (required): The field to explore relationships for
- **max_depth** (optional): Maximum traversal depth (default: 2)
- **include_scalars** (optional): Include scalar fields (default: True)

## Test Summary

- **Total tests**: 2
- **Successful**: 2
- **Failed**: 0
- **Success rate**: 100.0%

## Detailed Test Results

### Test 1: patient field relationships

**Status**: ✅ Success

#### Input Parameters

```json
{
  "field_name": "patient",
  "max_depth": 3,
  "include_scalars": true
}
```

#### Output

```json
{
  "field_name": "patient",
  "total_relationships": 156,
  "max_depth": 3,
  "include_scalars": true,
  "relationship_tree": {
    "patient": {
      "type": "Patient",
      "fields": {
        "id": {
          "type": "ID!",
          "is_scalar": true
        },
        "firstName": {
          "type": "String!",
          "is_scalar": true
        },
        "lastName": {
          "type": "String!",
          "is_scalar": true
        },
        "appointments": {
          "type": "[Appointment!]",
          "is_scalar": false,
          "fields": {
            "id": {
              "type": "ID!",
              "is_scalar": true
            },
            "scheduledAt": {
              "type": "DateTime!",
              "is_scalar": true
            },
            "provider": {
              "type": "Provider",
              "is_scalar": false,
              "fields": {
                "id": {
                  "type": "ID!",
                  "is_scalar": true
                },
                "firstName": {
                  "type": "String!",
                  "is_scalar": true
                },
                "lastName": {
                  "type": "String!",
                  "is_scalar": true
                }
              }
            }
          }
        },
        "diagnoses": {
          "type": "[Diagnosis!]",
          "is_scalar": false,
          "fields": {
            "icdCode": {
              "type": "String!",
              "is_scalar": true
            },
            "description": {
              "type": "String!",
              "is_scalar": true
            }
          }
        }
      }
    }
  },
  "related_fields": [
    "patient.id",
    "patient.firstName",
    "patient.lastName",
    "patient.appointments",
    "patient.appointments.id",
    "patient.appointments.scheduledAt",
    "patient.appointments.provider",
    "patient.appointments.provider.id",
    "patient.appointments.provider.firstName",
    "patient.diagnoses",
    "patient.diagnoses.icdCode"
  ],
  "suggestions": [
    "The 'patient' field connects to appointments, diagnoses, medications, and other medical records",
    "Consider using fragments for commonly accessed patient field combinations",
    "Deep nesting (3+ levels) may impact query performance"
  ]
}
```


---

### Test 2: appointment relationships no scalars

**Status**: ✅ Success

#### Input Parameters

```json
{
  "field_name": "appointment",
  "max_depth": 2,
  "include_scalars": false
}
```

#### Output

```json
{
  "field_name": "appointment",
  "total_relationships": 28,
  "max_depth": 2,
  "include_scalars": false,
  "relationship_tree": {
    "appointment": {
      "type": "Appointment",
      "fields": {
        "patient": {
          "type": "Patient",
          "is_scalar": false,
          "fields": {
            "appointments": {
              "type": "[Appointment!]",
              "is_scalar": false
            },
            "diagnoses": {
              "type": "[Diagnosis!]",
              "is_scalar": false
            },
            "medications": {
              "type": "[Medication!]",
              "is_scalar": false
            }
          }
        },
        "provider": {
          "type": "Provider",
          "is_scalar": false,
          "fields": {
            "appointments": {
              "type": "[Appointment!]",
              "is_scalar": false
            },
            "specialties": {
              "type": "[Specialty!]",
              "is_scalar": false
            }
          }
        },
        "location": {
          "type": "Location",
          "is_scalar": false,
          "fields": {
            "appointments": {
              "type": "[Appointment!]",
              "is_scalar": false
            }
          }
        }
      }
    }
  },
  "related_fields": [
    "appointment.patient",
    "appointment.patient.appointments",
    "appointment.patient.diagnoses",
    "appointment.provider",
    "appointment.provider.appointments",
    "appointment.location"
  ],
  "suggestions": [
    "Appointment connects Patient and Provider entities",
    "Be careful of circular references when querying nested appointments"
  ]
}
```


---

