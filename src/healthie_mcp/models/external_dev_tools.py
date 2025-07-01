"""Pydantic models for external developer tools."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum


class WorkflowCategory(str, Enum):
    """Healthcare workflow categories."""
    PATIENT_MANAGEMENT = "patient_management"
    APPOINTMENTS = "appointments"
    CLINICAL_DATA = "clinical_data"
    BILLING = "billing"
    PROVIDER_MANAGEMENT = "provider_management"
    INSURANCE = "insurance"
    COMMUNICATIONS = "communications"


class CodeLanguage(str, Enum):
    """Supported programming languages for code examples."""
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    PYTHON = "python"
    CURL = "curl"


class QueryTemplate(BaseModel):
    """A GraphQL query template for a specific workflow."""
    name: str
    description: str
    category: WorkflowCategory
    query: str
    variables: Dict[str, Any]
    required_variables: List[str]
    optional_variables: List[str]
    notes: Optional[str] = None


class QueryTemplateResult(BaseModel):
    """Result from query template generation."""
    templates: List[QueryTemplate]
    total_templates: int
    category_filter: Optional[str] = None
    error: Optional[str] = None


class FieldRelationship(BaseModel):
    """Information about field relationships in the schema."""
    field_name: str
    field_type: str
    path: str
    description: Optional[str] = None
    is_required: bool = False
    is_list: bool = False


class FieldRelationshipResult(BaseModel):
    """Result from field relationship exploration."""
    source_field: str
    related_fields: List[FieldRelationship]
    total_relationships: int
    max_depth: int
    suggestions: List[str]
    error: Optional[str] = None


class ValidationIssue(BaseModel):
    """A validation issue found in mutation input."""
    field_path: str
    issue_type: str  # "required", "invalid_type", "invalid_format", "healthcare_specific"
    message: str
    suggestion: Optional[str] = None
    severity: str  # "error", "warning", "info"


class InputValidationResult(BaseModel):
    """Result from mutation input validation."""
    is_valid: bool
    issues: List[ValidationIssue]
    total_errors: int
    total_warnings: int
    suggestions: List[str]
    error: Optional[str] = None


class PerformanceIssue(BaseModel):
    """A performance issue detected in a GraphQL query."""
    issue_type: str  # "n_plus_one", "deep_nesting", "large_result_set", "expensive_field"
    severity: str  # "high", "medium", "low"
    description: str
    location: str  # Where in the query the issue occurs
    suggestion: str
    estimated_impact: Optional[str] = None


class QueryPerformanceResult(BaseModel):
    """Result from query performance analysis."""
    overall_score: int  # 0-100, higher is better
    complexity_score: int
    issues: List[PerformanceIssue]
    total_issues: int
    suggestions: List[str]
    estimated_execution_time: Optional[str] = None
    error: Optional[str] = None


class CodeExample(BaseModel):
    """A code example in a specific language."""
    language: CodeLanguage
    title: str
    code: str
    description: Optional[str] = None
    dependencies: List[str] = []
    notes: Optional[str] = None


class CodeExampleInput(BaseModel):
    """Input for code example generation."""
    operation_name: str
    language: Optional[str] = None


class CodeExampleResult(BaseModel):
    """Result from code example generation."""
    operation_name: str
    examples: List[CodeExample]
    total_examples: int
    languages: List[CodeLanguage]
    error: Optional[str] = None


class ErrorSolution(BaseModel):
    """A solution for a specific API error."""
    problem: str
    solution: str
    code_example: Optional[str] = None
    documentation_link: Optional[str] = None


class ErrorDecodeResult(BaseModel):
    """Result from error message decoding."""
    original_error: str
    error_type: str
    plain_english: str
    solutions: List[ErrorSolution]
    is_healthcare_specific: bool
    compliance_notes: Optional[str] = None
    error: Optional[str] = None


class WorkflowStep(BaseModel):
    """A single step in a healthcare workflow."""
    step_number: int
    operation_type: str  # "query", "mutation"
    operation_name: str
    description: str
    required_inputs: List[str]
    expected_outputs: List[str]
    graphql_example: str
    notes: Optional[str] = None
    depends_on: List[int] = []  # Step numbers this step depends on


class WorkflowSequence(BaseModel):
    """A complete workflow sequence."""
    workflow_name: str
    category: WorkflowCategory
    description: str
    steps: List[WorkflowStep]
    total_steps: int
    estimated_duration: Optional[str] = None
    prerequisites: List[str] = []
    notes: Optional[str] = None


class WorkflowSequenceResult(BaseModel):
    """Result from workflow sequence building."""
    workflows: List[WorkflowSequence]
    total_workflows: int
    category_filter: Optional[str] = None
    error: Optional[str] = None


class FieldUsagePattern(BaseModel):
    """Information about field usage patterns."""
    field_name: str
    usage_frequency: float  # 0.0 to 1.0
    commonly_used_with: List[str]
    performance_impact: str  # "low", "medium", "high"
    healthcare_context: Optional[str] = None


class FieldSuggestion(BaseModel):
    """Suggestion for field selection."""
    suggestion_type: str  # "commonly_used_together", "complete_data_set", "performance_optimized"
    suggested_fields: List[str]
    reason: str
    performance_note: Optional[str] = None


class FieldUsageResult(BaseModel):
    """Result from field usage analysis."""
    analyzed_fields: List[str]
    usage_patterns: List[FieldUsagePattern]
    suggestions: List[FieldSuggestion]
    total_patterns: int
    error: Optional[str] = None