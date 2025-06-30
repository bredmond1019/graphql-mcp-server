"""Models for healthcare patterns detection."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class PatternCategory(str, Enum):
    """Categories of healthcare patterns."""
    PATIENT_MANAGEMENT = "patient_management"
    APPOINTMENTS = "appointments"
    CLINICAL_DATA = "clinical_data"
    BILLING = "billing"
    PROVIDER_MANAGEMENT = "provider_management"
    COMMUNICATIONS = "communications"
    REPORTING = "reporting"


class HealthcarePattern(BaseModel):
    """A detected healthcare pattern."""
    
    pattern_type: str = Field(
        description="Type of healthcare pattern detected"
    )
    category: PatternCategory = Field(
        description="Category this pattern belongs to"
    )
    elements: List[str] = Field(
        description="GraphQL types, fields, or operations that make up this pattern"
    )
    description: str = Field(
        description="Description of what this pattern represents"
    )
    recommendations: List[str] = Field(
        description="Best practices and recommendations for this pattern"
    )
    confidence: float = Field(
        default=1.0,
        description="Confidence score for pattern detection (0.0-1.0)"
    )


class HealthcarePatternsResult(BaseModel):
    """Result of healthcare patterns analysis."""
    
    patterns: List[HealthcarePattern] = Field(
        description="List of detected healthcare patterns"
    )
    total_patterns: int = Field(
        description="Total number of patterns found"
    )
    summary: str = Field(
        description="Summary of the analysis results"
    )
    categories_found: List[PatternCategory] = Field(
        description="List of pattern categories that were found"
    )