"""Field relationship explorer tool for external developers."""

import re
from typing import Optional, List, Set, Dict, Any
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from ..models.external_dev_tools import (
    FieldRelationshipResult, FieldRelationship
)
from ..base import BaseTool, SchemaManagerProtocol
from ..config.loader import ConfigLoader
from ..exceptions import ToolError


class FieldRelationshipInput(BaseModel):
    """Input for field relationship exploration."""
    field_name: str = Field(description="The field name to explore relationships for")
    max_depth: int = Field(2, description="Maximum depth to traverse relationships", ge=1, le=5)
    include_scalars: bool = Field(False, description="Whether to include scalar field relationships")


class FieldRelationshipConstants:
    """Constants for field relationship exploration."""
    
    # GraphQL scalar types
    SCALAR_TYPES = {
        'String', 'Int', 'Float', 'Boolean', 'ID', 'Date', 'DateTime', 
        'Time', 'JSON', 'Upload', 'BigInt', 'Decimal', 'UUID'
    }
    
    # Healthcare field categorization patterns
    HEALTHCARE_FIELD_PATTERNS = {
        'patient': ['patient', 'client'],
        'appointment': ['appointment', 'booking', 'schedule'],
        'provider': ['provider', 'practitioner', 'doctor', 'nurse', 'therapist'],
        'insurance': ['insurance', 'payer', 'coverage', 'plan'],
        'medication': ['medication', 'drug', 'prescription', 'rx'],
        'diagnosis': ['diagnosis', 'condition', 'icd', 'problem'],
        'allergy': ['allergy', 'allergen', 'reaction'],
        'clinical': ['note', 'record', 'observation', 'vital'],
        'forms': ['form', 'assessment', 'questionnaire', 'survey'],
        'billing': ['payment', 'billing', 'invoice', 'charge', 'fee']
    }
    
    # Healthcare field descriptions
    HEALTHCARE_DESCRIPTIONS = {
        'patient': "Patient/client information",
        'appointment': "Appointment scheduling data",
        'provider': "Healthcare provider information",
        'insurance': "Insurance and billing information",
        'medication': "Medication and prescription data",
        'diagnosis': "Medical diagnosis and conditions",
        'allergy': "Patient allergy information",
        'clinical': "Clinical notes and records",
        'forms': "Forms and assessments",
        'billing': "Payment and billing data"
    }
    
    # Suggestion templates
    SUGGESTION_TEMPLATES = {
        'patient': "When querying {field_name}, consider including patient demographic fields: {related_fields}",
        'appointment': "For appointment-related queries with {field_name}, include: {related_fields}",
        'provider': "Provider information commonly queried with {field_name}: {related_fields}",
        'insurance': "Insurance fields often needed with {field_name}: {related_fields}",
        'required': "Required fields to include: {related_fields}",
        'lists': "Consider pagination for list fields: {related_fields}"
    }


class FieldRelationshipTool(BaseTool[FieldRelationshipResult]):
    """Tool for exploring field relationships in GraphQL schema."""
    
    def __init__(self, schema_manager: SchemaManagerProtocol):
        """Initialize the field relationship tool."""
        super().__init__(schema_manager)
        self.config_loader = ConfigLoader()
        self._relationship_config: Optional[Dict[str, Any]] = None
    
    def get_tool_name(self) -> str:
        """Get the tool name."""
        return "field_relationships"
    
    def get_tool_description(self) -> str:
        """Get the tool description."""
        return (
            "Explore relationships between GraphQL fields across the healthcare schema "
            "to help build comprehensive queries and understand field connections"
        )
    
    def execute(self, input_data: FieldRelationshipInput) -> FieldRelationshipResult:
        """Explore field relationships in the schema.
        
        Args:
            input_data: Input containing field name and exploration options
            
        Returns:
            FieldRelationshipResult with relationships and suggestions
        """
        try:
            # Load configuration if available
            self._ensure_config_loaded()
            
            # Get schema content
            schema_content = self.schema_manager.get_schema_content()
            if not schema_content:
                raise ToolError("Schema not available. Please check your configuration.")
            
            # Find relationships for the specified field
            relationships = self._explore_relationships(
                schema_content, input_data.field_name, input_data.max_depth, input_data.include_scalars
            )
            
            # Generate suggestions based on relationships
            suggestions = self._generate_field_suggestions(input_data.field_name, relationships)
            
            return FieldRelationshipResult(
                source_field=input_data.field_name,
                related_fields=relationships,
                total_relationships=len(relationships),
                max_depth=input_data.max_depth,
                suggestions=suggestions
            )
            
        except Exception as e:
            return FieldRelationshipResult(
                source_field=input_data.field_name,
                related_fields=[],
                total_relationships=0,
                max_depth=input_data.max_depth,
                suggestions=[],
                error=f"Error exploring field relationships: {str(e)}"
            )
    
    def _ensure_config_loaded(self) -> None:
        """Ensure relationship configuration is loaded."""
        if self._relationship_config is None:
            try:
                self._relationship_config = self.config_loader.load_fields()
            except Exception:
                # Use default configuration if loading fails
                self._relationship_config = {}
    
    def _explore_relationships(
        self, 
        schema_content: str, 
        field_name: str, 
        max_depth: int, 
        include_scalars: bool
    ) -> List[FieldRelationship]:
        """Explore field relationships in the GraphQL schema.
        
        Args:
            schema_content: The GraphQL schema content
            field_name: Field to explore relationships for
            max_depth: Maximum depth to traverse
            include_scalars: Whether to include scalar types
            
        Returns:
            List of field relationships
        """
        relationships = []
        visited_types = set()
        
        # Find the initial field and its type
        initial_fields = self._find_field_definitions(schema_content, field_name)
        
        for field_def in initial_fields:
            # Extract relationships recursively
            field_relationships = self._extract_relationships_recursive(
                schema_content, field_def, "", 0, max_depth, include_scalars, visited_types
            )
            relationships.extend(field_relationships)
        
        # Remove duplicates and sort by relevance
        unique_relationships = self._deduplicate_relationships(relationships)
        return sorted(unique_relationships, key=lambda r: (len(r.path.split('.')), r.field_name))
    
    def _find_field_definitions(self, schema_content: str, field_name: str) -> List[Dict[str, Any]]:
        """Find all definitions of a field in the schema.
        
        Args:
            schema_content: The GraphQL schema content
            field_name: Field name to search for
            
        Returns:
            List of field definition dictionaries
        """
        field_definitions = []
        lines = schema_content.split('\n')
        
        current_type = None
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Track current type definition
            type_match = re.match(r'type\s+(\w+)', line)
            if type_match:
                current_type = type_match.group(1)
                continue
            
            # Look for field definitions
            field_match = re.match(rf'\s*{re.escape(field_name)}\s*[:\(]', line)
            if field_match and current_type:
                # Extract field type
                field_type = self._extract_field_type(line)
                field_definitions.append({
                    'field_name': field_name,
                    'field_type': field_type,
                    'parent_type': current_type,
                    'line_number': i + 1,
                    'definition': line.strip()
                })
        
        return field_definitions
    
    def _extract_field_type(self, field_definition: str) -> str:
        """Extract the type from a field definition.
        
        Args:
            field_definition: The field definition line
            
        Returns:
            The extracted field type
        """
        # Remove arguments and extract type
        cleaned = re.sub(r'\([^)]*\)', '', field_definition)
        type_match = re.search(r':\s*([^!\s\[\]]+)', cleaned)
        if type_match:
            return type_match.group(1).strip()
        return "Unknown"
    
    def _extract_relationships_recursive(
        self,
        schema_content: str,
        field_def: Dict[str, Any],
        current_path: str,
        current_depth: int,
        max_depth: int,
        include_scalars: bool,
        visited_types: Set[str]
    ) -> List[FieldRelationship]:
        """Recursively extract field relationships.
        
        Args:
            schema_content: The GraphQL schema content
            field_def: Current field definition
            current_path: Current path in traversal
            current_depth: Current traversal depth
            max_depth: Maximum depth to traverse
            include_scalars: Whether to include scalar types
            visited_types: Set of already visited types
            
        Returns:
            List of field relationships
        """
        if current_depth >= max_depth:
            return []
        
        relationships = []
        field_type = field_def['field_type']
        
        # Avoid infinite recursion
        if field_type in visited_types:
            return []
        
        visited_types.add(field_type)
        
        # Find type definition
        type_fields = self._get_type_fields(schema_content, field_type)
        
        for type_field in type_fields:
            field_path = f"{current_path}.{type_field['field_name']}" if current_path else type_field['field_name']
            
            # Skip scalars if not requested
            if not include_scalars and self._is_scalar_type(type_field['field_type']):
                continue
            
            # Create relationship
            relationship = FieldRelationship(
                field_name=type_field['field_name'],
                field_type=type_field['field_type'],
                path=field_path,
                description=self._get_field_description(type_field),
                is_required=self._is_required_field(type_field['definition']),
                is_list=self._is_list_field(type_field['definition'])
            )
            relationships.append(relationship)
            
            # Recurse for complex types
            if not self._is_scalar_type(type_field['field_type']):
                nested_relationships = self._extract_relationships_recursive(
                    schema_content, type_field, field_path, current_depth + 1,
                    max_depth, include_scalars, visited_types.copy()
                )
                relationships.extend(nested_relationships)
        
        visited_types.remove(field_type)
        return relationships
    
    def _get_type_fields(self, schema_content: str, type_name: str) -> List[Dict[str, Any]]:
        """Get all fields for a specific type.
        
        Args:
            schema_content: The GraphQL schema content
            type_name: Type name to get fields for
            
        Returns:
            List of field dictionaries
        """
        fields = []
        lines = schema_content.split('\n')
        
        in_type = False
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Check if we're entering the target type
            if re.match(rf'type\s+{re.escape(type_name)}\s*{{', line):
                in_type = True
                continue
            
            # Check if we're leaving the type
            if in_type and line == '}':
                break
            
            # Extract field if we're in the type
            if in_type and line and not line.startswith('#'):
                field_match = re.match(r'\s*(\w+)\s*[:\(]', line)
                if field_match:
                    field_name = field_match.group(1)
                    field_type = self._extract_field_type(line)
                    fields.append({
                        'field_name': field_name,
                        'field_type': field_type,
                        'definition': line.strip(),
                        'line_number': i + 1
                    })
        
        return fields
    
    def _is_scalar_type(self, type_name: str) -> bool:
        """Check if a type is a GraphQL scalar.
        
        Args:
            type_name: Type name to check
            
        Returns:
            True if scalar type, False otherwise
        """
        return type_name in FieldRelationshipConstants.SCALAR_TYPES
    
    def _is_required_field(self, definition: str) -> bool:
        """Check if a field is required (non-nullable).
        
        Args:
            definition: Field definition string
            
        Returns:
            True if required, False otherwise
        """
        return '!' in definition and not definition.strip().endswith('[!]')
    
    def _is_list_field(self, definition: str) -> bool:
        """Check if a field is a list type.
        
        Args:
            definition: Field definition string
            
        Returns:
            True if list type, False otherwise
        """
        return '[' in definition and ']' in definition
    
    def _get_field_description(self, field_def: Dict[str, Any]) -> Optional[str]:
        """Extract description for a field based on healthcare context.
        
        Args:
            field_def: Field definition dictionary
            
        Returns:
            Description string or None
        """
        field_name = field_def['field_name'].lower()
        
        # Check configuration descriptions first
        config_descriptions = self._relationship_config.get("descriptions", {})
        if field_name in config_descriptions:
            return config_descriptions[field_name]
        
        # Use pattern-based healthcare descriptions
        for category, patterns in FieldRelationshipConstants.HEALTHCARE_FIELD_PATTERNS.items():
            if any(pattern in field_name for pattern in patterns):
                return FieldRelationshipConstants.HEALTHCARE_DESCRIPTIONS.get(category)
        
        return None
    
    def _deduplicate_relationships(self, relationships: List[FieldRelationship]) -> List[FieldRelationship]:
        """Remove duplicate relationships based on field name and path.
        
        Args:
            relationships: List of relationships to deduplicate
            
        Returns:
            List of unique relationships
        """
        seen = set()
        unique_relationships = []
        
        for relationship in relationships:
            key = (relationship.field_name, relationship.path)
            if key not in seen:
                seen.add(key)
                unique_relationships.append(relationship)
        
        return unique_relationships
    
    def _generate_field_suggestions(self, field_name: str, relationships: List[FieldRelationship]) -> List[str]:
        """Generate suggestions based on field relationships.
        
        Args:
            field_name: Source field name
            relationships: List of related fields
            
        Returns:
            List of suggestion strings
        """
        suggestions = []
        
        # Group relationships by healthcare context
        categorized_fields = self._categorize_relationships(relationships)
        
        # Generate context-aware suggestions
        for category, fields in categorized_fields.items():
            if fields and category in FieldRelationshipConstants.SUGGESTION_TEMPLATES:
                template = FieldRelationshipConstants.SUGGESTION_TEMPLATES[category]
                related_fields = ', '.join([f.field_name for f in fields[:3]])
                suggestion = template.format(field_name=field_name, related_fields=related_fields)
                suggestions.append(suggestion)
        
        # Add special suggestions for required and list fields
        required_fields = [r for r in relationships if r.is_required]
        if required_fields:
            template = FieldRelationshipConstants.SUGGESTION_TEMPLATES['required']
            related_fields = ', '.join([f.field_name for f in required_fields[:5]])
            suggestions.append(template.format(related_fields=related_fields))
        
        list_fields = [r for r in relationships if r.is_list]
        if list_fields:
            template = FieldRelationshipConstants.SUGGESTION_TEMPLATES['lists']
            related_fields = ', '.join([f.field_name for f in list_fields[:3]])
            suggestions.append(template.format(related_fields=related_fields))
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def _categorize_relationships(self, relationships: List[FieldRelationship]) -> Dict[str, List[FieldRelationship]]:
        """Categorize relationships by healthcare context.
        
        Args:
            relationships: List of relationships to categorize
            
        Returns:
            Dictionary of categorized relationships
        """
        categorized = {}
        
        for relationship in relationships:
            field_name_lower = relationship.field_name.lower()
            
            for category, patterns in FieldRelationshipConstants.HEALTHCARE_FIELD_PATTERNS.items():
                if any(pattern in field_name_lower for pattern in patterns):
                    if category not in categorized:
                        categorized[category] = []
                    categorized[category].append(relationship)
                    break
        
        return categorized


def setup_field_relationship_tool(mcp: FastMCP, schema_manager: SchemaManagerProtocol):
    """Setup the field relationship tool."""
    tool = FieldRelationshipTool(schema_manager)

    @mcp.tool(name=tool.get_tool_name())
    def field_relationships(
        field_name: str,
        max_depth: int = 2,
        include_scalars: bool = False
    ) -> dict:
        """Explore relationships between GraphQL fields across the healthcare schema.
        
        This tool helps external developers understand how GraphQL fields connect
        to each other, making it easier to build comprehensive queries without
        manually traversing the schema.
        
        Args:
            field_name: The field name to explore relationships for
            max_depth: Maximum depth to traverse relationships (1-5, default 2)
            include_scalars: Whether to include scalar field relationships
                     
        Returns:
            FieldRelationshipResult with related fields and connection paths
        """
        input_data = FieldRelationshipInput(
            field_name=field_name,
            max_depth=max_depth,
            include_scalars=include_scalars
        )

        result = tool.execute(input_data)
        return result.model_dump()


