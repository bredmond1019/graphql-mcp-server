"""Unit tests for input validation helper tool functionality - simplified version."""

import pytest
from unittest.mock import Mock, MagicMock
from healthie_mcp.tools.input_validation import setup_input_validation_tool
from healthie_mcp.schema_manager import SchemaManager
from healthie_mcp.models.external_dev_tools import (
    InputValidationResult, ValidationIssue
)


class TestInputValidationHelperSimple:
    """Simplified test suite for input validation helper tool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_schema_manager = Mock(spec=SchemaManager)
        self.mock_mcp = MagicMock()
        self.registered_tools = {}
        
        # Mock the tool decorator to capture registered functions
        def mock_tool():
            def decorator(func):
                self.registered_tools[func.__name__] = func
                return func
            return decorator
        
        self.mock_mcp.tool = mock_tool
        
        # Simple schema for testing
        self.simple_schema = """
type Mutation {
    createUser(input: CreateUserInput!): User!
    updateUser(id: ID!, name: String): User!
    deleteUser(id: ID!): Boolean!
}

input CreateUserInput {
    name: String!
    email: String!
}
"""

    def test_setup_registers_function(self):
        """Test that setup registers the validation function."""
        setup_input_validation_tool(self.mock_mcp, self.mock_schema_manager)
        
        assert 'validate_mutation_input' in self.registered_tools
        assert callable(self.registered_tools['validate_mutation_input'])

    def test_returns_structured_result(self):
        """Test that validation returns InputValidationResult."""
        self.mock_schema_manager.get_schema_content.return_value = self.simple_schema
        
        setup_input_validation_tool(self.mock_mcp, self.mock_schema_manager)
        func = self.registered_tools['validate_mutation_input']
        
        result = func(
            mutation_name="createUser",
            input_data={"input": {"name": "John", "email": "john@example.com"}}
        )
        
        assert isinstance(result, InputValidationResult)
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'issues')

    def test_validate_missing_required_argument(self):
        """Test validation when required argument is missing."""
        self.mock_schema_manager.get_schema_content.return_value = self.simple_schema
        
        setup_input_validation_tool(self.mock_mcp, self.mock_schema_manager)
        func = self.registered_tools['validate_mutation_input']
        
        # Missing required 'input' argument
        result = func(
            mutation_name="createUser",
            input_data={}
        )
        
        assert not result.is_valid
        assert result.total_errors > 0
        
        # Should have error about missing input
        input_errors = [i for i in result.issues if i.field_path == "input"]
        assert len(input_errors) > 0
        assert input_errors[0].issue_type == "required"

    def test_validate_valid_input(self):
        """Test validation with valid input."""
        self.mock_schema_manager.get_schema_content.return_value = self.simple_schema
        
        setup_input_validation_tool(self.mock_mcp, self.mock_schema_manager)
        func = self.registered_tools['validate_mutation_input']
        
        # Valid input
        result = func(
            mutation_name="createUser",
            input_data={"input": {"name": "John", "email": "john@example.com"}}
        )
        
        assert result.is_valid
        assert result.total_errors == 0

    def test_validate_optional_arguments(self):
        """Test that optional arguments don't cause errors."""
        self.mock_schema_manager.get_schema_content.return_value = self.simple_schema
        
        setup_input_validation_tool(self.mock_mcp, self.mock_schema_manager)
        func = self.registered_tools['validate_mutation_input']
        
        # updateUser has optional 'name' argument
        result = func(
            mutation_name="updateUser",
            input_data={"id": "123"}  # name is optional
        )
        
        assert result.is_valid
        assert result.total_errors == 0

    def test_validate_unknown_arguments(self):
        """Test validation with unknown arguments."""
        self.mock_schema_manager.get_schema_content.return_value = self.simple_schema
        
        setup_input_validation_tool(self.mock_mcp, self.mock_schema_manager)
        func = self.registered_tools['validate_mutation_input']
        
        # Include unknown argument
        result = func(
            mutation_name="deleteUser",
            input_data={"id": "123", "unknownArg": "value"}
        )
        
        # Should warn about unknown argument
        assert result.is_valid  # Still valid
        assert result.total_warnings > 0
        
        unknown_issues = [i for i in result.issues if i.field_path == "unknownArg"]
        assert len(unknown_issues) > 0
        assert unknown_issues[0].severity == "warning"

    def test_mutation_not_found(self):
        """Test when mutation doesn't exist."""
        self.mock_schema_manager.get_schema_content.return_value = self.simple_schema
        
        setup_input_validation_tool(self.mock_mcp, self.mock_schema_manager)
        func = self.registered_tools['validate_mutation_input']
        
        result = func(
            mutation_name="nonExistentMutation",
            input_data={}
        )
        
        assert not result.is_valid
        assert result.error is not None
        assert "not found" in result.error.lower()

    def test_schema_not_available(self):
        """Test when schema is not available."""
        self.mock_schema_manager.get_schema_content.return_value = None
        
        setup_input_validation_tool(self.mock_mcp, self.mock_schema_manager)
        func = self.registered_tools['validate_mutation_input']
        
        result = func(
            mutation_name="createUser",
            input_data={}
        )
        
        assert not result.is_valid
        assert result.error is not None
        assert "schema not available" in result.error.lower()