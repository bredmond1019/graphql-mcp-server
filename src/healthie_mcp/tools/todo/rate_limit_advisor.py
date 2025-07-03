"""Rate limit advisor tool for analyzing and optimizing API usage - Refactored version."""

from typing import List, Optional, Dict, Any
from mcp.server.fastmcp import FastMCP
from ...models.rate_limit_advisor import (
    RateLimitAnalysis,
    UsagePattern,
    UsageForecast,
    OptimizationTip,
    CostProjection,
    CachingStrategy,
    QueryComplexity
)


class RateLimitAnalyzer:
    """Analyzes API usage patterns and provides optimization recommendations."""
    
    # Query complexity mapping
    COMPLEXITY_MAP = {
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
    
    # Rate limit thresholds
    DAILY_REQUEST_THRESHOLDS = {
        "high_risk": 50000,
        "medium_risk": 10000
    }
    
    PEAK_HOUR_THRESHOLDS = {
        "high_risk": 5000,
        "medium_risk": 1000
    }
    
    # Tier thresholds
    TIER_THRESHOLDS = {
        "enterprise": 1000000,
        "pro": 300000,
        "business": 100000,
        "starter": 0
    }
    
    def __init__(
        self,
        query_patterns: List[str],
        expected_requests_per_day: int,
        peak_hour_percentage: float = 20.0,
        concurrent_users: Optional[int] = None,
        average_response_size_kb: Optional[float] = None,
        include_cost_analysis: bool = True
    ):
        self.query_patterns = query_patterns
        self.expected_requests_per_day = expected_requests_per_day
        self.peak_hour_percentage = peak_hour_percentage
        self.concurrent_users = concurrent_users
        self.average_response_size_kb = average_response_size_kb
        self.include_cost_analysis = include_cost_analysis
        self.usage_patterns = []  # Initialize to store analyzed patterns
    
    def analyze(self) -> RateLimitAnalysis:
        """Perform complete rate limit analysis."""
        # Analyze query patterns
        self.usage_patterns = self._analyze_query_patterns()
        
        # Generate usage forecast
        forecast = self._generate_usage_forecast(self.usage_patterns)
        
        # Generate optimization tips
        optimization_tips = self._generate_optimization_tips(self.usage_patterns)
        
        # Generate cost projections
        cost_projections = []
        if self.include_cost_analysis:
            cost_projections = self._generate_cost_projections(forecast)
        
        # Generate caching strategies
        caching_strategies = self._generate_caching_strategies(self.usage_patterns)
        
        # Generate summary and recommendations
        summary = self._generate_summary(forecast, optimization_tips, caching_strategies)
        recommendations = self._generate_priority_recommendations(
            forecast, optimization_tips, caching_strategies
        )
        
        return RateLimitAnalysis(
            usage_patterns=self.usage_patterns,
            forecast=forecast,
            optimization_tips=optimization_tips,
            cost_projections=cost_projections,
            caching_strategies=caching_strategies,
            summary=summary,
            recommendations=recommendations
        )
    
    def _analyze_query_patterns(self) -> List[UsagePattern]:
        """Analyze query patterns to identify usage characteristics."""
        # Group patterns by type
        grouped_patterns = self._group_patterns_by_type()
        
        # Create usage patterns for each group
        patterns = []
        total_patterns = len(self.query_patterns)
        
        for pattern_name, queries in grouped_patterns.items():
            pattern = self._create_usage_pattern(
                pattern_name, queries, total_patterns
            )
            patterns.append(pattern)
        
        return patterns
    
    def _group_patterns_by_type(self) -> Dict[str, List[str]]:
        """Group query patterns by their type."""
        grouped = {}
        
        for pattern in self.query_patterns:
            pattern_type = self._determine_pattern_type(pattern)
            
            if pattern_type not in grouped:
                grouped[pattern_type] = []
            grouped[pattern_type].append(pattern)
        
        return grouped
    
    def _determine_pattern_type(self, pattern: str) -> str:
        """Determine the type category for a query pattern."""
        pattern_lower = pattern.lower()
        
        if "patient" in pattern_lower:
            if "demographic" in pattern_lower:
                return "Patient Demographics"
            elif "phi" in pattern_lower:
                return "Patient PHI Data"
            else:
                return "Patient Management"
        elif "appointment" in pattern_lower:
            return "Appointment Management"
        elif any(term in pattern_lower for term in ["billing", "claim", "payment", "insurance"]):
            return "Billing Operations"
        elif "provider" in pattern_lower:
            return "Provider Management"
        elif any(term in pattern_lower for term in ["clinical", "note", "form", "lab"]):
            return "Clinical Documentation"
        else:
            return "General Operations"
    
    def _create_usage_pattern(
        self, 
        pattern_name: str, 
        queries: List[str], 
        total_patterns: int
    ) -> UsagePattern:
        """Create a usage pattern from grouped queries."""
        # Determine maximum complexity
        max_complexity = self._determine_max_complexity(queries)
        
        # Calculate request metrics
        pattern_percentage = len(queries) / total_patterns
        pattern_daily_requests = self.expected_requests_per_day * pattern_percentage
        
        # Calculate per-minute rates
        requests_per_minute = pattern_daily_requests / (24 * 60)
        peak_multiplier = 3.0 if self.concurrent_users and self.concurrent_users > 50 else 2.0
        peak_requests_per_minute = requests_per_minute * peak_multiplier
        
        # Generate time distribution
        time_distribution = self._generate_time_distribution()
        
        return UsagePattern(
            pattern_name=pattern_name,
            requests_per_minute=round(requests_per_minute, 2),
            peak_requests_per_minute=round(peak_requests_per_minute, 2),
            query_types=queries,
            complexity=max_complexity,
            time_distribution=time_distribution
        )
    
    def _determine_max_complexity(self, queries: List[str]) -> QueryComplexity:
        """Determine the maximum complexity among queries."""
        max_complexity = QueryComplexity.LOW
        
        for query in queries:
            query_lower = query.lower()
            
            # Check for very high complexity patterns first
            if any(term in query_lower for term in ["bulk", "export", "sync"]):
                return QueryComplexity.VERY_HIGH
            
            # Check for nested/complex queries
            if "nested" in query_lower or ("with" in query_lower and "and" in query_lower):
                max_complexity = QueryComplexity.HIGH
                continue
                
            # Check other patterns
            for keyword, complexity in self.COMPLEXITY_MAP.items():
                if keyword in query_lower:
                    if list(QueryComplexity).index(complexity) > list(QueryComplexity).index(max_complexity):
                        max_complexity = complexity
        
        return max_complexity
    
    def _generate_time_distribution(self) -> Dict[int, float]:
        """Generate hourly time distribution for business hours."""
        distribution = {}
        business_hours = range(8, 18)  # 8 AM to 6 PM
        
        for hour in range(24):
            if hour in business_hours:
                distribution[hour] = 0.08  # 8% per business hour
            else:
                distribution[hour] = 0.02  # 2% per non-business hour
        
        return distribution
    
    def _generate_usage_forecast(self, usage_patterns: List[UsagePattern]) -> UsageForecast:
        """Generate usage forecast based on patterns."""
        monthly_requests = self.expected_requests_per_day * 30
        
        # Use the provided peak_hour_percentage or default to 25%
        percentage = self.peak_hour_percentage if self.peak_hour_percentage else 25.0
        peak_hour_requests = int(self.expected_requests_per_day * (percentage / 100))
        
        # Determine rate limit risk
        rate_limit_risk = self._calculate_rate_limit_risk(
            self.expected_requests_per_day, 
            peak_hour_requests, 
            usage_patterns
        )
        
        # Recommend tier
        recommended_tier = self._determine_recommended_tier(monthly_requests)
        
        return UsageForecast(
            daily_requests=self.expected_requests_per_day,
            monthly_requests=monthly_requests,
            peak_hour_requests=peak_hour_requests,
            rate_limit_risk=rate_limit_risk,
            recommended_tier=recommended_tier
        )
    
    def _calculate_rate_limit_risk(
        self, 
        daily_requests: int, 
        peak_hour_requests: int, 
        usage_patterns: List[UsagePattern]
    ) -> str:
        """Calculate rate limit risk level."""
        # Count high complexity patterns
        high_complexity_count = sum(
            1 for p in usage_patterns 
            if p.complexity in [QueryComplexity.HIGH, QueryComplexity.VERY_HIGH]
        )
        
        if (daily_requests > self.DAILY_REQUEST_THRESHOLDS["high_risk"] or 
            peak_hour_requests > self.PEAK_HOUR_THRESHOLDS["high_risk"]):
            return "high"
        elif (daily_requests > self.DAILY_REQUEST_THRESHOLDS["medium_risk"] or 
              peak_hour_requests > self.PEAK_HOUR_THRESHOLDS["medium_risk"] or 
              high_complexity_count > 2):
            return "medium"
        else:
            return "low"
    
    def _determine_recommended_tier(self, monthly_requests: int) -> str:
        """Determine recommended service tier based on usage."""
        for tier, threshold in sorted(self.TIER_THRESHOLDS.items(), 
                                     key=lambda x: x[1], reverse=True):
            if monthly_requests > threshold:
                return tier
        return "starter"
    
    def _generate_optimization_tips(self, usage_patterns: List[UsagePattern]) -> List[OptimizationTip]:
        """Generate optimization tips based on usage patterns."""
        tips = []
        
        # Add tips based on complexity
        for pattern in usage_patterns:
            if pattern.complexity in [QueryComplexity.HIGH, QueryComplexity.VERY_HIGH]:
                tips.append(self._create_complexity_optimization_tip(pattern))
        
        # Add general optimization tips
        if self.expected_requests_per_day >= 10000:
            tips.append(self._create_batch_optimization_tip())
        
        if self.concurrent_users and self.concurrent_users >= 50:
            tips.append(self._create_connection_pooling_tip())
        
        # Add additional tips for high volume scenarios
        if self.expected_requests_per_day >= 30000:
            tips.extend([
                self._create_request_queuing_tip(),
                self._create_rate_limiting_tip(),
                self._create_request_deduplication_tip()
            ])
        
        # Add caching tip for significant volume
        if self.expected_requests_per_day >= 5000:
            tips.append(self._create_aggressive_caching_tip())
        
        # Add healthcare-specific tips if we have healthcare patterns
        healthcare_patterns = [p for p in usage_patterns if any(
            term in p.pattern_name.lower() 
            for term in ['patient', 'appointment', 'clinical', 'billing', 'provider']
        )]
        if healthcare_patterns:
            tips.append(self._create_healthcare_optimization_tip())
        
        return tips
    
    def _create_complexity_optimization_tip(self, pattern: UsagePattern) -> OptimizationTip:
        """Create optimization tip for complex queries."""
        title = f"Query Optimization for {pattern.pattern_name}"
        description = f"Simplify and optimize {pattern.pattern_name} queries by implementing field selection, pagination, and query simplification"
        
        if pattern.complexity == QueryComplexity.VERY_HIGH:
            title = f"Simplify Complex {pattern.pattern_name} Queries"
            description = f"Reduce query complexity in {pattern.pattern_name} by breaking down nested queries and implementing batch processing"
        
        return OptimizationTip(
            title=title,
            description=description,
            impact="Could reduce API calls by 20-40%",
            implementation_effort="medium",
            example_code=self._get_optimization_example(pattern.pattern_name)
        )
    
    def _create_batch_optimization_tip(self) -> OptimizationTip:
        """Create batch processing optimization tip."""
        return OptimizationTip(
            title="Implement Batch Operations",
            description="Replace individual API calls with batch operations for bulk data processing",
            impact="Reduce API calls by up to 90% for bulk operations",
            implementation_effort="medium",
            example_code="""
// Instead of individual calls:
for (const patient of patients) {
  await api.updatePatient(patient.id, data);
}

// Use batch operations:
await api.batchUpdatePatients(patients.map(p => ({
  id: p.id,
  data: data
})));
"""
        )
    
    def _create_connection_pooling_tip(self) -> OptimizationTip:
        """Create connection pooling optimization tip."""
        return OptimizationTip(
            title="Enable Connection Pooling",
            description="Configure connection pooling to handle concurrent requests more efficiently",
            impact="Improve response times by 15-25%",
            implementation_effort="low",
            example_code="""
// Configure connection pooling
const client = new GraphQLClient({
  url: API_URL,
  connectionPool: {
    maxConnections: 20,
    idleTimeout: 30000
  }
});
"""
        )
    
    def _create_request_queuing_tip(self) -> OptimizationTip:
        """Create request queuing optimization tip."""
        return OptimizationTip(
            title="Implement Request Queuing",
            description="Queue and prioritize API requests to handle high-volume scenarios efficiently",
            impact="Prevent rate limit violations and improve system stability",
            implementation_effort="high",
            example_code="""
// Implement request queue with priority
const requestQueue = new RequestQueue({
  maxConcurrent: 10,
  rateLimitPerSecond: 100
});

// Queue requests with priority
await requestQueue.add(patientRequest, { priority: 'high' });
await requestQueue.add(reportRequest, { priority: 'low' });
"""
        )
    
    def _create_rate_limiting_tip(self) -> OptimizationTip:
        """Create client-side rate limiting tip."""
        return OptimizationTip(
            title="Client-Side Rate Limiting",
            description="Implement client-side rate limiting to stay within API limits",
            impact="Prevent API rejections and improve reliability",
            implementation_effort="medium",
            example_code="""
// Rate limiter with token bucket
const rateLimiter = new RateLimiter({
  tokensPerInterval: 100,
  interval: 'second'
});

// Check before making requests
if (await rateLimiter.removeTokens(1)) {
  // Make API call
  return api.call();
}
"""
        )
    
    def _create_request_deduplication_tip(self) -> OptimizationTip:
        """Create request deduplication tip."""
        return OptimizationTip(
            title="Request Deduplication",
            description="Eliminate duplicate requests within short time windows",
            impact="Reduce API calls by 15-30% by avoiding redundant requests",
            implementation_effort="medium",
            example_code="""
// Deduplication cache
const dedupCache = new Map();

async function deduplicatedRequest(key, requestFn) {
  if (dedupCache.has(key)) {
    return dedupCache.get(key);
  }
  
  const promise = requestFn();
  dedupCache.set(key, promise);
  
  // Clean up after 5 seconds
  setTimeout(() => dedupCache.delete(key), 5000);
  
  return promise;
}
"""
        )
    
    def _create_aggressive_caching_tip(self) -> OptimizationTip:
        """Create aggressive caching tip."""
        return OptimizationTip(
            title="Aggressive Caching Strategy",
            description="Implement multi-tier caching with longer TTLs for reference data",
            impact="Reduce API calls by 60-80% for frequently accessed data",
            implementation_effort="medium",
            example_code="""
// Multi-tier cache setup
const cache = {
  memory: new MemoryCache({ ttl: 300 }), // 5 minutes
  redis: new RedisCache({ ttl: 3600 }),  // 1 hour
  cdn: new CDNCache({ ttl: 86400 })      // 24 hours
};

// Cascading cache lookup
async function cachedRequest(key, requestFn) {
  return cache.memory.get(key) ||
         await cache.redis.get(key) ||
         await cache.cdn.get(key) ||
         await requestFn();
}
"""
        )
    
    def _get_optimization_example(self, pattern_name: str) -> str:
        """Get code example for pattern optimization."""
        examples = {
            "Patient Management": """
// Use field selection to reduce payload
const PATIENT_FIELDS = `
  id
  firstName
  lastName
  email
  phoneNumber
`;

// Only request needed fields
const patient = await api.query({
  patient: {
    args: { id },
    fields: PATIENT_FIELDS
  }
});
""",
            "Appointment Management": """
// Cache appointment availability
const availability = await cache.getOrSet(
  `availability:${providerId}:${date}`,
  async () => api.getAvailability(providerId, date),
  { ttl: 300 } // 5 minute cache
);
""",
            "default": """
// Implement field selection
const result = await api.query({
  resource: {
    args: { id },
    fields: ['id', 'name', 'status'] // Only needed fields
  }
});
"""
        }
        
        return examples.get(pattern_name, examples["default"])
    
    def _generate_cost_projections(self, forecast: UsageForecast) -> List[CostProjection]:
        """Generate cost projections for different scenarios."""
        projections = []
        tiers = ["starter", "business", "pro", "enterprise"]
        
        # Generate projections for multiple tiers
        for tier in tiers:
            # Skip tiers that are too low for the usage
            if self.TIER_THRESHOLDS.get(tier, 0) > forecast.monthly_requests * 2:
                continue
                
            monthly_cost = self._calculate_monthly_cost_for_tier(
                forecast.monthly_requests, tier
            )
            
            projection = CostProjection(
                tier=tier,
                monthly_cost=monthly_cost,
                annual_cost=monthly_cost * 12,
                included_requests=self._get_included_requests(tier),
                overage_rate=self._get_overage_rate(tier),
                estimated_overage=self._calculate_overage(forecast.monthly_requests, tier)
            )
            projections.append(projection)
            
            # Ensure we have at least 3 projections
            if len(projections) >= 3:
                break
        
        # If we don't have enough projections, add higher tiers
        if len(projections) < 3:
            remaining_tiers = [t for t in tiers if t not in [p.tier for p in projections]]
            for tier in remaining_tiers:
                monthly_cost = self._calculate_monthly_cost_for_tier(
                    forecast.monthly_requests, tier
                )
                
                projection = CostProjection(
                    tier=tier,
                    monthly_cost=monthly_cost,
                    annual_cost=monthly_cost * 12,
                    included_requests=self._get_included_requests(tier),
                    overage_rate=self._get_overage_rate(tier),
                    estimated_overage=self._calculate_overage(forecast.monthly_requests, tier)
                )
                projections.append(projection)
                
                if len(projections) >= 3:
                    break
        
        return projections
    
    def _calculate_monthly_cost(self, monthly_requests: int, scenario: str) -> float:
        """Calculate total monthly cost."""
        api_cost = self._calculate_api_cost(monthly_requests)
        data_cost = self._calculate_data_cost(monthly_requests)
        support_cost = self._get_support_cost(self._determine_recommended_tier(monthly_requests))
        
        return api_cost + data_cost + support_cost
    
    def _calculate_api_cost(self, monthly_requests: int) -> float:
        """Calculate API call costs (simplified)."""
        # Tiered pricing example
        if monthly_requests <= 100000:
            return monthly_requests * 0.0001  # $0.0001 per request
        elif monthly_requests <= 1000000:
            return 100000 * 0.0001 + (monthly_requests - 100000) * 0.00008
        else:
            return 100000 * 0.0001 + 900000 * 0.00008 + (monthly_requests - 1000000) * 0.00006
    
    def _calculate_data_cost(self, monthly_requests: int) -> float:
        """Calculate data transfer costs."""
        if self.average_response_size_kb:
            total_gb = (monthly_requests * self.average_response_size_kb) / (1024 * 1024)
            return total_gb * 0.09  # $0.09 per GB
        else:
            # Estimate 5KB average response
            total_gb = (monthly_requests * 5) / (1024 * 1024)
            return total_gb * 0.09
    
    def _get_support_cost(self, tier: str) -> float:
        """Get monthly support cost by tier."""
        support_costs = {
            "starter": 0,
            "business": 299,
            "pro": 999,
            "enterprise": 2999
        }
        return support_costs.get(tier, 0)
    
    def _get_included_requests(self, tier: str) -> int:
        """Get included requests for a tier."""
        included_requests = {
            "starter": 100000,
            "business": 500000,
            "pro": 2000000,
            "enterprise": 10000000
        }
        return included_requests.get(tier, 100000)
    
    def _get_overage_rate(self, tier: str) -> float:
        """Get overage rate per request for a tier."""
        overage_rates = {
            "starter": 0.0001,
            "business": 0.00008,
            "pro": 0.00006,
            "enterprise": 0.00004
        }
        return overage_rates.get(tier, 0.0001)
    
    def _calculate_overage(self, monthly_requests: int, tier: str) -> float:
        """Calculate overage cost for a tier."""
        included = self._get_included_requests(tier)
        if monthly_requests <= included:
            return 0.0
        
        overage_requests = monthly_requests - included
        overage_rate = self._get_overage_rate(tier)
        return overage_requests * overage_rate
    
    def _get_optimized_tier(self, monthly_requests: int) -> str:
        """Get an optimized tier that might save costs."""
        # Try to find a tier that includes all requests without overage
        for tier, threshold in sorted(self.TIER_THRESHOLDS.items(), 
                                     key=lambda x: x[1]):
            if monthly_requests <= self._get_included_requests(tier):
                return tier
        return "enterprise"
    
    def _calculate_monthly_cost_for_tier(self, monthly_requests: int, tier: str) -> float:
        """Calculate monthly cost for a specific tier."""
        support_cost = self._get_support_cost(tier)
        overage_cost = self._calculate_overage(monthly_requests, tier)
        
        # Base tier costs (simplified)
        base_costs = {
            "starter": 0,
            "business": 199,
            "pro": 599,
            "enterprise": 1999
        }
        base_cost = base_costs.get(tier, 0)
        
        return base_cost + support_cost + overage_cost
    
    def _generate_caching_strategies(self, usage_patterns: List[UsagePattern]) -> List[CachingStrategy]:
        """Generate caching strategies based on patterns."""
        strategies = []
        
        # Create caching strategies for all patterns (complexity-appropriate)
        for pattern in usage_patterns:
            strategy = self._create_caching_strategy(pattern)
            strategies.append(strategy)
        
        # Add general caching strategy for smaller responses
        if self.average_response_size_kb and self.average_response_size_kb < 50:
            strategies.append(self._create_edge_caching_strategy())
        
        # For high volume scenarios without specific response size, add edge caching
        if self.expected_requests_per_day >= 30000 and not self.average_response_size_kb:
            strategies.append(self._create_edge_caching_strategy())
        
        return strategies
    
    def _create_caching_strategy(self, pattern: UsagePattern) -> CachingStrategy:
        """Create caching strategy for a pattern."""
        ttl_map = {
            "Patient Management": "1 hour",
            "Patient Demographics": "4 hours",
            "Patient PHI Data": "30 minutes",
            "Provider Management": "24 hours",
            "Appointment Management": "5 minutes",
            "Clinical Documentation": "2 hours",
            "General Operations": "30 minutes"
        }
        
        cache_duration = ttl_map.get(pattern.pattern_name, "30 minutes")
        
        # Healthcare-specific considerations
        healthcare_considerations = []
        if any(term in pattern.pattern_name.lower() for term in ['patient', 'clinical', 'phi']):
            healthcare_considerations.extend([
                "HIPAA compliance required for PHI data caching",
                "Implement encryption at rest for sensitive data",
                "Audit logging for PHI access patterns",
                "Consider data residency requirements"
            ])
        
        base_considerations = [
            "Monitor cache hit rates",
            "Consider data freshness requirements", 
            "Implement cache warming for critical data"
        ]
        
        all_considerations = healthcare_considerations + base_considerations
        
        # Calculate reduction percentage based on pattern type
        reduction_percentage = 70
        if "demographics" in pattern.pattern_name.lower():
            reduction_percentage = 85  # Demographics are more cacheable
        elif "phi" in pattern.pattern_name.lower():
            reduction_percentage = 50  # PHI requires careful caching
        elif pattern.complexity == QueryComplexity.VERY_HIGH:
            reduction_percentage = 90  # High complexity benefits most from caching
        
        return CachingStrategy(
            strategy_name=f"{pattern.pattern_name} Caching",
            applicable_queries=pattern.query_types,
            cache_duration=cache_duration,
            expected_reduction=f"{reduction_percentage}% reduction ({max(1, int((reduction_percentage/100) * pattern.requests_per_minute))} req/min saved)",
            implementation_guide=[
                f"Implement cache key pattern: {pattern.pattern_name.lower().replace(' ', '_')}:{{id}}:{{hash}}",
                f"Set TTL to {cache_duration}",
                "Use cache-aside pattern for read operations",
                "Invalidate cache on mutations"
            ],
            considerations=all_considerations
        )
    
    def _create_edge_caching_strategy(self) -> CachingStrategy:
        """Create edge caching strategy."""
        return CachingStrategy(
            strategy_name="Edge Caching",
            applicable_queries=["static_resources", "configuration", "schema_introspection"],
            cache_duration="1-24 hours depending on content type",
            expected_reduction="80% reduction for static content requests",
            implementation_guide=[
                "Deploy CDN edge nodes",
                "Configure cache headers appropriately",
                "Implement cache key pattern: edge:{{resource}}:{{version}}",
                "Set up cache purging mechanisms"
            ],
            considerations=[
                "CDN costs vs API cost savings",
                "Geographic distribution of users",
                "Cache invalidation complexity"
            ]
        )
    
    def _create_healthcare_optimization_tip(self) -> OptimizationTip:
        """Create healthcare-specific optimization tip."""
        return OptimizationTip(
            title="Healthcare Data Optimization",
            description="Implement healthcare-specific optimizations including batch processing for patient records and HIPAA-compliant caching",
            impact="Reduce PHI data exposure and improve performance by 30-50%",
            implementation_effort="medium",
            example_code="""
// Batch patient data requests
const patientIds = ['pat1', 'pat2', 'pat3'];
const patients = await api.batchQuery({
  patients: {
    args: { ids: patientIds },
    fields: PATIENT_FIELDS
  }
});

// Use HIPAA-compliant caching
const cache = new HIPAACompliantCache({
  encryption: true,
  auditLogging: true,
  maxAge: 3600 // 1 hour for PHI
});
"""
        )
    
    def _generate_summary(
        self, 
        forecast: UsageForecast, 
        optimization_tips: List[OptimizationTip],
        caching_strategies: List[CachingStrategy]
    ) -> str:
        """Generate analysis summary."""
        risk_text = {
            "high": "High risk of hitting rate limits",
            "medium": "Moderate risk of rate limiting during peak hours",
            "low": "Low risk of rate limiting"
        }
        
        return (
            f"Analysis complete: {risk_text.get(forecast.rate_limit_risk, 'Unknown risk')}. "
            f"Recommended tier: {forecast.recommended_tier}. "
            f"Found {len(optimization_tips)} optimization opportunities and "
            f"{len(caching_strategies)} caching strategies."
        )
    
    def _generate_priority_recommendations(
        self,
        forecast: UsageForecast,
        optimization_tips: List[OptimizationTip],
        caching_strategies: List[CachingStrategy]
    ) -> List[str]:
        """Generate prioritized recommendations."""
        recommendations = []
        
        # High risk recommendations
        if forecast.rate_limit_risk == "high":
            recommendations.append("URGENT: Implement rate limiting and request queuing immediately")
            recommendations.append(f"Upgrade to {forecast.recommended_tier} tier to handle current load")
            recommendations.append("Implement aggressive caching strategies")
        
        # Medium risk recommendations
        elif forecast.rate_limit_risk == "medium":
            recommendations.append("Consider implementing request batching for bulk operations")
            recommendations.append(f"Monitor usage closely and prepare to upgrade to {forecast.recommended_tier} tier")
        
        # General recommendations
        if optimization_tips:
            recommendations.append(f"Implement top {min(3, len(optimization_tips))} optimization tips for immediate impact")
        
        if caching_strategies:
            recommendations.append("Deploy caching strategies starting with highest-volume endpoints")
        
        if self.concurrent_users and self.concurrent_users > 50:
            recommendations.append("Implement connection pooling and request deduplication")
        
        # Healthcare-specific recommendations
        if any('patient' in p.pattern_name.lower() or 'clinical' in p.pattern_name.lower() 
               for p in self.usage_patterns):
            recommendations.append("Ensure HIPAA compliance for all patient data caching")
            recommendations.append("Implement audit logging for PHI access patterns")
        
        return recommendations


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
            
            # Create analyzer and run analysis
            analyzer = RateLimitAnalyzer(
                query_patterns=query_patterns,
                expected_requests_per_day=expected_requests_per_day,
                peak_hour_percentage=peak_hour_percentage,
                concurrent_users=concurrent_users,
                average_response_size_kb=average_response_size_kb,
                include_cost_analysis=include_cost_analysis
            )
            
            return analyzer.analyze()
            
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