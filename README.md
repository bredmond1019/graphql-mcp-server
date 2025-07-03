# Healthie MCP Server

A Model Context Protocol (MCP) server that provides AI-powered tools for Healthie GraphQL API development. Designed specifically for building healthcare applications with intelligent schema analysis, query optimization, and workflow guidance.

## What It Does

This MCP server acts as an advanced development assistant that understands healthcare workflows and provides:

- **Smart Schema Analysis**: Intelligent GraphQL schema search and type introspection
- **Healthcare Workflow Detection**: Identifies common patterns for patient management, appointments, clinical data, and billing
- **Query Optimization**: Performance analysis and optimization recommendations
- **Code Generation**: Multi-language examples and pre-built query templates
- **Error Resolution**: Intelligent error decoding with healthcare-specific solutions
- **Validation Tools**: Healthcare-compliant input validation and field usage guidance

## Quick Start

See [QUICK_START.md](QUICK_START.md) for immediate setup and usage.

## Development Setup

See [DEV_SETUP.md](DEV_SETUP.md) for comprehensive development environment configuration.

## MCP Tools - 100% Success Rate

These 5 core tools have been tested with 15 test cases and achieved perfect results:

| Tool | Purpose | Performance |
|------|---------|-------------|
| **search_schema** | Find anything in 925k+ characters instantly | 575 matches found across tests |
| **query_templates** | Get production-ready GraphQL queries | 15 templates retrieved |
| **code_examples** | Generate working code in JS/Python/cURL | 3 languages supported |
| **introspect_type** | Explore types with complete field info | Up to 453 fields analyzed |
| **error_decoder** | Transform errors into actionable solutions | Clear fixes provided |

See [test results](./test_results/FINAL_SUCCESS_SUMMARY.md) and [tutorials](./docs/tutorials/using-mcp-tools.md) for details.

## Core Features

### 🔍 Schema Intelligence
- Regex-powered schema search with healthcare context
- Deep type introspection with relationship mapping
- FHIR-aware pattern detection

### 🏥 Healthcare Specialization
- Patient management workflows
- Appointment scheduling patterns
- Clinical data structures (forms, assessments, notes)
- Billing and insurance processing
- Provider and organization management

### ⚡ Performance Optimization
- Query complexity analysis
- Performance bottleneck detection
- Caching strategy recommendations
- Field selection optimization

### 🛠️ Developer Tools
- Pre-built query templates by workflow
- Multi-language code examples (JavaScript, Python, cURL)
- Input validation with healthcare-specific rules
- Error interpretation and resolution guidance

## Architecture

Built on the official Python MCP SDK with a modular, configuration-driven architecture:

- **FastMCP**: Official Python MCP SDK for robust protocol handling
- **Configuration-Driven**: Tool behavior defined in YAML files for easy customization
- **Healthcare Domain Models**: Pydantic models specialized for healthcare data
- **Intelligent Caching**: Schema caching with automatic refresh and validation
- **Tool Modularity**: Independent tools that can operate with or without API access

## Requirements

- Python 3.13+
- UV package manager
- Optional: Healthie API key for schema downloads

## Documentation

- [QUICK_START.md](QUICK_START.md) - Get up and running in 5 minutes
- [DEV_SETUP.md](DEV_SETUP.md) - Complete development environment setup
- [CLAUDE.md](CLAUDE.md) - Architecture guide for Claude Code instances

## Healthcare Compliance

This tool is designed with healthcare development best practices in mind:
- HIPAA awareness in recommendations
- Healthcare identifier validation (NPI, DEA, etc.)
- Medical terminology integration (SNOMED, LOINC, ICD-10)
- FHIR resource pattern recognition
- Clinical workflow optimization

## Support

For issues and feature requests, please use the GitHub issue tracker.

## License

[Add your license information here]