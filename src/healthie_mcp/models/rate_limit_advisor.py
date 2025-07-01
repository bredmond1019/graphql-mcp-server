"""Models for rate limit advisor tool."""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class QueryComplexity(str, Enum):
    """Query complexity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class UsagePattern(BaseModel):
    """Represents a usage pattern for API requests."""
    
    pattern_name: str = Field(
        description="Name of the usage pattern"
    )
    requests_per_minute: float = Field(
        description="Average requests per minute"
    )
    peak_requests_per_minute: float = Field(
        description="Peak requests per minute"
    )
    query_types: List[str] = Field(
        description="Types of queries in this pattern"
    )
    complexity: QueryComplexity = Field(
        description="Overall complexity of queries"
    )
    time_distribution: Dict[int, float] = Field(
        default_factory=dict,
        description="Distribution of requests by hour (0-23)"
    )


class UsageForecast(BaseModel):
    """Forecast of API usage."""
    
    daily_requests: int = Field(
        description="Estimated daily API requests"
    )
    monthly_requests: int = Field(
        description="Estimated monthly API requests"
    )
    peak_hour_requests: int = Field(
        description="Estimated requests during peak hour"
    )
    rate_limit_risk: str = Field(
        description="Risk level of hitting rate limits (low, medium, high)"
    )
    recommended_tier: str = Field(
        description="Recommended API tier based on usage"
    )


class OptimizationTip(BaseModel):
    """An optimization tip for reducing rate limit impact."""
    
    title: str = Field(
        description="Title of the optimization tip"
    )
    description: str = Field(
        description="Detailed description of the optimization"
    )
    impact: str = Field(
        description="Expected impact on rate limit usage"
    )
    implementation_effort: str = Field(
        description="Implementation effort (low, medium, high)"
    )
    example_code: Optional[str] = Field(
        default=None,
        description="Example code snippet"
    )


class CostProjection(BaseModel):
    """Cost projection for API usage."""
    
    tier: str = Field(
        description="API tier name"
    )
    monthly_cost: float = Field(
        description="Estimated monthly cost in USD"
    )
    annual_cost: float = Field(
        description="Estimated annual cost in USD"
    )
    included_requests: int = Field(
        description="Number of requests included in tier"
    )
    overage_rate: Optional[float] = Field(
        default=None,
        description="Cost per additional request"
    )
    estimated_overage: Optional[float] = Field(
        default=None,
        description="Estimated monthly overage cost"
    )


class CachingStrategy(BaseModel):
    """A caching strategy recommendation."""
    
    strategy_name: str = Field(
        description="Name of the caching strategy"
    )
    applicable_queries: List[str] = Field(
        description="Types of queries this strategy applies to"
    )
    cache_duration: str = Field(
        description="Recommended cache duration"
    )
    expected_reduction: str = Field(
        description="Expected reduction in API calls"
    )
    implementation_guide: List[str] = Field(
        description="Steps to implement this caching strategy"
    )
    considerations: List[str] = Field(
        description="Important considerations and trade-offs"
    )


class RateLimitAnalysis(BaseModel):
    """Complete rate limit analysis result."""
    
    usage_patterns: List[UsagePattern] = Field(
        description="Identified usage patterns"
    )
    forecast: UsageForecast = Field(
        description="Usage forecast based on patterns"
    )
    optimization_tips: List[OptimizationTip] = Field(
        description="Tips for optimizing API usage"
    )
    cost_projections: List[CostProjection] = Field(
        description="Cost projections for different tiers"
    )
    caching_strategies: List[CachingStrategy] = Field(
        description="Recommended caching strategies"
    )
    summary: str = Field(
        description="Executive summary of the analysis"
    )
    recommendations: List[str] = Field(
        description="Priority recommendations"
    )