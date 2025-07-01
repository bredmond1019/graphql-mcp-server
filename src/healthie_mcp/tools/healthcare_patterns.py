"""Healthcare patterns analysis tool for the Healthie MCP server - Refactored version."""

from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP
from ..models.healthcare_patterns import HealthcarePatternsResult, HealthcarePattern, PatternCategory


class HealthcarePatternAnalyzer:
    """Analyzes GraphQL schema for healthcare workflow patterns."""
    
    # Pattern definitions with keywords and recommendations
    PATTERN_DEFINITIONS = {
        PatternCategory.PATIENT_MANAGEMENT: {
            'keywords': [
                'patient', 'user', 'client', 'demographic', 'profile', 'contact',
                'emergency_contact', 'family_history', 'medical_history'
            ],
            'description': 'Patient data management and demographics',
            'recommendations': [
                'Use patient queries for retrieving comprehensive patient information',
                'Implement proper access controls for sensitive patient data',
                'Consider FHIR Patient resource patterns for interoperability',
                'Validate patient identifiers before mutations'
            ]
        },
        PatternCategory.APPOINTMENTS: {
            'keywords': [
                'appointment', 'booking', 'schedule', 'calendar', 'availability',
                'slot', 'recurring', 'cancel', 'reschedule', 'reminder'
            ],
            'description': 'Appointment scheduling and management workflows',
            'recommendations': [
                'Check availability before booking appointments',
                'Handle timezone considerations for scheduling',
                'Implement proper cancellation and rescheduling workflows',
                'Set up automated appointment reminders'
            ]
        },
        PatternCategory.CLINICAL_DATA: {
            'keywords': [
                'note', 'form', 'assessment', 'measurement', 'vital', 'lab',
                'observation', 'diagnosis', 'medication', 'prescription',
                'care_plan', 'goal', 'treatment'
            ],
            'description': 'Clinical documentation and care management',
            'recommendations': [
                'Follow clinical documentation best practices',
                'Ensure proper provider authentication for clinical data',
                'Implement care plan workflows with measurable goals',
                'Use structured data formats for assessments and forms'
            ]
        },
        PatternCategory.BILLING: {
            'keywords': [
                'billing', 'payment', 'invoice', 'charge', 'insurance',
                'claim', 'authorization', 'copay', 'deductible', 'balance',
                'transaction', 'refund'
            ],
            'description': 'Billing, payments, and insurance processing',
            'recommendations': [
                'Validate insurance information before processing claims',
                'Implement secure payment processing workflows',
                'Handle payment failures and retry logic gracefully',
                'Maintain audit trails for all financial transactions'
            ]
        },
        PatternCategory.PROVIDER_MANAGEMENT: {
            'keywords': [
                'provider', 'practitioner', 'organization', 'license',
                'credential', 'specialty', 'location', 'staff', 'role'
            ],
            'description': 'Healthcare provider and organization management',
            'recommendations': [
                'Validate provider credentials and licenses',
                'Implement role-based access controls',
                'Manage provider-patient relationships properly',
                'Handle multi-location provider scenarios'
            ]
        }
    }
    
    # Maximum elements to include per pattern for readability
    MAX_ELEMENTS_PER_PATTERN = 10
    
    def __init__(self, schema_content: str):
        self.schema_content = schema_content
        self.schema_lines = schema_content.lower().split('\n')
    
    def analyze(self, category_filter: Optional[str] = None) -> List[HealthcarePattern]:
        """Analyze schema for healthcare patterns with optional category filter."""
        patterns = []
        
        for pattern_category, config in self.PATTERN_DEFINITIONS.items():
            # Apply category filter if specified
            if self._should_skip_category(pattern_category, category_filter):
                continue
            
            # Find elements for this pattern
            found_elements = self._find_pattern_elements(config['keywords'])
            
            # Create pattern if elements were found
            if found_elements:
                pattern = self._create_pattern(
                    pattern_category, 
                    config, 
                    found_elements
                )
                patterns.append(pattern)
        
        return patterns
    
    def _should_skip_category(
        self, 
        pattern_category: PatternCategory, 
        category_filter: Optional[str]
    ) -> bool:
        """Check if category should be skipped based on filter."""
        return category_filter and category_filter != pattern_category.value
    
    def _find_pattern_elements(self, keywords: List[str]) -> List[str]:
        """Find schema elements matching the given keywords."""
        found_elements = []
        
        for keyword in keywords:
            elements = self._search_keyword_in_schema(keyword)
            found_elements.extend(elements)
        
        return found_elements
    
    def _search_keyword_in_schema(self, keyword: str) -> List[str]:
        """Search for a specific keyword in schema lines."""
        elements = []
        
        for line_num, line in enumerate(self.schema_lines):
            if self._is_relevant_line(line, keyword):
                elements.append(f"Line {line_num + 1}: {line.strip()}")
        
        return elements
    
    def _is_relevant_line(self, line: str, keyword: str) -> bool:
        """Check if a line contains the keyword and is a relevant schema element."""
        if keyword not in line:
            return False
        
        # Check if it's a type definition, input definition, or field
        relevant_indicators = ['type ', 'input ', ':']
        return any(indicator in line for indicator in relevant_indicators)
    
    def _create_pattern(
        self, 
        category: PatternCategory, 
        config: Dict[str, Any], 
        found_elements: List[str]
    ) -> HealthcarePattern:
        """Create a HealthcarePattern from found elements."""
        return HealthcarePattern(
            pattern_type=self._format_pattern_type(category),
            category=category,
            description=config['description'],
            elements=found_elements[:self.MAX_ELEMENTS_PER_PATTERN],
            recommendations=config['recommendations']
        )
    
    def _format_pattern_type(self, category: PatternCategory) -> str:
        """Format pattern type for display."""
        return f"{category.value.replace('_', ' ').title()} Pattern"


def setup_healthcare_patterns_tool(mcp: FastMCP, schema_manager) -> None:
    """Setup the healthcare patterns tool with the MCP server."""
    
    @mcp.tool()
    def find_healthcare_patterns(category: Optional[str] = None) -> HealthcarePatternsResult:
        """Analyze the GraphQL schema to identify common healthcare workflow patterns.
        
        This tool examines the Healthie GraphQL schema to identify common healthcare
        workflows and provides recommendations for each pattern. It's designed to help
        developers understand healthcare-specific API usage patterns.
        
        Args:
            category: Optional category to filter patterns (patient_management, appointments, 
                     clinical_data, billing, provider_management, communications, reporting)
                     If not provided, all patterns will be analyzed.
                     
        Returns:
            HealthcarePatternsResult with detected patterns and recommendations
        """
        try:
            # Get schema content
            schema_content = schema_manager.get_schema_content()
            if not schema_content:
                raise ValueError("Schema not available. Please check your configuration.")
            
            # Create analyzer and run analysis
            analyzer = HealthcarePatternAnalyzer(schema_content)
            patterns = analyzer.analyze(category)
            
            # Generate result
            return _create_result(patterns)
            
        except Exception as e:
            # Return error in structured format
            return _create_error_result(str(e))


def _create_result(patterns: List[HealthcarePattern]) -> HealthcarePatternsResult:
    """Create a successful result from found patterns."""
    # Get unique categories found
    categories_found = list(set(p.category for p in patterns))
    
    # Generate summary
    if patterns:
        summary = f"Found {len(patterns)} healthcare patterns across {len(categories_found)} categories"
    else:
        summary = "No healthcare patterns found in the schema"
    
    return HealthcarePatternsResult(
        patterns=patterns,
        total_patterns=len(patterns),
        summary=summary,
        categories_found=categories_found
    )


def _create_error_result(error_message: str) -> HealthcarePatternsResult:
    """Create an error result."""
    return HealthcarePatternsResult(
        patterns=[],
        total_patterns=0,
        summary=f"Error analyzing healthcare patterns: {error_message}",
        categories_found=[]
    )