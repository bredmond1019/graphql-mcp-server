# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the Healthie MCP Server.

## 🚨 Common Issues

### 1. Import Errors

**Problem:** `ImportError: No module named 'healthie_mcp'`

**Solutions:**
```bash
# Check you're in the right directory
cd python-mcp-server

# Install dependencies
uv sync

# Run from project root
uv run python examples/scripts/development-tools/test-basic-imports.py
```

### 2. Schema Loading Issues

**Problem:** `⚠️ No schema available. Some validations will be limited.`

**Cause:** Missing or invalid API configuration

**Solutions:**
```bash
# Set API URL (required)
export HEALTHIE_API_URL="https://staging-api.gethealthie.com/graphql"

# Set API key (optional but recommended)
# Option 1: Use environment file
cp .env.development.example .env.development
# Edit .env.development and add your actual API key

# Option 2: Export directly
export HEALTHIE_API_KEY="<your-actual-api-key>"

# Test configuration
uv run python examples/scripts/development-tools/test-basic-imports.py
```

### 3. Tool Execution Failures

**Problem:** Tools return empty results or errors

**Debugging steps:**
1. **Check configuration:**
   ```bash
   uv run python -c "from src.healthie_mcp.config.settings import get_settings; print(get_settings())"
   ```

2. **Test individual tools:**
   ```bash
   uv run python examples/scripts/development-tools/test-basic-imports.py
   ```

3. **Verify YAML configs:**
   ```bash
   ls src/healthie_mcp/config/data/
   ```

### 4. Authentication Errors

**Problem:** `HTTP error 401 Unauthorized` or `HTTP error 404 Not Found`

**Solutions:**
- **For development:** Use staging API without authentication
- **For production:** Obtain valid API key from Healthie
- **For testing:** Most tools work without API access (config-driven)

### 5. Network/Connection Issues

**Problem:** `HTTPError`, `ConnectionError`, or timeouts

**Solutions:**
```bash
# Check network connectivity
curl -I https://staging-api.gethealthie.com/graphql

# Test with longer timeout
export REQUEST_TIMEOUT="60"

# Use cached schema (if available)
export CACHE_ENABLED="true"
```

## 🔧 Diagnostic Commands

### Quick Health Check
```bash
# Test all basic functionality
uv run python examples/scripts/development-tools/test-basic-imports.py
```

### Configuration Check
```bash
# Show current settings
uv run python -c "
from src.healthie_mcp.config.settings import get_settings
settings = get_settings()
print(f'API URL: {settings.healthie_api_url}')
print(f'Schema Dir: {settings.schema_dir}')
print(f'Cache Enabled: {settings.cache_enabled}')
"
```

### Tool Functionality Test
```bash
# Test config-driven tools (work without API)
uv run python -c "
from src.healthie_mcp.tools.query_templates import QueryTemplatesTool
from src.healthie_mcp.schema_manager import SchemaManager
tool = QueryTemplatesTool(SchemaManager('https://example.com', '.'))
result = tool.execute()
print(f'Found {result.total_count} templates')
"
```

### Query Validation Test
```bash
# Test GraphQL validation
uv run python examples/scripts/schema-tools/validate-queries.py --query "{ patients { id } }"
```

## 🐛 Debug Mode

Enable verbose logging for detailed diagnostics:

```bash
# Set debug mode
export DEBUG_MODE="true"
export LOG_LEVEL="DEBUG"

# Run with verbose output
uv run python examples/scripts/development-tools/test-basic-imports.py
```

## 📋 Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HEALTHIE_API_URL` | ✅ | staging URL | Healthie GraphQL endpoint |
| `HEALTHIE_API_KEY` | ❌ | None | API authentication key |
| `SCHEMA_DIR` | ❌ | `schemas` | Local schema cache directory |
| `CACHE_ENABLED` | ❌ | `true` | Enable schema caching |
| `CACHE_DURATION_HOURS` | ❌ | `24` | Schema cache duration |
| `LOG_LEVEL` | ❌ | `INFO` | Logging verbosity |
| `DEBUG_MODE` | ❌ | `false` | Enable debug features |

## 🔍 Common Error Messages

### `Session manager can only be accessed after calling streamable_http_app()`
**Cause:** Trying to access FastMCP internals before initialization
**Solution:** Use the diagnostic scripts instead of direct server access

### `HTTP error '404 Not Found'`
**Cause:** Invalid API endpoint or missing authentication
**Solution:** Check API URL and authentication setup

### `Configuration error: Invalid YAML`
**Cause:** Corrupted or invalid YAML configuration files
**Solution:** Check `src/healthie_mcp/config/data/` for syntax errors

### `Tool execution failed: 'str' object has no attribute 'dict'`
**Cause:** Type mismatch in tool parameters
**Solution:** Check parameter types in tool documentation

## 🚀 Performance Issues

### Slow Tool Execution
1. **Enable caching:**
   ```bash
   export CACHE_ENABLED="true"
   ```

2. **Check network latency:**
   ```bash
   ping staging-api.gethealthie.com
   ```

3. **Use specific tool filters:**
   ```bash
   # Instead of broad searches
   search_schema query=".*"
   
   # Use specific filters
   search_schema query="patient" type_filter="type"
   ```

### Memory Usage
For large schemas or many tools:
```bash
# Monitor memory usage
top -p $(pgrep -f "python.*healthie_mcp")

# Reduce cache duration if needed
export CACHE_DURATION_HOURS="1"
```

## 📞 Getting Help

### 1. Check Existing Resources
- ✅ Run diagnostic scripts first
- ✅ Review this troubleshooting guide
- ✅ Check [examples directory](../../examples/)
- ✅ Review [tool documentation](./tool-overview.md)

### 2. Gather Information
Before seeking help, collect:
- Error messages (full stack traces)
- Environment variables (`env | grep HEALTHIE`)
- Python version (`python --version`)
- Package versions (`uv show`)
- Operating system details

### 3. Report Issues
When reporting issues:
- Include diagnostic output
- Provide minimal reproduction steps
- Specify expected vs actual behavior
- Include relevant configuration

### 4. Community Resources
- Check existing GitHub issues
- Review documentation and examples
- Test with minimal configuration first

## ✅ Quick Resolution Checklist

When something isn't working:

- [ ] Run `uv sync` to ensure dependencies are installed
- [ ] Check you're in the `python-mcp-server` directory
- [ ] Run the basic imports test
- [ ] Verify environment variables are set
- [ ] Test with a simple query validation
- [ ] Check network connectivity to Healthie API
- [ ] Review error messages for specific issues
- [ ] Try with debug mode enabled

Most issues can be resolved by following these steps systematically.