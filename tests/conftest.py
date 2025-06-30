"""
Pytest configuration and shared fixtures for Healthie MCP Server tests.

This module contains pytest configuration, shared fixtures, and test utilities
that are used across multiple test modules.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any, AsyncGenerator
import asyncio


@pytest.fixture
def sample_graphql_schema() -> Dict[str, Any]:
    """Provides a sample GraphQL schema for testing."""
    return {
        "data": {
            "__schema": {
                "types": [
                    {
                        "name": "Query",
                        "kind": "OBJECT",
                        "fields": [
                            {
                                "name": "patients",
                                "type": {"name": "Patient", "kind": "OBJECT"},
                                "description": "Get patients"
                            }
                        ]
                    },
                    {
                        "name": "Patient",
                        "kind": "OBJECT",
                        "fields": [
                            {
                                "name": "id",
                                "type": {"name": "ID", "kind": "SCALAR"},
                                "description": "Patient ID"
                            },
                            {
                                "name": "name",
                                "type": {"name": "String", "kind": "SCALAR"},
                                "description": "Patient name"
                            }
                        ]
                    }
                ]
            }
        }
    }


@pytest.fixture
def sample_graphql_response() -> Dict[str, Any]:
    """Provides a sample GraphQL response for testing."""
    return {
        "data": {
            "patients": [
                {"id": "1", "name": "John Doe"},
                {"id": "2", "name": "Jane Smith"}
            ]
        }
    }


@pytest.fixture
def mock_httpx_client():
    """Provides a mocked HTTPX client for testing."""
    client = AsyncMock()
    client.post = AsyncMock()
    client.get = AsyncMock()
    return client


@pytest.fixture
def mock_config():
    """Provides a mock configuration object for testing."""
    config = Mock()
    config.api_url = "https://api.gethealthie.com/graphql"
    config.api_token = "test_token"
    config.timeout = 30
    config.max_retries = 3
    return config


@pytest.fixture
async def event_loop() -> AsyncGenerator[asyncio.AbstractEventLoop, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Test markers for better test organization
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_api: mark test as requiring external API access"
    )
    config.addinivalue_line(
        "markers", "requires_auth: mark test as requiring authentication"
    )