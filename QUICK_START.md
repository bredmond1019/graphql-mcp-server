# Quick Start Guide

Get the Healthie MCP Server running in 5 minutes.

## Prerequisites

- Python 3.13+
- [UV package manager](https://docs.astral.sh/uv/) installed

## 1. Installation

```bash
# Clone and enter the repository
cd python-mcp-server

# Install dependencies
uv sync
```

## 2. Basic Setup

```bash
# Set required environment variables
export HEALTHIE_API_URL="https://staging-api.gethealthie.com/graphql"

# Optional: Add your Healthie API key for schema downloads
export HEALTHIE_API_KEY="your-api-key-here"
```

## 3. Test the Server

```bash
# Run in development mode with MCP Inspector
uv run mcp dev src/healthie_mcp/server.py:mcp
```

This opens the MCP Inspector in your browser where you can test all available tools.

## 4. Install in Claude Desktop

```bash
# Install the server for Claude Desktop
uv run mcp install src/healthie_mcp/server.py:mcp --name "Healthie Development Assistant"
```

## 5. Try It Out

### In MCP Inspector or Claude Desktop:

**Search the schema:**
```
search_schema(query: "patient", type_filter: "type")
```

**Get query templates:**
```
query_templates(workflow: "patient_management")
```

**Analyze healthcare patterns:**
```
find_healthcare_patterns(category: "appointments")
```

**Get code examples:**
```
code_examples(operation: "create_patient", language: "javascript")
```

## Available Tools

The server provides 11 specialized tools:

### Core Schema Tools
- **search_schema** - Search GraphQL schema with regex
- **introspect_type** - Get detailed type information
- **find_healthcare_patterns** - Detect healthcare workflows

### Developer Tools
- **query_templates** - Pre-built GraphQL queries
- **code_examples** - Multi-language code samples
- **input_validation** - Validate GraphQL inputs
- **error_decoder** - Interpret and solve errors
- **query_performance** - Analyze query performance
- **field_relationships** - Explore field connections
- **workflow_sequences** - Multi-step workflow guidance
- **field_usage** - Field usage recommendations

## Next Steps

- See [DEV_SETUP.md](DEV_SETUP.md) for development environment setup
- Check out [CLAUDE.md](CLAUDE.md) for architecture details
- Explore the configuration files in `src/healthie_mcp/config/data/` to customize tool behavior

## Troubleshooting

**Schema not found?**
- Make sure `HEALTHIE_API_URL` is set
- Add `HEALTHIE_API_KEY` if you have one
- The server will work with limited functionality without a schema

**Tools not working?**
- Check that all dependencies are installed: `uv sync`
- Verify the server is running: `uv run mcp dev src/healthie_mcp/server.py:mcp`

**Need help?**
- Run tests to verify installation: `uv run pytest`
- Check the logs for error messages
- Review environment variables are set correctly