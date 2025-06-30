"""Field relationship explorer tool for external developers."""

import re
from typing import Optional, List, Set
from mcp.server.fastmcp import FastMCP
from ..models.external_dev_tools import (
    FieldRelationshipResult, FieldRelationship
)


def setup_field_relationship_tool(mcp: FastMCP, schema_manager) -> None:
    """Setup the field relationship explorer tool with the MCP server."""
    
    @mcp.tool()
    def explore_field_relationships(
        field_name: str,
        max_depth: int = 2,
        include_scalars: bool = False
    ) -> FieldRelationshipResult:
        """Explore relationships between GraphQL fields across the healthcare schema.
        
        This tool helps external developers understand how GraphQL fields connect
        to each other, making it easier to build comprehensive queries without
        manually traversing the schema.
        
        Args:
            field_name: The field name to explore relationships for
            max_depth: Maximum depth to traverse relationships (1-3, default 2)
            include_scalars: Whether to include scalar field relationships
                     
        Returns:
            FieldRelationshipResult with related fields and connection paths
        """
        try:
            schema_content = schema_manager.get_schema_content()
            if not schema_content:
                raise ValueError("Schema not available. Please check your configuration.")
            
            # Find relationships for the specified field
            relationships = _explore_relationships(
                schema_content, field_name, max_depth, include_scalars
            )
            
            # Generate suggestions based on relationships
            suggestions = _generate_field_suggestions(field_name, relationships)
            
            return FieldRelationshipResult(
                source_field=field_name,
                related_fields=relationships,
                total_relationships=len(relationships),
                max_depth=max_depth,
                suggestions=suggestions
            )
            
        except Exception as e:
            return FieldRelationshipResult(
                source_field=field_name,
                related_fields=[],
                total_relationships=0,
                max_depth=max_depth,
                suggestions=[],
                error=f"Error exploring field relationships: {str(e)}"
            )


def _explore_relationships(
    schema_content: str, 
    field_name: str, 
    max_depth: int, 
    include_scalars: bool
) -> List[FieldRelationship]:
    """Explore field relationships in the GraphQL schema."""
    relationships = []
    visited_types = set()
    
    # Find the initial field and its type
    initial_fields = _find_field_definitions(schema_content, field_name)
    
    for field_def in initial_fields:
        # Extract relationships recursively
        field_relationships = _extract_relationships_recursive(
            schema_content, field_def, "", 0, max_depth, include_scalars, visited_types
        )
        relationships.extend(field_relationships)
    
    # Remove duplicates and sort by relevance
    unique_relationships = _deduplicate_relationships(relationships)
    return sorted(unique_relationships, key=lambda r: (len(r.path.split('.')), r.field_name))


def _find_field_definitions(schema_content: str, field_name: str) -> List[dict]:
    """Find all definitions of a field in the schema."""
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
            field_type = _extract_field_type(line)
            field_definitions.append({
                'field_name': field_name,
                'field_type': field_type,
                'parent_type': current_type,
                'line_number': i + 1,
                'definition': line.strip()
            })
    
    return field_definitions


def _extract_field_type(field_definition: str) -> str:
    """Extract the type from a field definition."""
    # Remove arguments and extract type
    cleaned = re.sub(r'\([^)]*\)', '', field_definition)
    type_match = re.search(r':\s*([^!\s]+[!]?)', cleaned)
    if type_match:
        return type_match.group(1).strip('!')
    return "Unknown"


def _extract_relationships_recursive(
    schema_content: str,
    field_def: dict,
    current_path: str,
    current_depth: int,
    max_depth: int,
    include_scalars: bool,
    visited_types: Set[str]
) -> List[FieldRelationship]:
    """Recursively extract field relationships."""
    if current_depth >= max_depth:
        return []
    
    relationships = []
    field_type = field_def['field_type']
    
    # Avoid infinite recursion
    if field_type in visited_types:
        return []
    
    visited_types.add(field_type)
    
    # Find type definition
    type_fields = _get_type_fields(schema_content, field_type)
    
    for type_field in type_fields:
        field_path = f"{current_path}.{type_field['field_name']}" if current_path else type_field['field_name']
        
        # Skip scalars if not requested
        if not include_scalars and _is_scalar_type(type_field['field_type']):
            continue
        
        # Create relationship
        relationship = FieldRelationship(
            field_name=type_field['field_name'],
            field_type=type_field['field_type'],
            path=field_path,
            description=_get_field_description(type_field),
            is_required=_is_required_field(type_field['definition']),
            is_list=_is_list_field(type_field['definition'])
        )
        relationships.append(relationship)
        
        # Recurse for complex types
        if not _is_scalar_type(type_field['field_type']):
            nested_relationships = _extract_relationships_recursive(
                schema_content, type_field, field_path, current_depth + 1,
                max_depth, include_scalars, visited_types.copy()
            )
            relationships.extend(nested_relationships)
    
    visited_types.remove(field_type)
    return relationships


def _get_type_fields(schema_content: str, type_name: str) -> List[dict]:
    """Get all fields for a specific type."""
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
                field_type = _extract_field_type(line)
                fields.append({
                    'field_name': field_name,
                    'field_type': field_type,
                    'definition': line.strip(),
                    'line_number': i + 1
                })
    
    return fields


def _is_scalar_type(type_name: str) -> bool:
    """Check if a type is a GraphQL scalar."""
    scalar_types = {
        'String', 'Int', 'Float', 'Boolean', 'ID', 'Date', 'DateTime', 
        'Time', 'JSON', 'Upload', 'BigInt', 'Decimal'
    }
    return type_name in scalar_types


def _is_required_field(definition: str) -> bool:
    """Check if a field is required (non-nullable)."""
    return '!' in definition and not definition.strip().endswith('[!]')


def _is_list_field(definition: str) -> bool:
    """Check if a field is a list type."""
    return '[' in definition and ']' in definition


def _get_field_description(field_def: dict) -> Optional[str]:
    """Extract description for a field based on healthcare context."""
    field_name = field_def['field_name'].lower()
    field_type = field_def['field_type'].lower()
    
    # Healthcare-specific descriptions
    if 'patient' in field_name or 'client' in field_name:
        return "Patient/client information"
    elif 'appointment' in field_name:
        return "Appointment scheduling data"
    elif 'provider' in field_name or 'practitioner' in field_name:
        return "Healthcare provider information"
    elif 'insurance' in field_name:
        return "Insurance and billing information"
    elif 'medication' in field_name or 'drug' in field_name:
        return "Medication and prescription data"
    elif 'diagnosis' in field_name or 'condition' in field_name:
        return "Medical diagnosis and conditions"
    elif 'allergy' in field_name:
        return "Patient allergy information"
    elif 'note' in field_name or 'record' in field_name:
        return "Clinical notes and records"
    elif 'form' in field_name or 'assessment' in field_name:
        return "Forms and assessments"
    elif 'payment' in field_name or 'billing' in field_name:
        return "Payment and billing data"
    else:
        return None


def _deduplicate_relationships(relationships: List[FieldRelationship]) -> List[FieldRelationship]:
    """Remove duplicate relationships based on field name and path."""
    seen = set()
    unique_relationships = []
    
    for relationship in relationships:
        key = (relationship.field_name, relationship.path)
        if key not in seen:
            seen.add(key)
            unique_relationships.append(relationship)
    
    return unique_relationships


def _generate_field_suggestions(field_name: str, relationships: List[FieldRelationship]) -> List[str]:
    """Generate suggestions based on field relationships."""
    suggestions = []
    
    # Group relationships by healthcare context
    patient_fields = [r for r in relationships if 'patient' in r.field_name.lower() or 'client' in r.field_name.lower()]
    appointment_fields = [r for r in relationships if 'appointment' in r.field_name.lower()]
    provider_fields = [r for r in relationships if 'provider' in r.field_name.lower()]
    insurance_fields = [r for r in relationships if 'insurance' in r.field_name.lower()]
    
    # Generate context-aware suggestions
    if patient_fields:
        suggestions.append(f"When querying {field_name}, consider including patient demographic fields: {', '.join([f.field_name for f in patient_fields[:3]])}")
    
    if appointment_fields:
        suggestions.append(f"For appointment-related queries with {field_name}, include: {', '.join([f.field_name for f in appointment_fields[:3]])}")
    
    if provider_fields:
        suggestions.append(f"Provider information commonly queried with {field_name}: {', '.join([f.field_name for f in provider_fields[:3]])}")
    
    if insurance_fields:
        suggestions.append(f"Insurance fields often needed with {field_name}: {', '.join([f.field_name for f in insurance_fields[:3]])}")
    
    # General suggestions
    required_fields = [r for r in relationships if r.is_required]
    if required_fields:
        suggestions.append(f"Required fields to include: {', '.join([f.field_name for f in required_fields[:5]])}")
    
    # Performance suggestions
    list_fields = [r for r in relationships if r.is_list]
    if list_fields:
        suggestions.append(f"Consider pagination for list fields: {', '.join([f.field_name for f in list_fields[:3]])}")
    
    return suggestions[:5]  # Limit to 5 suggestions