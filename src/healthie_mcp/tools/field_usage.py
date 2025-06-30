"""Field usage analytics tool for external developers."""

from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP
from ..models.external_dev_tools import (
    FieldUsageResult, FieldUsagePattern, FieldSuggestion
)


def setup_field_usage_tool(mcp: FastMCP, schema_manager) -> None:
    """Setup the field usage analytics tool with the MCP server."""
    
    @mcp.tool()
    def analyze_field_usage(
        field_names: List[str],
        suggest_optimizations: bool = True
    ) -> FieldUsageResult:
        """Analyze field usage patterns and suggest optimal field combinations.
        
        This tool helps external developers understand which fields are commonly
        used together and provides recommendations for complete data sets.
        
        Args:
            field_names: List of field names to analyze
            suggest_optimizations: Whether to include performance optimization suggestions
                     
        Returns:
            FieldUsageResult with usage patterns and field suggestions
        """
        try:
            schema_content = schema_manager.get_schema_content()
            if not schema_content:
                raise ValueError("Schema not available. Please check your configuration.")
            
            # Analyze usage patterns for the provided fields
            patterns = _analyze_usage_patterns(field_names, schema_content)
            
            # Generate field suggestions
            suggestions = _generate_field_suggestions(field_names, patterns, suggest_optimizations)
            
            return FieldUsageResult(
                analyzed_fields=field_names,
                usage_patterns=patterns,
                suggestions=suggestions,
                total_patterns=len(patterns)
            )
            
        except Exception as e:
            return FieldUsageResult(
                analyzed_fields=field_names,
                usage_patterns=[],
                suggestions=[],
                total_patterns=0,
                error=f"Error analyzing field usage: {str(e)}"
            )


def _analyze_usage_patterns(field_names: List[str], schema_content: str) -> List[FieldUsagePattern]:
    """Analyze usage patterns for the given fields."""
    patterns = []
    
    # Healthcare-specific field relationship knowledge
    field_relationships = _get_healthcare_field_relationships()
    
    for field_name in field_names:
        field_lower = field_name.lower()
        
        # Find common usage patterns based on healthcare domain knowledge
        commonly_used_with = []
        performance_impact = "low"
        healthcare_context = None
        usage_frequency = 0.5  # Default moderate usage
        
        # Patient/Client fields
        if 'patient' in field_lower or 'client' in field_lower:
            commonly_used_with = ['firstName', 'lastName', 'email', 'phone', 'dateOfBirth']
            healthcare_context = "Patient demographic data - core information for most healthcare operations"
            usage_frequency = 0.9
            
        # Appointment fields
        elif 'appointment' in field_lower:
            commonly_used_with = ['startTime', 'endTime', 'status', 'provider', 'client']
            healthcare_context = "Appointment data - essential for scheduling and care coordination"
            usage_frequency = 0.8
            performance_impact = "medium"
            
        # Provider fields
        elif 'provider' in field_lower:
            commonly_used_with = ['name', 'specialty', 'license', 'location']
            healthcare_context = "Provider information - important for patient matching and care delivery"
            usage_frequency = 0.7
            
        # Insurance fields
        elif 'insurance' in field_lower:
            commonly_used_with = ['name', 'memberNumber', 'groupNumber', 'status']
            healthcare_context = "Insurance data - critical for billing and authorization"
            usage_frequency = 0.6
            performance_impact = "high"  # Insurance verification can be slow
            
        # Clinical fields
        elif any(term in field_lower for term in ['note', 'form', 'assessment', 'medication']):
            commonly_used_with = ['createdAt', 'provider', 'client', 'status']
            healthcare_context = "Clinical data - requires careful handling due to PHI sensitivity"
            usage_frequency = 0.7
            performance_impact = "medium"
            
        # Billing fields
        elif any(term in field_lower for term in ['payment', 'invoice', 'billing']):
            commonly_used_with = ['amount', 'status', 'date', 'client']
            healthcare_context = "Financial data - important for revenue cycle management"
            usage_frequency = 0.5
            performance_impact = "medium"
        
        # Create pattern
        pattern = FieldUsagePattern(
            field_name=field_name,
            usage_frequency=usage_frequency,
            commonly_used_with=commonly_used_with,
            performance_impact=performance_impact,
            healthcare_context=healthcare_context
        )
        patterns.append(pattern)
    
    return patterns


def _generate_field_suggestions(
    field_names: List[str], 
    patterns: List[FieldUsagePattern], 
    suggest_optimizations: bool
) -> List[FieldSuggestion]:
    """Generate field selection suggestions based on patterns."""
    suggestions = []
    
    # Collect all commonly used fields
    all_common_fields = set()
    for pattern in patterns:
        all_common_fields.update(pattern.commonly_used_with)
    
    # Remove fields that are already in the analyzed list
    missing_common_fields = all_common_fields - set(field_names)
    
    if missing_common_fields:
        suggestions.append(FieldSuggestion(
            suggestion_type="commonly_used_together",
            suggested_fields=list(missing_common_fields)[:5],  # Limit to 5
            reason="These fields are commonly requested together with your selected fields",
            performance_note="Adding these fields to your initial query can reduce the need for additional API calls"
        ))
    
    # Complete data set suggestions
    patient_fields = [f for f in field_names if 'patient' in f.lower() or 'client' in f.lower()]
    if patient_fields:
        complete_patient_fields = [
            'id', 'firstName', 'lastName', 'email', 'phone', 'dateOfBirth', 
            'address', 'emergencyContact', 'insuranceInfo'
        ]
        missing_patient_fields = set(complete_patient_fields) - set(field_names)
        if missing_patient_fields:
            suggestions.append(FieldSuggestion(
                suggestion_type="complete_data_set",
                suggested_fields=list(missing_patient_fields),
                reason="Complete patient data set for comprehensive patient management",
                performance_note="Fetching complete patient data upfront reduces subsequent API calls"
            ))
    
    # Performance optimization suggestions
    if suggest_optimizations:
        high_impact_fields = [p for p in patterns if p.performance_impact == "high"]
        if high_impact_fields:
            suggestions.append(FieldSuggestion(
                suggestion_type="performance_optimized",
                suggested_fields=[p.field_name for p in high_impact_fields],
                reason="These fields have high performance impact and should be used carefully",
                performance_note="Consider caching these fields or requesting them only when necessary"
            ))
        
        # Pagination suggestions for list fields
        list_field_indicators = ['appointments', 'notes', 'forms', 'payments', 'medications']
        list_fields = [f for f in field_names if any(indicator in f.lower() for indicator in list_field_indicators)]
        if list_fields:
            suggestions.append(FieldSuggestion(
                suggestion_type="performance_optimized",
                suggested_fields=['first', 'after', 'pageInfo'],
                reason="Add pagination fields for list queries to improve performance",
                performance_note="Use 'first: 20' to limit results and include pageInfo for pagination"
            ))
    
    # Healthcare-specific suggestions
    clinical_fields = [f for f in field_names if any(term in f.lower() for term in ['note', 'form', 'medication', 'diagnosis'])]
    if clinical_fields:
        suggestions.append(FieldSuggestion(
            suggestion_type="complete_data_set",
            suggested_fields=['provider', 'createdAt', 'status', 'isPrivate'],
            reason="Essential metadata for clinical data management and compliance",
            performance_note="Include provider and timestamp information for audit trails"
        ))
    
    return suggestions


def _get_healthcare_field_relationships() -> Dict[str, List[str]]:
    """Get predefined healthcare field relationships."""
    return {
        'patient': ['demographics', 'insurance', 'appointments', 'medical_history'],
        'appointment': ['patient', 'provider', 'scheduling', 'billing'],
        'provider': ['credentials', 'schedule', 'patients', 'organization'],
        'insurance': ['patient', 'authorization', 'billing', 'claims'],
        'clinical_note': ['patient', 'provider', 'appointment', 'diagnosis'],
        'medication': ['patient', 'provider', 'prescription', 'pharmacy'],
        'billing': ['patient', 'insurance', 'services', 'payments']
    }