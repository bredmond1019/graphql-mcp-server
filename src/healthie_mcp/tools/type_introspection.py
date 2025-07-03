"""Type introspection tool for the Healthie MCP server.

This tool provides comprehensive information about GraphQL types including
fields, relationships, and metadata. Useful for understanding the structure
and capabilities of types in the Healthie API.
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

from ..models.type_introspection import TypeIntrospectionResult, TypeInfo, FieldInfo, EnumValue
from ..base import BaseTool, SchemaManagerProtocol
from ..config.loader import get_config_loader
from ..exceptions import ToolError
from graphql import build_schema, GraphQLObjectType, GraphQLInterfaceType, GraphQLUnionType, GraphQLEnumType, GraphQLInputObjectType


class TypeIntrospectionConstants:
    """Constants for type introspection tool."""
    
    # GraphQL type kinds
    KIND_OBJECT = "OBJECT"
    KIND_INTERFACE = "INTERFACE"
    KIND_UNION = "UNION"
    KIND_ENUM = "ENUM"
    KIND_INPUT_OBJECT = "INPUT_OBJECT"
    KIND_SCALAR = "SCALAR"
    KIND_ERROR = "ERROR"
    
    # Built-in scalar types
    SCALAR_TYPES = {
        'String', 'Int', 'Float', 'Boolean', 'ID',
        'Date', 'DateTime', 'Time', 'JSON', 'Upload'
    }
    
    # GraphQL operation types to exclude from field extraction
    OPERATION_TYPES = {'query', 'mutation', 'subscription'}
    
    # Type name patterns to identify
    TYPE_SUFFIXES = {
        'Connection': 'GraphQL Relay Connection',
        'Edge': 'GraphQL Relay Edge',
        'Input': 'GraphQL Input Type',
        'Payload': 'GraphQL Mutation Payload',
        'Result': 'GraphQL Result Type'
    }
    
    # Healthcare-specific type categories
    HEALTHCARE_TYPES = {
        'patient': ['Client', 'Patient', 'User'],
        'provider': ['Provider', 'Practitioner', 'Doctor'],
        'appointment': ['Appointment', 'Visit', 'Session'],
        'clinical': ['Note', 'Form', 'Assessment', 'Medication'],
        'billing': ['Payment', 'Invoice', 'Billing', 'Charge'],
        'insurance': ['Insurance', 'Coverage', 'Payer']
    }


class TypeIntrospectionInput(BaseModel):
    """Input parameters for type introspection."""
    
    type_name: str = Field(
        description="The name of the GraphQL type to introspect (e.g., 'User', 'Patient', 'Appointment')"
    )


class TypeIntrospectionTool(BaseTool[TypeIntrospectionResult]):
    """Tool for introspecting GraphQL types and their metadata."""
    
    def __init__(self, schema_manager: SchemaManagerProtocol):
        """Initialize the tool.
        
        Args:
            schema_manager: Schema manager instance for accessing GraphQL schema
        """
        super().__init__(schema_manager)
        self.config_loader = get_config_loader()
    
    def get_tool_name(self) -> str:
        """Get the tool name."""
        return "introspect_type"
    
    def get_tool_description(self) -> str:
        """Get the tool description."""
        return "Get detailed information about a specific GraphQL type including fields, relationships, and metadata"
    
    def execute(self, input_data: TypeIntrospectionInput) -> TypeIntrospectionResult:
        """Get detailed information about a specific GraphQL type.
        
        Args:
            input_data: Input containing the type name to introspect
            
        Returns:
            TypeIntrospectionResult with structured type information
        """
        try:
            # Extract type_name from input
            type_name = input_data.type_name
            # Validate inputs
            if not type_name or not type_name.strip():
                error_type = TypeInfo(
                    name=type_name or "",
                    kind=TypeIntrospectionConstants.KIND_ERROR,
                    description="Type name is required and cannot be empty",
                    fields=[],
                    interfaces=[],
                    possible_types=[],
                    enum_values=[]
                )
                return TypeIntrospectionResult(type_info=error_type)
            
            type_name = type_name.strip()
            
            schema_content = self.schema_manager.get_schema_content()
            if not schema_content:
                error_type = TypeInfo(
                    name=type_name,
                    kind=TypeIntrospectionConstants.KIND_ERROR,
                    description="Schema not available. Please check your configuration.",
                    fields=[],
                    interfaces=[],
                    possible_types=[],
                    enum_values=[]
                )
                return TypeIntrospectionResult(type_info=error_type)
            
            # Parse the schema
            try:
                schema = build_schema(schema_content)
            except Exception as e:
                error_type = TypeInfo(
                    name=type_name,
                    kind=TypeIntrospectionConstants.KIND_ERROR,
                    description=f"Failed to parse schema: {str(e)}",
                    fields=[],
                    interfaces=[],
                    possible_types=[],
                    enum_values=[]
                )
                return TypeIntrospectionResult(type_info=error_type)
            
            # Get the type from the schema
            type_def = schema.type_map.get(type_name)
            if type_def is None:
                error_type = TypeInfo(
                    name=type_name,
                    kind=TypeIntrospectionConstants.KIND_ERROR,
                    description=f"Type '{type_name}' not found in schema.",
                    fields=[],
                    interfaces=[],
                    possible_types=[],
                    enum_values=[]
                )
                return TypeIntrospectionResult(type_info=error_type)
            
            # Extract type information based on type kind
            type_info = self._extract_type_info(type_def)
            
            return TypeIntrospectionResult(
                type_info=type_info
            )
            
        except Exception as e:
            # Return error in structured format
            error_type = TypeInfo(
                name=type_name or "",
                kind=TypeIntrospectionConstants.KIND_ERROR,
                description=f"Error introspecting type: {str(e)}",
                fields=[],
                interfaces=[],
                possible_types=[],
                enum_values=[]
            )
            return TypeIntrospectionResult(
                type_info=error_type
            )

    def _extract_type_info(self, type_def) -> TypeInfo:
        """Extract structured information from a GraphQL type definition."""
        kind = self._determine_type_kind(type_def)
        
        # Extract fields for object and interface types
        fields = self._extract_fields(type_def)
        
        # Extract interfaces for object types
        interfaces = self._extract_interfaces(type_def)
        
        # Extract possible types for union and interface types
        possible_types = self._extract_possible_types(type_def)
        
        # Extract enum values for enum types
        enum_values = self._extract_enum_values(type_def)
        
        # Enhance description with healthcare context if applicable
        enhanced_description = self._enhance_description(type_def)
        
        return TypeInfo(
            name=type_def.name,
            kind=kind,
            description=enhanced_description,
            fields=fields,
            interfaces=interfaces,
            possible_types=possible_types,
            enum_values=enum_values
        )
    
    def _determine_type_kind(self, type_def) -> str:
        """Determine the GraphQL type kind."""
        class_name = type_def.__class__.__name__
        
        if 'Object' in class_name:
            return TypeIntrospectionConstants.KIND_OBJECT
        elif 'Interface' in class_name:
            return TypeIntrospectionConstants.KIND_INTERFACE
        elif 'Union' in class_name:
            return TypeIntrospectionConstants.KIND_UNION
        elif 'Enum' in class_name:
            return TypeIntrospectionConstants.KIND_ENUM
        elif 'InputObject' in class_name:
            return TypeIntrospectionConstants.KIND_INPUT_OBJECT
        elif 'Scalar' in class_name:
            return TypeIntrospectionConstants.KIND_SCALAR
        else:
            return class_name.replace('GraphQL', '').replace('Type', '').upper()
    
    def _extract_fields(self, type_def) -> List[FieldInfo]:
        """Extract field information from a type definition."""
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
        
        return fields
    
    def _extract_interfaces(self, type_def) -> List[str]:
        """Extract interface names from an object type."""
        interfaces = []
        
        if isinstance(type_def, GraphQLObjectType) and type_def.interfaces:
            interfaces = [interface.name for interface in type_def.interfaces]
        
        return interfaces
    
    def _extract_possible_types(self, type_def) -> List[str]:
        """Extract possible types for union and interface types."""
        possible_types = []
        
        if isinstance(type_def, GraphQLUnionType):
            possible_types = [t.name for t in type_def.types]
        elif isinstance(type_def, GraphQLInterfaceType):
            # For interfaces, we would need to search the entire schema
            # to find implementing types. This is more complex and may
            # not be necessary for most use cases.
            pass
        
        return possible_types
    
    def _extract_enum_values(self, type_def) -> List[EnumValue]:
        """Extract enum values from an enum type."""
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
        
        return enum_values
    
    def _enhance_description(self, type_def) -> str:
        """Enhance type description with healthcare context and patterns."""
        base_description = type_def.description or ""
        type_name = type_def.name
        
        # Add healthcare context if applicable
        healthcare_context = self._get_healthcare_context(type_name)
        if healthcare_context:
            if base_description:
                return f"{base_description}\n\nHealthcare Context: {healthcare_context}"
            else:
                return f"Healthcare Context: {healthcare_context}"
        
        # Add type pattern information
        pattern_info = self._get_type_pattern_info(type_name)
        if pattern_info:
            if base_description:
                return f"{base_description}\n\nType Pattern: {pattern_info}"
            else:
                return f"Type Pattern: {pattern_info}"
        
        return base_description
    
    def _get_healthcare_context(self, type_name: str) -> Optional[str]:
        """Get healthcare context for a type name."""
        type_name_lower = type_name.lower()
        
        for category, type_names in TypeIntrospectionConstants.HEALTHCARE_TYPES.items():
            if any(ht_name.lower() in type_name_lower for ht_name in type_names):
                contexts = {
                    'patient': "Represents patient/client data in the healthcare system. Contains PHI and requires HIPAA compliance.",
                    'provider': "Represents healthcare providers, practitioners, or doctors. Important for care delivery and patient matching.",
                    'appointment': "Represents scheduling and appointment data. Essential for care coordination and patient flow.",
                    'clinical': "Represents clinical documentation and patient care data. Highly sensitive PHI requiring careful handling.",
                    'billing': "Represents financial and billing information. Important for revenue cycle management.",
                    'insurance': "Represents insurance and coverage information. Critical for billing and authorization processes."
                }
                return contexts.get(category)
        
        return None
    
    def _get_type_pattern_info(self, type_name: str) -> Optional[str]:
        """Get type pattern information based on naming conventions."""
        for suffix, description in TypeIntrospectionConstants.TYPE_SUFFIXES.items():
            if type_name.endswith(suffix):
                return description
        
        if type_name in TypeIntrospectionConstants.SCALAR_TYPES:
            return "GraphQL Scalar Type"
        
        return None


def setup_type_introspection_tool(mcp: FastMCP, schema_manager) -> None:
    """Setup the type introspection tool with the MCP server."""
    tool = TypeIntrospectionTool(schema_manager)
    
    @mcp.tool()
    def introspect_type(type_name: str) -> dict:
        """Get detailed information about a specific GraphQL type.
        
        This tool provides comprehensive information about GraphQL types including
        fields, relationships, and metadata. Useful for understanding the structure
        and capabilities of types in the Healthie API.
        
        Args:
            type_name: The name of the GraphQL type to introspect (e.g., "User", "Patient", "Appointment")
            
        Returns:
            TypeIntrospectionResult with structured type information
        """
        input_data = TypeIntrospectionInput(type_name=type_name)
        result = tool.execute(input_data)
        return result.model_dump()