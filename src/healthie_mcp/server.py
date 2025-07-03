"""Healthie MCP Server using the official Python MCP SDK.

This server provides GraphQL schema assistance and Healthie-specific development tools
through the Model Context Protocol (MCP).
"""

from mcp.server.fastmcp import FastMCP
from .config import get_settings
from .schema_manager import SchemaManager
from .tools.schema_search import setup_schema_search_tool
from .tools.type_introspection import setup_type_introspection_tool  
from .tools.query_templates import setup_query_templates_tool
from .tools.field_relationships import setup_field_relationship_tool
from .tools.code_examples import setup_code_examples_tool
from .tools.error_decoder import setup_error_decoder_tool
from .tools.workflow_sequences import setup_workflow_sequence_tool
from .tools.compliance_checker import setup_compliance_checker_tool

# Create the FastMCP server
mcp = FastMCP("Healthie Development Assistant")

# Initialize components
settings = get_settings()
schema_manager = SchemaManager(
    api_endpoint=str(settings.healthie_api_url),
    cache_dir=settings.schema_dir
)

# Setup working tools (8 total)
setup_schema_search_tool(mcp, schema_manager)
setup_type_introspection_tool(mcp, schema_manager)
setup_query_templates_tool(mcp, schema_manager)
setup_field_relationship_tool(mcp, schema_manager)
setup_code_examples_tool(mcp, schema_manager)
setup_error_decoder_tool(mcp, schema_manager)
setup_workflow_sequence_tool(mcp, schema_manager)
setup_compliance_checker_tool(mcp, schema_manager)

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