"""Query performance analyzer tool for external developers."""

import re
from typing import List, Dict, Any, Set
from mcp.server.fastmcp import FastMCP
from ..models.external_dev_tools import (
    QueryPerformanceResult, PerformanceIssue
)


def setup_query_performance_tool(mcp: FastMCP, schema_manager) -> None:
    """Setup the query performance analyzer tool with the MCP server."""
    
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
        try:
            schema_content = schema_manager.get_schema_content()
            if not schema_content:
                raise ValueError("Schema not available. Please check your configuration.")
            
            # Analyze query for performance issues
            issues = _analyze_performance_issues(query, schema_content)
            
            # Calculate overall performance score
            overall_score = _calculate_performance_score(issues)
            complexity_score = _calculate_complexity_score(query)
            
            # Generate optimization suggestions
            suggestions = []
            if include_suggestions:
                suggestions = _generate_optimization_suggestions(query, issues)
            
            # Estimate execution time category
            estimated_time = _estimate_execution_time(complexity_score, issues)
            
            return QueryPerformanceResult(
                overall_score=overall_score,
                complexity_score=complexity_score,
                issues=issues,
                total_issues=len(issues),
                suggestions=suggestions,
                estimated_execution_time=estimated_time
            )
            
        except Exception as e:
            return QueryPerformanceResult(
                overall_score=0,
                complexity_score=0,
                issues=[],
                total_issues=0,
                suggestions=[],
                error=f"Error analyzing query performance: {str(e)}"
            )


def _analyze_performance_issues(query: str, schema_content: str) -> List[PerformanceIssue]:
    """Analyze query for various performance issues."""
    issues = []
    
    # Analyze query structure
    query_structure = _parse_query_structure(query)
    
    # Check for N+1 query problems
    n_plus_one_issues = _detect_n_plus_one_patterns(query_structure, schema_content)
    issues.extend(n_plus_one_issues)
    
    # Check for deep nesting
    deep_nesting_issues = _detect_deep_nesting(query_structure)
    issues.extend(deep_nesting_issues)
    
    # Check for potentially expensive fields
    expensive_field_issues = _detect_expensive_fields(query_structure, schema_content)
    issues.extend(expensive_field_issues)
    
    # Check for large result sets
    large_result_issues = _detect_large_result_sets(query_structure)
    issues.extend(large_result_issues)
    
    # Check for missing pagination
    pagination_issues = _detect_missing_pagination(query_structure)
    issues.extend(pagination_issues)
    
    return issues


def _parse_query_structure(query: str) -> Dict[str, Any]:
    """Parse GraphQL query into a structured format for analysis."""
    # Remove comments and normalize whitespace
    cleaned_query = re.sub(r'#.*$', '', query, flags=re.MULTILINE)
    cleaned_query = ' '.join(cleaned_query.split())
    
    # Extract operation type and name
    operation_match = re.match(r'^\s*(query|mutation|subscription)\s*(\w+)?\s*', cleaned_query)
    operation_type = operation_match.group(1) if operation_match else 'query'
    operation_name = operation_match.group(2) if operation_match else None
    
    # Extract field selections
    fields = _extract_field_selections(cleaned_query)
    
    # Calculate nesting depth
    max_depth = _calculate_max_nesting_depth(cleaned_query)
    
    return {
        'operation_type': operation_type,
        'operation_name': operation_name,
        'fields': fields,
        'max_depth': max_depth,
        'raw_query': query
    }


def _extract_field_selections(query: str) -> List[Dict[str, Any]]:
    """Extract field selections from the query."""
    fields = []
    
    # Simple field extraction - matches field names
    field_pattern = r'\b(\w+)\s*(?:\([^)]*\))?\s*\{'
    matches = re.finditer(field_pattern, query)
    
    for match in matches:
        field_name = match.group(1)
        if field_name not in ['query', 'mutation', 'subscription']:
            fields.append({
                'name': field_name,
                'position': match.start(),
                'has_arguments': '(' in match.group(0),
                'is_connection': _is_connection_field(field_name)
            })
    
    return fields


def _calculate_max_nesting_depth(query: str) -> int:
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


def _detect_n_plus_one_patterns(query_structure: Dict[str, Any], schema_content: str) -> List[PerformanceIssue]:
    """Detect potential N+1 query patterns."""
    issues = []
    
    # Look for patterns where we query lists and then individual fields
    for field in query_structure['fields']:
        if field['is_connection'] or _is_list_field_in_schema(field['name'], schema_content):
            # Check if we're selecting nested object fields
            if _has_nested_object_selections(field['name'], query_structure['raw_query']):
                issues.append(PerformanceIssue(
                    issue_type="n_plus_one",
                    severity="high",
                    description=f"Potential N+1 query on field '{field['name']}'",
                    location=f"Field: {field['name']}",
                    suggestion="Consider using DataLoader or request specific fields only when needed",
                    estimated_impact="Could cause 1 + N database queries where N is the number of items"
                ))
    
    return issues


def _detect_deep_nesting(query_structure: Dict[str, Any]) -> List[PerformanceIssue]:
    """Detect queries with excessive nesting depth."""
    issues = []
    max_depth = query_structure['max_depth']
    
    if max_depth > 10:
        issues.append(PerformanceIssue(
            issue_type="deep_nesting",
            severity="high",
            description=f"Query nesting depth is {max_depth} levels deep",
            location="Query structure",
            suggestion="Break complex queries into multiple simpler queries",
            estimated_impact="Deep nesting can cause exponential performance degradation"
        ))
    elif max_depth > 6:
        issues.append(PerformanceIssue(
            issue_type="deep_nesting",
            severity="medium",
            description=f"Query nesting depth is {max_depth} levels deep",
            location="Query structure",
            suggestion="Consider reducing nesting depth for better performance",
            estimated_impact="May cause slower query execution"
        ))
    
    return issues


def _detect_expensive_fields(query_structure: Dict[str, Any], schema_content: str) -> List[PerformanceIssue]:
    """Detect potentially expensive fields in the query."""
    issues = []
    expensive_patterns = [
        'search', 'history', 'records', 'documents', 'attachments', 
        'logs', 'audit', 'analytics', 'reports', 'aggregations'
    ]
    
    for field in query_structure['fields']:
        field_name_lower = field['name'].lower()
        for pattern in expensive_patterns:
            if pattern in field_name_lower:
                issues.append(PerformanceIssue(
                    issue_type="expensive_field",
                    severity="medium",
                    description=f"Field '{field['name']}' may be computationally expensive",
                    location=f"Field: {field['name']}",
                    suggestion="Consider adding filters or limiting the data requested",
                    estimated_impact="May cause slower response times"
                ))
                break
    
    return issues


def _detect_large_result_sets(query_structure: Dict[str, Any]) -> List[PerformanceIssue]:
    """Detect queries that might return large result sets."""
    issues = []
    
    # Check for queries on collections without apparent limits
    query_text = query_structure['raw_query'].lower()
    collection_fields = ['clients', 'appointments', 'providers', 'notes', 'forms', 'payments']
    
    for collection in collection_fields:
        if collection in query_text:
            # Check if there's a 'first' or 'limit' parameter
            if not re.search(rf'{collection}\s*\([^)]*(?:first|limit)', query_text):
                issues.append(PerformanceIssue(
                    issue_type="large_result_set",
                    severity="medium",
                    description=f"Query on '{collection}' without apparent limit",
                    location=f"Collection: {collection}",
                    suggestion=f"Add pagination parameters like 'first: 20' to limit results",
                    estimated_impact="May return large datasets causing slow responses"
                ))
    
    return issues


def _detect_missing_pagination(query_structure: Dict[str, Any]) -> List[PerformanceIssue]:
    """Detect connection fields without proper pagination."""
    issues = []
    
    for field in query_structure['fields']:
        if field['is_connection']:
            query_text = query_structure['raw_query']
            field_section = _extract_field_section(query_text, field['name'])
            
            # Check if pagination info is requested
            if 'pageInfo' not in field_section:
                issues.append(PerformanceIssue(
                    issue_type="missing_pagination",
                    severity="low",
                    description=f"Connection field '{field['name']}' missing pageInfo",
                    location=f"Field: {field['name']}",
                    suggestion="Include pageInfo { hasNextPage, endCursor } for proper pagination",
                    estimated_impact="Cannot implement proper pagination without pageInfo"
                ))
    
    return issues


def _calculate_performance_score(issues: List[PerformanceIssue]) -> int:
    """Calculate overall performance score (0-100)."""
    if not issues:
        return 100
    
    penalty_map = {
        'high': 25,
        'medium': 15,
        'low': 5
    }
    
    total_penalty = sum(penalty_map.get(issue.severity, 10) for issue in issues)
    score = max(0, 100 - total_penalty)
    
    return score


def _calculate_complexity_score(query: str) -> int:
    """Calculate query complexity score."""
    # Simple complexity calculation based on:
    # - Number of fields
    # - Nesting depth
    # - Number of arguments
    
    field_count = len(re.findall(r'\b\w+\s*(?:\([^)]*\))?\s*\{', query))
    nesting_depth = _calculate_max_nesting_depth(query)
    argument_count = len(re.findall(r'\([^)]+\)', query))
    
    complexity = (field_count * 2) + (nesting_depth * 5) + argument_count
    return min(complexity, 100)  # Cap at 100


def _estimate_execution_time(complexity_score: int, issues: List[PerformanceIssue]) -> str:
    """Estimate query execution time category."""
    high_severity_issues = len([i for i in issues if i.severity == 'high'])
    
    if high_severity_issues > 2 or complexity_score > 80:
        return "Potentially slow (>2s)"
    elif high_severity_issues > 0 or complexity_score > 50:
        return "Moderate (500ms-2s)"
    elif complexity_score > 25:
        return "Fast (100ms-500ms)"
    else:
        return "Very fast (<100ms)"


def _generate_optimization_suggestions(query: str, issues: List[PerformanceIssue]) -> List[str]:
    """Generate optimization suggestions based on analysis."""
    suggestions = []
    
    # Issue-based suggestions
    issue_types = {issue.issue_type for issue in issues}
    
    if 'n_plus_one' in issue_types:
        suggestions.append("Implement DataLoader pattern for related data fetching")
    
    if 'deep_nesting' in issue_types:
        suggestions.append("Split complex queries into multiple simpler queries")
    
    if 'large_result_set' in issue_types:
        suggestions.append("Add pagination with 'first' parameter to limit results")
    
    if 'expensive_field' in issue_types:
        suggestions.append("Add filters to expensive fields to reduce computation")
    
    # General healthcare-specific suggestions
    suggestions.extend([
        "Use specific field selection instead of requesting all available fields",
        "Consider caching for frequently accessed patient data",
        "Implement proper error handling for failed queries",
        "Test queries with realistic data volumes before production use"
    ])
    
    return suggestions[:5]  # Limit to 5 suggestions


def _is_connection_field(field_name: str) -> bool:
    """Check if a field is likely a GraphQL connection."""
    connection_patterns = ['Connection', 'connections', 'edges', 'nodes']
    return any(pattern in field_name for pattern in connection_patterns)


def _is_list_field_in_schema(field_name: str, schema_content: str) -> bool:
    """Check if a field returns a list type in the schema."""
    # Simple pattern matching for list fields
    list_patterns = [f'{field_name}: \\[', f'{field_name}\\s*:\\s*\\[']
    return any(re.search(pattern, schema_content) for pattern in list_patterns)


def _has_nested_object_selections(field_name: str, query: str) -> bool:
    """Check if a field has nested object selections."""
    # Look for the field followed by object selections
    pattern = rf'{field_name}\s*(?:\([^)]*\))?\s*\{{[^}}]*\w+\s*\{{'
    return re.search(pattern, query) is not None


def _extract_field_section(query: str, field_name: str) -> str:
    """Extract the section of query related to a specific field."""
    # Find field and extract its section
    pattern = rf'{field_name}\s*(?:\([^)]*\))?\s*\{{([^}}]+)\}}'
    match = re.search(pattern, query)
    return match.group(1) if match else ""