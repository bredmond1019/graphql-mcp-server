"""Field usage analytics tool for external developers.

This tool analyzes field usage patterns and provides recommendations for optimal
field combinations based on healthcare domain knowledge and common usage patterns.
"""

from typing import List, Dict, Any, Optional, Set
from enum import Enum
from pydantic import BaseModel, Field

from ...models.external_dev_tools import (
    FieldUsageResult, FieldUsagePattern, FieldSuggestion
)
from ...base import BaseTool, SchemaManagerProtocol
from ...config.loader import get_config_loader
from ...exceptions import ToolError


class FieldUsageConstants:
    """Constants for field usage analysis tool."""
    
    # Performance impact levels
    PERFORMANCE_LOW = "low"
    PERFORMANCE_MEDIUM = "medium"
    PERFORMANCE_HIGH = "high"
    
    # Healthcare field categories
    PATIENT_FIELDS = {'patient', 'client', 'user'}
    APPOINTMENT_FIELDS = {'appointment', 'visit', 'session'}
    PROVIDER_FIELDS = {'provider', 'practitioner', 'doctor'}
    INSURANCE_FIELDS = {'insurance', 'coverage', 'payer'}
    CLINICAL_FIELDS = {'note', 'form', 'assessment', 'medication', 'diagnosis'}
    BILLING_FIELDS = {'payment', 'invoice', 'billing', 'charge'}
    
    # Default usage frequencies
    DEFAULT_FREQUENCIES = {
        'patient': 0.9,
        'appointment': 0.8,
        'provider': 0.7,
        'clinical': 0.7,
        'insurance': 0.6,
        'billing': 0.5
    }
    
    # Common field combinations
    FIELD_COMBINATIONS = {
        'patient': ['firstName', 'lastName', 'email', 'phone', 'dateOfBirth'],
        'appointment': ['startTime', 'endTime', 'status', 'provider', 'client'],
        'provider': ['name', 'specialty', 'license', 'location'],
        'insurance': ['name', 'memberNumber', 'groupNumber', 'status'],
        'clinical': ['createdAt', 'provider', 'client', 'status'],
        'billing': ['amount', 'status', 'date', 'client']
    }
    
    # Healthcare contexts
    HEALTHCARE_CONTEXTS = {
        'patient': "Patient demographic data - core information for most healthcare operations",
        'appointment': "Appointment data - essential for scheduling and care coordination",
        'provider': "Provider information - important for patient matching and care delivery",
        'insurance': "Insurance data - critical for billing and authorization",
        'clinical': "Clinical data - requires careful handling due to PHI sensitivity",
        'billing': "Financial data - important for revenue cycle management"
    }
    
    # Suggestion types
    SUGGESTION_COMMONLY_USED = "commonly_used_together"
    SUGGESTION_COMPLETE_DATA = "complete_data_set"
    SUGGESTION_PERFORMANCE = "performance_optimized"
    
    # List field indicators for pagination suggestions
    LIST_FIELD_INDICATORS = ['appointments', 'notes', 'forms', 'payments', 'medications']
    
    # Pagination fields to suggest
    PAGINATION_FIELDS = ['first', 'after', 'pageInfo']
    
    # Complete patient data set
    COMPLETE_PATIENT_FIELDS = [
        'id', 'firstName', 'lastName', 'email', 'phone', 'dateOfBirth',
        'address', 'emergencyContact', 'insuranceInfo'
    ]
    
    # Clinical metadata fields
    CLINICAL_METADATA_FIELDS = ['provider', 'createdAt', 'status', 'isPrivate']


class FieldUsageInput(BaseModel):
    """Input parameters for field usage analysis."""
    
    field_names: List[str] = Field(
        description="List of field names to analyze for usage patterns"
    )
    
    suggest_optimizations: bool = Field(
        True,
        description="Whether to include performance optimization suggestions"
    )


class FieldUsageTool(BaseTool[FieldUsageResult]):
    """Tool for analyzing field usage patterns and providing optimization suggestions."""
    
    def __init__(self, schema_manager: SchemaManagerProtocol):
        """Initialize the tool.
        
        Args:
            schema_manager: Schema manager instance for accessing GraphQL schema
        """
        super().__init__(schema_manager)
        self.config_loader = get_config_loader()
        self._field_relationships_cache: Optional[Dict[str, List[str]]] = None
    
    def get_tool_name(self) -> str:
        """Get the tool name."""
        return "analyze_field_usage"
    
    def get_tool_description(self) -> str:
        """Get the tool description."""
        return "Analyze field usage patterns and suggest optimal field combinations for healthcare workflows"
    
    def execute(
        self,
        field_names: List[str],
        suggest_optimizations: bool = True
    ) -> FieldUsageResult:
        """Analyze field usage patterns and suggest optimal field combinations.
        
        Args:
            field_names: List of field names to analyze
            suggest_optimizations: Whether to include performance optimization suggestions
                     
        Returns:
            FieldUsageResult with usage patterns and field suggestions
        """
        try:
            # Validate inputs
            if not field_names:
                raise ToolError("At least one field name must be provided")
            
            # Schema content is not strictly required for field usage analysis
            # as it's based on domain knowledge, but we'll try to get it
            schema_content = None
            try:
                schema_content = self.schema_manager.get_schema_content()
            except Exception:
                # Continue without schema - analysis will be based on patterns only
                pass
            
            # Analyze usage patterns for the provided fields
            patterns = self._analyze_usage_patterns(field_names, schema_content)
            
            # Generate field suggestions
            suggestions = self._generate_field_suggestions(field_names, patterns, suggest_optimizations)
            
            return FieldUsageResult(
                analyzed_fields=field_names,
                usage_patterns=patterns,
                suggestions=suggestions,
                total_patterns=len(patterns)
            )
            
        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Error analyzing field usage: {str(e)}")

    def _analyze_usage_patterns(self, field_names: List[str], schema_content: Optional[str]) -> List[FieldUsagePattern]:
        """Analyze usage patterns for the given fields."""
        patterns = []
        
        for field_name in field_names:
            pattern = self._analyze_single_field_pattern(field_name)
            patterns.append(pattern)
        
        return patterns
    
    def _analyze_single_field_pattern(self, field_name: str) -> FieldUsagePattern:
        """Analyze usage pattern for a single field."""
        field_lower = field_name.lower()
        
        # Determine field category and get defaults
        category = self._determine_field_category(field_lower)
        commonly_used_with = FieldUsageConstants.FIELD_COMBINATIONS.get(category, [])
        healthcare_context = FieldUsageConstants.HEALTHCARE_CONTEXTS.get(category)
        usage_frequency = FieldUsageConstants.DEFAULT_FREQUENCIES.get(category, 0.5)
        performance_impact = self._determine_performance_impact(field_lower, category)
        
        return FieldUsagePattern(
            field_name=field_name,
            usage_frequency=usage_frequency,
            commonly_used_with=commonly_used_with,
            performance_impact=performance_impact,
            healthcare_context=healthcare_context
        )
    
    def _determine_field_category(self, field_lower: str) -> str:
        """Determine the healthcare category of a field."""
        if any(term in field_lower for term in FieldUsageConstants.PATIENT_FIELDS):
            return 'patient'
        elif any(term in field_lower for term in FieldUsageConstants.APPOINTMENT_FIELDS):
            return 'appointment'
        elif any(term in field_lower for term in FieldUsageConstants.PROVIDER_FIELDS):
            return 'provider'
        elif any(term in field_lower for term in FieldUsageConstants.INSURANCE_FIELDS):
            return 'insurance'
        elif any(term in field_lower for term in FieldUsageConstants.CLINICAL_FIELDS):
            return 'clinical'
        elif any(term in field_lower for term in FieldUsageConstants.BILLING_FIELDS):
            return 'billing'
        else:
            return 'general'
    
    def _determine_performance_impact(self, field_lower: str, category: str) -> str:
        """Determine the performance impact of a field."""
        if category == 'insurance':
            return FieldUsageConstants.PERFORMANCE_HIGH
        elif category in ['appointment', 'clinical', 'billing']:
            return FieldUsageConstants.PERFORMANCE_MEDIUM
        else:
            return FieldUsageConstants.PERFORMANCE_LOW

    def _generate_field_suggestions(
        self,
        field_names: List[str], 
        patterns: List[FieldUsagePattern], 
        suggest_optimizations: bool
    ) -> List[FieldSuggestion]:
        """Generate field selection suggestions based on patterns."""
        suggestions = []
        
        # Generate commonly used suggestions
        commonly_used_suggestion = self._generate_commonly_used_suggestion(field_names, patterns)
        if commonly_used_suggestion:
            suggestions.append(commonly_used_suggestion)
        
        # Generate complete data set suggestions
        complete_data_suggestions = self._generate_complete_data_suggestions(field_names)
        suggestions.extend(complete_data_suggestions)
        
        # Generate performance optimization suggestions
        if suggest_optimizations:
            performance_suggestions = self._generate_performance_suggestions(field_names, patterns)
            suggestions.extend(performance_suggestions)
        
        # Generate healthcare-specific suggestions
        healthcare_suggestions = self._generate_healthcare_suggestions(field_names)
        suggestions.extend(healthcare_suggestions)
        
        return suggestions
    
    def _generate_commonly_used_suggestion(self, field_names: List[str], patterns: List[FieldUsagePattern]) -> Optional[FieldSuggestion]:
        """Generate suggestions for commonly used fields."""
        all_common_fields = set()
        for pattern in patterns:
            all_common_fields.update(pattern.commonly_used_with)
        
        missing_common_fields = all_common_fields - set(field_names)
        
        if missing_common_fields:
            return FieldSuggestion(
                suggestion_type=FieldUsageConstants.SUGGESTION_COMMONLY_USED,
                suggested_fields=list(missing_common_fields)[:5],
                reason="These fields are commonly requested together with your selected fields",
                performance_note="Adding these fields to your initial query can reduce the need for additional API calls"
            )
        return None
    
    def _generate_complete_data_suggestions(self, field_names: List[str]) -> List[FieldSuggestion]:
        """Generate complete data set suggestions."""
        suggestions = []
        
        # Patient data completeness
        patient_fields = [f for f in field_names if any(term in f.lower() for term in FieldUsageConstants.PATIENT_FIELDS)]
        if patient_fields:
            missing_patient_fields = set(FieldUsageConstants.COMPLETE_PATIENT_FIELDS) - set(field_names)
            if missing_patient_fields:
                suggestions.append(FieldSuggestion(
                    suggestion_type=FieldUsageConstants.SUGGESTION_COMPLETE_DATA,
                    suggested_fields=list(missing_patient_fields),
                    reason="Complete patient data set for comprehensive patient management",
                    performance_note="Fetching complete patient data upfront reduces subsequent API calls"
                ))
        
        return suggestions
    
    def _generate_performance_suggestions(self, field_names: List[str], patterns: List[FieldUsagePattern]) -> List[FieldSuggestion]:
        """Generate performance optimization suggestions."""
        suggestions = []
        
        # High impact field warnings
        high_impact_fields = [p for p in patterns if p.performance_impact == FieldUsageConstants.PERFORMANCE_HIGH]
        if high_impact_fields:
            suggestions.append(FieldSuggestion(
                suggestion_type=FieldUsageConstants.SUGGESTION_PERFORMANCE,
                suggested_fields=[p.field_name for p in high_impact_fields],
                reason="These fields have high performance impact and should be used carefully",
                performance_note="Consider caching these fields or requesting them only when necessary"
            ))
        
        # Pagination suggestions
        list_fields = [f for f in field_names if any(indicator in f.lower() for indicator in FieldUsageConstants.LIST_FIELD_INDICATORS)]
        if list_fields:
            suggestions.append(FieldSuggestion(
                suggestion_type=FieldUsageConstants.SUGGESTION_PERFORMANCE,
                suggested_fields=FieldUsageConstants.PAGINATION_FIELDS,
                reason="Add pagination fields for list queries to improve performance",
                performance_note="Use 'first: 20' to limit results and include pageInfo for pagination"
            ))
        
        return suggestions
    
    def _generate_healthcare_suggestions(self, field_names: List[str]) -> List[FieldSuggestion]:
        """Generate healthcare-specific suggestions."""
        suggestions = []
        
        # Clinical data metadata
        clinical_fields = [f for f in field_names if any(term in f.lower() for term in FieldUsageConstants.CLINICAL_FIELDS)]
        if clinical_fields:
            suggestions.append(FieldSuggestion(
                suggestion_type=FieldUsageConstants.SUGGESTION_COMPLETE_DATA,
                suggested_fields=FieldUsageConstants.CLINICAL_METADATA_FIELDS,
                reason="Essential metadata for clinical data management and compliance",
                performance_note="Include provider and timestamp information for audit trails"
            ))
        
        return suggestions


def setup_field_usage_tool(mcp, schema_manager) -> None:
    """Setup the field usage analytics tool with the MCP server."""
    tool = FieldUsageTool(schema_manager)
    
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
        return tool.execute(
            field_names=field_names,
            suggest_optimizations=suggest_optimizations
        )
