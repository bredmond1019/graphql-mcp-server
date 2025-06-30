"""Healthcare patterns analysis tool for the Healthie MCP server."""

from typing import Optional
from mcp.server.fastmcp import FastMCP
from ..models.healthcare_patterns import HealthcarePatternsResult, HealthcarePattern, PatternCategory


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
            schema_content = schema_manager.get_schema_content()
            if not schema_content:
                raise ValueError("Schema not available. Please check your configuration.")
            
            # Analyze schema for healthcare patterns
            patterns = _analyze_healthcare_patterns(schema_content, category)
            
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
            
        except Exception as e:
            # Return error in structured format
            return HealthcarePatternsResult(
                patterns=[],
                total_patterns=0,
                summary=f"Error analyzing healthcare patterns: {str(e)}",
                categories_found=[]
            )


def _analyze_healthcare_patterns(schema_content: str, category_filter: Optional[str] = None):
    """Analyze schema content for healthcare patterns."""
    patterns = []
    
    # Define pattern categories and their associated keywords
    pattern_definitions = {
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
    
    # Analyze each pattern category
    for pattern_category, config in pattern_definitions.items():
        # Skip if category filter is specified and doesn't match
        if category_filter and category_filter != pattern_category.value:
            continue
            
        # Search for pattern keywords in schema
        found_elements = []
        for keyword in config['keywords']:
            # Case-insensitive search for keyword
            lines = schema_content.lower().split('\n')
            for line_num, line in enumerate(lines):
                if keyword in line and ('type ' in line or 'input ' in line or ':' in line):
                    found_elements.append(f"Line {line_num + 1}: {line.strip()}")
        
        # Create pattern if elements were found
        if found_elements:
            pattern = HealthcarePattern(
                pattern_type=f"{pattern_category.value.replace('_', ' ').title()} Pattern",
                category=pattern_category,
                description=config['description'],
                elements=found_elements[:10],  # Limit to first 10 for readability
                recommendations=config['recommendations']
            )
            patterns.append(pattern)
    
    return patterns