# Development Setup Guide

Complete development environment setup for contributing to the Healthie MCP Server. This guide covers setting up the development environment for the production-ready MCP server with 8 working tools for GraphQL schema assistance and healthcare-specific development workflows.

## Prerequisites

- Python 3.13+
- [UV package manager](https://docs.astral.sh/uv/) - Fast Python package manager
- Git
- Code editor (VS Code recommended with Python extensions)

## 1. Environment Setup

### Clone and Install

```bash
# Clone the repository
git clone https://github.com/bredmond1019/graphql-mcp-server
cd python-mcp-server

# Install dependencies including dev tools
uv sync --dev

# Verify installation
uv run pytest --version
uv run python -c "import healthie_mcp; print('✓ Package installed successfully')"
```

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required - Healthie GraphQL API endpoint
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

# Production settings (when deploying)
# HEALTHIE_API_URL=https://api.gethealthie.com/graphql
# LOG_LEVEL=INFO
# DEBUG_MODE=false
```

## 2. Development Workflow

### Quick Start - Test the 8 Working Tools

```bash
# Verify all 8 working tools are functioning
uv run python misc/test_phase_2_simple.py

# Test individual tools interactively
uv run mcp dev src/healthie_mcp/server.py:mcp
# This opens MCP Inspector at http://localhost:3000
```

### Running the Complete Test Suite

```bash
# Run all tests (requires 85% coverage)
uv run pytest

# Run with detailed coverage report
uv run pytest --cov=src/healthie_mcp --cov-report=term-missing --cov-report=html:htmlcov

# View coverage report in browser
open htmlcov/index.html  # macOS
# or visit file:///path/to/project/htmlcov/index.html

# Run specific test categories
uv run pytest -m unit          # Unit tests only
uv run pytest -m integration   # Integration tests only
uv run pytest -m "not slow"    # Skip slow tests
uv run pytest -m requires_api  # Tests requiring API access

# Run specific test files
uv run pytest tests/unit/test_schema_search_tool.py -v
uv run pytest tests/unit/test_compliance_checker_tool.py -v

# Run single test with detailed output
uv run pytest tests/unit/test_config.py::TestConfig::test_default_configuration -v -s
```

### Phase 2 Test Suite (Production-Ready Tools)

The project includes a comprehensive Phase 2 test suite for the 8 working tools:

```bash
# Run the complete Phase 2 test suite
uv run python misc/test_phase_2_all_tools.py

# Generate detailed test reports (creates markdown files)
# Results saved to test_results/phase_2/

# View test summary
cat test_results/phase_2/PHASE_2_SUMMARY.md
```

### Development Server

```bash
# Run with live reload (development mode) - opens MCP Inspector
uv run mcp dev src/healthie_mcp/server.py:mcp

# Run with specific log level and debug mode
LOG_LEVEL=DEBUG DEBUG_MODE=true uv run mcp dev src/healthie_mcp/server.py:mcp

# Run without opening browser (headless)
uv run mcp dev src/healthie_mcp/server.py:mcp --no-inspector

# Production-like server (without dev tools)
uv run python -m healthie_mcp.server
```

### Code Quality and Testing Standards

The project maintains high code quality with strict pytest configuration:

```bash
# Coverage requirement: 85% minimum (enforced by CI)
# Test discovery: tests/ directory structure
# Async testing: Built-in asyncio support
# Test markers: unit, integration, e2e, slow, requires_api, requires_auth

# Code formatting and linting (when added)
# uv run ruff format .
# uv run ruff check .
# uv run mypy src/healthie_mcp
```

## 3. Project Structure

```
src/healthie_mcp/
├── server.py              # FastMCP server entry point
├── schema_manager.py      # GraphQL schema management
├── base.py               # Abstract base classes and protocols
├── constants.py          # Project constants
├── exceptions.py         # Custom exception hierarchy
├── config/               # Configuration system
│   ├── settings.py       # Application settings
│   ├── loader.py         # YAML config loader
│   └── data/            # YAML configuration files
├── models/              # Pydantic data models
├── tools/               # MCP tool implementations
│   ├── [8 WORKING TOOLS]
│   ├── schema_search.py           # Search GraphQL schema
│   ├── query_templates.py         # Query template generation
│   ├── code_examples.py           # Code examples and snippets
│   ├── type_introspection.py      # Type introspection utilities
│   ├── error_decoder.py           # Error decoding and debugging
│   ├── compliance_checker.py      # Healthcare compliance checking
│   ├── workflow_sequences.py      # Workflow sequence helpers
│   ├── field_relationships.py     # Field relationship analysis
│   └── todo/                      # Future tools (not yet integrated)
│       ├── api_usage_analytics.py
│       ├── environment_manager.py
│       ├── field_usage.py
│       ├── healthcare_patterns.py
│       ├── input_validation.py
│       ├── integration_testing.py
│       ├── performance_analyzer.py
│       ├── rate_limit_advisor.py
│       └── webhook_configurator.py
└── utils/               # Utility functions
    ├── graphql_utils.py   # GraphQL-specific utilities
    ├── text_utils.py      # Text processing utilities
    └── validation_utils.py # Validation helpers

tests/                   # Comprehensive test suite
├── conftest.py          # Pytest configuration and fixtures
├── unit/               # Unit tests (85%+ coverage required)
│   ├── test_config.py
│   ├── test_schema_manager.py
│   ├── test_server.py
│   └── test_[tool_name]_tool.py  # Tests for each working tool
├── integration/        # Integration tests
│   └── test_server_integration.py
├── e2e/               # End-to-end tests (when implemented)
├── fixtures/          # Test fixtures and mock data
│   ├── graphql/       # GraphQL schema fixtures
│   ├── mcp/          # MCP-specific fixtures
│   └── schemas/      # Schema test data
└── helpers/          # Test helper functions
    └── assertion_helpers.py

misc/                   # Development and testing utilities
├── test_phase_2_simple.py      # Quick tool verification
├── test_phase_2_all_tools.py   # Comprehensive tool testing
└── run_server*.py              # Various server execution scripts

test_results/           # Generated test documentation
├── phase_2/           # Phase 2 test results (8 working tools)
│   ├── PHASE_2_SUMMARY.md
│   └── [01-08]_*_detailed.md   # Detailed results for each tool
└── [other test documentation]

schemas/               # GraphQL schema files
├── schema.graphql     # Main Healthie schema
└── introspection.json # Schema introspection data

docs/                  # Project documentation
├── api/              # API reference documentation
├── guides/           # User guides and tutorials
└── tutorials/        # Step-by-step tutorials

examples/             # Integration examples
├── integrations/     # Language-specific integration examples
├── mcp-tools/       # MCP tool usage examples
├── scripts/         # Development scripts
└── workflows/       # Healthcare workflow examples
```

## 4. Working with the 8 Production Tools

### Current Production-Ready Tools

The server includes 8 fully tested and working tools:

1. **schema_search** - Search GraphQL schema elements
2. **query_templates** - Generate GraphQL query templates
3. **code_examples** - Create code examples in multiple languages
4. **introspect_type** - Explore GraphQL type definitions
5. **error_decoder** - Analyze and debug GraphQL errors
6. **compliance_checker** - Validate healthcare compliance
7. **workflow_sequences** - Manage multi-step workflows
8. **field_relationships** - Analyze GraphQL field relationships

### Testing Individual Tools

```bash
# Test a specific tool interactively
uv run mcp dev src/healthie_mcp/server.py:mcp

# In MCP Inspector, test tools like:
# search_schema: {"pattern": "patient", "type_filter": "OBJECT"}
# query_templates: {"operation_name": "GetPatients", "operation_type": "query"}
# code_examples: {"query": "query GetPatients {...}", "language": "python"}
```

## 5. Extending the Working Tools

### 1. Create New Tool (Following Existing Patterns)

```python
# src/healthie_mcp/tools/my_new_tool.py
from typing import Dict, Any, List
from ..base import BaseTool, SchemaManagerProtocol
from ..models.my_models import MyToolResult
from ..config import get_settings

class MyTool(BaseTool[MyToolResult]):
    """Tool description for healthcare-specific functionality."""

    def __init__(self, schema_manager: SchemaManagerProtocol):
        super().__init__(schema_manager)
        self.settings = get_settings()

    def get_tool_name(self) -> str:
        return "my_tool"

    def get_tool_description(self) -> str:
        return "Description of what my tool does for healthcare workflows"

    def execute(self, **kwargs) -> MyToolResult:
        """Execute the tool with provided parameters."""
        try:
            # Implementation following healthcare compliance patterns
            result = self._process_request(**kwargs)
            return MyToolResult(
                success=True,
                data=result,
                metadata={"tool": self.get_tool_name()}
            )
        except Exception as e:
            return MyToolResult(
                success=False,
                error=str(e),
                metadata={"tool": self.get_tool_name()}
            )

    def _process_request(self, **kwargs) -> Dict[str, Any]:
        """Process the request with healthcare-specific logic."""
        # Implementation here
        pass

def setup_my_tool(mcp, schema_manager: SchemaManagerProtocol):
    """Setup function following established patterns."""
    tool = MyTool(schema_manager)

    @mcp.tool(name=tool.get_tool_name(), description=tool.get_tool_description())
    async def my_tool_handler(**kwargs) -> Dict[str, Any]:
        result = tool.execute(**kwargs)
        return result.model_dump()
```

### 2. Create Pydantic Models (Healthcare-Focused)

```python
# src/healthie_mcp/models/my_models.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class MyToolInput(BaseModel):
    """Input model following healthcare data patterns."""
    patient_filter: Optional[str] = Field(None, description="Patient identifier or filter")
    include_phi: bool = Field(default=False, description="Include PHI in results (requires authorization)")
    operation_type: str = Field(description="Type of healthcare operation")
    compliance_level: str = Field(default="HIPAA", description="Compliance framework to follow")

class MyToolResult(BaseModel):
    """Result model with healthcare compliance metadata."""
    success: bool = Field(description="Whether the operation succeeded")
    data: Optional[Dict[str, Any]] = Field(None, description="Tool result data")
    error: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(description="Additional metadata")
    compliance_info: Optional[Dict[str, Any]] = Field(None, description="Compliance validation results")
    phi_exposure_risk: str = Field(default="LOW", description="PHI exposure risk level")
```

### 3. Add Configuration (Healthcare-Specific)

```yaml
# src/healthie_mcp/config/data/my_tool.yaml
settings:
  max_records: 1000
  default_compliance_level: "HIPAA"
  enable_phi_filtering: true
  audit_logging: true

healthcare_patterns:
  - name: "Patient Data Access"
    description: "Safe patient data access patterns"
    rules:
      - "Always validate authorization"
      - "Log all PHI access attempts"
      - "Apply minimum necessary principle"

  - name: "Appointment Management"
    description: "Healthcare appointment workflows"
    rules:
      - "Verify provider credentials"
      - "Check patient consent"
      - "Maintain audit trail"

compliance_frameworks:
  HIPAA:
    required_fields: ["authorization", "audit_trail"]
    phi_protection: true
  HITECH:
    encryption_required: true
    breach_notification: true
```

### 4. Register Tool in Server

```python
# In src/healthie_mcp/server.py
from .tools.my_new_tool import setup_my_tool

# Add to server setup (around line 57)
setup_my_tool(mcp, schema_manager)
```

### 5. Write Comprehensive Tests

```python
# tests/unit/test_my_new_tool.py
import pytest
from unittest.mock import Mock
from healthie_mcp.tools.my_new_tool import MyTool
from healthie_mcp.models.my_models import MyToolResult

class TestMyTool:
    """Test suite for MyTool following project patterns."""

    @pytest.fixture
    def mock_schema_manager(self):
        """Mock schema manager for testing."""
        manager = Mock()
        manager.get_schema_content.return_value = "mock schema"
        return manager

    @pytest.fixture
    def tool(self, mock_schema_manager):
        """Create tool instance for testing."""
        return MyTool(mock_schema_manager)

    @pytest.mark.unit
    def test_tool_initialization(self, tool):
        """Test tool initializes correctly."""
        assert tool.get_tool_name() == "my_tool"
        assert "healthcare" in tool.get_tool_description().lower()

    @pytest.mark.unit
    def test_tool_execution_success(self, tool):
        """Test successful tool execution."""
        result = tool.execute(operation_type="test")
        assert isinstance(result, MyToolResult)
        assert result.success is True

    @pytest.mark.unit
    def test_tool_execution_error_handling(self, tool):
        """Test tool handles errors gracefully."""
        # Test with invalid parameters
        result = tool.execute()  # Missing required params
        assert isinstance(result, MyToolResult)
        assert result.success is False
        assert result.error is not None

    @pytest.mark.integration
    def test_healthcare_compliance_validation(self, tool):
        """Test healthcare compliance features."""
        result = tool.execute(
            operation_type="patient_query",
            compliance_level="HIPAA"
        )
        assert result.phi_exposure_risk in ["LOW", "MEDIUM", "HIGH"]
        assert "compliance_info" in result.metadata
```

## 6. Configuration System

The project uses a sophisticated two-tier configuration system optimized for healthcare applications:

### Application Configuration

- Runtime settings in `config/settings.py` using Pydantic Settings
- Environment variable based with `.env` file support
- Automatic validation and type checking
- Healthcare compliance defaults

### Tool Configuration

- YAML files in `config/data/` for each tool
- Loaded dynamically with intelligent caching
- Healthcare-specific patterns and compliance rules
- Allows tool customization without code changes

### Current Configuration Files

```bash
# View all configuration files
ls src/healthie_mcp/config/data/

# Key configuration files for working tools:
src/healthie_mcp/config/data/
├── queries.yaml              # Query template configurations
├── examples.yaml             # Code example settings
├── patterns.yaml             # Healthcare workflow patterns
├── compliance_checker.yaml   # HIPAA/HITECH compliance rules
├── errors.yaml              # Error handling patterns
└── validation.yaml          # Input validation rules
```

### Adding New Configuration

```python
# In config/loader.py - add new loader method
def load_my_config(self) -> Dict[str, Any]:
    """Load my tool specific configuration."""
    return self.load_file("my_tool")

# Create config/data/my_tool.yaml following healthcare patterns
healthcare_settings:
  phi_protection_level: "STRICT"
  audit_requirements: true
  compliance_frameworks: ["HIPAA", "HITECH"]

patterns:
  patient_access:
    description: "Safe patient data access"
    required_authorization: true
    audit_logging: true
```

## 7. Testing Guidelines

### Test Categories and Markers

The project uses comprehensive test markers for organizing test execution:

- **unit**: Test individual components in isolation (fast, no external dependencies)
- **integration**: Test component interactions and tool combinations
- **e2e**: Test complete end-to-end workflows (when implemented)
- **slow**: Tests taking >1 second to execute
- **requires_api**: Tests needing external Healthie API access
- **requires_auth**: Tests needing valid authentication credentials

### Writing Tests Following Project Patterns

```python
import pytest
from unittest.mock import Mock, AsyncMock
from healthie_mcp.tools.my_tool import MyTool
from healthie_mcp.models.my_models import MyToolResult

class TestMyTool:
    """Test suite following healthcare testing patterns."""

    @pytest.fixture
    def mock_schema_manager(self):
        """Standard schema manager mock."""
        manager = Mock()
        manager.get_schema_content.return_value = "type Patient { id: ID! }"
        return manager

    @pytest.mark.unit
    def test_my_function_unit(self, mock_schema_manager):
        """Unit test with healthcare data validation."""
        tool = MyTool(mock_schema_manager)
        result = tool.execute(operation_type="patient_query")

        assert isinstance(result, MyToolResult)
        assert result.success is True
        assert result.phi_exposure_risk in ["LOW", "MEDIUM", "HIGH"]

    @pytest.mark.integration
    def test_tool_integration_with_compliance(self, mock_schema_manager):
        """Integration test with compliance checking."""
        tool = MyTool(mock_schema_manager)
        result = tool.execute(
            operation_type="patient_query",
            compliance_level="HIPAA",
            include_phi=False
        )

        assert result.success is True
        assert "compliance_info" in result.metadata
        assert result.phi_exposure_risk == "LOW"

    @pytest.mark.slow
    @pytest.mark.requires_api
    def test_with_real_healthie_api(self):
        """Test against real Healthie API (requires auth)."""
        # Only run in CI or with explicit flag
        if not pytest.config.getoption("--run-api-tests"):
            pytest.skip("API tests require --run-api-tests flag")

        # Implementation for real API testing
        pass
```

### Coverage Requirements and Quality Standards

- **Minimum 85% coverage required** (enforced by pytest-cov)
- **All new code must include comprehensive tests**
- **Healthcare compliance scenarios must be tested**
- **Error handling and edge cases must be covered**

```bash
# Generate detailed coverage reports
uv run pytest --cov=src/healthie_mcp --cov-report=html:htmlcov --cov-report=term-missing

# View coverage in browser
open htmlcov/index.html

# Check specific coverage for a tool
uv run pytest tests/unit/test_my_tool.py --cov=src/healthie_mcp/tools/my_tool --cov-report=term-missing
```

### Testing the 8 Working Tools

```bash
# Test all working tools quickly
uv run pytest tests/unit/ -k "search_schema or query_templates or code_examples or introspect_type or error_decoder or compliance_checker or workflow_sequences or field_relationships"

# Test specific tool categories
uv run pytest -m unit tests/unit/test_compliance_checker_tool.py
uv run pytest -m integration tests/integration/

# Run healthcare-specific test scenarios
uv run pytest -k "healthcare or compliance or phi"
```

## 8. Debugging and Development Tools

### Enable Debug Logging and Development Mode

```bash
# Full debug mode with detailed logging
DEBUG_MODE=true LOG_LEVEL=DEBUG uv run mcp dev src/healthie_mcp/server.py:mcp

# Debug specific components
HEALTHIE_API_LOG_LEVEL=DEBUG uv run mcp dev src/healthie_mcp/server.py:mcp

# Test with mock data (offline development)
CACHE_ENABLED=true DEBUG_MODE=true uv run mcp dev src/healthie_mcp/server.py:mcp
```

### MCP Inspector (Interactive Testing)

The MCP Inspector provides powerful debugging capabilities:

- **Automatically opens** when running `mcp dev` (http://localhost:3000)
- **Test all 8 working tools** interactively with real parameters
- **View request/response data** in real-time
- **Debug tool registration** and parameter validation
- **Test healthcare compliance** scenarios safely

```bash
# Start with MCP Inspector
uv run mcp dev src/healthie_mcp/server.py:mcp

# Example tool tests in Inspector:
# search_schema: {"pattern": "Patient", "type_filter": "OBJECT"}
# compliance_checker: {"query": "query GetPatient($id: ID!) { patient(id: $id) { name email } }", "frameworks": ["HIPAA"]}
```

### Development Scripts

```bash
# Quick verification of all working tools
uv run python misc/test_phase_2_simple.py

# Test MCP connection and tool registration
uv run python misc/test_mcp_connection.py

# Validate schema loading
uv run python misc/test_with_schema.py

# Test individual tool components
uv run python examples/scripts/development-tools/test-basic-imports.py
```

### Common Issues and Solutions

1. **Schema not loading**

   - Check `HEALTHIE_API_URL` in `.env` file
   - Verify network connectivity to Healthie API
   - Check if `schemas/` directory exists and is writable

2. **Tool not registering**

   - Verify setup function is called in `server.py`
   - Check tool class follows `BaseTool` interface
   - Ensure all imports are correct

3. **Import errors**

   - Run `uv sync --dev` to install all dependencies
   - Check Python version is 3.13+
   - Verify virtual environment is activated

4. **Test failures**

   - Check mock objects match expected interfaces
   - Verify test fixtures in `tests/fixtures/`
   - Run with `-v -s` flags for detailed output

5. **Healthcare compliance issues**
   - Review `config/data/compliance_checker.yaml`
   - Check PHI exposure risk calculations
   - Validate audit logging configuration

### Performance Debugging

```bash
# Profile tool execution
uv run python -m cProfile -o profile.out misc/test_phase_2_simple.py

# Memory usage analysis
uv run python -m tracemalloc misc/test_phase_2_simple.py

# Async debugging
DEBUG_ASYNCIO=1 uv run mcp dev src/healthie_mcp/server.py:mcp
```

## 9. Contributing Guidelines

### Code Standards and Patterns

1. **Follow existing healthcare-focused patterns**

   - Use the established `BaseTool` interface for all tools
   - Implement proper error handling with healthcare context
   - Include PHI exposure risk assessment in tool outputs
   - Follow HIPAA compliance patterns in data handling

2. **Code Quality Requirements**

   - Maintain 85%+ test coverage for all new code
   - Write comprehensive unit and integration tests
   - Use type hints and Pydantic models consistently
   - Follow async/await patterns for I/O operations

3. **Healthcare Compliance**
   - Review PHI handling in all data processing
   - Implement audit logging for sensitive operations
   - Include compliance metadata in tool responses
   - Test with healthcare-specific scenarios

### Development Workflow

```bash
# 1. Set up development environment
uv sync --dev
cp .env.example .env  # Configure environment variables

# 2. Verify current working tools
uv run python misc/test_phase_2_simple.py

# 3. Make your changes following existing patterns
# - Add new tools to src/healthie_mcp/tools/
# - Create models in src/healthie_mcp/models/
# - Add configuration in src/healthie_mcp/config/data/

# 4. Write comprehensive tests
uv run pytest tests/unit/test_my_new_tool.py -v

# 5. Ensure coverage requirements
uv run pytest --cov=src/healthie_mcp --cov-fail-under=85

# 6. Test with MCP Inspector
uv run mcp dev src/healthie_mcp/server.py:mcp

# 7. Run full test suite
uv run pytest
```

### Extending Working Tools

When enhancing the 8 production-ready tools:

1. **Understand the tool's purpose** by reviewing its phase 2 test results
2. **Follow the established patterns** in the existing implementation
3. **Add healthcare-specific enhancements** that maintain compliance
4. **Update configuration files** to support new features
5. **Write tests** that cover both functionality and compliance scenarios

### Moving Tools from TODO to Production

To promote a tool from `tools/todo/` to production:

1. **Review the tool implementation** for completeness and compliance
2. **Create comprehensive test suite** following project patterns
3. **Add proper error handling** and healthcare context
4. **Update server.py** to register the tool
5. **Add configuration files** if needed
6. **Test thoroughly** with Phase 2 test patterns
7. **Update documentation** to reflect the new working tool

### Documentation Updates

When contributing:

- Update relevant documentation in `docs/`
- Add examples to `examples/` directory if creating new workflows
- Update tool count and descriptions in README files
- Ensure all paths and commands work with current structure

### Review Checklist

Before submitting contributions:

- [ ] All tests pass with 85%+ coverage
- [ ] Healthcare compliance patterns followed
- [ ] MCP Inspector testing completed
- [ ] Configuration files updated if needed
- [ ] Documentation reflects changes
- [ ] Code follows existing patterns
- [ ] Error handling includes healthcare context
- [ ] PHI exposure risks assessed and documented

## 10. IDE Setup (VS Code)

### Recommended Extensions

**Essential Extensions:**

- Python (Microsoft) - Core Python support
- Pylance (Microsoft) - Advanced language features and type checking
- Python Test Explorer - Visual test runner integration
- YAML - YAML file support for configuration files

**Healthcare Development Extensions:**

- GitLens - Git integration for collaborative healthcare development
- REST Client - Test GraphQL endpoints directly in VS Code
- JSON Schema - Validation for GraphQL schema files

### Recommended VS Code Settings

Create or update `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",

  // Testing configuration
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests", "--verbose", "--tb=short"],
  "python.testing.autoTestDiscoverOnSaveEnabled": true,

  // Type checking
  "python.analysis.typeCheckingMode": "basic",
  "python.analysis.autoImportCompletions": true,

  // File associations for healthcare development
  "files.associations": {
    "*.graphql": "graphql",
    "*.yaml": "yaml",
    "*.yml": "yaml"
  },

  // Healthcare-specific settings
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/htmlcov": false // Keep coverage reports visible
  },

  // Auto-save for safer healthcare development
  "files.autoSave": "afterDelay",
  "files.autoSaveDelay": 1000
}
```

### VS Code Tasks for Healthcare Development

Create `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Test All Working Tools",
      "type": "shell",
      "command": "uv run python misc/test_phase_2_simple.py",
      "group": "test",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      }
    },
    {
      "label": "Run MCP Server with Inspector",
      "type": "shell",
      "command": "uv run mcp dev src/healthie_mcp/server.py:mcp",
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "dedicated"
      }
    },
    {
      "label": "Run Tests with Coverage",
      "type": "shell",
      "command": "uv run pytest --cov=src/healthie_mcp --cov-report=html:htmlcov",
      "group": "test",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      }
    }
  ]
}
```

### Launch Configuration for Debugging

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug MCP Server",
      "type": "python",
      "request": "launch",
      "module": "healthie_mcp.server",
      "console": "integratedTerminal",
      "env": {
        "DEBUG_MODE": "true",
        "LOG_LEVEL": "DEBUG"
      }
    },
    {
      "name": "Debug Individual Tool Test",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["tests/unit/test_compliance_checker_tool.py", "-v", "-s"],
      "console": "integratedTerminal"
    }
  ]
}
```

### Development Workflow in VS Code

1. **Start Development**: Use `Ctrl+Shift+P` → "Tasks: Run Task" → "Run MCP Server with Inspector"
2. **Run Tests**: Use `Ctrl+Shift+P` → "Tasks: Run Task" → "Test All Working Tools"
3. **Debug Issues**: Use the Debug panel with the "Debug MCP Server" configuration
4. **Check Coverage**: Use `Ctrl+Shift+P` → "Tasks: Run Task" → "Run Tests with Coverage"

This setup provides a comprehensive development environment optimized for healthcare MCP tool development with proper testing, debugging, and compliance validation.
