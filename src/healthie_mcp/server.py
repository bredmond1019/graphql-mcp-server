"""Healthie MCP Server using the official Python MCP SDK.

This server provides GraphQL schema assistance and Healthie-specific development tools
through the Model Context Protocol (MCP).
"""

import os
from mcp.server.fastmcp import FastMCP
from .config import get_settings
from .schema_manager import SchemaManager

# Core tools (always available)
from .tools.schema_search import setup_schema_search_tool
from .tools.type_introspection import setup_type_introspection_tool  
from .tools.query_templates import setup_query_templates_tool
from .tools.field_relationships import setup_field_relationship_tool
from .tools.code_examples import setup_code_examples_tool
from .tools.error_decoder import setup_error_decoder_tool
from .tools.workflow_sequences import setup_workflow_sequence_tool
from .tools.compliance_checker import setup_compliance_checker_tool

# Additional tools (dev environment only)
from .tools.additional.input_validation import setup_input_validation_tool
from .tools.additional.performance_analyzer import setup_query_performance_tool
from .tools.additional.healthcare_patterns import setup_healthcare_patterns_tool
from .tools.additional.rate_limit_advisor import setup_rate_limit_advisor_tool
from .tools.additional.field_usage import setup_field_usage_tool
from .tools.additional.integration_testing import setup_integration_testing_tool
from .tools.additional.webhook_configurator import setup_webhook_configurator_tool
from .tools.additional.api_usage_analytics import setup_api_usage_analytics_tool
from .tools.additional.environment_manager import setup_environment_manager_tool

# Create the FastMCP server
mcp = FastMCP("Healthie Development Assistant")

# Initialize components
settings = get_settings()
schema_manager = SchemaManager(
    api_endpoint=str(settings.healthie_api_url),
    cache_dir=settings.schema_dir
)

# Setup core tools (8 total - always available)
setup_schema_search_tool(mcp, schema_manager)
setup_type_introspection_tool(mcp, schema_manager)
setup_query_templates_tool(mcp, schema_manager)
setup_field_relationship_tool(mcp, schema_manager)
setup_code_examples_tool(mcp, schema_manager)
setup_error_decoder_tool(mcp, schema_manager)
setup_workflow_sequence_tool(mcp, schema_manager)
setup_compliance_checker_tool(mcp, schema_manager)

# Setup additional tools (9 total - dev environment only)
# Enable with: export HEALTHIE_ENABLE_ADDITIONAL_TOOLS=true
enable_additional_tools = os.getenv("HEALTHIE_ENABLE_ADDITIONAL_TOOLS", "false").lower() == "true"

if enable_additional_tools:
    print("🧪 Additional tools enabled - loading 9 additional tools...")
    setup_input_validation_tool(mcp, schema_manager)
    setup_query_performance_tool(mcp, schema_manager)
    setup_healthcare_patterns_tool(mcp, schema_manager)
    setup_rate_limit_advisor_tool(mcp, schema_manager)
    setup_field_usage_tool(mcp, schema_manager)
    setup_integration_testing_tool(mcp, schema_manager)
    setup_webhook_configurator_tool(mcp, schema_manager)
    setup_api_usage_analytics_tool(mcp, schema_manager)
    setup_environment_manager_tool(mcp, schema_manager)
    print("✅ All 17 tools loaded (8 core + 9 additional)")
else:
    print("📋 Running with 8 core tools only. Set HEALTHIE_ENABLE_ADDITIONAL_TOOLS=true to enable 9 additional tools.")

@mcp.resource("healthie://schema/current")
def get_current_schema() -> str:
    """Get the current Healthie GraphQL schema."""
    return schema_manager.get_schema_content()

@mcp.resource("healthie://config")
def get_server_config() -> str:
    """Get the current server configuration."""
    return f"""Healthie MCP Server Configuration:
- API URL: {settings.healthie_api_url}
- Schema Directory: {settings.schema_dir}
- Cache Enabled: {settings.cache_enabled}
- Log Level: {settings.log_level}
"""

if __name__ == "__main__":
    mcp.run()