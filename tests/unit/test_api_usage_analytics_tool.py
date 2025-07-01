"""Unit tests for API usage analytics tool."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.healthie_mcp.models.api_usage_analytics import (
    ApiUsageAnalyticsInput,
    ApiUsageAnalyticsResult,
    TimeRange,
    MetricType,
    OptimizationType,
    UsagePattern,
    PerformanceInsight,
    OptimizationSuggestion,
    PerformanceMetric,
    AnalyticsReport
)
from src.healthie_mcp.tools.api_usage_analytics import ApiUsageAnalyzer


class TestApiUsageAnalyticsTool:
    """Test cases for API usage analytics tool."""
    
    @pytest.fixture
    def mock_schema_manager(self):
        """Create mock schema manager."""
        return Mock()
    
    @pytest.fixture
    def tool(self, mock_schema_manager):
        """Create tool instance."""
        return ApiUsageAnalyzer(mock_schema_manager)
    
    @pytest.fixture
    def sample_config(self):
        """Sample configuration for testing."""
        return {
            "usage_patterns": {
                "peak_hours": {
                    "description": "High traffic during business hours",
                    "detection_criteria": {
                        "time_windows": ["9-11", "14-16"],
                        "threshold_multiplier": 1.5
                    }
                },
                "batch_operations": {
                    "description": "Multiple similar operations in sequence",
                    "detection_criteria": {
                        "min_operations": 5,
                        "time_window_seconds": 60
                    }
                }
            },
            "performance_thresholds": {
                "response_time": {
                    "good": 100,
                    "warning": 500,
                    "critical": 1000,
                    "unit": "ms"
                },
                "error_rate": {
                    "good": 0.01,
                    "warning": 0.05,
                    "critical": 0.10,
                    "unit": "percentage"
                }
            },
            "optimization_rules": {
                "query_batching": {
                    "conditions": {
                        "min_similar_queries": 3,
                        "time_window_seconds": 30
                    },
                    "impact": {
                        "request_reduction": 0.7,
                        "performance_gain": 0.5
                    }
                },
                "field_selection": {
                    "conditions": {
                        "unused_field_percentage": 0.5,
                        "min_fields": 10
                    },
                    "impact": {
                        "data_transfer_reduction": 0.6,
                        "performance_gain": 0.3
                    }
                }
            },
            "healthcare_metrics": {
                "phi_access": {
                    "sensitive_fields": ["ssn", "dob", "diagnosis", "medications"],
                    "compliance_checks": ["access_logging", "encryption", "authorization"]
                },
                "workflow_patterns": {
                    "patient_registration": ["create_patient", "add_insurance", "schedule_appointment"],
                    "clinical_documentation": ["create_encounter", "add_notes", "update_diagnosis"]
                }
            }
        }
    
    def test_api_usage_analytics_tracks_patterns(self, tool, sample_config):
        """Test that the tool tracks usage patterns over time."""
        # Arrange
        with patch.object(tool.config_loader, 'load_api_usage_analytics', return_value=sample_config):
            input_data = ApiUsageAnalyticsInput(
                time_range=TimeRange.DAY,
                include_patterns=True
            )
            
            # Mock usage data
            mock_usage_data = {
                "operations": [
                    {"name": "get_patient", "timestamp": "2024-01-15T10:30:00Z", "count": 150},
                    {"name": "get_patient", "timestamp": "2024-01-15T10:31:00Z", "count": 145},
                    {"name": "get_patient", "timestamp": "2024-01-15T10:32:00Z", "count": 160},
                    {"name": "update_patient", "timestamp": "2024-01-15T14:30:00Z", "count": 200},
                    {"name": "create_appointment", "timestamp": "2024-01-15T14:31:00Z", "count": 180}
                ]
            }
            
            with patch.object(tool, '_fetch_usage_data', return_value=mock_usage_data):
                # Act
                result = tool.execute(input_data)
                
                # Assert
                assert result.success is True
                assert result.report is not None
                assert len(result.report.usage_patterns) > 0
                
                # Check for peak hours pattern
                peak_pattern = next((p for p in result.report.usage_patterns 
                                   if p.pattern_type == "peak_hours"), None)
                assert peak_pattern is not None
                assert peak_pattern.description == "High traffic during business hours"
                assert peak_pattern.impact == "high"
                assert peak_pattern.frequency > 0
                
                # Check for batch operations pattern
                batch_pattern = next((p for p in result.report.usage_patterns 
                                    if p.pattern_type == "batch_operations"), None)
                assert batch_pattern is not None
                assert batch_pattern.frequency == 1  # One batch of three consecutive get_patient calls
    
    def test_api_usage_analytics_provides_insights(self, tool, sample_config):
        """Test that the tool provides performance insights and metrics."""
        # Arrange
        with patch.object(tool.config_loader, 'load_api_usage_analytics', return_value=sample_config):
            input_data = ApiUsageAnalyticsInput(
                time_range=TimeRange.WEEK,
                include_insights=True
            )
            
            # Mock performance data
            mock_performance_data = {
                "operations": [
                    {
                        "name": "get_patient_list",
                        "avg_response_time": 850,
                        "max_response_time": 2000,
                        "error_count": 5,
                        "total_count": 1000
                    },
                    {
                        "name": "create_appointment",
                        "avg_response_time": 120,
                        "max_response_time": 300,
                        "error_count": 2,
                        "total_count": 500
                    }
                ]
            }
            
            with patch.object(tool, '_fetch_performance_data', return_value=mock_performance_data):
                # Act
                result = tool.execute(input_data)
                
                # Assert
                assert result.success is True
                assert result.report is not None
                assert len(result.report.performance_insights) > 0
                
                # Check for slow operation insight
                slow_op_insight = next((i for i in result.report.performance_insights 
                                      if i.category == "performance"), None)
                assert slow_op_insight is not None
                assert "get_patient_list" in slow_op_insight.affected_operations
                assert slow_op_insight.impact_score >= 7.0  # High impact due to slow response
                assert len(slow_op_insight.recommended_actions) > 0
    
    def test_api_usage_analytics_calculates_metrics(self, tool, sample_config):
        """Test that the tool calculates performance metrics."""
        # Arrange
        with patch.object(tool.config_loader, 'load_api_usage_analytics', return_value=sample_config):
            input_data = ApiUsageAnalyticsInput(
                time_range=TimeRange.MONTH,
                metric_types=[MetricType.RESPONSE_TIME, MetricType.ERROR_RATE]
            )
            
            # Mock metrics data
            mock_metrics_data = {
                "current_period": {
                    "avg_response_time": 250,
                    "total_requests": 50000,
                    "error_count": 500
                },
                "previous_period": {
                    "avg_response_time": 200,
                    "total_requests": 45000,
                    "error_count": 400
                }
            }
            
            with patch.object(tool, '_fetch_metrics_data', return_value=mock_metrics_data):
                # Act
                result = tool.execute(input_data)
                
                # Assert
                assert result.success is True
                assert result.report is not None
                assert len(result.report.metrics) >= 2
                
                # Check response time metric
                response_metric = next((m for m in result.report.metrics 
                                      if m.metric_type == MetricType.RESPONSE_TIME), None)
                assert response_metric is not None
                assert response_metric.value == 250
                assert response_metric.unit == "ms"
                assert response_metric.trend == "increasing"
                assert response_metric.change_percentage == 25.0  # 25% increase
                assert response_metric.threshold_status == "warning"  # Above 100ms good threshold
                
                # Check error rate metric
                error_metric = next((m for m in result.report.metrics 
                                   if m.metric_type == MetricType.ERROR_RATE), None)
                assert error_metric is not None
                assert error_metric.value == 0.01  # 1% error rate
                assert error_metric.unit == "percentage"
                assert error_metric.threshold_status == "good"  # At the good threshold
    
    def test_api_usage_analytics_suggests_optimizations(self, tool, sample_config):
        """Test that the tool suggests optimizations based on usage data."""
        # Arrange
        with patch.object(tool.config_loader, 'load_api_usage_analytics', return_value=sample_config):
            input_data = ApiUsageAnalyticsInput(
                time_range=TimeRange.WEEK,
                include_optimizations=True
            )
            
            # Mock optimization opportunity data
            mock_optimization_data = {
                "query_patterns": [
                    {
                        "pattern": "repeated_similar_queries",
                        "operations": ["get_patient", "get_patient", "get_patient"],
                        "time_window": 30,
                        "count": 5
                    }
                ],
                "field_usage": {
                    "get_patient": {
                        "total_fields": 20,
                        "used_fields": 8,
                        "unused_percentage": 0.6
                    }
                }
            }
            
            with patch.object(tool, '_analyze_optimization_opportunities', 
                            return_value=mock_optimization_data):
                # Act
                result = tool.execute(input_data)
                
                # Assert
                assert result.success is True
                assert result.report is not None
                assert len(result.report.optimization_suggestions) > 0
                
                # Check for query batching suggestion
                batch_suggestion = next((s for s in result.report.optimization_suggestions 
                                       if s.optimization_type == OptimizationType.QUERY_BATCHING), None)
                assert batch_suggestion is not None
                assert batch_suggestion.implementation_effort in ["low", "medium"]
                assert batch_suggestion.expected_impact == "high"
                assert batch_suggestion.example_before is not None
                assert batch_suggestion.example_after is not None
                assert "request_reduction" in batch_suggestion.estimated_improvement
                
                # Check for field selection suggestion
                field_suggestion = next((s for s in result.report.optimization_suggestions 
                                       if s.optimization_type == OptimizationType.FIELD_SELECTION), None)
                assert field_suggestion is not None
                assert field_suggestion.estimated_improvement["data_transfer_reduction"] == 0.6
    
    def test_api_usage_analytics_generates_reports(self, tool, sample_config):
        """Test that the tool generates comprehensive analytics reports."""
        # Arrange
        with patch.object(tool.config_loader, 'load_api_usage_analytics', return_value=sample_config):
            input_data = ApiUsageAnalyticsInput(
                time_range=TimeRange.QUARTER,
                include_healthcare_analysis=True
            )
            
            # Mock comprehensive data
            mock_comprehensive_data = {
                "summary": {
                    "total_requests": 500000,
                    "unique_operations": 45,
                    "avg_response_time": 180,
                    "error_rate": 0.02
                },
                "top_operations": [
                    {"name": "get_patient", "count": 150000, "percentage": 30},
                    {"name": "create_appointment", "count": 75000, "percentage": 15},
                    {"name": "update_insurance", "count": 50000, "percentage": 10}
                ],
                "healthcare_compliance": {
                    "phi_access_count": 200000,
                    "encryption_compliance": 100,
                    "audit_log_coverage": 98.5,
                    "authorization_failures": 150
                },
                "workflow_efficiency": {
                    "patient_registration": {
                        "avg_completion_time": 300,
                        "success_rate": 95,
                        "bottlenecks": ["insurance_verification"]
                    }
                }
            }
            
            with patch.object(tool, '_generate_comprehensive_report', 
                            return_value=mock_comprehensive_data):
                # Act
                result = tool.execute(input_data)
                
                # Assert
                assert result.success is True
                assert result.report is not None
                
                # Check report metadata
                assert result.report.time_range == TimeRange.QUARTER
                assert result.report.total_requests == 500000
                assert result.report.unique_operations == 45
                assert result.report.average_response_time == 180
                assert result.report.error_rate == 0.02
                
                # Check top operations
                assert len(result.report.top_operations) >= 3
                assert result.report.top_operations[0]["name"] == "get_patient"
                assert result.report.top_operations[0]["percentage"] == 30
                
                # Check healthcare compliance
                assert "phi_access_count" in result.report.healthcare_compliance
                assert result.report.healthcare_compliance["encryption_compliance"] == 100
                assert result.report.healthcare_compliance["audit_log_coverage"] == 98.5
                
                # Check workflow efficiency
                assert "incomplete_workflows" in result.report.workflow_efficiency
                workflows = result.report.workflow_efficiency["incomplete_workflows"]
                assert len(workflows) > 0
                assert workflows[0]["workflow"] == "patient_registration"
                
                # Check quick stats
                assert "total_requests" in result.quick_stats
                assert "avg_response_time" in result.quick_stats
                assert "error_rate" in result.quick_stats
                
                # Check export formats
                assert "pdf" in result.export_formats
                assert "csv" in result.export_formats
                assert "json" in result.export_formats
                
                # Check critical findings
                if result.critical_findings:
                    assert isinstance(result.critical_findings, list)
                    assert all(isinstance(f, str) for f in result.critical_findings)
    
    def test_api_usage_analytics_handles_empty_data(self, tool, sample_config):
        """Test that the tool handles cases with no usage data."""
        # Arrange
        with patch.object(tool.config_loader, 'load_api_usage_analytics', return_value=sample_config):
            input_data = ApiUsageAnalyticsInput(time_range=TimeRange.HOUR)
            
            with patch.object(tool, '_fetch_usage_data', return_value={}):
                # Act
                result = tool.execute(input_data)
                
                # Assert
                assert result.success is True
                assert result.report is not None
                assert result.report.total_requests == 0
                assert len(result.report.usage_patterns) == 0
                assert len(result.report.optimization_suggestions) == 0
                assert any("No usage data available" in step for step in result.next_steps)
    
    def test_api_usage_analytics_filters_by_operations(self, tool, sample_config):
        """Test that the tool can filter analysis by specific operations."""
        # Arrange
        with patch.object(tool.config_loader, 'load_api_usage_analytics', return_value=sample_config):
            input_data = ApiUsageAnalyticsInput(
                time_range=TimeRange.DAY,
                operations=["get_patient", "create_appointment"]
            )
            
            mock_filtered_data = {
                "operations": [
                    {"name": "get_patient", "count": 100},
                    {"name": "create_appointment", "count": 50}
                ]
            }
            
            with patch.object(tool, '_fetch_usage_data', return_value=mock_filtered_data):
                # Act
                result = tool.execute(input_data)
                
                # Assert
                assert result.success is True
                assert result.report is not None
                # Only the specified operations should be in the report
                operation_names = [op["name"] for op in result.report.top_operations]
                assert all(op in ["get_patient", "create_appointment"] for op in operation_names)
    
    def test_api_usage_analytics_healthcare_specific(self, tool, sample_config):
        """Test healthcare-specific analysis features."""
        # Arrange
        with patch.object(tool.config_loader, 'load_api_usage_analytics', return_value=sample_config):
            input_data = ApiUsageAnalyticsInput(
                time_range=TimeRange.MONTH,
                include_healthcare_analysis=True
            )
            
            # Act
            result = tool.execute(input_data)
            
            # Assert
            assert result.success is True
            assert result.report is not None
            
            # Verify healthcare analysis was performed
            assert result.report.phi_access_patterns is not None
            assert "high_risk_access" in result.report.phi_access_patterns
            assert "access_frequency" in result.report.phi_access_patterns
            
            # Check healthcare compliance data
            assert result.report.healthcare_compliance is not None
            assert isinstance(result.report.healthcare_compliance, dict)
            
            # Check workflow efficiency 
            assert result.report.workflow_efficiency is not None
            assert isinstance(result.report.workflow_efficiency, dict)
            # The actual implementation returns workflow data
            assert "incomplete_workflows" in result.report.workflow_efficiency
            
            # Check for PHI-related insights
            phi_insight = next((i for i in result.report.performance_insights 
                              if i.category == "security"), None)
            assert phi_insight is not None
            assert phi_insight.title == "PHI access patterns detected"
    
    def test_api_usage_analytics_error_handling(self, tool, sample_config):
        """Test error handling in the analytics tool."""
        # Arrange
        with patch.object(tool.config_loader, 'load_api_usage_analytics', return_value=sample_config):
            input_data = ApiUsageAnalyticsInput(time_range=TimeRange.YEAR)
            
            with patch.object(tool, '_fetch_usage_data', 
                            side_effect=Exception("API connection failed")):
                # Act
                result = tool.execute(input_data)
                
                # Assert
                assert result.success is False
                assert result.error == "Failed to generate analytics report: API connection failed"
                assert result.report is None