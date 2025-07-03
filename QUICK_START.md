# Quick Start Guide

Get the Healthie MCP Server running in 5 minutes and start using 8 powerful healthcare development tools.

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

## 5. Try the 8 Working Tools

All tools have been thoroughly tested with **100% success rate**. Here are real examples that work:

### 🔍 **search_schema** - Find anything in the GraphQL schema
```json
{
  "query": "patient",
  "type_filter": "all"
}
```
**What it does:** Searches through the entire Healthie GraphQL schema to find types, fields, arguments, and enums related to your query.

### 📋 **query_templates** - Generate ready-to-use GraphQL queries
```json
{
  "operation_name": "appointment",
  "operation_type": "query"
}
```
**What it does:** Creates complete GraphQL query templates with all available fields and proper variable definitions.

### 💻 **code_examples** - Get working code in multiple languages
```json
{
  "operation": "createPatient",
  "language": "python",
  "include_auth": true
}
```
**What it does:** Generates complete, runnable code examples with authentication, error handling, and best practices.

### 🔎 **introspect_type** - Deep dive into GraphQL types
```json
{
  "type_name": "Patient",
  "include_deprecated": false
}
```
**What it does:** Provides detailed information about GraphQL types, including all fields, relationships, and deprecation status.

### 🛠️ **error_decoder** - Fix GraphQL errors instantly
```json
{
  "error_message": "Field 'invalidField' doesn't exist on type 'Patient'",
  "query": "{ patient { invalidField } }"
}
```
**What it does:** Analyzes GraphQL errors and provides specific solutions with corrected queries.

### ✅ **compliance_checker** - Ensure HIPAA/healthcare compliance
```json
{
  "query": "{ patients { id email medicalRecords } }",
  "frameworks": ["HIPAA", "HITECH"]
}
```
**What it does:** Analyzes GraphQL queries for healthcare compliance violations and provides audit recommendations.

### 🔄 **workflow_sequences** - Multi-step healthcare workflows
```json
{
  "workflow_type": "patient_onboarding"
}
```
**What it does:** Provides step-by-step workflows for complex healthcare processes like patient registration and appointment scheduling.

### 🔗 **field_relationships** - Explore data connections
```json
{
  "field_name": "patient",
  "include_scalars": false
}
```
**What it does:** Maps relationships between GraphQL fields to help you understand data structure and navigation paths.

## Available Tools Summary

**8 Production-Ready Tools (100% Success Rate):**

| Tool | Purpose | Use Case |
|------|---------|----------|
| `search_schema` | Schema exploration | Find available operations and types |
| `query_templates` | Query generation | Get ready-to-use GraphQL templates |
| `code_examples` | Code generation | Complete examples in Python/TypeScript/JavaScript |
| `introspect_type` | Type analysis | Understand data structures in detail |
| `error_decoder` | Error resolution | Fix GraphQL errors with specific solutions |
| `compliance_checker` | Healthcare compliance | Ensure HIPAA/HITECH compliance |
| `workflow_sequences` | Process guidance | Multi-step healthcare workflows |
| `field_relationships` | Data mapping | Explore field connections and relationships |

## Real-World Example Workflow

Here's how to use multiple tools together for patient management:

### Step 1: Explore the schema
```bash
# Find patient-related operations
search_schema(query: "patient", type_filter: "all")
```

### Step 2: Get a query template
```bash
# Generate a patient query template
query_templates(operation_name: "patient", operation_type: "query")
```

### Step 3: Generate working code
```bash
# Get Python code for patient queries
code_examples(operation: "patient", language: "python", include_auth: true)
```

### Step 4: Check compliance
```bash
# Ensure the query is HIPAA compliant
compliance_checker(query: "{ patient(id: \"123\") { id firstName email } }", frameworks: ["HIPAA"])
```

## Test Results Reference

All tools have been comprehensively tested. View detailed test results:
- **Phase 2 Summary:** `/test_results/phase_2/PHASE_2_SUMMARY.md`
- **Individual Tool Tests:** `/test_results/phase_2/01_search_schema_detailed.md` through `08_field_relationships_detailed.md`
- **16 successful tests** across 8 tools with **100% success rate**

## Next Steps

### For Developers
- Explore `/examples/` for complete integration examples
- Check `/docs/guides/` for detailed usage guides
- See `/test_results/phase_2/` for comprehensive test results

### For Integration
- Review `/examples/integrations/python/` for Python client setup
- Check `/examples/integrations/javascript/` for frontend integration
- Use `/examples/workflows/patient-management/` for healthcare workflows

## Troubleshooting

### Common Issues

**❌ Schema not found?**
- ✅ Ensure `HEALTHIE_API_URL` is set: `export HEALTHIE_API_URL="https://staging-api.gethealthie.com/graphql"`
- ✅ Add `HEALTHIE_API_KEY` if available
- ✅ Server works with limited functionality without schema

**❌ Tools not working in MCP Inspector?**
- ✅ Verify installation: `uv sync`
- ✅ Check server status: `uv run mcp dev src/healthie_mcp/server.py:mcp`
- ✅ Ensure browser opens to MCP Inspector interface

**❌ Claude Desktop integration failing?**
- ✅ Reinstall: `uv run mcp install src/healthie_mcp/server.py:mcp --name "Healthie Development Assistant"`
- ✅ Restart Claude Desktop after installation
- ✅ Check Claude Desktop logs for connection errors

**❌ Environment variables not working?**
- ✅ Check current values: `echo $HEALTHIE_API_URL`
- ✅ Re-export if needed: `export HEALTHIE_API_URL="https://staging-api.gethealthie.com/graphql"`
- ✅ Add to your shell profile (`.bashrc`, `.zshrc`) for persistence

### Verification Commands

**Test installation:**
```bash
uv run pytest tests/ -v
```

**Verify MCP tools:**
```bash
python misc/test_phase_2_simple.py
```

**Check server health:**
```bash
python misc/run_server.py
```

### Getting Help

1. **Check test results**: Review `/test_results/phase_2/PHASE_2_SUMMARY.md` for working examples
2. **Run diagnostics**: Use `uv run pytest tests/test_setup.py` to verify environment
3. **View logs**: Check console output from `uv run mcp dev` for error details
4. **Example code**: Reference `/examples/` directory for working integrations

### Performance Tips

- **Schema caching**: First run downloads schema locally for faster subsequent operations
- **Tool selection**: Use specific tools rather than trying all 8 for better performance
- **Error handling**: Use `error_decoder` tool when GraphQL queries fail
- **Compliance**: Run `compliance_checker` early in development to catch issues

## Success Indicators

✅ MCP Inspector opens in browser  
✅ All 8 tools listed in interface  
✅ Sample queries return realistic healthcare data  
✅ No errors in console output  
✅ Claude Desktop shows "Healthie Development Assistant" in MCP settings