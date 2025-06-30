# Development Scripts

This directory contains utility scripts for developing and debugging with the Healthie MCP server.

## 🛠️ Development Tools

### `test-basic-imports.py`
Tests basic imports and validates the MCP server setup.

```bash
# Run basic tests
uv run python examples/scripts/development-tools/test-basic-imports.py

# What it tests:
# ✅ Configuration loading
# ✅ Schema manager setup  
# ✅ Tool imports and creation
# ✅ YAML configuration loading
# ✅ Tool execution
```

**Use this to:**
- Verify your installation is working
- Debug import errors
- Test tool functionality
- Validate configuration

### `test-mcp-connection.py` (Advanced)
Comprehensive MCP server testing with detailed diagnostics.

```bash
# Full server test (requires more setup)
uv run python examples/scripts/development-tools/test-mcp-connection.py --verbose

# Test specific tool
uv run python examples/scripts/development-tools/test-mcp-connection.py --tool search_schema
```

**Note:** This script requires the MCP server to be fully initialized, which may need additional setup.

## 🔍 Schema Tools

### `validate-queries.py`
Validates GraphQL queries against the Healthie schema.

```bash
# Validate a single query
uv run python examples/scripts/schema-tools/validate-queries.py --query "{ patients { id name } }"

# Validate multiple queries from file
uv run python examples/scripts/schema-tools/validate-queries.py examples/scripts/schema-tools/test-queries.json --batch

# Verbose output with analysis
uv run python examples/scripts/schema-tools/validate-queries.py --query "{ patients { id } }" --verbose

# Save results to file
uv run python examples/scripts/schema-tools/validate-queries.py queries.json --output results.json
```

**Features:**
- ✅ GraphQL syntax validation
- ⚠️ Schema validation (when schema is available)
- 📊 Query complexity analysis
- 💡 Healthcare-specific recommendations
- 📁 Batch processing support
- 📄 JSON output for automation

### `test-queries.json`
Sample queries for testing validation.

## 🚀 Quick Start

1. **Basic health check:**
   ```bash
   uv run python examples/scripts/development-tools/test-basic-imports.py
   ```

2. **Validate your queries:**
   ```bash
   uv run python examples/scripts/schema-tools/validate-queries.py --query "your query here"
   ```

3. **Test with sample queries:**
   ```bash
   uv run python examples/scripts/schema-tools/validate-queries.py examples/scripts/schema-tools/test-queries.json --batch
   ```

## 🔧 Common Issues

### Import Errors
If you see import errors, make sure you're running from the project root:
```bash
cd python-mcp-server
uv run python examples/scripts/...
```

### Schema Access
Without a valid `HEALTHIE_API_KEY`, schema validation will be skipped but syntax validation still works.

### Dependencies
All required dependencies should be installed via:
```bash
uv sync
```

## 📝 Creating New Scripts

When creating new development scripts:

1. **Add proper imports:**
   ```python
   # Add the MCP server to the path
   project_root = Path(__file__).parent.parent.parent
   sys.path.insert(0, str(project_root / "src"))
   ```

2. **Use error handling:**
   ```python
   try:
       from healthie_mcp.config.settings import get_settings
   except ImportError as e:
       print(f"❌ Import failed: {e}")
       sys.exit(1)
   ```

3. **Make them executable:**
   ```bash
   chmod +x your-script.py
   ```

4. **Add usage documentation:**
   Include a docstring with usage examples at the top of your script.

## 🎯 Script Status

| Script | Status | Purpose |
|--------|--------|---------|
| `test-basic-imports.py` | ✅ Working | Validate basic setup |
| `test-mcp-connection.py` | ⚠️ Partial | Full MCP server testing |
| `validate-queries.py` | ✅ Working | GraphQL query validation |

**Legend:**
- ✅ Working: Fully functional
- ⚠️ Partial: Works with limitations
- ❌ Broken: Needs fixes