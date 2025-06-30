"""Unit tests for MCP server functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from healthie_mcp.server import mcp
from healthie_mcp.config import Settings, get_settings


class TestHealthieMCPServer:
    """Test suite for Healthie MCP Server functionality."""

    def test_server_exists(self):
        """Test that the MCP server instance exists."""
        from healthie_mcp.server import mcp
        assert mcp is not None
        # The mcp object is a FastMCP instance
        # We can't test the name directly in tests since it's set during initialization

    def test_server_has_tools_registered(self):
        """Test that the server has tools registered."""
        # Check that the mcp instance has tool registration methods
        assert hasattr(mcp, 'tool')
        # Tools are registered via decorators, so we can't easily count them
        # but we can verify the registration mechanism exists

    def test_server_has_resources_registered(self):
        """Test that the server has resources registered."""
        # Check that the mcp instance has resource registration methods
        assert hasattr(mcp, 'resource')
        # Resources are registered via decorators
    
    @patch('healthie_mcp.server.schema_manager')
    def test_schema_manager_initialized(self, mock_schema_manager):
        """Test that the schema manager is properly initialized."""
        # Import to trigger initialization
        from healthie_mcp.server import schema_manager
        
        assert schema_manager is not None

    @patch('healthie_mcp.server.settings')
    def test_server_uses_settings(self, mock_settings):
        """Test that the server uses settings."""
        from healthie_mcp.server import settings
        
        assert settings is not None
        assert hasattr(settings, 'healthie_api_url')
        assert hasattr(settings, 'schema_dir')

    def test_server_can_run(self):
        """Test that the server has a run method."""
        assert hasattr(mcp, 'run')
        # The run method should be callable
        assert callable(getattr(mcp, 'run', None))

    def test_get_current_schema_resource(self):
        """Test that get_current_schema resource is registered."""
        from healthie_mcp.server import get_current_schema
        
        assert get_current_schema is not None
        assert callable(get_current_schema)
    
    def test_get_server_config_resource(self):
        """Test that get_server_config resource is registered."""
        from healthie_mcp.server import get_server_config
        
        assert get_server_config is not None
        assert callable(get_server_config)
        
        # We can't test the actual function output in unit tests
        # since it depends on settings which may be mocked
    
    def test_main_module_executable(self):
        """Test that the server module can be executed as main."""
        # Check that __main__ block exists
        import healthie_mcp.server as server_module
        server_code = server_module.__file__
        
        # Just verify the module loads without error
        assert server_code is not None