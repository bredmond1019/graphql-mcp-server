"""Unit tests for type introspection MCP tool functionality."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

# Mock the MCP module before importing our modules
sys.modules['mcp'] = MagicMock()
sys.modules['mcp.server'] = MagicMock()
sys.modules['mcp.server.fastmcp'] = MagicMock()

import pytest
from healthie_mcp.tools.type_introspection import setup_type_introspection_tool
from healthie_mcp.models.type_introspection import TypeIntrospectionResult, TypeInfo, FieldInfo, EnumValue


class TestTypeIntrospectionTool:
    """Test suite for type introspection MCP tool functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_schema_manager = Mock()
        self.mock_mcp = MagicMock()
        self.registered_tools = {}
        
        # Mock the tool decorator to capture registered functions
        def mock_tool():
            def decorator(func):
                self.registered_tools[func.__name__] = func
                return func
            return decorator
        
        self.mock_mcp.tool = mock_tool

    def test_introspect_type_tool_is_registered(self):
        """Test that introspect_type tool is registered in the MCP server."""
        setup_type_introspection_tool(self.mock_mcp, self.mock_schema_manager)
        
        assert 'introspect_type' in self.registered_tools
        assert callable(self.registered_tools['introspect_type'])

    def test_introspect_specific_graphql_type_user(self):
        """Test introspecting a specific GraphQL type like 'User'."""
        # Mock GraphQL schema content with User type
        mock_schema_content = """
        scalar DateTime
        
        interface Node {
          id: ID!
        }
        
        type Query {
          user: User
        }
        
        type User implements Node {
          id: ID!
          name: String!
          email: String!
          role: UserRole!
          "The organization this user belongs to"
          organization: Organization
          createdAt: DateTime!
          updatedAt: DateTime!
        }
        
        type Organization {
          id: ID!
          name: String!
        }
        
        enum UserRole {
          ADMIN
          PROVIDER
          PATIENT
          STAFF
        }
        """
        
        self.mock_schema_manager.get_schema_content.return_value = mock_schema_content
        setup_type_introspection_tool(self.mock_mcp, self.mock_schema_manager)
        introspect_tool = self.registered_tools['introspect_type']
        
        result = introspect_tool(type_name="User")
        
        # Test structured output using Pydantic models
        assert isinstance(result, TypeIntrospectionResult)
        
        type_info = result.type_info
        assert isinstance(type_info, TypeInfo)
        
        # Check TypeInfo structure
        assert type_info.name == 'User'
        assert type_info.kind == 'OBJECT'
        assert len(type_info.fields) > 0
        assert 'Node' in type_info.interfaces
        
        # Check FieldInfo structures
        fields = type_info.fields
        
        # Find a specific field to test
        id_field = next((f for f in fields if f.name == 'id'), None)
        assert id_field is not None
        assert id_field.type == 'ID!'
        
        # Check for field with description
        org_field = next((f for f in fields if f.name == 'organization'), None)
        assert org_field is not None
        assert org_field.description == 'The organization this user belongs to'

    def test_introspect_specific_graphql_type_patient(self):
        """Test introspecting a specific GraphQL type like 'Patient'."""
        mock_schema_content = """
        scalar DateTime
        scalar Date
        
        type Query {
          patient: Patient
        }
        
        type Patient {
          id: ID!
          name: String!
          email: String
          phone: String
          dateOfBirth: Date
          organization: Organization!
          createdAt: DateTime!
          updatedAt: DateTime!
        }
        
        type Organization {
          id: ID!
          name: String!
        }
        """
        
        self.mock_schema_manager.get_schema_content.return_value = mock_schema_content
        setup_type_introspection_tool(self.mock_mcp, self.mock_schema_manager)
        introspect_tool = self.registered_tools['introspect_type']
        
        result = introspect_tool(type_name="Patient")
        
        assert isinstance(result, TypeIntrospectionResult)
        type_info = result.type_info
        assert type_info.name == 'Patient'
        assert type_info.kind == 'OBJECT'
        assert len(type_info.fields) >= 8  # All fields should be present

    def test_structured_output_pydantic_models(self):
        """Test that results use structured Pydantic models for type safety."""
        mock_schema_content = """
        type Query {
          test: TestType
        }
        
        type TestType {
          requiredField: String!
          optionalField: String
          intField: Int
          floatField: Float
          boolField: Boolean
        }
        """
        
        self.mock_schema_manager.get_schema_content.return_value = mock_schema_content
        setup_type_introspection_tool(self.mock_mcp, self.mock_schema_manager)
        introspect_tool = self.registered_tools['introspect_type']
        
        result = introspect_tool(type_name="TestType")
        
        # Verify the structure matches our expected Pydantic models
        assert isinstance(result, TypeIntrospectionResult)
        assert isinstance(result.type_info, TypeInfo)
        
        type_info = result.type_info
        # TypeInfo model fields
        assert hasattr(type_info, 'name')
        assert hasattr(type_info, 'kind')
        assert hasattr(type_info, 'description')
        assert hasattr(type_info, 'fields')
        assert hasattr(type_info, 'interfaces')
        
        # FieldInfo model fields
        for field in type_info.fields:
            assert isinstance(field, FieldInfo)
            assert hasattr(field, 'name')
            assert hasattr(field, 'type')
            assert hasattr(field, 'description')
            assert hasattr(field, 'deprecated')

    def test_error_handling_nonexistent_types(self):
        """Test error handling for non-existent types."""
        mock_schema_content = """
        type Query {
          user: User
        }
        
        type User {
          id: ID!
          name: String!
        }
        """
        
        self.mock_schema_manager.get_schema_content.return_value = mock_schema_content
        setup_type_introspection_tool(self.mock_mcp, self.mock_schema_manager)
        introspect_tool = self.registered_tools['introspect_type']
        
        result = introspect_tool(type_name="NonExistentType")
        
        assert isinstance(result, TypeIntrospectionResult)
        assert result.type_info.kind == "ERROR"
        assert 'not found' in result.type_info.description.lower()

    def test_results_include_field_types_descriptions_deprecation(self):
        """Test that results include field types, descriptions, and deprecation info."""
        mock_schema_content = """
        type Query {
          complex: ComplexType
        }
        
        type ComplexType {
          "The unique identifier"
          id: ID!
          "User's display name"
          name: String!
          "Deprecated field - use name instead"
          title: String @deprecated(reason: "Use name field instead")
          "Optional description field"
          description: String
          "Required numeric field"
          count: Int!
        }
        """
        
        self.mock_schema_manager.get_schema_content.return_value = mock_schema_content
        setup_type_introspection_tool(self.mock_mcp, self.mock_schema_manager)
        introspect_tool = self.registered_tools['introspect_type']
        
        result = introspect_tool(type_name="ComplexType")
        
        type_info = result.type_info
        fields = type_info.fields
        
        # Check field types are captured
        id_field = next((f for f in fields if f.name == 'id'), None)
        assert id_field.type == 'ID!'
        
        name_field = next((f for f in fields if f.name == 'name'), None)
        assert name_field.type == 'String!'
        
        count_field = next((f for f in fields if f.name == 'count'), None)
        assert count_field.type == 'Int!'
        
        # Check descriptions are captured
        assert id_field.description == 'The unique identifier'
        assert name_field.description == "User's display name"
        
        # Check deprecation info
        title_field = next((f for f in fields if f.name == 'title'), None)
        assert title_field is not None
        assert title_field.deprecated is True
        assert 'Use name field instead' in title_field.deprecation_reason

    def test_interface_and_union_type_handling(self):
        """Test interface and union type handling."""
        # Test interface type
        mock_interface_schema = """
        type Query {
          user: User
        }
        
        interface Node {
          id: ID!
        }
        
        type User implements Node {
          id: ID!
          name: String!
        }
        """
        
        self.mock_schema_manager.get_schema_content.return_value = mock_interface_schema
        setup_type_introspection_tool(self.mock_mcp, self.mock_schema_manager)
        introspect_tool = self.registered_tools['introspect_type']
        
        result = introspect_tool(type_name="Node")
        
        type_info = result.type_info
        assert type_info.kind == 'INTERFACE'
        assert len(type_info.fields) >= 1
        
        # Test that implementing types are included
        user_result = introspect_tool(type_name="User")
        user_info = user_result.type_info
        assert 'Node' in user_info.interfaces
        
        # Test union type
        mock_union_schema = """
        type Query {
          search: SearchResult
        }
        
        union SearchResult = User | Patient | Organization
        
        type User {
          id: ID!
          name: String!
        }
        
        type Patient {
          id: ID!
          name: String!
        }
        
        type Organization {
          id: ID!
          name: String!
        }
        """
        
        self.mock_schema_manager.get_schema_content.return_value = mock_union_schema
        setup_type_introspection_tool(self.mock_mcp, self.mock_schema_manager)
        introspect_tool = self.registered_tools['introspect_type']
        
        result = introspect_tool(type_name="SearchResult")
        
        type_info = result.type_info
        assert type_info.kind == 'UNION'
        assert len(type_info.possible_types) > 0
        assert 'User' in type_info.possible_types
        assert 'Patient' in type_info.possible_types
        assert 'Organization' in type_info.possible_types

    def test_enum_value_introspection(self):
        """Test enum value introspection."""
        mock_schema_content = """
        type Query {
          testEnum: UserRole
        }
        
        enum UserRole {
          "Administrator with full access"
          ADMIN
          "Healthcare provider"
          PROVIDER
          "Patient user"  
          PATIENT
          "Staff member"
          STAFF
          "Deprecated role - use STAFF instead"
          ASSISTANT @deprecated(reason: "Use STAFF role instead")
        }
        """
        
        self.mock_schema_manager.get_schema_content.return_value = mock_schema_content
        setup_type_introspection_tool(self.mock_mcp, self.mock_schema_manager)
        introspect_tool = self.registered_tools['introspect_type']
        
        result = introspect_tool(type_name="UserRole")
        
        type_info = result.type_info
        assert type_info.kind == 'ENUM'
        assert len(type_info.enum_values) == 5
        
        # Check enum value structure
        admin_value = next((v for v in type_info.enum_values if v.name == 'ADMIN'), None)
        assert admin_value is not None
        assert isinstance(admin_value, EnumValue)
        assert admin_value.description == 'Administrator with full access'
        assert admin_value.deprecated is False
        
        # Check deprecated enum value
        assistant_value = next((v for v in type_info.enum_values if v.name == 'ASSISTANT'), None)
        assert assistant_value is not None
        assert assistant_value.deprecated is True
        assert 'Use STAFF role instead' in assistant_value.deprecation_reason