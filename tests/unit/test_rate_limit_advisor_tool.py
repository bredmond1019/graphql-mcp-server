"""Tests for rate limit advisor tool."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

# Mock the MCP module before importing our modules
sys.modules['mcp'] = MagicMock()
sys.modules['mcp.server'] = MagicMock()
sys.modules['mcp.server.fastmcp'] = MagicMock()

import pytest
from healthie_mcp.tools.rate_limit_advisor import setup_rate_limit_advisor_tool
from healthie_mcp.models.rate_limit_advisor import (
    RateLimitAnalysis,
    UsagePattern,
    UsageForecast,
    OptimizationTip,
    CostProjection,
    CachingStrategy,
    QueryComplexity
)


class TestRateLimitAdvisorToolRegistration:
    """Test rate limit advisor tool registration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_schema_manager = Mock()
        self.mock_mcp = MagicMock()
        self.registered_tools = {}
        
        # Mock the tool decorator to capture registered functions
        def mock_tool():
            def decorator(func):
                self.registered_tools[func.__name__] = func
                return func
            return decorator
        
        self.mock_mcp.tool = mock_tool
    
    def test_analyze_rate_limits_tool_is_registered(self):
        """Test that analyze_rate_limits tool is registered."""
        setup_rate_limit_advisor_tool(self.mock_mcp, self.mock_schema_manager)
        
        assert 'analyze_rate_limits' in self.registered_tools
        assert callable(self.registered_tools['analyze_rate_limits'])


class TestRateLimitAdvisorFunctionality:
    """Test rate limit advisor functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_schema_manager = Mock()
        self.mock_mcp = MagicMock()
        self.registered_tools = {}
        
        # Mock the tool decorator to capture registered functions
        def mock_tool():
            def decorator(func):
                self.registered_tools[func.__name__] = func
                return func
            return decorator
        
        self.mock_mcp.tool = mock_tool
    
    def test_rate_limit_advisor_analyzes_query_patterns(self):
        """Test that the tool analyzes query patterns for rate limit impact."""
        setup_rate_limit_advisor_tool(self.mock_mcp, self.mock_schema_manager)
        analyze_tool = self.registered_tools['analyze_rate_limits']
        
        # Test with patient list queries
        query_info = {
            "query_types": ["patient_list", "appointment_list"],
            "expected_volume": 1000,
            "time_period": "daily"
        }
        
        result = analyze_tool(
            query_patterns=query_info["query_types"],
            expected_requests_per_day=query_info["expected_volume"]
        )
        
        assert isinstance(result, RateLimitAnalysis)
        assert len(result.usage_patterns) > 0
        
        # Check that patterns are identified
        pattern = result.usage_patterns[0]
        assert isinstance(pattern, UsagePattern)
        assert pattern.pattern_name is not None
        assert pattern.requests_per_minute > 0
        assert pattern.complexity in QueryComplexity
        assert "patient_list" in pattern.query_types or "appointment_list" in pattern.query_types
    
    def test_rate_limit_advisor_forecasts_usage(self):
        """Test that the tool forecasts API usage based on planned queries."""
        setup_rate_limit_advisor_tool(self.mock_mcp, self.mock_schema_manager)
        analyze_tool = self.registered_tools['analyze_rate_limits']
        
        result = analyze_tool(
            query_patterns=["patient_details", "appointment_create"],
            expected_requests_per_day=5000,
            peak_hour_percentage=25  # 25% of traffic in peak hour
        )
        
        assert isinstance(result.forecast, UsageForecast)
        assert result.forecast.daily_requests == 5000
        assert result.forecast.monthly_requests == 5000 * 30  # Approximate
        assert result.forecast.peak_hour_requests == 1250  # 25% of 5000
        assert result.forecast.rate_limit_risk in ["low", "medium", "high"]
        assert result.forecast.recommended_tier is not None
    
    def test_rate_limit_advisor_provides_optimization_tips(self):
        """Test that the tool provides optimization tips to reduce rate limit hits."""
        setup_rate_limit_advisor_tool(self.mock_mcp, self.mock_schema_manager)
        analyze_tool = self.registered_tools['analyze_rate_limits']
        
        # High volume scenario that should trigger optimization tips
        result = analyze_tool(
            query_patterns=["patient_list", "appointment_list", "billing_details"],
            expected_requests_per_day=10000
        )
        
        assert len(result.optimization_tips) > 0
        
        tip = result.optimization_tips[0]
        assert isinstance(tip, OptimizationTip)
        assert tip.title is not None
        assert tip.description is not None
        assert tip.impact is not None
        assert tip.implementation_effort in ["low", "medium", "high"]
        
        # Should include tips like batching, pagination, field selection
        tip_titles = [t.title.lower() for t in result.optimization_tips]
        assert any(keyword in ' '.join(tip_titles) for keyword in ["batch", "pagination", "field", "cache"])
    
    def test_rate_limit_advisor_calculates_cost_projections(self):
        """Test that the tool calculates cost projections for different usage levels."""
        setup_rate_limit_advisor_tool(self.mock_mcp, self.mock_schema_manager)
        analyze_tool = self.registered_tools['analyze_rate_limits']
        
        result = analyze_tool(
            query_patterns=["patient_create", "appointment_update"],
            expected_requests_per_day=2000,
            include_cost_analysis=True
        )
        
        assert len(result.cost_projections) > 0
        
        # Should have multiple tier options
        assert len(result.cost_projections) >= 3
        
        for projection in result.cost_projections:
            assert isinstance(projection, CostProjection)
            assert projection.tier is not None
            assert projection.monthly_cost >= 0
            assert projection.annual_cost == projection.monthly_cost * 12
            assert projection.included_requests > 0
            
        # Tiers should be ordered by cost
        costs = [p.monthly_cost for p in result.cost_projections]
        assert costs == sorted(costs)
    
    def test_rate_limit_advisor_suggests_caching_strategies(self):
        """Test that the tool suggests appropriate caching strategies."""
        setup_rate_limit_advisor_tool(self.mock_mcp, self.mock_schema_manager)
        analyze_tool = self.registered_tools['analyze_rate_limits']
        
        result = analyze_tool(
            query_patterns=["patient_demographics", "provider_list", "insurance_verification"],
            expected_requests_per_day=8000
        )
        
        assert len(result.caching_strategies) > 0
        
        strategy = result.caching_strategies[0]
        assert isinstance(strategy, CachingStrategy)
        assert strategy.strategy_name is not None
        assert len(strategy.applicable_queries) > 0
        assert strategy.cache_duration is not None
        assert strategy.expected_reduction is not None
        assert len(strategy.implementation_guide) > 0
        assert len(strategy.considerations) > 0
        
        # Should have strategies for different query types
        strategy_names = [s.strategy_name.lower() for s in result.caching_strategies]
        assert any("demographic" in name or "static" in name for name in strategy_names)
        assert any("provider" in name or "reference" in name for name in strategy_names)
    
    def test_handles_high_volume_scenarios(self):
        """Test handling of high-volume API usage scenarios."""
        setup_rate_limit_advisor_tool(self.mock_mcp, self.mock_schema_manager)
        analyze_tool = self.registered_tools['analyze_rate_limits']
        
        # Very high volume scenario
        result = analyze_tool(
            query_patterns=["patient_sync", "appointment_bulk_create", "billing_batch"],
            expected_requests_per_day=50000,
            concurrent_users=100
        )
        
        assert result.forecast.rate_limit_risk == "high"
        assert len(result.optimization_tips) >= 5  # Should have many optimization suggestions
        assert result.forecast.recommended_tier in ["enterprise", "pro", "business"]
        
        # Should recommend aggressive caching
        cache_reductions = []
        for strategy in result.caching_strategies:
            if "%" in strategy.expected_reduction:
                # Extract the highest percentage from ranges like "60-70%"
                import re
                percentages = re.findall(r'\d+', strategy.expected_reduction)
                if percentages:
                    cache_reductions.append(max(int(p) for p in percentages))
        
        assert max(cache_reductions) >= 50  # At least one strategy should reduce by 50%+
    
    def test_handles_complex_query_patterns(self):
        """Test analysis of complex query patterns."""
        setup_rate_limit_advisor_tool(self.mock_mcp, self.mock_schema_manager)
        analyze_tool = self.registered_tools['analyze_rate_limits']
        
        result = analyze_tool(
            query_patterns=["nested_patient_with_appointments_and_forms", "bulk_export"],
            expected_requests_per_day=1000,
            average_response_size_kb=500
        )
        
        # Complex queries should be identified as high complexity
        complex_patterns = [p for p in result.usage_patterns if p.complexity in [QueryComplexity.HIGH, QueryComplexity.VERY_HIGH]]
        assert len(complex_patterns) > 0
        
        # Should recommend query optimization
        optimization_titles = [t.title.lower() for t in result.optimization_tips]
        assert any("query" in title and ("optim" in title or "simplif" in title) for title in optimization_titles)
    
    def test_structured_output_format(self):
        """Test that output follows structured format."""
        setup_rate_limit_advisor_tool(self.mock_mcp, self.mock_schema_manager)
        analyze_tool = self.registered_tools['analyze_rate_limits']
        
        result = analyze_tool(
            query_patterns=["patient_search"],
            expected_requests_per_day=500
        )
        
        assert isinstance(result, RateLimitAnalysis)
        assert isinstance(result.usage_patterns, list)
        assert isinstance(result.forecast, UsageForecast)
        assert isinstance(result.optimization_tips, list)
        assert isinstance(result.cost_projections, list)
        assert isinstance(result.caching_strategies, list)
        assert isinstance(result.summary, str)
        assert isinstance(result.recommendations, list)
        
        # Summary should be informative
        assert len(result.summary) > 50
        assert len(result.recommendations) > 0
    
    def test_healthcare_specific_recommendations(self):
        """Test that recommendations are healthcare-aware."""
        setup_rate_limit_advisor_tool(self.mock_mcp, self.mock_schema_manager)
        analyze_tool = self.registered_tools['analyze_rate_limits']
        
        result = analyze_tool(
            query_patterns=["patient_phi", "clinical_notes", "lab_results"],
            expected_requests_per_day=3000
        )
        
        # Should include healthcare-specific considerations
        all_text = result.summary + " ".join(result.recommendations)
        healthcare_keywords = ["hipaa", "phi", "compliance", "audit", "patient", "clinical"]
        assert any(keyword in all_text.lower() for keyword in healthcare_keywords)
        
        # Caching strategies should consider PHI
        cache_considerations = []
        for strategy in result.caching_strategies:
            cache_considerations.extend(strategy.considerations)
        
        cache_text = " ".join(cache_considerations).lower()
        assert any(keyword in cache_text for keyword in ["phi", "sensitive", "compliance", "hipaa"])