"""Pydantic models for type introspection structured output."""

from typing import List, Optional, Union, Any
from pydantic import BaseModel, Field


class EnumValue(BaseModel):
    """Model representing a GraphQL enum value."""
    
    name: str = Field(..., description="Name of the enum value")
    description: Optional[str] = Field(None, description="Description of the enum value")
    deprecated: bool = Field(False, description="Whether this enum value is deprecated")
    deprecation_reason: Optional[str] = Field(None, description="Reason for deprecation if deprecated")


class FieldInfo(BaseModel):
    """Model representing a GraphQL field."""
    
    name: str = Field(..., description="Name of the field")
    type: str = Field(..., description="Type of the field (e.g., 'String!', 'ID', '[User!]!')")
    description: Optional[str] = Field(None, description="Description of the field")
    required: bool = Field(False, description="Whether this field is required (non-null)")
    deprecated: bool = Field(False, description="Whether this field is deprecated")
    deprecation_reason: Optional[str] = Field(None, description="Reason for deprecation if deprecated")
    arguments: Optional[List[dict]] = Field(default_factory=list, description="Field arguments if any")


class TypeInfo(BaseModel):
    """Model representing GraphQL type information."""
    
    name: str = Field(..., description="Name of the GraphQL type")
    kind: str = Field(..., description="Kind of type (OBJECT, INTERFACE, UNION, ENUM, SCALAR, INPUT_OBJECT)")
    description: Optional[str] = Field(None, description="Description of the type")
    fields: List[FieldInfo] = Field(default_factory=list, description="Fields of the type (for objects and interfaces)")
    interfaces: List[str] = Field(default_factory=list, description="Interfaces implemented by this type")
    union_types: List[str] = Field(default_factory=list, description="Types in the union (for union types)")
    enum_values: List[EnumValue] = Field(default_factory=list, description="Enum values (for enum types)")
    possible_types: List[str] = Field(default_factory=list, description="Possible types (for interfaces and unions)")


class TypeIntrospectionResult(BaseModel):
    """Result model for type introspection operations."""
    
    type_info: Optional[TypeInfo] = Field(None, description="The introspected type information")
    error: Optional[str] = Field(None, description="Error message if introspection failed")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            # Add any custom encoders if needed
        }