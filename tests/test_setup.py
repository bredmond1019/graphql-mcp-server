"""
Test module to verify the basic project setup and test configuration.

This module contains simple tests to ensure that the testing infrastructure
is properly configured and working correctly.
"""

import pytest
from healthie_mcp import main


@pytest.mark.unit
def test_main_function_exists():
    """Test that the main function exists and is callable."""
    assert callable(main)


@pytest.mark.unit
def test_main_function_runs_without_error(capsys):
    """Test that the main function runs without throwing an error."""
    main()
    captured = capsys.readouterr()
    assert "Hello from healthie-mcp!" in captured.out


@pytest.mark.unit
def test_pytest_markers_are_configured():
    """Test that custom pytest markers are properly configured."""
    # This test will pass if markers are configured correctly
    # and fail if --strict-markers is enabled but markers are not defined
    pass


@pytest.mark.unit
async def test_async_testing_works():
    """Test that async testing is properly configured."""
    # Simple async test to verify pytest-asyncio is working
    result = await async_helper_function()
    assert result == "async works"


async def async_helper_function():
    """Helper function to test async functionality."""
    return "async works"


@pytest.mark.unit
def test_fixtures_are_available(sample_graphql_schema, mock_config):
    """Test that shared fixtures are available and working."""
    assert sample_graphql_schema is not None
    assert "data" in sample_graphql_schema
    assert mock_config.api_url == "https://api.gethealthie.com/graphql"


@pytest.mark.unit
class TestProjectStructure:
    """Test class to verify project structure and imports."""

    def test_package_imports(self):
        """Test that the package can be imported successfully."""
        import healthie_mcp
        assert hasattr(healthie_mcp, 'main')

    def test_package_structure(self):
        """Test that the expected package structure exists."""
        # This test ensures that our package is properly structured
        # for the TDD development process
        try:
            import healthie_mcp
            assert True  # Import successful
        except ImportError as e:
            pytest.fail(f"Package import failed: {e}")


@pytest.mark.slow
def test_slow_test_marker():
    """Test that demonstrates the slow test marker."""
    import time
    # Simulate a slow operation
    time.sleep(0.1)
    assert True