"""Rate limit advisor tool for analyzing and optimizing API usage."""

from typing import List, Optional, Dict, Any
from mcp.server.fastmcp import FastMCP
from ..models.rate_limit_advisor import (
    RateLimitAnalysis,
    UsagePattern,
    UsageForecast,
    OptimizationTip,
    CostProjection,
    CachingStrategy,
    QueryComplexity
)


def setup_rate_limit_advisor_tool(mcp: FastMCP, schema_manager) -> None:
    """Setup the rate limit advisor tool with the MCP server."""
    
    @mcp.tool()
    def analyze_rate_limits(
        query_patterns: List[str],
        expected_requests_per_day: int,
        peak_hour_percentage: Optional[float] = None,
        concurrent_users: Optional[int] = None,
        average_response_size_kb: Optional[float] = None,
        include_cost_analysis: bool = True
    ) -> RateLimitAnalysis:
        """Analyze API usage patterns and provide rate limit optimization recommendations.
        
        This tool helps developers understand and optimize their API usage to avoid rate limits,
        reduce costs, and improve performance. It's particularly important for healthcare
        applications that need to scale efficiently while maintaining compliance.
        
        Args:
            query_patterns: List of query types you plan to use (e.g., ["patient_list", "appointment_create"])
            expected_requests_per_day: Expected number of API requests per day
            peak_hour_percentage: Percentage of daily traffic in peak hour (default: 20%)
            concurrent_users: Number of concurrent users (helps estimate burst patterns)
            average_response_size_kb: Average response size in KB (helps with caching recommendations)
            include_cost_analysis: Whether to include cost projections (default: True)
            
        Returns:
            RateLimitAnalysis with usage patterns, forecasts, optimizations, and recommendations
        """
        try:
            # Default peak hour percentage if not provided
            if peak_hour_percentage is None:
                peak_hour_percentage = 20.0
            
            # Analyze query patterns
            usage_patterns = _analyze_query_patterns(
                query_patterns, 
                expected_requests_per_day,
                concurrent_users
            )
            
            # Generate usage forecast
            forecast = _generate_usage_forecast(
                expected_requests_per_day,
                peak_hour_percentage,
                usage_patterns
            )
            
            # Generate optimization tips
            optimization_tips = _generate_optimization_tips(
                query_patterns,
                expected_requests_per_day,
                usage_patterns,
                average_response_size_kb
            )
            
            # Generate cost projections
            cost_projections = []
            if include_cost_analysis:
                cost_projections = _generate_cost_projections(
                    forecast.monthly_requests,
                    forecast.rate_limit_risk
                )
            
            # Generate caching strategies
            caching_strategies = _generate_caching_strategies(
                query_patterns,
                usage_patterns,
                average_response_size_kb
            )
            
            # Generate summary and recommendations
            summary = _generate_summary(
                forecast,
                len(optimization_tips),
                len(caching_strategies)
            )
            
            recommendations = _generate_priority_recommendations(
                forecast,
                optimization_tips,
                caching_strategies,
                query_patterns
            )
            
            return RateLimitAnalysis(
                usage_patterns=usage_patterns,
                forecast=forecast,
                optimization_tips=optimization_tips,
                cost_projections=cost_projections,
                caching_strategies=caching_strategies,
                summary=summary,
                recommendations=recommendations
            )
            
        except Exception as e:
            # Return minimal analysis on error
            return RateLimitAnalysis(
                usage_patterns=[],
                forecast=UsageForecast(
                    daily_requests=expected_requests_per_day,
                    monthly_requests=expected_requests_per_day * 30,
                    peak_hour_requests=int(expected_requests_per_day * 0.2),
                    rate_limit_risk="unknown",
                    recommended_tier="standard"
                ),
                optimization_tips=[],
                cost_projections=[],
                caching_strategies=[],
                summary=f"Error analyzing rate limits: {str(e)}",
                recommendations=["Please review your input parameters and try again"]
            )


def _analyze_query_patterns(
    query_patterns: List[str],
    expected_requests_per_day: int,
    concurrent_users: Optional[int]
) -> List[UsagePattern]:
    """Analyze query patterns to identify usage characteristics."""
    patterns = []
    
    # Define complexity mapping
    complexity_map = {
        "list": QueryComplexity.MEDIUM,
        "bulk": QueryComplexity.VERY_HIGH,
        "create": QueryComplexity.LOW,
        "update": QueryComplexity.LOW,
        "delete": QueryComplexity.LOW,
        "details": QueryComplexity.LOW,
        "search": QueryComplexity.HIGH,
        "export": QueryComplexity.VERY_HIGH,
        "sync": QueryComplexity.VERY_HIGH,
        "nested": QueryComplexity.HIGH,
        "batch": QueryComplexity.HIGH
    }
    
    # Group patterns by type
    grouped_patterns = {}
    for pattern in query_patterns:
        pattern_lower = pattern.lower()
        
        # Determine pattern type
        if "patient" in pattern_lower:
            pattern_type = "Patient Management"
        elif "appointment" in pattern_lower:
            pattern_type = "Appointment Management"
        elif "billing" in pattern_lower or "claim" in pattern_lower or "payment" in pattern_lower:
            pattern_type = "Billing Operations"
        elif "provider" in pattern_lower:
            pattern_type = "Provider Management"
        elif "clinical" in pattern_lower or "note" in pattern_lower or "form" in pattern_lower:
            pattern_type = "Clinical Documentation"
        else:
            pattern_type = "General Operations"
        
        if pattern_type not in grouped_patterns:
            grouped_patterns[pattern_type] = []
        grouped_patterns[pattern_type].append(pattern)
    
    # Create usage patterns
    total_patterns = len(query_patterns)
    for pattern_name, queries in grouped_patterns.items():
        # Determine complexity
        max_complexity = QueryComplexity.LOW
        for query in queries:
            query_lower = query.lower()
            for keyword, complexity in complexity_map.items():
                if keyword in query_lower:
                    if list(QueryComplexity).index(complexity) > list(QueryComplexity).index(max_complexity):
                        max_complexity = complexity
        
        # Calculate requests for this pattern
        pattern_percentage = len(queries) / total_patterns
        pattern_daily_requests = expected_requests_per_day * pattern_percentage
        
        # Estimate requests per minute
        requests_per_minute = pattern_daily_requests / (24 * 60)
        peak_multiplier = 3.0 if concurrent_users and concurrent_users > 50 else 2.0
        peak_requests_per_minute = requests_per_minute * peak_multiplier
        
        # Create time distribution (simplified)
        time_distribution = {}
        business_hours = range(8, 18)  # 8 AM to 6 PM
        for hour in range(24):
            if hour in business_hours:
                time_distribution[hour] = 0.08  # 8% per business hour
            else:
                time_distribution[hour] = 0.02  # 2% per non-business hour
        
        pattern = UsagePattern(
            pattern_name=pattern_name,
            requests_per_minute=round(requests_per_minute, 2),
            peak_requests_per_minute=round(peak_requests_per_minute, 2),
            query_types=queries,
            complexity=max_complexity,
            time_distribution=time_distribution
        )
        patterns.append(pattern)
    
    return patterns


def _generate_usage_forecast(
    expected_requests_per_day: int,
    peak_hour_percentage: float,
    usage_patterns: List[UsagePattern]
) -> UsageForecast:
    """Generate usage forecast based on patterns."""
    monthly_requests = expected_requests_per_day * 30
    peak_hour_requests = int(expected_requests_per_day * (peak_hour_percentage / 100))
    
    # Determine rate limit risk based on volume and complexity
    high_complexity_count = sum(1 for p in usage_patterns if p.complexity in [QueryComplexity.HIGH, QueryComplexity.VERY_HIGH])
    
    if expected_requests_per_day > 50000 or peak_hour_requests > 5000:
        rate_limit_risk = "high"
    elif expected_requests_per_day > 10000 or peak_hour_requests > 1000 or high_complexity_count > 2:
        rate_limit_risk = "medium"
    else:
        rate_limit_risk = "low"
    
    # Recommend tier based on usage
    if monthly_requests > 1000000:
        recommended_tier = "enterprise"
    elif monthly_requests > 300000:
        recommended_tier = "pro"
    elif monthly_requests > 100000:
        recommended_tier = "business"
    else:
        recommended_tier = "starter"
    
    return UsageForecast(
        daily_requests=expected_requests_per_day,
        monthly_requests=monthly_requests,
        peak_hour_requests=peak_hour_requests,
        rate_limit_risk=rate_limit_risk,
        recommended_tier=recommended_tier
    )


def _generate_optimization_tips(
    query_patterns: List[str],
    expected_requests_per_day: int,
    usage_patterns: List[UsagePattern],
    average_response_size_kb: Optional[float]
) -> List[OptimizationTip]:
    """Generate optimization tips based on usage patterns."""
    tips = []
    
    # Check for list queries that could benefit from pagination
    list_queries = [q for q in query_patterns if "list" in q.lower()]
    if list_queries:
        tips.append(OptimizationTip(
            title="Implement Efficient Pagination",
            description="Use cursor-based pagination for list queries to reduce response sizes and improve performance. Fetch only the data you need.",
            impact="30-50% reduction in response time and bandwidth",
            implementation_effort="low",
            example_code="""
query GetPatients($cursor: String, $limit: Int = 20) {
  patients(after: $cursor, first: $limit) {
    edges {
      node {
        id
        firstName
        lastName
      }
      cursor
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}"""
        ))
    
    # Field selection optimization (always include for best practices)
    tips.append(OptimizationTip(
        title="Optimize Field Selection",
        description="Request only the fields you need. Avoid fetching entire objects when you only need specific fields.",
        impact="40-60% reduction in response size",
        implementation_effort="low",
        example_code="""
# Instead of fetching all fields:
query { patients { ...AllPatientFields } }

# Fetch only needed fields:
query { 
  patients { 
    id 
    firstName 
    lastName 
    dateOfBirth 
  } 
}"""
    ))
    
    # Check for opportunities to batch requests
    if len(query_patterns) > 3 and expected_requests_per_day > 5000:
        tips.append(OptimizationTip(
            title="Batch Multiple Queries",
            description="Combine multiple related queries into a single request using GraphQL's ability to request multiple resources.",
            impact="50-70% reduction in request count",
            implementation_effort="medium",
            example_code="""
query BatchedQueries($patientId: ID!) {
  patient(id: $patientId) {
    ...PatientDetails
  }
  appointments(patientId: $patientId) {
    ...AppointmentList
  }
  forms(patientId: $patientId) {
    ...FormsList
  }
}"""
        ))
    
    
    # Complex query optimization
    complex_patterns = [p for p in usage_patterns if p.complexity in [QueryComplexity.HIGH, QueryComplexity.VERY_HIGH]]
    if complex_patterns:
        tips.append(OptimizationTip(
            title="Query Optimization - Simplify Complex Queries",
            description="Break down complex nested queries into simpler, separate queries. This improves cacheability and reduces server load.",
            impact="20-40% improvement in query performance",
            implementation_effort="medium"
        ))
    
    # Rate limiting strategy
    if expected_requests_per_day > 10000:
        tips.append(OptimizationTip(
            title="Implement Request Queuing",
            description="Use a request queue with rate limiting to smooth out traffic spikes and avoid hitting rate limits.",
            impact="Prevents rate limit errors during peak usage",
            implementation_effort="high",
            example_code="""
// Example using p-queue for JavaScript
import PQueue from 'p-queue';

const queue = new PQueue({ 
  concurrency: 10, 
  interval: 1000, 
  intervalCap: 50 
});

async function makeApiCall(query) {
  return queue.add(() => graphqlClient.request(query));
}"""
        ))
    
    # Webhook optimization for real-time needs
    if any("sync" in p.lower() or "real" in p.lower() or "bulk" in p.lower() for p in query_patterns):
        tips.append(OptimizationTip(
            title="Use Webhooks for Real-time Updates",
            description="Replace polling queries with webhook subscriptions for real-time data updates. This dramatically reduces API calls.",
            impact="80-90% reduction in polling requests",
            implementation_effort="medium"
        ))
    
    # Add data synchronization optimization for high-volume scenarios
    if expected_requests_per_day > 20000:
        tips.append(OptimizationTip(
            title="Implement Incremental Sync Strategy",
            description="Use timestamps and change tracking to sync only modified data instead of full dataset pulls.",
            impact="70-85% reduction in data transfer",
            implementation_effort="high",
            example_code="""
query IncrementalSync($lastSyncTime: DateTime!) {
  patients(updatedAfter: $lastSyncTime) {
    id
    updatedAt
    ...PatientChanges
  }
  appointments(modifiedSince: $lastSyncTime) {
    id
    modifiedAt
    ...AppointmentChanges
  }
}"""
        ))
    
    return tips


def _generate_cost_projections(
    monthly_requests: int,
    rate_limit_risk: str
) -> List[CostProjection]:
    """Generate cost projections for different tiers."""
    # Simplified tier structure (would be loaded from configuration in production)
    tiers = [
        {
            "name": "starter",
            "monthly_cost": 0,
            "included_requests": 10000,
            "overage_rate": 0.001
        },
        {
            "name": "growth",
            "monthly_cost": 99,
            "included_requests": 100000,
            "overage_rate": 0.0008
        },
        {
            "name": "business",
            "monthly_cost": 299,
            "included_requests": 500000,
            "overage_rate": 0.0006
        },
        {
            "name": "pro",
            "monthly_cost": 999,
            "included_requests": 2000000,
            "overage_rate": 0.0004
        },
        {
            "name": "enterprise",
            "monthly_cost": 2999,
            "included_requests": 10000000,
            "overage_rate": 0.0002
        }
    ]
    
    projections = []
    for tier_data in tiers:
        overage = max(0, monthly_requests - tier_data["included_requests"])
        overage_cost = overage * tier_data["overage_rate"] if overage > 0 else None
        
        projection = CostProjection(
            tier=tier_data["name"],
            monthly_cost=tier_data["monthly_cost"],
            annual_cost=tier_data["monthly_cost"] * 12,
            included_requests=tier_data["included_requests"],
            overage_rate=tier_data["overage_rate"] if overage > 0 else None,
            estimated_overage=round(overage_cost, 2) if overage_cost else None
        )
        projections.append(projection)
    
    return projections


def _generate_caching_strategies(
    query_patterns: List[str],
    usage_patterns: List[UsagePattern],
    average_response_size_kb: Optional[float]
) -> List[CachingStrategy]:
    """Generate caching strategy recommendations."""
    strategies = []
    
    # Fix the missing variable issue in the function
    expected_requests_per_day = sum(p.requests_per_minute * 60 * 24 for p in usage_patterns)
    
    # Check for static/reference data
    static_patterns = ["provider", "insurance", "location", "specialty", "organization"]
    static_queries = [q for q in query_patterns if any(p in q.lower() for p in static_patterns)]
    
    if static_queries:
        strategies.append(CachingStrategy(
            strategy_name="Reference Data Caching",
            applicable_queries=static_queries,
            cache_duration="24 hours",
            expected_reduction="70-80% for reference data queries",
            implementation_guide=[
                "Identify reference data that changes infrequently",
                "Implement a local cache with TTL of 24 hours",
                "Use cache headers to leverage browser caching",
                "Implement cache invalidation webhooks for updates"
            ],
            considerations=[
                "Reference data like providers and locations change infrequently",
                "Consider HIPAA compliance for cached PHI",
                "Implement cache versioning for updates"
            ]
        ))
    
    # Patient demographic caching - include any patient or clinical data queries
    patient_queries = [q for q in query_patterns if any(term in q.lower() for term in ["patient", "clinical", "phi", "note", "lab"])]
    if patient_queries:
        strategies.append(CachingStrategy(
            strategy_name="Patient Demographics Caching",
            applicable_queries=patient_queries,
            cache_duration="1-4 hours",
            expected_reduction="50-60% for repeat patient lookups",
            implementation_guide=[
                "Cache patient demographics with shorter TTL",
                "Use patient ID as cache key",
                "Implement user-specific cache isolation",
                "Clear cache on patient updates"
            ],
            considerations=[
                "PHI must be cached securely with encryption",
                "Implement proper access controls on cached data",
                "Consider HIPAA audit requirements for cached PHI",
                "Cache should be user/session specific",
                "Ensure HIPAA compliance for all cached healthcare data"
            ]
        ))
    
    # List query result caching
    list_queries = [q for q in query_patterns if "list" in q.lower()]
    if list_queries and expected_requests_per_day > 5000:
        strategies.append(CachingStrategy(
            strategy_name="List Query Result Caching",
            applicable_queries=list_queries,
            cache_duration="5-15 minutes",
            expected_reduction="40-50% for frequently accessed lists",
            implementation_guide=[
                "Cache paginated list results with query parameters as key",
                "Implement smart cache invalidation on mutations",
                "Use conditional requests with ETags",
                "Consider implementing a cache-aside pattern"
            ],
            considerations=[
                "List data changes more frequently than reference data",
                "Cache invalidation complexity increases with relationships",
                "Consider real-time requirements for list freshness"
            ]
        ))
    
    # High-volume query deduplication
    high_volume_patterns = [p for p in usage_patterns if p.requests_per_minute > 10]
    if high_volume_patterns:
        strategies.append(CachingStrategy(
            strategy_name="Request Deduplication",
            applicable_queries=[qt for p in high_volume_patterns for qt in p.query_types],
            cache_duration="1-5 seconds",
            expected_reduction="20-30% for duplicate requests",
            implementation_guide=[
                "Implement request deduplication at the client level",
                "Cache identical requests made within short time windows",
                "Use request signatures as cache keys",
                "Implement promise-based deduplication for concurrent requests"
            ],
            considerations=[
                "Particularly effective for dashboard-style applications",
                "Prevents duplicate requests from multiple components",
                "Minimal cache duration reduces stale data risk"
            ]
        ))
    
    # Add aggressive caching for very high volume scenarios
    if expected_requests_per_day > 20000:
        strategies.append(CachingStrategy(
            strategy_name="Aggressive Response Caching",
            applicable_queries=query_patterns,
            cache_duration="30-60 minutes",
            expected_reduction="60-70% overall reduction",
            implementation_guide=[
                "Implement comprehensive response caching",
                "Use cache-control headers effectively",
                "Consider CDN integration for global caching",
                "Implement smart cache warming strategies"
            ],
            considerations=[
                "Balance freshness requirements with performance",
                "Consider HIPAA implications for cached PHI",
                "Implement proper cache invalidation strategies",
                "Monitor cache hit rates and adjust TTLs accordingly"
            ]
        ))
    
    return strategies


def _generate_summary(
    forecast: UsageForecast,
    optimization_count: int,
    caching_count: int
) -> str:
    """Generate executive summary of the analysis."""
    risk_description = {
        "low": "well within normal limits",
        "medium": "approaching limits during peak hours",
        "high": "likely to hit rate limits frequently"
    }
    
    summary = f"Based on your expected usage of {forecast.daily_requests:,} requests per day "
    summary += f"({forecast.monthly_requests:,} monthly), your API usage is {risk_description.get(forecast.rate_limit_risk, 'at uncertain risk')}. "
    summary += f"We recommend the '{forecast.recommended_tier}' tier for your usage level. "
    summary += f"We've identified {optimization_count} optimization opportunities and {caching_count} caching strategies "
    summary += "that could significantly reduce your API usage and improve performance."
    
    return summary


def _generate_priority_recommendations(
    forecast: UsageForecast,
    optimization_tips: List[OptimizationTip],
    caching_strategies: List[CachingStrategy],
    query_patterns: List[str]
) -> List[str]:
    """Generate priority recommendations based on analysis."""
    recommendations = []
    
    # Tier recommendation
    if forecast.rate_limit_risk == "high":
        recommendations.append(f"Upgrade to '{forecast.recommended_tier}' tier immediately to avoid service disruptions")
    elif forecast.rate_limit_risk == "medium":
        recommendations.append(f"Consider upgrading to '{forecast.recommended_tier}' tier to ensure headroom for growth")
    
    # Top optimization recommendations
    if optimization_tips:
        low_effort_tips = [t for t in optimization_tips if t.implementation_effort == "low"]
        if low_effort_tips:
            recommendations.append(f"Implement {low_effort_tips[0].title} for quick wins (low effort, high impact)")
    
    # Caching recommendations
    if caching_strategies:
        high_impact_strategies = [s for s in caching_strategies if "70%" in s.expected_reduction or "80%" in s.expected_reduction]
        if high_impact_strategies:
            recommendations.append(f"Prioritize {high_impact_strategies[0].strategy_name} for maximum request reduction")
    
    # Healthcare-specific recommendations
    healthcare_queries = [q for q in query_patterns if any(term in q.lower() for term in ["patient", "clinical", "phi", "appointment"])]
    if healthcare_queries:
        recommendations.append("Ensure all caching strategies comply with HIPAA requirements for PHI handling")
        recommendations.append("Implement audit logging for all cached healthcare data access")
    
    # Monitoring recommendation
    if forecast.daily_requests > 1000:
        recommendations.append("Set up API usage monitoring and alerts to track rate limit approaching")
    
    # Webhook recommendation for high-volume scenarios
    if forecast.daily_requests > 10000:
        recommendations.append("Evaluate webhook integration to replace high-frequency polling operations")
    
    return recommendations