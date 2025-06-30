"""Type introspection tool for the Healthie MCP server."""

from mcp.server.fastmcp import FastMCP
from ..models.type_introspection import TypeIntrospectionResult
from graphql import build_schema, GraphQLObjectType, GraphQLInterfaceType, GraphQLUnionType, GraphQLEnumType, GraphQLInputObjectType


def setup_type_introspection_tool(mcp: FastMCP, schema_manager) -> None:
    """Setup the type introspection tool with the MCP server."""
    
    @mcp.tool()
    def introspect_type(type_name: str) -> TypeIntrospectionResult:
        """Get detailed information about a specific GraphQL type.
        
        This tool provides comprehensive information about GraphQL types including
        fields, relationships, and metadata. Useful for understanding the structure
        and capabilities of types in the Healthie API.
        
        Args:
            type_name: The name of the GraphQL type to introspect (e.g., "User", "Patient", "Appointment")
            
        Returns:
            TypeIntrospectionResult with structured type information
        """
        try:
            schema_content = schema_manager.get_schema_content()
            if not schema_content:
                raise ValueError("Schema not available. Please check your configuration.")
            
            # Parse the schema
            schema = build_schema(schema_content)
            
            # Get the type from the schema
            type_def = schema.type_map.get(type_name)
            if type_def is None:
                raise ValueError(f"Type '{type_name}' not found in schema.")
            
            # Extract type information based on type kind
            type_info = _extract_type_info(type_def)
            
            return TypeIntrospectionResult(
                type_info=type_info
            )
            
        except Exception as e:
            # Return error in structured format
            from ..models.type_introspection import TypeInfo, FieldInfo
            error_type = TypeInfo(
                name=type_name,
                kind="ERROR",
                description=f"Error introspecting type: {str(e)}",
                fields=[],
                interfaces=[],
                possible_types=[],
                enum_values=[]
            )
            return TypeIntrospectionResult(
                type_info=error_type
            )


def _extract_type_info(type_def):
    """Extract structured information from a GraphQL type definition."""
    from ..models.type_introspection import TypeInfo, FieldInfo, EnumValue
    
    kind = type_def.__class__.__name__.replace('GraphQL', '').replace('Type', '').upper()
    
    # Extract fields for object and interface types
    fields = []
    if hasattr(type_def, 'fields'):
        for field_name, field_def in type_def.fields.items():
            field_info = FieldInfo(
                name=field_name,
                type=str(field_def.type),
                description=field_def.description or "",
                deprecated=field_def.deprecation_reason is not None,
                deprecation_reason=field_def.deprecation_reason
            )
            fields.append(field_info)
    
    # Extract interfaces for object types
    interfaces = []
    if isinstance(type_def, GraphQLObjectType) and type_def.interfaces:
        interfaces = [interface.name for interface in type_def.interfaces]
    
    # Extract possible types for union and interface types
    possible_types = []
    if isinstance(type_def, GraphQLUnionType):
        possible_types = [t.name for t in type_def.types]
    elif isinstance(type_def, GraphQLInterfaceType):
        # This would require schema introspection to find implementing types
        # For now, we'll leave it empty as it requires more complex logic
        pass
    
    # Extract enum values for enum types
    enum_values = []
    if isinstance(type_def, GraphQLEnumType):
        for value_name, value_def in type_def.values.items():
            enum_value = EnumValue(
                name=value_name,
                description=value_def.description or "",
                deprecated=value_def.deprecation_reason is not None,
                deprecation_reason=value_def.deprecation_reason
            )
            enum_values.append(enum_value)
    
    return TypeInfo(
        name=type_def.name,
        kind=kind,
        description=type_def.description or "",
        fields=fields,
        interfaces=interfaces,
        possible_types=possible_types,
        enum_values=enum_values
    )