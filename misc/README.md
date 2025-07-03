# Miscellaneous Development Utilities

This directory contains various development and testing utilities for the Healthie MCP server.

## Test Scripts

### Environment and Setup Verification

- **`test_env.py`** - Verifies that environment variables are being loaded correctly from `.env.development`
- **`verify_setup.py`** - Comprehensive verification of the MCP server setup, checking imports, settings, and tool availability

### Tool Testing

- **`test_all_tools.py`** - Attempts to test all 8 MCP tools by directly instantiating tool classes
- **`test_tools_direct.py`** - Direct testing of MCP tools using their class interfaces
- **`test_tools_live.py`** - Tests MCP tools through the live server interface
- **`test_phase_2_simple.py`** - Generates comprehensive test results for all 8 working tools
- **`test_phase_2_all_tools.py`** - Extended test suite with multiple test cases per tool
- **`test_mcp_tools.py`** - Original MCP tools testing script
- **`test_mcp_tools_fixed.py`** - Fixed version of MCP tools testing
- **`test_local_server.py`** - Tests for local server functionality
- **`test_with_schema.py`** - Tests that require a GraphQL schema
- **`test_tools.py`** - General tool testing utilities

### Server Runners and Utilities

- **`run_server.py`** - Basic server runner for testing
- **`run_server_with_auth.py`** - Runs the MCP server with explicit authentication setup
- **`download_schema.py`** - Downloads the GraphQL schema from Healthie API

### Documentation

- **`MCP_TEST_SUMMARY.md`** - Summary of MCP tool tests
- **`TEST_SUMMARY.md`** - General test summary

## Usage

Most scripts can be run directly with UV:

```bash
# Verify environment setup
uv run python misc/verify_setup.py

# Test environment variables
uv run python misc/test_env.py

# Run comprehensive tool tests
uv run python misc/test_phase_2_simple.py

# Download GraphQL schema
uv run python misc/download_schema.py
```

## Notes

- All scripts now use environment variables from `.env.development` instead of hardcoded API keys
- Make sure you have copied `.env.development.example` to `.env.development` and added your API key
- Test results are saved to the `test_results/` directory
- These files are kept for reference and development but are not part of the main codebase