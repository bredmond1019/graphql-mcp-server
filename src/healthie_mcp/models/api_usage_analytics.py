"""Data models for API usage analytics tool."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

from pydantic import BaseModel, Field


class TimeRange(str, Enum):
    """Time range for analytics."""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class MetricType(str, Enum):
    """Types of metrics to calculate."""
    REQUEST_COUNT = "request_count"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    DATA_TRANSFER = "data_transfer"
    COMPLEXITY_SCORE = "complexity_score"
    COST_ESTIMATE = "cost_estimate"


class OptimizationType(str, Enum):
    """Types of optimizations."""
    QUERY_BATCHING = "query_batching"
    FIELD_SELECTION = "field_selection"
    CACHING_STRATEGY = "caching_strategy"
    PAGINATION = "pagination"
    ERROR_HANDLING = "error_handling"
    RATE_LIMITING = "rate_limiting"


class UsagePattern(BaseModel):
    """Represents a usage pattern."""
    pattern_type: str = Field(description="Type of pattern detected")
    description: str = Field(description="Description of the pattern")
    frequency: int = Field(description="Frequency of occurrence")
    impact: str = Field(description="Impact level: high, medium, low")
    time_range: TimeRange = Field(description="Time range for the pattern")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional pattern details")


class PerformanceMetric(BaseModel):
    """Performance metric data."""
    metric_type: MetricType = Field(description="Type of metric")
    value: float = Field(description="Metric value")
    unit: str = Field(description="Unit of measurement")
    trend: str = Field(description="Trend: increasing, decreasing, stable")
    change_percentage: Optional[float] = Field(None, description="Percentage change from previous period")
    threshold_status: str = Field(description="Status relative to threshold: normal, warning, critical")


class PerformanceInsight(BaseModel):
    """Performance insight based on analytics."""
    category: str = Field(description="Category of insight")
    title: str = Field(description="Title of the insight")
    description: str = Field(description="Detailed description")
    impact_score: float = Field(description="Impact score from 0-10")
    affected_operations: List[str] = Field(description="Operations affected by this insight")
    recommended_actions: List[str] = Field(description="Recommended actions to take")
    potential_savings: Optional[Dict[str, Any]] = Field(None, description="Potential cost/time savings")


class OptimizationSuggestion(BaseModel):
    """Optimization suggestion for API usage."""
    optimization_type: OptimizationType = Field(description="Type of optimization")
    title: str = Field(description="Title of the suggestion")
    description: str = Field(description="Detailed description")
    implementation_effort: str = Field(description="Implementation effort: low, medium, high")
    expected_impact: str = Field(description="Expected impact: low, medium, high")
    example_before: Optional[str] = Field(None, description="Example code before optimization")
    example_after: Optional[str] = Field(None, description="Example code after optimization")
    estimated_improvement: Dict[str, Any] = Field(description="Estimated improvements")


class AnalyticsReport(BaseModel):
    """Comprehensive analytics report."""
    report_id: str = Field(description="Unique report identifier")
    generated_at: datetime = Field(description="When the report was generated")
    time_range: TimeRange = Field(description="Time range covered by the report")
    start_date: datetime = Field(description="Start date of the analysis period")
    end_date: datetime = Field(description="End date of the analysis period")
    
    # Summary statistics
    total_requests: int = Field(description="Total number of API requests")
    unique_operations: int = Field(description="Number of unique operations used")
    average_response_time: float = Field(description="Average response time in ms")
    error_rate: float = Field(description="Error rate percentage")
    
    # Top operations
    top_operations: List[Dict[str, Any]] = Field(description="Most frequently used operations")
    slowest_operations: List[Dict[str, Any]] = Field(description="Operations with slowest response times")
    error_prone_operations: List[Dict[str, Any]] = Field(description="Operations with highest error rates")
    
    # Patterns and insights
    usage_patterns: List[UsagePattern] = Field(description="Detected usage patterns")
    performance_insights: List[PerformanceInsight] = Field(description="Performance insights")
    optimization_suggestions: List[OptimizationSuggestion] = Field(description="Optimization suggestions")
    
    # Metrics
    metrics: List[PerformanceMetric] = Field(description="Performance metrics")
    
    # Healthcare-specific insights
    healthcare_compliance: Dict[str, Any] = Field(description="Healthcare compliance insights")
    phi_access_patterns: Dict[str, Any] = Field(description="PHI access patterns")
    workflow_efficiency: Dict[str, Any] = Field(description="Healthcare workflow efficiency metrics")


class ApiUsageAnalyticsInput(BaseModel):
    """Input for API usage analytics tool."""
    time_range: TimeRange = Field(description="Time range for analysis")
    operations: Optional[List[str]] = Field(None, description="Specific operations to analyze")
    metric_types: Optional[List[MetricType]] = Field(None, description="Specific metrics to calculate")
    include_patterns: bool = Field(True, description="Include usage pattern detection")
    include_insights: bool = Field(True, description="Include performance insights")
    include_optimizations: bool = Field(True, description="Include optimization suggestions")
    include_healthcare_analysis: bool = Field(True, description="Include healthcare-specific analysis")


class ApiUsageAnalyticsResult(BaseModel):
    """Result from API usage analytics tool."""
    success: bool = Field(description="Whether the analysis was successful")
    report: Optional[AnalyticsReport] = Field(None, description="Analytics report if successful")
    quick_stats: Dict[str, Any] = Field(description="Quick statistics summary")
    critical_findings: List[str] = Field(description="Critical findings requiring immediate attention")
    export_formats: List[str] = Field(description="Available export formats for the report")
    next_steps: List[str] = Field(description="Recommended next steps based on analysis")
    error: Optional[str] = Field(None, description="Error message if analysis failed")