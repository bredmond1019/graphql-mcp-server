"""Constants used throughout the Healthie MCP server."""

from typing import Final
from enum import Enum


# GraphQL Constants
GRAPHQL_INTROSPECTION_QUERY: Final[str] = """
query IntrospectionQuery {
  __schema {
    types {
      name
      kind
      description
      fields(includeDeprecated: true) {
        name
        description
        args {
          name
          description
          type {
            name
            kind
          }
          defaultValue
        }
        type {
          name
          kind
        }
        isDeprecated
        deprecationReason
      }
      inputFields {
        name
        description
        type {
          name
          kind
        }
        defaultValue
      }
      interfaces {
        name
        kind
      }
      enumValues(includeDeprecated: true) {
        name
        description
        isDeprecated
        deprecationReason
      }
      possibleTypes {
        name
        kind
      }
    }
  }
}
"""

# Schema File Constants
SCHEMA_FILE_NAME: Final[str] = "healthie_schema.graphql"
SCHEMA_CACHE_DURATION_HOURS: Final[int] = 24

# GraphQL Type Kinds
class GraphQLTypeKind(str, Enum):
    """GraphQL type kinds as defined in the GraphQL specification."""
    SCALAR = "SCALAR"
    OBJECT = "OBJECT"
    INTERFACE = "INTERFACE"
    UNION = "UNION"
    ENUM = "ENUM"
    INPUT_OBJECT = "INPUT_OBJECT"
    LIST = "LIST"
    NON_NULL = "NON_NULL"


# Common GraphQL Scalar Types
GRAPHQL_SCALAR_TYPES: Final[set[str]] = {
    "String", "Int", "Float", "Boolean", "ID",
    "Date", "DateTime", "Time", "JSON", "Upload",
    "BigInt", "Decimal"
}

# Healthcare-specific Keywords
PATIENT_KEYWORDS: Final[list[str]] = [
    'patient', 'user', 'client', 'demographic', 'profile', 'contact',
    'emergency_contact', 'family_history', 'medical_history'
]

APPOINTMENT_KEYWORDS: Final[list[str]] = [
    'appointment', 'booking', 'schedule', 'calendar', 'availability',
    'slot', 'recurring', 'cancel', 'reschedule', 'reminder'
]

CLINICAL_KEYWORDS: Final[list[str]] = [
    'note', 'form', 'assessment', 'measurement', 'vital', 'lab',
    'observation', 'diagnosis', 'medication', 'prescription',
    'care_plan', 'goal', 'treatment'
]

BILLING_KEYWORDS: Final[list[str]] = [
    'billing', 'payment', 'invoice', 'charge', 'insurance',
    'claim', 'authorization', 'copay', 'deductible', 'balance',
    'transaction', 'refund'
]

PROVIDER_KEYWORDS: Final[list[str]] = [
    'provider', 'practitioner', 'organization', 'license',
    'credential', 'specialty', 'location', 'staff', 'role'
]

# HTTP Constants
DEFAULT_TIMEOUT_SECONDS: Final[int] = 30
MAX_RETRIES: Final[int] = 3
RETRY_DELAY_SECONDS: Final[int] = 1

# Validation Constants
EMAIL_REGEX: Final[str] = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
PHONE_REGEX: Final[str] = r'^(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$'
DATE_FORMAT: Final[str] = '%Y-%m-%d'
DATETIME_FORMAT: Final[str] = '%Y-%m-%dT%H:%M:%S'

# Performance Thresholds
class PerformanceThreshold(str, Enum):
    """Performance thresholds for query analysis."""
    FAST = "Very fast (<100ms)"
    MODERATE_FAST = "Fast (100ms-500ms)"
    MODERATE = "Moderate (500ms-2s)"
    SLOW = "Potentially slow (>2s)"


MAX_QUERY_DEPTH: Final[int] = 10
EXPENSIVE_FIELD_PATTERNS: Final[list[str]] = [
    'search', 'history', 'records', 'documents', 'attachments',
    'logs', 'audit', 'analytics', 'reports', 'aggregations'
]

# Error Messages
ERROR_SCHEMA_NOT_AVAILABLE: Final[str] = "Schema not available. Please check your configuration."
ERROR_INVALID_REGEX: Final[str] = "Invalid regex pattern: {error}"
ERROR_MUTATION_NOT_FOUND: Final[str] = "Mutation '{mutation_name}' not found in schema"
ERROR_INVALID_TYPE_FILTER: Final[str] = "Invalid type_filter '{filter}'. Must be one of: {valid_filters}"

# Success Messages
SUCCESS_SCHEMA_LOADED: Final[str] = "GraphQL schema loaded successfully"
SUCCESS_SCHEMA_REFRESHED: Final[str] = "GraphQL schema refreshed from API"

# File Paths
TEMPLATES_DIR: Final[str] = "templates"
CONFIG_DIR: Final[str] = "config"

# MCP Resource URIs
RESOURCE_SCHEMA_CURRENT: Final[str] = "healthie://schema/current"
RESOURCE_CONFIG: Final[str] = "healthie://config"