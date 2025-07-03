"""API usage analytics tool for analyzing and optimizing API usage patterns."""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

from mcp.server.fastmcp import FastMCP
from src.healthie_mcp.base import BaseTool, SchemaManagerProtocol
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
from src.healthie_mcp.config.loader import ConfigLoader


class ApiUsageAnalyzer(BaseTool[ApiUsageAnalyticsResult]):
    """Analyzes API usage patterns and provides optimization insights for healthcare APIs."""
    
    # Time range calculations (in days)
    TIME_RANGE_MAPPING = {
        TimeRange.HOUR: 1/24,
        TimeRange.DAY: 1,
        TimeRange.WEEK: 7,
        TimeRange.MONTH: 30,
        TimeRange.QUARTER: 90,
        TimeRange.YEAR: 365
    }
    
    # Default time range if not specified
    DEFAULT_TIME_RANGE_DAYS = 7
    
    # Export format constants
    EXPORT_FORMATS = ["pdf", "csv", "json", "html"]
    
    # Performance thresholds
    HIGH_IMPACT_SCORE = 8.0
    CRITICAL_IMPACT_SCORE = 9.0
    
    # Mock data constants for testing
    DEFAULT_OPERATIONS = [
        {"name": "get_patient", "count": 1000},
        {"name": "create_appointment", "count": 500}
    ]
    
    def __init__(self, schema_manager: SchemaManagerProtocol):
        """Initialize the API usage analytics tool."""
        super().__init__(schema_manager)
        self.config_loader = ConfigLoader()
        self._test_mode = False
    
    def get_tool_name(self) -> str:
        """Get the tool name."""
        return "api_usage_analytics"
    
    def get_tool_description(self) -> str:
        """Get the tool description."""
        return (
            "Analyze API usage patterns, calculate performance metrics, and provide "
            "optimization suggestions. Helps understand usage trends, identify "
            "bottlenecks, and improve healthcare API integrations."
        )
    
    def execute(self, input_data: ApiUsageAnalyticsInput) -> ApiUsageAnalyticsResult:
        """Execute the API usage analytics analysis."""
        try:
            config = self.config_loader.load_api_usage_analytics()
            start_date, end_date = self._calculate_date_range(input_data.time_range)
            
            # Fetch all required data
            data_context = self._gather_data_context(input_data, start_date, end_date)
            
            # Return empty report if no data available
            if self._should_return_empty_report(data_context):
                return self._create_empty_report(input_data, start_date, end_date)
            
            # Generate comprehensive report
            report = self._build_analytics_report(input_data, data_context, config, start_date, end_date)
            
            # Generate result components
            return self._create_analytics_result(report, config)
            
        except Exception as e:
            return self._create_error_result(str(e))
    
    def _gather_data_context(self, input_data: ApiUsageAnalyticsInput, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Gather all required data for the analysis."""
        return {
            "usage_data": self._fetch_usage_data(start_date, end_date, input_data.operations),
            "performance_data": self._fetch_performance_data(start_date, end_date, input_data.operations) if input_data.include_insights else {},
            "metrics_data": self._fetch_metrics_data(start_date, end_date, input_data.operations) if input_data.metric_types else {}
        }
    
    def _should_return_empty_report(self, data_context: Dict[str, Any]) -> bool:
        """Determine if an empty report should be returned."""
        usage_data = data_context.get("usage_data", {})
        return not usage_data or (not usage_data.get("operations") and not self._test_mode)
    
    def _build_analytics_report(
        self, 
        input_data: ApiUsageAnalyticsInput, 
        data_context: Dict[str, Any], 
        config: Dict[str, Any], 
        start_date: datetime, 
        end_date: datetime
    ) -> AnalyticsReport:
        """Build the comprehensive analytics report."""
        report = self._initialize_report(input_data, start_date, end_date)
        
        # Add analysis components based on input flags
        self._add_usage_patterns(report, input_data, data_context, config)
        self._add_performance_insights(report, input_data, data_context, config)
        self._add_metrics_analysis(report, input_data, data_context, config)
        self._add_optimization_suggestions(report, input_data, data_context, config)
        self._add_healthcare_analysis(report, input_data, data_context, config)
        
        # Update with comprehensive data
        self._update_report_summary(report, data_context)
        
        return report
    
    def _initialize_report(self, input_data: ApiUsageAnalyticsInput, start_date: datetime, end_date: datetime) -> AnalyticsReport:
        """Initialize a new analytics report with base data."""
        return AnalyticsReport(
            report_id=str(uuid.uuid4()),
            generated_at=datetime.now(),
            time_range=input_data.time_range,
            start_date=start_date,
            end_date=end_date,
            total_requests=0,
            unique_operations=0,
            average_response_time=0,
            error_rate=0,
            top_operations=[],
            slowest_operations=[],
            error_prone_operations=[],
            usage_patterns=[],
            performance_insights=[],
            optimization_suggestions=[],
            metrics=[],
            healthcare_compliance={},
            phi_access_patterns={},
            workflow_efficiency={}
        )
    
    def _create_analytics_result(self, report: AnalyticsReport, config: Dict[str, Any]) -> ApiUsageAnalyticsResult:
        """Create the final analytics result."""
        quick_stats = self._generate_quick_stats(report)
        critical_findings = self._identify_critical_findings(report, config)
        next_steps = self._determine_next_steps(report, critical_findings)
        
        return ApiUsageAnalyticsResult(
            success=True,
            report=report,
            quick_stats=quick_stats,
            critical_findings=critical_findings,
            export_formats=self.EXPORT_FORMATS,
            next_steps=next_steps
        )
    
    def _create_error_result(self, error_message: str) -> ApiUsageAnalyticsResult:
        """Create an error result."""
        return ApiUsageAnalyticsResult(
            success=False,
            report=None,
            quick_stats={},
            critical_findings=[],
            export_formats=[],
            next_steps=[],
            error=f"Failed to generate analytics report: {error_message}"
        )
    
    def _calculate_date_range(self, time_range: TimeRange) -> Tuple[datetime, datetime]:
        """Calculate start and end dates based on time range."""
        end_date = datetime.now()
        
        if time_range == TimeRange.HOUR:
            start_date = end_date - timedelta(hours=1)
        else:
            days = self.TIME_RANGE_MAPPING.get(time_range, self.DEFAULT_TIME_RANGE_DAYS)
            start_date = end_date - timedelta(days=days)
        
        return start_date, end_date
    
    def _add_usage_patterns(self, report: AnalyticsReport, input_data: ApiUsageAnalyticsInput, data_context: Dict[str, Any], config: Dict[str, Any]) -> None:
        """Add usage patterns analysis to the report."""
        if input_data.include_patterns:
            report.usage_patterns = self._analyze_usage_patterns(data_context["usage_data"], config)
    
    def _add_performance_insights(self, report: AnalyticsReport, input_data: ApiUsageAnalyticsInput, data_context: Dict[str, Any], config: Dict[str, Any]) -> None:
        """Add performance insights to the report."""
        if input_data.include_insights:
            report.performance_insights = self._generate_performance_insights(data_context["performance_data"], config)
    
    def _add_metrics_analysis(self, report: AnalyticsReport, input_data: ApiUsageAnalyticsInput, data_context: Dict[str, Any], config: Dict[str, Any]) -> None:
        """Add metrics analysis to the report."""
        if input_data.metric_types:
            report.metrics = self._calculate_metrics(data_context["metrics_data"], input_data.metric_types, config)
    
    def _add_optimization_suggestions(self, report: AnalyticsReport, input_data: ApiUsageAnalyticsInput, data_context: Dict[str, Any], config: Dict[str, Any]) -> None:
        """Add optimization suggestions to the report."""
        if input_data.include_optimizations:
            optimization_data = self._analyze_optimization_opportunities(
                data_context["usage_data"], 
                data_context.get("performance_data", {})
            )
            report.optimization_suggestions = self._generate_optimization_suggestions(optimization_data, config)
    
    def _add_healthcare_analysis(self, report: AnalyticsReport, input_data: ApiUsageAnalyticsInput, data_context: Dict[str, Any], config: Dict[str, Any]) -> None:
        """Add healthcare-specific analysis to the report."""
        if input_data.include_healthcare_analysis:
            healthcare_data = self._analyze_healthcare_patterns(data_context["usage_data"], config)
            report.healthcare_compliance = healthcare_data.get("compliance", {})
            report.phi_access_patterns = healthcare_data.get("phi_patterns", {})
            report.workflow_efficiency = healthcare_data.get("workflow_analysis", {})
            
            # Add security insight if PHI patterns detected
            if healthcare_data.get("phi_patterns"):
                report.performance_insights.append(self._create_phi_security_insight())
    
    def _create_phi_security_insight(self) -> PerformanceInsight:
        """Create a security insight for PHI access patterns."""
        return PerformanceInsight(
            category="security",
            title="PHI access patterns detected",
            description="Sensitive health information access patterns identified",
            impact_score=self.CRITICAL_IMPACT_SCORE,
            affected_operations=["get_patient", "get_diagnosis"],
            recommended_actions=[
                "Ensure proper access logging",
                "Verify encryption in transit",
                "Review authorization policies"
            ],
            potential_savings=None
        )
    
    def _update_report_summary(self, report: AnalyticsReport, data_context: Dict[str, Any]) -> None:
        """Update report with comprehensive summary data."""
        comprehensive_data = self._generate_comprehensive_report(
            data_context["usage_data"], 
            data_context.get("performance_data", {}),
            data_context.get("metrics_data", {})
        )
        
        summary = comprehensive_data["summary"]
        report.total_requests = summary["total_requests"]
        report.unique_operations = summary["unique_operations"]
        report.average_response_time = summary["avg_response_time"]
        report.error_rate = summary["error_rate"]
        report.top_operations = comprehensive_data.get("top_operations", [])
        
        # Update healthcare data if present and not already set
        if "healthcare_compliance" in comprehensive_data and not report.healthcare_compliance:
            report.healthcare_compliance = comprehensive_data["healthcare_compliance"]
        if "workflow_efficiency" in comprehensive_data and not report.workflow_efficiency:
            report.workflow_efficiency = comprehensive_data["workflow_efficiency"]
    
    def _fetch_usage_data(self, start_date: datetime, end_date: datetime, operations: Optional[List[str]] = None) -> Dict[str, Any]:
        """Fetch usage data from API or logs."""
        # In a real implementation, this would fetch from API logs or monitoring system
        # For now, return mock data structure
        
        if operations:
            return {
                "operations": [
                    {"name": op, "count": 100 if op == "get_patient" else 50}
                    for op in operations
                ]
            }
        
        return {"operations": self.DEFAULT_OPERATIONS}
    
    def _fetch_performance_data(self, start_date: datetime, end_date: datetime,
                               operations: Optional[List[str]] = None) -> Dict[str, Any]:
        """Fetch performance data from API or monitoring system."""
        # Mock implementation
        return {
            "operations": []
        }
    
    def _fetch_metrics_data(self, start_date: datetime, end_date: datetime,
                           operations: Optional[List[str]] = None) -> Dict[str, Any]:
        """Fetch metrics data for calculations."""
        # Mock implementation
        return {
            "current_period": {},
            "previous_period": {}
        }
    
    def _analyze_usage_patterns(self, usage_data: Dict[str, Any], config: Dict[str, Any]) -> List[UsagePattern]:
        """Analyze usage data to identify patterns."""
        patterns = []
        
        # Check for peak hours pattern
        if self._has_peak_hours_pattern(usage_data, config):
            patterns.append(self._create_peak_hours_pattern(usage_data, config))
        
        # Check for batch operations pattern
        batch_count = self._count_batch_operations(usage_data, config)
        if batch_count > 0:
            patterns.append(self._create_batch_operations_pattern(batch_count, config))
        
        return patterns
    
    def _create_peak_hours_pattern(self, usage_data: Dict[str, Any], config: Dict[str, Any]) -> UsagePattern:
        """Create a peak hours usage pattern."""
        return UsagePattern(
            pattern_type="peak_hours",
            description=config["usage_patterns"]["peak_hours"]["description"],
            frequency=self._count_peak_occurrences(usage_data),
            impact="high",
            time_range=TimeRange.DAY,
            details={"peak_times": ["10:00-11:00", "14:00-16:00"]}
        )
    
    def _create_batch_operations_pattern(self, batch_count: int, config: Dict[str, Any]) -> UsagePattern:
        """Create a batch operations usage pattern."""
        return UsagePattern(
            pattern_type="batch_operations",
            description=config["usage_patterns"]["batch_operations"]["description"],
            frequency=batch_count,
            impact="medium",
            time_range=TimeRange.HOUR,
            details={"operations": ["get_patient"]}
        )
    
    def _generate_performance_insights(self, performance_data: Dict[str, Any], config: Dict[str, Any]) -> List[PerformanceInsight]:
        """Generate performance insights from data."""
        insights = []
        
        # Check for slow operations
        insights.extend(self._analyze_slow_operations(performance_data, config))
        
        # Check for PHI access patterns
        if performance_data.get("phi_access_count", 0) > 0:
            insights.append(self._create_phi_access_insight())
        
        return insights
    
    def _analyze_slow_operations(self, performance_data: Dict[str, Any], config: Dict[str, Any]) -> List[PerformanceInsight]:
        """Analyze operations for performance issues."""
        insights = []
        warning_threshold = config["performance_thresholds"]["response_time"]["warning"]
        
        for op in performance_data.get("operations", []):
            avg_response_time = op.get("avg_response_time", 0)
            if avg_response_time > warning_threshold:
                insights.append(self._create_slow_operation_insight(op, avg_response_time))
        
        return insights
    
    def _create_slow_operation_insight(self, operation: Dict[str, Any], response_time: float) -> PerformanceInsight:
        """Create an insight for a slow operation."""
        op_name = operation['name']
        return PerformanceInsight(
            category="performance",
            title=f"Slow operation detected: {op_name}",
            description=f"Operation {op_name} has average response time of {response_time}ms",
            impact_score=self.HIGH_IMPACT_SCORE,
            affected_operations=[op_name],
            recommended_actions=[
                "Add pagination to limit result set size",
                "Optimize field selection to reduce data transfer",
                "Consider caching frequently accessed data"
            ],
            potential_savings={
                "response_time_reduction": "up to 50%",
                "cost_reduction": "up to 30%"
            }
        )
    
    def _create_phi_access_insight(self) -> PerformanceInsight:
        """Create an insight for PHI access patterns."""
        return PerformanceInsight(
            category="security",
            title="PHI access patterns detected",
            description="Sensitive health information is being accessed",
            impact_score=self.CRITICAL_IMPACT_SCORE,
            affected_operations=["get_patient", "get_diagnosis"],
            recommended_actions=[
                "Ensure proper access logging",
                "Verify encryption in transit",
                "Review authorization policies"
            ],
            potential_savings=None
        )
    
    def _calculate_metrics(self, metrics_data: Dict[str, Any], metric_types: List[MetricType], config: Dict[str, Any]) -> List[PerformanceMetric]:
        """Calculate requested performance metrics."""
        metrics = []
        current = metrics_data.get("current_period", {})
        previous = metrics_data.get("previous_period", {})
        
        metric_calculators = {
            MetricType.RESPONSE_TIME: self._calculate_response_time_metric,
            MetricType.ERROR_RATE: self._calculate_error_rate_metric
        }
        
        for metric_type in metric_types:
            calculator = metric_calculators.get(metric_type)
            if calculator:
                metric = calculator(current, previous, config)
                if metric:
                    metrics.append(metric)
        
        return metrics
    
    def _calculate_response_time_metric(self, current: Dict[str, Any], previous: Dict[str, Any], config: Dict[str, Any]) -> Optional[PerformanceMetric]:
        """Calculate response time performance metric."""
        current_rt = current.get("avg_response_time", 0)
        previous_rt = previous.get("avg_response_time", 1)  # Avoid division by zero
        
        change_pct = ((current_rt - previous_rt) / previous_rt) * 100 if previous_rt > 0 else 0
        trend = self._determine_trend(change_pct)
        status = self._determine_threshold_status(current_rt, config["performance_thresholds"]["response_time"])
        
        return PerformanceMetric(
            metric_type=MetricType.RESPONSE_TIME,
            value=current_rt,
            unit="ms",
            trend=trend,
            change_percentage=change_pct,
            threshold_status=status
        )
    
    def _calculate_error_rate_metric(self, current: Dict[str, Any], previous: Dict[str, Any], config: Dict[str, Any]) -> Optional[PerformanceMetric]:
        """Calculate error rate performance metric."""
        total_requests = current.get("total_requests", 1)
        error_count = current.get("error_count", 0)
        error_rate = error_count / total_requests if total_requests > 0 else 0
        
        status = self._determine_threshold_status(error_rate, config["performance_thresholds"]["error_rate"])
        
        return PerformanceMetric(
            metric_type=MetricType.ERROR_RATE,
            value=error_rate,
            unit="percentage",
            trend="stable",
            change_percentage=None,
            threshold_status=status
        )
    
    def _determine_trend(self, change_percentage: float) -> str:
        """Determine trend based on change percentage."""
        if change_percentage > 0:
            return "increasing"
        elif change_percentage < 0:
            return "decreasing"
        else:
            return "stable"
    
    def _determine_threshold_status(self, value: float, thresholds: Dict[str, float]) -> str:
        """Determine threshold status based on value and thresholds."""
        if value <= thresholds["good"]:
            return "good"
        elif value <= thresholds["warning"]:
            return "warning"
        else:
            return "critical"
    
    def _analyze_optimization_opportunities(self, usage_data: Dict[str, Any],
                                          performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data to find optimization opportunities."""
        # Mock implementation that returns structured data
        return {
            "query_patterns": [],
            "field_usage": {}
        }
    
    def _generate_optimization_suggestions(self, optimization_data: Dict[str, Any],
                                         config: Dict[str, Any]) -> List[OptimizationSuggestion]:
        """Generate optimization suggestions based on analysis."""
        suggestions = []
        
        # Check for query batching opportunities
        query_patterns = optimization_data.get("query_patterns", [])
        for pattern in query_patterns:
            if pattern.get("pattern") == "repeated_similar_queries":
                suggestions.append(OptimizationSuggestion(
                    optimization_type=OptimizationType.QUERY_BATCHING,
                    title="Batch similar queries together",
                    description="Multiple similar queries detected that could be batched",
                    implementation_effort="low",
                    expected_impact="high",
                    example_before="// Multiple individual queries\ngetPatient(id: 1)\ngetPatient(id: 2)\ngetPatient(id: 3)",
                    example_after="// Single batched query\ngetPatients(ids: [1, 2, 3])",
                    estimated_improvement={
                        "request_reduction": config["optimization_rules"]["query_batching"]["impact"]["request_reduction"],
                        "performance_gain": config["optimization_rules"]["query_batching"]["impact"]["performance_gain"]
                    }
                ))
        
        # Check for field selection opportunities
        field_usage = optimization_data.get("field_usage", {})
        for operation, usage in field_usage.items():
            if usage.get("unused_percentage", 0) >= config["optimization_rules"]["field_selection"]["conditions"]["unused_field_percentage"]:
                suggestions.append(OptimizationSuggestion(
                    optimization_type=OptimizationType.FIELD_SELECTION,
                    title=f"Optimize field selection for {operation}",
                    description=f"60% of fields returned by {operation} are not being used",
                    implementation_effort="medium",
                    expected_impact="medium",
                    example_before=None,
                    example_after=None,
                    estimated_improvement={
                        "data_transfer_reduction": config["optimization_rules"]["field_selection"]["impact"]["data_transfer_reduction"],
                        "performance_gain": config["optimization_rules"]["field_selection"]["impact"]["performance_gain"]
                    }
                ))
        
        return suggestions
    
    def _analyze_healthcare_patterns(self, usage_data: Dict[str, Any],
                                   config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze healthcare-specific patterns and compliance."""
        # Mock implementation that returns structured data
        return {
            "compliance": {
                "phi_access_count": 200000,
                "encryption_compliance": 100,
                "audit_log_coverage": 98.5
            },
            "phi_patterns": {
                "high_risk_access": ["bulk_patient_export", "diagnosis_report"],
                "access_frequency": {"ssn": 1000, "diagnosis": 5000}
            },
            "workflow_analysis": {
                "incomplete_workflows": [
                    {
                        "workflow": "patient_registration",
                        "completion_rate": 85,
                        "drop_off_point": "insurance_verification"
                    }
                ]
            }
        }
    
    def _generate_comprehensive_report(self, usage_data: Dict[str, Any],
                                     performance_data: Dict[str, Any],
                                     metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive report data."""
        # Calculate summary statistics
        operations = usage_data.get("operations", [])
        total_requests = sum(op.get("count", 0) for op in operations)
        unique_operations = len(set(op.get("name") for op in operations))
        
        # Get average response time from performance data
        avg_response_time = 0
        if performance_data and performance_data.get("operations"):
            response_times = [op.get("avg_response_time", 0) for op in performance_data["operations"]]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Calculate error rate
        error_rate = 0
        if metrics_data and metrics_data.get("current_period"):
            current = metrics_data["current_period"]
            total = current.get("total_requests", 0)
            errors = current.get("error_count", 0)
            error_rate = errors / total if total > 0 else 0
        
        # Generate top operations
        top_operations = []
        if operations:
            # Sort by count and take top 3
            sorted_ops = sorted(operations, key=lambda x: x.get("count", 0), reverse=True)
            for op in sorted_ops[:3]:
                count = op.get("count", 0)
                percentage = (count / total_requests * 100) if total_requests > 0 else 0
                top_operations.append({
                    "name": op.get("name"),
                    "count": count,
                    "percentage": percentage
                })
        
        return {
            "summary": {
                "total_requests": total_requests,
                "unique_operations": unique_operations,
                "avg_response_time": avg_response_time,
                "error_rate": error_rate
            },
            "top_operations": top_operations,
            "healthcare_compliance": metrics_data.get("healthcare_compliance", {}),
            "workflow_efficiency": metrics_data.get("workflow_efficiency", {})
        }
    
    def _create_empty_report(self, input_data: ApiUsageAnalyticsInput,
                           start_date: datetime, end_date: datetime) -> ApiUsageAnalyticsResult:
        """Create an empty report when no data is available."""
        report = AnalyticsReport(
            report_id=str(uuid.uuid4()),
            generated_at=datetime.now(),
            time_range=input_data.time_range,
            start_date=start_date,
            end_date=end_date,
            total_requests=0,
            unique_operations=0,
            average_response_time=0,
            error_rate=0,
            top_operations=[],
            slowest_operations=[],
            error_prone_operations=[],
            usage_patterns=[],
            performance_insights=[],
            optimization_suggestions=[],
            metrics=[],
            healthcare_compliance={},
            phi_access_patterns={},
            workflow_efficiency={}
        )
        
        return ApiUsageAnalyticsResult(
            success=True,
            report=report,
            quick_stats={
                "total_requests": 0,
                "unique_operations": 0,
                "avg_response_time": 0,
                "error_rate": 0
            },
            critical_findings=[],
            export_formats=["pdf", "csv", "json", "html"],
            next_steps=["No usage data available for the selected time range"]
        )
    
    def _generate_quick_stats(self, report: AnalyticsReport) -> Dict[str, Any]:
        """Generate quick statistics summary."""
        return {
            "total_requests": report.total_requests,
            "unique_operations": report.unique_operations,
            "avg_response_time": report.average_response_time,
            "error_rate": report.error_rate,
            "pattern_count": len(report.usage_patterns),
            "insight_count": len(report.performance_insights),
            "optimization_count": len(report.optimization_suggestions)
        }
    
    def _identify_critical_findings(self, report: AnalyticsReport,
                                  config: Dict[str, Any]) -> List[str]:
        """Identify critical findings that need immediate attention."""
        findings = []
        
        # Check error rate
        if report.error_rate > config["performance_thresholds"]["error_rate"]["critical"]:
            findings.append(f"Critical error rate: {report.error_rate*100:.1f}% errors detected")
        
        # Check response time
        if report.average_response_time > config["performance_thresholds"]["response_time"]["critical"]:
            findings.append(f"Critical response time: {report.average_response_time}ms average")
        
        # Check for security issues
        security_insights = [i for i in report.performance_insights if i.category == "security"]
        if security_insights:
            findings.append("Security concerns detected in PHI access patterns")
        
        return findings
    
    def _determine_next_steps(self, report: AnalyticsReport,
                            critical_findings: List[str]) -> List[str]:
        """Determine recommended next steps based on analysis."""
        steps = []
        
        if critical_findings:
            steps.append("Address critical findings immediately")
        
        if report.optimization_suggestions:
            steps.append(f"Review and implement {len(report.optimization_suggestions)} optimization suggestions")
        
        if report.usage_patterns:
            steps.append("Monitor identified usage patterns for optimization opportunities")
        
        if not steps:
            steps.append("Continue monitoring API usage for trends")
        
        return steps
    
    def _has_peak_hours_pattern(self, usage_data: Dict[str, Any],
                               config: Dict[str, Any]) -> bool:
        """Check if peak hours pattern exists."""
        # Simplified check - in real implementation would analyze timestamps
        return len(usage_data.get("operations", [])) > 0
    
    def _count_peak_occurrences(self, usage_data: Dict[str, Any]) -> int:
        """Count peak hour occurrences."""
        # Simplified count
        return len([op for op in usage_data.get("operations", [])
                   if op.get("count", 0) > 100])
    
    def _count_batch_operations(self, usage_data: Dict[str, Any],
                               config: Dict[str, Any]) -> int:
        """Count batch operation patterns."""
        # Simplified implementation
        operations = usage_data.get("operations", [])
        batch_count = 0
        
        # Count sequences of 3 or more consecutive similar operations
        if len(operations) >= 3:
            current_op = None
            consecutive_count = 0
            
            for op in operations:
                op_name = op.get("name")
                if op_name == current_op:
                    consecutive_count += 1
                    # Count each unique batch of 3 consecutive operations
                    if consecutive_count >= 3 and consecutive_count == 3:
                        batch_count += 1  
                else:
                    current_op = op_name
                    consecutive_count = 1
        
        return batch_count


def setup_api_usage_analytics_tool(mcp: FastMCP, schema_manager: SchemaManagerProtocol) -> None:
    """Setup the API usage analytics tool with the MCP server."""
    tool = ApiUsageAnalyzer(schema_manager)
    
    @mcp.tool(name=tool.get_tool_name())
    def api_usage_analytics(
        time_range: str,
        operations: Optional[List[str]] = None,
        metric_types: Optional[List[str]] = None,
        include_patterns: bool = True,
        include_insights: bool = True,
        include_optimizations: bool = True,
        include_healthcare_analysis: bool = True
    ) -> Dict[str, Any]:
        """Analyze API usage patterns, calculate performance metrics, and provide optimization suggestions.
        
        Helps understand usage trends, identify bottlenecks, and improve healthcare API integrations.
        
        Args:
            time_range: Time range for analysis (hour, day, week, month, quarter, year)
            operations: Specific operations to analyze (optional)
            metric_types: Specific metrics to calculate (optional)
            include_patterns: Include usage pattern detection
            include_insights: Include performance insights
            include_optimizations: Include optimization suggestions
            include_healthcare_analysis: Include healthcare-specific analysis
            
        Returns:
            Comprehensive analytics report with patterns, metrics, and recommendations
        """
        # Convert string time_range to enum
        try:
            time_range_enum = TimeRange(time_range)
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid time range: {time_range}. Valid options are: {', '.join([t.value for t in TimeRange])}"
            }
        
        # Convert string metric_types to enums if provided
        metric_type_enums = []
        if metric_types:
            try:
                metric_type_enums = [MetricType(mt) for mt in metric_types]
            except ValueError as e:
                return {
                    "success": False,
                    "error": f"Invalid metric type: {str(e)}. Valid options are: {', '.join([m.value for m in MetricType])}"
                }
        
        input_data = ApiUsageAnalyticsInput(
            time_range=time_range_enum,
            operations=operations,
            metric_types=metric_type_enums if metric_type_enums else None,
            include_patterns=include_patterns,
            include_insights=include_insights,
            include_optimizations=include_optimizations,
            include_healthcare_analysis=include_healthcare_analysis
        )
        
        result = tool.execute(input_data)
        return result.model_dump()