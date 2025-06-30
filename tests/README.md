# Healthie MCP Server Tests

This directory contains the complete test suite for the Healthie MCP Server project.

## Test Structure

```
tests/
├── README.md                    # This file
├── conftest.py                  # Pytest configuration and shared fixtures
├── test_setup.py               # Basic setup verification tests
├── unit/                       # Unit tests (fast, isolated)
├── integration/                # Integration tests (component interactions)
├── e2e/                        # End-to-end tests (complete workflows)
├── fixtures/                   # Test data and mock responses
│   ├── graphql/               # GraphQL response fixtures
│   ├── schemas/               # GraphQL schema fixtures
│   └── mcp/                   # MCP protocol message fixtures
└── helpers/                    # Test utility functions
    ├── __init__.py
    └── assertion_helpers.py    # Custom assertion functions
```

## Running Tests

### Basic Commands

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Run specific test file
uv run pytest tests/test_setup.py

# Run with verbose output
uv run pytest -v

# Run tests without coverage (faster)
uv run pytest --no-cov
```

### Test Categories

```bash
# Run only unit tests
uv run pytest -m unit

# Run only integration tests
uv run pytest -m integration

# Run only end-to-end tests
uv run pytest -m e2e

# Run only fast tests (exclude slow tests)
uv run pytest -m "not slow"

# Run tests that require API access
uv run pytest -m requires_api

# Run tests that require authentication
uv run pytest -m requires_auth
```

### Development Workflow

```bash
# Run fast tests during development
uv run pytest -m "unit and not slow" --no-cov

# Run all tests before committing
uv run pytest

# Run specific test during TDD
uv run pytest tests/unit/test_config.py::test_config_loads_from_environment -v
```

## Test Markers

The following pytest markers are available:

- `@pytest.mark.unit`: Unit tests that test individual components in isolation
- `@pytest.mark.integration`: Integration tests that test component interactions  
- `@pytest.mark.e2e`: End-to-end tests that test complete workflows
- `@pytest.mark.slow`: Tests that take longer than 1 second to run
- `@pytest.mark.requires_api`: Tests that require access to external APIs
- `@pytest.mark.requires_auth`: Tests that require valid authentication credentials

## Test Fixtures

Common fixtures are available in `conftest.py`:

- `sample_graphql_schema`: Sample GraphQL schema for testing
- `sample_graphql_response`: Sample GraphQL response data
- `mock_httpx_client`: Mocked HTTP client for testing
- `mock_config`: Mock configuration object
- `event_loop`: Async event loop for testing

## Writing Tests

### Test Naming Convention

```python
def test_[component]_[action]_[expected_result]():
    """Clear description of what is being tested."""
```

### Example Test Structure

```python
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.mark.unit
async def test_graphql_client_executes_query_successfully(mock_httpx_client, sample_graphql_response):
    """Test that GraphQL client successfully executes a query."""
    # Arrange
    mock_httpx_client.post.return_value.json.return_value = sample_graphql_response
    client = GraphQLClient(http_client=mock_httpx_client)
    
    # Act
    result = await client.execute_query("{ patients { id name } }")
    
    # Assert
    assert result == sample_graphql_response
    mock_httpx_client.post.assert_called_once()
```

### Custom Assertions

Use custom assertion helpers for better error messages:

```python
from tests.helpers.assertion_helpers import assert_graphql_response_valid, assert_schema_type_exists

def test_schema_contains_patient_type(sample_schema):
    assert_schema_type_exists(sample_schema, "Patient")
    assert_graphql_response_valid(sample_schema)
```

## Test Data Management

### Fixtures Directory

- `fixtures/graphql/`: Store sample GraphQL responses
- `fixtures/schemas/`: Store GraphQL schema introspection responses  
- `fixtures/mcp/`: Store MCP protocol messages

### Creating Test Fixtures

```python
# tests/fixtures/graphql/patient_response.json
{
  "data": {
    "patients": [
      {"id": "1", "name": "John Doe"},
      {"id": "2", "name": "Jane Smith"}
    ]
  }
}
```

```python
# Load fixture in test
import json
from pathlib import Path

def load_fixture(filename):
    fixture_path = Path(__file__).parent / "fixtures" / "graphql" / filename
    return json.loads(fixture_path.read_text())
```

## Test-Driven Development (TDD)

Follow the Red-Green-Refactor cycle:

1. **Red**: Write a failing test that describes the desired functionality
2. **Green**: Write the minimal code to make the test pass
3. **Refactor**: Improve the code while keeping tests green

### TDD Example

```python
# Step 1: RED - Write failing test
@pytest.mark.unit
def test_config_loads_api_url_from_environment():
    """Test that configuration loads API URL from environment variable."""
    import os
    os.environ["HEALTHIE_API_URL"] = "https://test.api.com"
    
    config = Config()
    
    assert config.api_url == "https://test.api.com"

# Step 2: GREEN - Write minimal implementation
class Config:
    def __init__(self):
        import os
        self.api_url = os.environ.get("HEALTHIE_API_URL")

# Step 3: REFACTOR - Improve implementation
from pydantic import BaseModel, Field
import os

class Config(BaseModel):
    api_url: str = Field(default_factory=lambda: os.environ.get("HEALTHIE_API_URL", ""))
```

## Coverage Requirements

- **Unit Tests**: 95% line coverage minimum
- **Integration Tests**: 85% workflow coverage
- **E2E Tests**: 80% critical path coverage

## Performance Guidelines

- **Unit Tests**: < 100ms per test
- **Integration Tests**: < 1s per test  
- **E2E Tests**: < 10s per test

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure to run `uv sync --dev` to install the package in development mode
2. **Coverage Errors**: Use `--no-cov` flag during development for faster test runs
3. **Async Test Issues**: Ensure `pytest-asyncio` is installed and `async def` functions are used correctly

### Getting Help

- Check the test output for detailed error messages
- Use `-v` flag for verbose output
- Use `--pdb` flag to drop into debugger on failures
- Check the project's TDD plan in `tasks/plan.md` for detailed implementation guidance