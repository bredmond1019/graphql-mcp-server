"""Query performance analyzer tool for external developers.

This tool analyzes GraphQL queries for potential performance issues and optimization
opportunities, helping developers prevent slow queries in healthcare applications.
"""

import re
from typing import List, Dict, Any, Set, Optional
from enum import Enum
from pydantic import BaseModel, Field

from ..models.external_dev_tools import (
    QueryPerformanceResult, PerformanceIssue
)
from ..base import BaseTool, SchemaManagerProtocol
from ..config.loader import get_config_loader
from ..exceptions import ToolError


class PerformanceConstants:
    """Constants for query performance analysis tool."""
    
    # Performance issue types
    ISSUE_N_PLUS_ONE = "n_plus_one"
    ISSUE_DEEP_NESTING = "deep_nesting"
    ISSUE_EXPENSIVE_FIELD = "expensive_field"
    ISSUE_LARGE_RESULT_SET = "large_result_set"
    ISSUE_MISSING_PAGINATION = "missing_pagination"
    
    # Severity levels
    SEVERITY_HIGH = "high"
    SEVERITY_MEDIUM = "medium"
    SEVERITY_LOW = "low"
    
    # Performance thresholds
    MAX_NESTING_DEPTH_HIGH = 10
    MAX_NESTING_DEPTH_MEDIUM = 6
    
    # Query patterns
    OPERATION_PATTERN = r'^\s*(query|mutation|subscription)\s*(\w+)?\s*'
    FIELD_PATTERN = r'\b(\w+)\s*(?:\([^)]*\))?\s*\{'
    
    # Expensive field patterns
    EXPENSIVE_PATTERNS = [
        'search', 'history', 'records', 'documents', 'attachments',
        'logs', 'audit', 'analytics', 'reports', 'aggregations'
    ]
    
    # Collection fields that typically return lists
    COLLECTION_FIELDS = ['clients', 'appointments', 'providers', 'notes', 'forms', 'payments']
    
    # Connection field indicators
    CONNECTION_PATTERNS = ['Connection', 'connections', 'edges', 'nodes']
    
    # List field patterns for schema detection
    LIST_FIELD_PATTERNS = [
        r'{field_name}: \[',
        r'{field_name}\s*:\s*\['
    ]
    
    # Performance score penalties
    PENALTY_MAP = {
        SEVERITY_HIGH: 25,
        SEVERITY_MEDIUM: 15,
        SEVERITY_LOW: 5
    }
    
    # Complexity calculation weights
    COMPLEXITY_FIELD_WEIGHT = 2
    COMPLEXITY_NESTING_WEIGHT = 5
    COMPLEXITY_ARGUMENT_WEIGHT = 1
    COMPLEXITY_MAX_SCORE = 100
    
    # Execution time categories
    EXECUTION_TIME_VERY_FAST = "Very fast (<100ms)"
    EXECUTION_TIME_FAST = "Fast (100ms-500ms)"
    EXECUTION_TIME_MODERATE = "Moderate (500ms-2s)"
    EXECUTION_TIME_SLOW = "Potentially slow (>2s)"
    
    # Optimization suggestions
    OPTIMIZATION_SUGGESTIONS = [
        "Use specific field selection instead of requesting all available fields",
        "Consider caching for frequently accessed patient data",
        "Implement proper error handling for failed queries",
        "Test queries with realistic data volumes before production use"
    ]


class PerformanceAnalysisInput(BaseModel):
    """Input parameters for query performance analysis."""
    
    query: str = Field(
        description="The GraphQL query to analyze for performance issues"
    )
    
    include_suggestions: bool = Field(
        True,
        description="Whether to include optimization suggestions in the result"
    )


class QueryPerformanceTool(BaseTool[QueryPerformanceResult]):
    """Tool for analyzing GraphQL query performance and optimization opportunities."""
    
    def __init__(self, schema_manager: SchemaManagerProtocol):
        """Initialize the tool.
        
        Args:
            schema_manager: Schema manager instance for accessing GraphQL schema
        """
        super().__init__(schema_manager)
        self.config_loader = get_config_loader()
    
    def get_tool_name(self) -> str:
        """Get the tool name."""
        return "analyze_query_performance"
    
    def get_tool_description(self) -> str:
        """Get the tool description."""
        return "Analyze GraphQL query for potential performance issues and optimization opportunities"
    
    def execute(
        self,
        query: str,
        include_suggestions: bool = True
    ) -> QueryPerformanceResult:
        """Analyze GraphQL query for potential performance issues.
        
        Args:
            query: The GraphQL query to analyze
            include_suggestions: Whether to include optimization suggestions
                     
        Returns:
            QueryPerformanceResult with performance analysis and optimization suggestions
        """
        try:
            # Validate inputs
            if not query or not query.strip():
                raise ToolError("Query is required and cannot be empty")
            
            # Schema content is helpful but not strictly required for basic analysis
            schema_content = None
            try:
                schema_content = self.schema_manager.get_schema_content()
            except Exception:
                # Continue without schema - analysis will be based on patterns only
                pass
            
            # Analyze query for performance issues
            issues = self._analyze_performance_issues(query, schema_content)
            
            # Calculate overall performance score
            overall_score = self._calculate_performance_score(issues)
            complexity_score = self._calculate_complexity_score(query)
            
            # Generate optimization suggestions
            suggestions = []
            if include_suggestions:
                suggestions = self._generate_optimization_suggestions(query, issues)
            
            # Estimate execution time category
            estimated_time = self._estimate_execution_time(complexity_score, issues)
            
            return QueryPerformanceResult(
                overall_score=overall_score,
                complexity_score=complexity_score,
                issues=issues,
                total_issues=len(issues),
                suggestions=suggestions,
                estimated_execution_time=estimated_time
            )
            
        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Error analyzing query performance: {str(e)}")

    def _analyze_performance_issues(self, query: str, schema_content: Optional[str]) -> List[PerformanceIssue]:
        """Analyze query for various performance issues."""
        issues = []
        
        # Analyze query structure
        query_structure = self._parse_query_structure(query)
        
        # Check for N+1 query problems
        n_plus_one_issues = self._detect_n_plus_one_patterns(query_structure, schema_content)
        issues.extend(n_plus_one_issues)
        
        # Check for deep nesting
        deep_nesting_issues = self._detect_deep_nesting(query_structure)
        issues.extend(deep_nesting_issues)
        
        # Check for potentially expensive fields
        expensive_field_issues = self._detect_expensive_fields(query_structure)
        issues.extend(expensive_field_issues)
        
        # Check for large result sets
        large_result_issues = self._detect_large_result_sets(query_structure)
        issues.extend(large_result_issues)
        
        # Check for missing pagination
        pagination_issues = self._detect_missing_pagination(query_structure)
        issues.extend(pagination_issues)
        
        return issues

    def _parse_query_structure(self, query: str) -> Dict[str, Any]:
        """Parse GraphQL query into a structured format for analysis."""
        # Remove comments and normalize whitespace
        cleaned_query = re.sub(r'#.*$', '', query, flags=re.MULTILINE)
        cleaned_query = ' '.join(cleaned_query.split())
        
        # Extract operation type and name
        operation_match = re.match(PerformanceConstants.OPERATION_PATTERN, cleaned_query)
        operation_type = operation_match.group(1) if operation_match else 'query'
        operation_name = operation_match.group(2) if operation_match else None
        
        # Extract field selections
        fields = self._extract_field_selections(cleaned_query)
        
        # Calculate nesting depth
        max_depth = self._calculate_max_nesting_depth(cleaned_query)
        
        return {
            'operation_type': operation_type,
            'operation_name': operation_name,
            'fields': fields,
            'max_depth': max_depth,
            'raw_query': query
        }

    def _extract_field_selections(self, query: str) -> List[Dict[str, Any]]:
        """Extract field selections from the query."""
        fields = []
        
        # Simple field extraction - matches field names
        matches = re.finditer(PerformanceConstants.FIELD_PATTERN, query)
        
        for match in matches:
            field_name = match.group(1)
            if field_name not in ['query', 'mutation', 'subscription']:
                fields.append({
                    'name': field_name,
                    'position': match.start(),
                    'has_arguments': '(' in match.group(0),
                    'is_connection': self._is_connection_field(field_name)
                })
        
        return fields

    def _calculate_max_nesting_depth(self, query: str) -> int:
        """Calculate the maximum nesting depth of the query."""
        max_depth = 0
        current_depth = 0
        
        for char in query:
            if char == '{':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == '}':
                current_depth -= 1
        
        return max_depth

    def _detect_n_plus_one_patterns(self, query_structure: Dict[str, Any], schema_content: Optional[str]) -> List[PerformanceIssue]:
        """Detect potential N+1 query patterns."""
        issues = []
        
        # Look for patterns where we query lists and then individual fields
        for field in query_structure['fields']:
            if field['is_connection'] or self._is_list_field_in_schema(field['name'], schema_content):
                # Check if we're selecting nested object fields
                if self._has_nested_object_selections(field['name'], query_structure['raw_query']):
                    issues.append(PerformanceIssue(
                        issue_type=PerformanceConstants.ISSUE_N_PLUS_ONE,
                        severity=PerformanceConstants.SEVERITY_HIGH,
                        description=f"Potential N+1 query on field '{field['name']}'",
                        location=f"Field: {field['name']}",
                        suggestion="Consider using DataLoader or request specific fields only when needed",
                        estimated_impact="Could cause 1 + N database queries where N is the number of items"
                    ))
        
        return issues

    def _detect_deep_nesting(self, query_structure: Dict[str, Any]) -> List[PerformanceIssue]:
        """Detect queries with excessive nesting depth."""
        issues = []
        max_depth = query_structure['max_depth']
        
        if max_depth > PerformanceConstants.MAX_NESTING_DEPTH_HIGH:
            issues.append(PerformanceIssue(
                issue_type=PerformanceConstants.ISSUE_DEEP_NESTING,
                severity=PerformanceConstants.SEVERITY_HIGH,
                description=f"Query nesting depth is {max_depth} levels deep",
                location="Query structure",
                suggestion="Break complex queries into multiple simpler queries",
                estimated_impact="Deep nesting can cause exponential performance degradation"
            ))
        elif max_depth > PerformanceConstants.MAX_NESTING_DEPTH_MEDIUM:
            issues.append(PerformanceIssue(
                issue_type=PerformanceConstants.ISSUE_DEEP_NESTING,
                severity=PerformanceConstants.SEVERITY_MEDIUM,
                description=f"Query nesting depth is {max_depth} levels deep",
                location="Query structure",
                suggestion="Consider reducing nesting depth for better performance",
                estimated_impact="May cause slower query execution"
            ))
        
        return issues

    def _detect_expensive_fields(self, query_structure: Dict[str, Any]) -> List[PerformanceIssue]:
        """Detect potentially expensive fields in the query."""
        issues = []
        
        for field in query_structure['fields']:
            field_name_lower = field['name'].lower()
            for pattern in PerformanceConstants.EXPENSIVE_PATTERNS:
                if pattern in field_name_lower:
                    issues.append(PerformanceIssue(
                        issue_type=PerformanceConstants.ISSUE_EXPENSIVE_FIELD,
                        severity=PerformanceConstants.SEVERITY_MEDIUM,
                        description=f"Field '{field['name']}' may be computationally expensive",
                        location=f"Field: {field['name']}",
                        suggestion="Consider adding filters to expensive fields to reduce computation",
                        estimated_impact="May cause slower response times"
                    ))
                    break
        
        return issues

    def _detect_large_result_sets(self, query_structure: Dict[str, Any]) -> List[PerformanceIssue]:
        """Detect queries that might return large result sets."""
        issues = []
        
        # Check for queries on collections without apparent limits
        query_text = query_structure['raw_query'].lower()
        
        for collection in PerformanceConstants.COLLECTION_FIELDS:
            if collection in query_text:
                # Check if there's a 'first' or 'limit' parameter
                if not re.search(rf'{collection}\s*\([^)]*(?:first|limit)', query_text):
                    issues.append(PerformanceIssue(
                        issue_type=PerformanceConstants.ISSUE_LARGE_RESULT_SET,
                        severity=PerformanceConstants.SEVERITY_MEDIUM,
                        description=f"Query on '{collection}' without apparent limit",
                        location=f"Collection: {collection}",
                        suggestion=f"Add pagination parameters like 'first: 20' to limit results",
                        estimated_impact="May return large datasets causing slow responses"
                    ))
        
        return issues

    def _detect_missing_pagination(self, query_structure: Dict[str, Any]) -> List[PerformanceIssue]:
        """Detect connection fields without proper pagination."""
        issues = []
        
        for field in query_structure['fields']:
            if field['is_connection']:
                query_text = query_structure['raw_query']
                field_section = self._extract_field_section(query_text, field['name'])
                
                # Check if pagination info is requested
                if 'pageInfo' not in field_section:
                    issues.append(PerformanceIssue(
                        issue_type=PerformanceConstants.ISSUE_MISSING_PAGINATION,
                        severity=PerformanceConstants.SEVERITY_LOW,
                        description=f"Connection field '{field['name']}' missing pageInfo",
                        location=f"Field: {field['name']}",
                        suggestion="Include pageInfo { hasNextPage, endCursor } for proper pagination",
                        estimated_impact="Cannot implement proper pagination without pageInfo"
                    ))
        
        return issues

    def _calculate_performance_score(self, issues: List[PerformanceIssue]) -> int:
        """Calculate overall performance score (0-100)."""
        if not issues:
            return 100
        
        total_penalty = sum(PerformanceConstants.PENALTY_MAP.get(issue.severity, 10) for issue in issues)
        score = max(0, 100 - total_penalty)
        
        return score

    def _calculate_complexity_score(self, query: str) -> int:
        """Calculate query complexity score."""
        # Simple complexity calculation based on:
        # - Number of fields
        # - Nesting depth
        # - Number of arguments
        
        field_count = len(re.findall(PerformanceConstants.FIELD_PATTERN, query))
        nesting_depth = self._calculate_max_nesting_depth(query)
        argument_count = len(re.findall(r'\([^)]+\)', query))
        
        complexity = (
            (field_count * PerformanceConstants.COMPLEXITY_FIELD_WEIGHT) +
            (nesting_depth * PerformanceConstants.COMPLEXITY_NESTING_WEIGHT) +
            (argument_count * PerformanceConstants.COMPLEXITY_ARGUMENT_WEIGHT)
        )
        return min(complexity, PerformanceConstants.COMPLEXITY_MAX_SCORE)

    def _estimate_execution_time(self, complexity_score: int, issues: List[PerformanceIssue]) -> str:
        """Estimate query execution time category."""
        high_severity_issues = len([i for i in issues if i.severity == PerformanceConstants.SEVERITY_HIGH])
        
        if high_severity_issues > 2 or complexity_score > 80:
            return PerformanceConstants.EXECUTION_TIME_SLOW
        elif high_severity_issues > 0 or complexity_score > 50:
            return PerformanceConstants.EXECUTION_TIME_MODERATE
        elif complexity_score > 25:
            return PerformanceConstants.EXECUTION_TIME_FAST
        else:
            return PerformanceConstants.EXECUTION_TIME_VERY_FAST

    def _generate_optimization_suggestions(self, query: str, issues: List[PerformanceIssue]) -> List[str]:
        """Generate optimization suggestions based on analysis."""
        suggestions = []
        
        # Issue-based suggestions
        issue_types = {issue.issue_type for issue in issues}
        
        if PerformanceConstants.ISSUE_N_PLUS_ONE in issue_types:
            suggestions.append("Implement DataLoader pattern for related data fetching")
        
        if PerformanceConstants.ISSUE_DEEP_NESTING in issue_types:
            suggestions.append("Split complex queries into multiple simpler queries")
        
        if PerformanceConstants.ISSUE_LARGE_RESULT_SET in issue_types:
            suggestions.append("Add pagination with 'first' parameter to limit results")
        
        if PerformanceConstants.ISSUE_EXPENSIVE_FIELD in issue_types:
            suggestions.append("Add filters to expensive fields to reduce computation")
        
        # Add general optimization suggestions
        suggestions.extend(PerformanceConstants.OPTIMIZATION_SUGGESTIONS)
        
        return suggestions[:5]  # Limit to 5 suggestions

    def _is_connection_field(self, field_name: str) -> bool:
        """Check if a field is likely a GraphQL connection."""
        return any(pattern in field_name for pattern in PerformanceConstants.CONNECTION_PATTERNS)

    def _is_list_field_in_schema(self, field_name: str, schema_content: Optional[str]) -> bool:
        """Check if a field returns a list type in the schema."""
        if not schema_content:
            return False
        
        # Simple pattern matching for list fields
        list_patterns = [pattern.format(field_name=field_name) for pattern in PerformanceConstants.LIST_FIELD_PATTERNS]
        return any(re.search(pattern, schema_content) for pattern in list_patterns)

    def _has_nested_object_selections(self, field_name: str, query: str) -> bool:
        """Check if a field has nested object selections."""
        # Look for the field followed by object selections
        pattern = rf'{field_name}\s*(?:\([^)]*\))?\s*\{{[^}}]*\w+\s*\{{'
        return re.search(pattern, query) is not None

    def _extract_field_section(self, query: str, field_name: str) -> str:
        """Extract the section of query related to a specific field."""
        # Find field and extract its section
        pattern = rf'{field_name}\s*(?:\([^)]*\))?\s*\{{([^}}]+)\}}'
        match = re.search(pattern, query)
        return match.group(1) if match else ""


def setup_query_performance_tool(mcp, schema_manager) -> None:
    """Setup the query performance analyzer tool with the MCP server."""
    tool = QueryPerformanceTool(schema_manager)
    
    @mcp.tool()
    def analyze_query_performance(
        query: str,
        include_suggestions: bool = True
    ) -> QueryPerformanceResult:
        """Analyze GraphQL query for potential performance issues and optimization opportunities.
        
        This tool helps external developers identify performance bottlenecks in their
        GraphQL queries before executing them, preventing slow queries in healthcare applications.
        
        Args:
            query: The GraphQL query to analyze
            include_suggestions: Whether to include optimization suggestions
                     
        Returns:
            QueryPerformanceResult with performance analysis and optimization suggestions
        """
        return tool.execute(
            query=query,
            include_suggestions=include_suggestions
        )