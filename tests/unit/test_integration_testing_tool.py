"""Unit tests for integration testing MCP tool functionality."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

# Mock the MCP module before importing our modules
sys.modules['mcp'] = MagicMock()
sys.modules['mcp.server'] = MagicMock()
sys.modules['mcp.server.fastmcp'] = MagicMock()

from healthie_mcp.models.integration_testing import (
    IntegrationTestInput, IntegrationTestingResult, IntegrationTestReport,
    TestResult, TestCategory, TestSeverity
)


class TestIntegrationTestingTool:
    """Test suite for integration testing MCP tool functionality."""

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

    def test_integration_testing_validates_auth_setup(self):
        """Test that integration testing validates authentication setup."""
        # Import the setup function (this will fail initially)
        from healthie_mcp.tools.integration_testing import setup_integration_testing_tool
        
        # Setup the tool
        setup_integration_testing_tool(self.mock_mcp, self.mock_schema_manager)
        
        # Get the registered function
        assert 'integration_testing' in self.registered_tools
        test_func = self.registered_tools['integration_testing']
        
        # Test input for authentication validation
        test_input = IntegrationTestInput(
            environment="staging",
            auth_method="api_key",
            test_mutations=False,
            test_categories=[TestCategory.AUTHENTICATION]
        )
        
        # Mock environment without API key
        with patch.dict('os.environ', {}, clear=True):
            result = test_func(**test_input.model_dump())
            
            # Should return error about missing API key
            assert isinstance(result, IntegrationTestingResult)
            assert result.error is not None
            assert "API key" in result.error or "authentication" in result.error.lower()

    def test_integration_testing_basic_query_execution(self):
        """Test that integration testing can execute basic queries."""
        from healthie_mcp.tools.integration_testing import setup_integration_testing_tool
        
        setup_integration_testing_tool(self.mock_mcp, self.mock_schema_manager)
        test_func = self.registered_tools['integration_testing']
        
        test_input = IntegrationTestInput(
            environment="staging",
            auth_method="api_key",
            test_mutations=False,
            test_categories=[TestCategory.QUERIES]
        )
        
        # Mock successful API key validation
        with patch.dict('os.environ', {'HEALTHIE_API_KEY': 'test_key'}):
            with patch('httpx.Client') as mock_client:
                # Mock successful query response
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'data': {'__schema': {'types': []}}
                }
                mock_client.return_value.__enter__.return_value.post.return_value = mock_response
                
                result = test_func(**test_input.model_dump())
                
                assert isinstance(result, IntegrationTestingResult)
                assert result.error is None
                assert result.report is not None
                assert result.report.total_tests > 0

    def test_integration_testing_mutation_safety_checks(self):
        """Test that integration testing handles mutation safety properly."""
        from healthie_mcp.tools.integration_testing import setup_integration_testing_tool
        
        setup_integration_testing_tool(self.mock_mcp, self.mock_schema_manager)
        test_func = self.registered_tools['integration_testing']
        
        test_input = IntegrationTestInput(
            environment="production",  # Production environment
            auth_method="api_key",
            test_mutations=True,  # Requesting mutations in production
            test_categories=[TestCategory.MUTATIONS]
        )
        
        with patch.dict('os.environ', {'HEALTHIE_API_KEY': 'test_key'}):
            result = test_func(**test_input.model_dump())
            
            # Should either skip mutations in production or add safety warnings
            assert isinstance(result, IntegrationTestingResult)
            
            if result.error is None:
                # If no error, should have warnings about production mutations
                mutation_results = [r for r in result.report.test_results 
                                  if r.category == TestCategory.MUTATIONS]
                if mutation_results:
                    has_warnings = any(r.severity == TestSeverity.WARNING for r in mutation_results)
                    assert has_warnings, "Should have warnings about production mutations"

    def test_integration_testing_error_handling_validation(self):
        """Test that integration testing properly handles and reports errors."""
        from healthie_mcp.tools.integration_testing import setup_integration_testing_tool
        
        setup_integration_testing_tool(self.mock_mcp, self.mock_schema_manager)
        test_func = self.registered_tools['integration_testing']
        
        test_input = IntegrationTestInput(
            environment="staging",
            auth_method="api_key",
            test_categories=[TestCategory.ERROR_HANDLING]
        )
        
        with patch.dict('os.environ', {'HEALTHIE_API_KEY': 'test_key'}):
            with patch('httpx.Client') as mock_client:
                # Mock API error response
                mock_response = Mock()
                mock_response.status_code = 400
                mock_response.json.return_value = {
                    'errors': [{'message': 'Invalid query'}]
                }
                mock_client.return_value.__enter__.return_value.post.return_value = mock_response
                
                result = test_func(**test_input.model_dump())
                
                assert isinstance(result, IntegrationTestingResult)
                assert result.error is None  # Tool should handle API errors gracefully
                assert result.report is not None
                
                # Should have error handling test results
                error_tests = [r for r in result.report.test_results 
                              if r.category == TestCategory.ERROR_HANDLING]
                assert len(error_tests) > 0

    def test_integration_testing_performance_measurement(self):
        """Test that integration testing measures and reports performance."""
        from healthie_mcp.tools.integration_testing import setup_integration_testing_tool
        
        setup_integration_testing_tool(self.mock_mcp, self.mock_schema_manager)
        test_func = self.registered_tools['integration_testing']
        
        test_input = IntegrationTestInput(
            environment="staging",
            auth_method="api_key",
            test_categories=[TestCategory.PERFORMANCE]
        )
        
        with patch.dict('os.environ', {'HEALTHIE_API_KEY': 'test_key'}):
            with patch('httpx.Client') as mock_client:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {'data': {}}
                mock_client.return_value.__enter__.return_value.post.return_value = mock_response
                
                result = test_func(**test_input.model_dump())
                
                assert isinstance(result, IntegrationTestingResult)
                assert result.error is None
                assert result.report.execution_time_seconds > 0
                
                # Should have performance measurements
                perf_tests = [r for r in result.report.test_results 
                             if r.category == TestCategory.PERFORMANCE]
                if perf_tests:
                    assert any(r.execution_time_ms is not None for r in perf_tests)