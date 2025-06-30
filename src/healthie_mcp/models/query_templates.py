"""Models for query templates tool."""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


class WorkflowCategory(str, Enum):
    """Categories of healthcare workflows."""
    PATIENT_MANAGEMENT = "patient_management"
    APPOINTMENTS = "appointments"
    CLINICAL_DATA = "clinical_data"
    BILLING = "billing"


class QueryTemplate(BaseModel):
    """A GraphQL query template for common operations."""
    
    name: str = Field(description="Name of the query template")
    description: str = Field(description="Description of what the query does")
    category: WorkflowCategory = Field(description="Workflow category this query belongs to")
    query: str = Field(description="The GraphQL query string")
    variables: Dict[str, Any] = Field(
        default_factory=dict,
        description="Example variables for the query"
    )
    required_variables: List[str] = Field(
        default_factory=list,
        description="List of required variable names"
    )
    optional_variables: List[str] = Field(
        default_factory=list,
        description="List of optional variable names"
    )
    notes: str = Field(
        default="",
        description="Additional notes or tips for using this query"
    )


class QueryTemplatesResult(BaseModel):
    """Result from the query templates tool."""
    
    templates: List[QueryTemplate] = Field(
        description="List of query templates"
    )
    total_count: int = Field(
        description="Total number of templates returned"
    )
    categories_available: List[str] = Field(
        description="List of all available workflow categories"
    )
    filtered_by: Optional[str] = Field(
        default=None,
        description="Category filter applied, if any"
    )
    tips: List[str] = Field(
        default_factory=list,
        description="General tips for using the templates"
    )
    template_counts_by_category: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of templates in each category"
    )