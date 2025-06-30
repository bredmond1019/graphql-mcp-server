"""Unit tests for schema search MCP tool functionality."""

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
from healthie_mcp.tools.schema_search import setup_schema_search_tool
from healthie_mcp.schema_manager import SchemaManager
from healthie_mcp.models.schema_search import SchemaSearchResult, SchemaMatch


class TestSchemaSearchTool:
    """Test suite for schema search MCP tool functionality."""

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
        
        # Sample schema content for testing
        self.sample_schema = """
type User {
    id: ID!
    firstName: String!
    lastName: String!
    email: String!
    phone: String
    appointments: [Appointment!]!
}

type Appointment {
    id: ID!
    startTime: DateTime!
    endTime: DateTime!
    client: User!
    provider: Provider!
    status: AppointmentStatus!
}

type Provider {
    id: ID!
    name: String!
    specialty: String
    license: String!
}

enum AppointmentStatus {
    SCHEDULED
    COMPLETED
    CANCELLED
    NO_SHOW
}

type Query {
    user(id: ID!): User
    appointment(id: ID!): Appointment
    searchUsers(term: String!): [User!]!
}

type Mutation {
    createUser(input: CreateUserInput!): CreateUserPayload!
    updateAppointment(id: ID!, input: UpdateAppointmentInput!): Appointment!
}
"""

    def test_setup_schema_search_tool_registers_function(self):
        """Test that setup_schema_search_tool registers the search function."""
        setup_schema_search_tool(self.mock_mcp, self.mock_schema_manager)
        
        assert 'search_schema' in self.registered_tools
        assert callable(self.registered_tools['search_schema'])

    def test_search_schema_basic_search(self):
        """Test basic schema search functionality."""
        self.mock_schema_manager.get_schema_content.return_value = self.sample_schema
        
        setup_schema_search_tool(self.mock_mcp, self.mock_schema_manager)
        search_func = self.registered_tools['search_schema']
        
        # Search for "User"
        result = search_func(query="User", type_filter="any", context_lines=2)
        
        assert isinstance(result, SchemaSearchResult)
        assert result.total_matches > 0
        assert len(result.matches) > 0
        
        # Check that we found User type matches
        user_matches = [m for m in result.matches if "type User" in m.content]
        assert len(user_matches) > 0

    def test_search_schema_case_insensitive(self):
        """Test that search is case-insensitive by default."""
        self.mock_schema_manager.get_schema_content.return_value = self.sample_schema
        
        setup_schema_search_tool(self.mock_mcp, self.mock_schema_manager)
        search_func = self.registered_tools['search_schema']
        
        # Search for "user" (lowercase) should find "User" type
        result = search_func(query="user", type_filter="any", context_lines=1)
        
        assert result.total_matches > 0
        user_type_found = any("type User" in m.content for m in result.matches)
        assert user_type_found

    def test_search_schema_type_filter(self):
        """Test schema search with type filtering."""
        self.mock_schema_manager.get_schema_content.return_value = self.sample_schema
        
        setup_schema_search_tool(self.mock_mcp, self.mock_schema_manager)
        search_func = self.registered_tools['search_schema']
        
        # Search only in queries
        query_result = search_func(query="user", type_filter="query", context_lines=1)
        assert all("Query" in m.content or m.location == "Query" for m in query_result.matches)
        
        # Search only in mutations
        mutation_result = search_func(query="create", type_filter="mutation", context_lines=1)
        assert all("Mutation" in m.content or m.location == "Mutation" for m in mutation_result.matches)
        
        # Search only in types
        type_result = search_func(query="String", type_filter="type", context_lines=0)
        type_matches = [m for m in type_result.matches if m.location in ["User", "Provider"]]
        assert len(type_matches) > 0

    def test_search_schema_enum_filter(self):
        """Test schema search for enum types."""
        self.mock_schema_manager.get_schema_content.return_value = self.sample_schema
        
        setup_schema_search_tool(self.mock_mcp, self.mock_schema_manager)
        search_func = self.registered_tools['search_schema']
        
        # Search for enums
        result = search_func(query="Status", type_filter="enum", context_lines=1)
        
        enum_matches = [m for m in result.matches if "enum" in m.content or m.location == "AppointmentStatus"]
        assert len(enum_matches) > 0

    def test_search_schema_regex_support(self):
        """Test schema search with regex patterns."""
        self.mock_schema_manager.get_schema_content.return_value = self.sample_schema
        
        setup_schema_search_tool(self.mock_mcp, self.mock_schema_manager)
        search_func = self.registered_tools['search_schema']
        
        # Search for fields ending with "Time"
        result = search_func(query=r"\w+Time", type_filter="any", context_lines=0)
        
        time_fields = [m for m in result.matches if "Time" in m.content]
        assert len(time_fields) > 0
        assert any("startTime" in m.content for m in time_fields)
        assert any("endTime" in m.content for m in time_fields)

    def test_search_schema_context_lines(self):
        """Test that context_lines parameter works correctly."""
        self.mock_schema_manager.get_schema_content.return_value = self.sample_schema
        
        setup_schema_search_tool(self.mock_mcp, self.mock_schema_manager)
        search_func = self.registered_tools['search_schema']
        
        # Search with different context sizes
        result_0 = search_func(query="firstName", type_filter="any", context_lines=0)
        result_2 = search_func(query="firstName", type_filter="any", context_lines=2)
        
        # With more context, content should be longer
        assert len(result_2.matches[0].content) > len(result_0.matches[0].content)

    def test_search_schema_no_results(self):
        """Test search that returns no results."""
        self.mock_schema_manager.get_schema_content.return_value = self.sample_schema
        
        setup_schema_search_tool(self.mock_mcp, self.mock_schema_manager)
        search_func = self.registered_tools['search_schema']
        
        # Search for something that doesn't exist
        result = search_func(query="NonExistentType", type_filter="any", context_lines=1)
        
        assert result.total_matches == 0
        assert len(result.matches) == 0
        assert result.error is None

    def test_search_schema_error_handling(self):
        """Test error handling in schema search."""
        # Simulate schema not available
        self.mock_schema_manager.get_schema_content.return_value = None
        
        setup_schema_search_tool(self.mock_mcp, self.mock_schema_manager)
        search_func = self.registered_tools['search_schema']
        
        result = search_func(query="User", type_filter="any", context_lines=1)
        
        assert result.total_matches == 0
        assert len(result.matches) == 0
        assert result.error is not None
        assert "Schema not available" in result.error

    def test_search_schema_empty_query(self):
        """Test search with empty query."""
        self.mock_schema_manager.get_schema_content.return_value = self.sample_schema
        
        setup_schema_search_tool(self.mock_mcp, self.mock_schema_manager)
        search_func = self.registered_tools['search_schema']
        
        # Empty query should return no results
        result = search_func(query="", type_filter="any", context_lines=1)
        
        assert result.total_matches == 0
        assert len(result.matches) == 0

    def test_search_schema_match_structure(self):
        """Test that schema matches have the correct structure."""
        self.mock_schema_manager.get_schema_content.return_value = self.sample_schema
        
        setup_schema_search_tool(self.mock_mcp, self.mock_schema_manager)
        search_func = self.registered_tools['search_schema']
        
        result = search_func(query="email", type_filter="any", context_lines=1)
        
        assert result.total_matches > 0
        
        # Check match structure
        match = result.matches[0]
        assert isinstance(match, SchemaMatch)
        assert hasattr(match, 'line_number')
        assert hasattr(match, 'content')
        assert hasattr(match, 'match_type')
        assert hasattr(match, 'location')
        
        # Verify match data
        assert match.line_number > 0
        assert "email" in match.content.lower()
        assert match.match_type in ["type", "input", "enum", "query", "mutation", "field"]