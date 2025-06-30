# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive Model Context Protocol (MCP) server that provides AI tools with advanced access to Healthie's GraphQL API. The project acts as an intelligent development assistant for healthcare applications, offering schema analysis, query optimization, healthcare workflow guidance, and extensive developer tools. It represents a complete transformation from a simple Node.js wrapper to a production-ready healthcare API development platform.

## Key Commands

```bash
# Install dependencies
uv sync

# Run the MCP server in development mode with inspector
uv run mcp dev src/healthie_mcp/server.py:mcp

# Install in Claude Desktop
uv run mcp install src/healthie_mcp/server.py:mcp --name "Healthie Development Assistant"

# Run all tests
uv run pytest

# Run tests without coverage requirement
uv run pytest --no-cov

# Run tests with coverage report
uv run pytest --cov=src/healthie_mcp --cov-report=term-missing

# Run specific test categories
uv run pytest -m unit          # Unit tests only
uv run pytest -m integration   # Integration tests only
uv run pytest -m "not slow"    # Skip slow tests

# Run a specific test file
uv run pytest tests/unit/test_config.py -v

# Run a single test
uv run pytest tests/unit/test_config.py::TestConfig::test_default_configuration -v

# Test server startup (useful for debugging)
uv run python -c "from src.healthie_mcp.server import mcp; print('✅ Server ready')"
```

## Architecture Overview

### Core Components

1. **FastMCP Server** (`server.py`): Entry point using the official Python MCP SDK that registers 11 specialized tools and 2 resources

2. **Schema Manager** (`schema_manager.py`): Intelligent GraphQL schema management with automatic downloading, caching, validation, and refresh logic

3. **Configuration System**: Two-tier architecture for maximum flexibility:
   - **Application Settings** (`config/settings.py`): Runtime configuration with Pydantic validation
   - **Tool Configuration** (`config/data/*.yaml`): 8 YAML files containing tool behavior, templates, patterns, and rules
   - **Configuration Loader** (`config/loader.py`): Cached YAML loading with error handling

4. **Base Architecture** (`base.py`): Abstract base classes and protocols ensuring consistent tool implementation with dependency injection

5. **Exception System** (`exceptions.py`): Custom exception hierarchy with structured error details for healthcare-aware error handling

### Tool Architecture

All tools follow a consistent pattern:
- Extend `BaseTool` abstract class with generic typing
- Implement required abstract methods: `get_tool_name()`, `get_tool_description()`, `execute()`
- Use dependency injection for `SchemaManagerProtocol`
- Return structured Pydantic models
- Configuration-driven behavior through YAML files

### Tool Categories (11 Total)

**Core Schema Tools** (require valid Healthie schema):
- `search_schema`: Advanced regex-based schema search with type filtering and context
- `introspect_type`: Comprehensive type information with fields, relationships, and metadata
- `find_healthcare_patterns`: Healthcare workflow pattern detection with FHIR awareness

**External Developer Tools** (configuration-driven, work independently):
- `query_templates`: Pre-built GraphQL queries organized by healthcare workflows
- `code_examples`: Multi-language examples (JavaScript, Python, cURL) with authentication
- `input_validation`: Healthcare-compliant validation with medical identifier support
- `error_decoder`: Intelligent error interpretation with healthcare-specific solutions
- `query_performance`: Performance analysis with healthcare workflow optimization
- `field_relationships`: Deep schema relationship mapping and usage patterns
- `workflow_sequences`: Multi-step healthcare workflow guidance and best practices
- `field_usage`: Field usage recommendations with healthcare context

### Configuration Architecture

**8 YAML Configuration Files** in `config/data/`:
1. **`queries.yaml`**: GraphQL query templates by workflow category
2. **`patterns.yaml`**: Healthcare patterns, keywords, and FHIR mappings
3. **`errors.yaml`**: Error types, solutions, and code examples
4. **`validation.yaml`**: Validation rules, patterns, and healthcare-specific constraints
5. **`workflows.yaml`**: Multi-step workflow sequences for common operations
6. **`fields.yaml`**: Field relationships and usage patterns
7. **`performance.yaml`**: Performance thresholds and optimization rules
8. **`examples.yaml`**: Code examples for different programming languages

**Benefits of Configuration-Driven Design**:
- Healthcare experts can modify behavior without coding
- Environment-specific customizations
- Easy maintenance and updates
- Hot-reloadable configuration changes

## Environment Variables

```bash
# Required
export HEALTHIE_API_URL="https://staging-api.gethealthie.com/graphql"

# Optional but recommended for full functionality
export HEALTHIE_API_KEY="your-api-key"  # Required for schema downloads

# Configuration
export SCHEMA_DIR="./schemas"          # Local schema cache directory
export CACHE_ENABLED="true"           # Enable schema caching
export CACHE_DURATION_HOURS="24"      # Schema cache duration

# Logging and debugging
export LOG_LEVEL="INFO"               # DEBUG, INFO, WARNING, ERROR, CRITICAL
export DEBUG_MODE="false"             # Enable debug mode

# Network settings
export REQUEST_TIMEOUT="30"           # HTTP request timeout in seconds
export MAX_RETRIES="3"                # Maximum retry attempts
```

## Development Workflow

### Tool Development Process
1. **Create Pydantic Models**: Define input/output models in `models/`
2. **Extend BaseTool**: Implement required abstract methods
3. **Add Configuration**: Create/update YAML files for tool behavior
4. **Register Tool**: Add setup function call in `server.py`
5. **Write Tests**: Create comprehensive tests with multiple categories
6. **Documentation**: Update tool descriptions and examples

### Testing Strategy
- **89 tests currently passing** with comprehensive coverage
- **Test Categories**: 
  - `unit`: Individual component testing
  - `integration`: Component interaction testing
  - `e2e`: Complete workflow testing
  - `slow`: Tests taking >1 second
  - `requires_api`: Tests needing external API access
  - `requires_auth`: Tests needing valid credentials

### Configuration Management
- **Non-destructive updates**: Modify YAML files without code changes
- **Version control**: All configuration is tracked in git
- **Validation**: Configuration errors are caught at load time
- **Caching**: YAML files are cached for performance

## Healthcare Domain Specialization

### FHIR Integration
- **Resource Mapping**: Automatically identifies FHIR-compatible patterns
- **Standard Terminologies**: Integration with SNOMED, LOINC, ICD-10
- **Interoperability**: Recommendations for healthcare data exchange

### Healthcare Workflows
- **Patient Management**: Demographics, medical records, consent management
- **Appointment Scheduling**: Availability, booking, reminders, cancellations
- **Clinical Documentation**: Forms, assessments, notes, care plans, goals
- **Billing & Insurance**: Claims processing, payment workflows, authorization
- **Provider Management**: Credentials, licenses, organizations, specialties

### Compliance & Security
- **HIPAA Awareness**: Built into recommendations and validation rules
- **PHI Handling**: Guidance for proper handling of protected health information
- **Medical Identifiers**: Validation for NPI, DEA, medical record numbers
- **Audit Requirements**: Structured logging and error tracking

## Key Implementation Patterns

### 1. Dependency Injection
```python
class MyTool(BaseTool[MyResult]):
    def __init__(self, schema_manager: SchemaManagerProtocol):
        super().__init__(schema_manager)  # Schema access injected
```

### 2. Configuration-Driven Behavior
```python
# Tool loads behavior from YAML
config = self.config_loader.load_queries()
templates = self._process_config(config)
```

### 3. Structured Error Handling
```python
try:
    result = tool.execute(**params)
except ToolError as e:
    return structured_error_response(e)
```

### 4. Type-Safe Models
```python
class ToolInput(BaseModel):
    param: str = Field(description="Parameter description")

class ToolResult(BaseModel):
    data: List[str] = Field(description="Result data")
```

## Performance Considerations

### Schema Management
- **Intelligent Caching**: TTL-based with validation
- **Lazy Loading**: Schema loaded on first access
- **Background Refresh**: Automatic schema updates

### Configuration Loading
- **LRU Caching**: Frequently used configs cached in memory
- **Batch Loading**: Related configurations loaded together
- **Error Recovery**: Graceful fallback for invalid configurations

### Tool Execution
- **Async Support**: All tools support async execution
- **Resource Pooling**: Shared resources across tool instances
- **Memory Efficiency**: Large datasets processed in chunks

## Testing & Quality Assurance

### Current Test Status
- ✅ **89/89 tests passing** (100% pass rate)
- ✅ **Core functionality fully tested**
- ✅ **MCP server integration verified**
- ✅ **Configuration system validated**

### Quality Standards
- **Type Safety**: Full Pydantic validation throughout
- **Error Handling**: Comprehensive exception management
- **Code Coverage**: Aiming for 85% coverage (currently ~54%)
- **Healthcare Compliance**: HIPAA-aware design patterns

## Important Notes

### Technical Requirements
- **Python 3.13+**: Uses modern Python features and typing
- **UV Package Manager**: Preferred over pip for dependency management
- **FastMCP**: Official Python MCP SDK with async support
- **Pydantic**: Type validation and serialization
- **PyYAML**: Configuration file processing

### Operational Modes
- **Full Mode**: With Healthie API access and schema
- **Limited Mode**: Configuration-driven tools only (no schema required)
- **Development Mode**: Enhanced logging and debugging
- **Production Mode**: Optimized performance and error handling

### Healthcare Focus
- **Domain Expertise**: Built-in understanding of healthcare workflows
- **Compliance First**: HIPAA considerations in all recommendations
- **Interoperability**: FHIR-aware patterns and mappings
- **Clinical Context**: Medical terminology and identifier validation

## Documentation

- **[README.md](README.md)**: Project overview and features
- **[QUICK_START.md](QUICK_START.md)**: 5-minute setup guide
- **[DEV_SETUP.md](DEV_SETUP.md)**: Comprehensive development setup
- **[IMPROVEMENTS.md](IMPROVEMENTS.md)**: Improvements over original Node.js version