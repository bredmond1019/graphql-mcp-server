# Development Setup Guide

Complete development environment setup for contributing to the Healthie MCP Server.

## Prerequisites

- Python 3.13+
- [UV package manager](https://docs.astral.sh/uv/)
- Git
- Code editor (VS Code recommended)

## 1. Environment Setup

### Clone and Install

```bash
# Clone the repository
git clone <repository-url>
cd python-mcp-server

# Install dependencies including dev tools
uv sync --dev

# Verify installation
uv run pytest --version
```

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required
HEALTHIE_API_URL=https://staging-api.gethealthie.com/graphql

# Optional but recommended for full functionality
HEALTHIE_API_KEY=your-api-key-here

# Development settings
LOG_LEVEL=DEBUG
DEBUG_MODE=true
CACHE_ENABLED=true
SCHEMA_DIR=./schemas

# Test settings
REQUEST_TIMEOUT=30
MAX_RETRIES=3
```

## 2. Development Workflow

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/healthie_mcp --cov-report=term-missing

# Run specific test categories
uv run pytest -m unit          # Unit tests only
uv run pytest -m integration   # Integration tests only
uv run pytest -m "not slow"    # Skip slow tests

# Run specific test files
uv run pytest tests/unit/test_config.py -v

# Run single test
uv run pytest tests/unit/test_config.py::TestConfig::test_default_configuration -v
```

### Development Server

```bash
# Run with live reload (development mode)
uv run mcp dev src/healthie_mcp/server.py:mcp

# Run with specific log level
LOG_LEVEL=DEBUG uv run mcp dev src/healthie_mcp/server.py:mcp
```

### Code Quality

The project uses pytest with strict configuration:

```bash
# Coverage requirement: 85%
# Test discovery: tests/ directory
# Async testing: Built-in support
# Markers: unit, integration, e2e, slow, requires_api, requires_auth
```

## 3. Project Structure

```
src/healthie_mcp/
├── server.py              # FastMCP server entry point
├── schema_manager.py      # GraphQL schema management
├── base.py               # Abstract base classes
├── constants.py          # Project constants
├── exceptions.py         # Custom exception hierarchy
├── config/               # Configuration system
│   ├── settings.py       # Application settings
│   ├── loader.py         # YAML config loader
│   └── data/            # YAML configuration files
├── models/              # Pydantic data models
├── tools/               # MCP tool implementations
└── utils/               # Utility functions

tests/
├── unit/                # Unit tests
├── integration/         # Integration tests
├── e2e/                 # End-to-end tests
├── fixtures/            # Test fixtures
└── helpers/             # Test helper functions
```

## 4. Adding New Tools

### 1. Create Tool Class

```python
# src/healthie_mcp/tools/my_new_tool.py
from ..base import BaseTool, SchemaManagerProtocol
from ..models.my_models import MyToolResult

class MyTool(BaseTool[MyToolResult]):
    def get_tool_name(self) -> str:
        return "my_tool"
    
    def get_tool_description(self) -> str:
        return "Description of what my tool does"
    
    def execute(self, **kwargs) -> MyToolResult:
        # Implementation here
        pass

def setup_my_tool(mcp, schema_manager):
    tool = MyTool(schema_manager)
    # Register with MCP
    @mcp.tool(name=tool.get_tool_name(), description=tool.get_tool_description())
    async def my_tool_handler(**kwargs):
        return tool.execute(**kwargs)
```

### 2. Create Pydantic Models

```python
# src/healthie_mcp/models/my_models.py
from pydantic import BaseModel, Field

class MyToolInput(BaseModel):
    param1: str = Field(description="First parameter")
    param2: int = Field(default=10, description="Second parameter")

class MyToolResult(BaseModel):
    result: str = Field(description="Tool result")
    metadata: dict = Field(description="Additional metadata")
```

### 3. Add Configuration (Optional)

```yaml
# src/healthie_mcp/config/data/my_tool.yaml
settings:
  default_value: "example"
  max_items: 100

patterns:
  - name: "Pattern 1"
    description: "First pattern"
    rules:
      - "rule1"
      - "rule2"
```

### 4. Register Tool

```python
# In src/healthie_mcp/server.py
from .tools.my_new_tool import setup_my_tool

# Add to server setup
setup_my_tool(mcp, schema_manager)
```

### 5. Write Tests

```python
# tests/unit/test_my_new_tool.py
import pytest
from healthie_mcp.tools.my_new_tool import MyTool

class TestMyTool:
    def test_tool_execution(self):
        # Test implementation
        pass
```

## 5. Configuration System

The project uses a two-tier configuration system:

### Application Configuration
- Runtime settings in `config/settings.py`
- Environment variable based
- Pydantic validation

### Tool Configuration
- YAML files in `config/data/`
- Loaded dynamically with caching
- Allows tool customization without code changes

### Adding New Configuration

```python
# In config/loader.py - add new loader method
def load_my_config(self) -> Dict[str, Any]:
    return self.load_file("my_config")

# Create config/data/my_config.yaml
my_settings:
  option1: value1
  option2: value2
```

## 6. Testing Guidelines

### Test Categories
- **Unit**: Test individual components in isolation
- **Integration**: Test component interactions
- **E2E**: Test complete workflows
- **Slow**: Tests taking >1 second
- **Requires API**: Tests needing external API access
- **Requires Auth**: Tests needing valid credentials

### Writing Tests
```python
import pytest
from unittest.mock import Mock

@pytest.mark.unit
def test_my_function():
    # Unit test implementation
    pass

@pytest.mark.integration
def test_tool_integration():
    # Integration test implementation
    pass

@pytest.mark.slow
@pytest.mark.requires_api
def test_with_real_api():
    # API-dependent test
    pass
```

### Coverage Requirements
- Minimum 85% coverage required
- All new code must include tests
- Use `--cov-report=html:htmlcov` for detailed coverage reports

## 7. Debugging

### Enable Debug Logging
```bash
DEBUG_MODE=true LOG_LEVEL=DEBUG uv run mcp dev src/healthie_mcp/server.py:mcp
```

### MCP Inspector
- Automatically opens when running in dev mode
- Test tools interactively
- View request/response data
- Debug tool registration issues

### Common Issues
1. **Schema not loading**: Check API key and network access
2. **Tool not registering**: Verify setup function is called in server.py
3. **Import errors**: Ensure all dependencies are installed with `uv sync`
4. **Test failures**: Check that mock objects match expected interfaces

## 8. Contributing

1. Follow the existing code patterns
2. Add comprehensive tests for new features
3. Update configuration files as needed
4. Ensure 85% test coverage
5. Follow healthcare compliance guidelines in recommendations

## 9. IDE Setup (VS Code)

Recommended extensions:
- Python
- Pylance
- Python Test Explorer
- YAML

Recommended settings:
```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "python.linting.enabled": true
}
```