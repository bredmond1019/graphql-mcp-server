"""Pre-built GraphQL query templates for common operations.

This tool provides templates for frequently used GraphQL queries and mutations
in the Healthie API, organized by workflow categories.
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

from ..models.query_templates import QueryTemplatesResult, QueryTemplate, WorkflowCategory
from ..base import BaseTool, SchemaManagerProtocol
from ..config.loader import get_config_loader
from ..exceptions import ConfigurationError, ToolError


class QueryTemplatesInput(BaseModel):
    """Input parameters for the query templates tool."""
    
    workflow: Optional[str] = Field(
        None,
        description="Filter templates by workflow (patient_management, appointments, clinical_data, billing)"
    )
    
    include_variables: bool = Field(
        True,
        description="Include example variables with each template"
    )


class QueryTemplatesTool(BaseTool[QueryTemplatesResult]):
    """Tool for retrieving pre-built GraphQL query templates."""
    
    def __init__(self, schema_manager: SchemaManagerProtocol):
        """Initialize the tool.
        
        Args:
            schema_manager: Schema manager instance (required for consistency)
        """
        super().__init__(schema_manager)
        self.config_loader = get_config_loader()
        self._templates_cache: Optional[Dict[str, List[Dict[str, Any]]]] = None
    
    def get_tool_name(self) -> str:
        """Get the tool name."""
        return "query_templates"
    
    def get_tool_description(self) -> str:
        """Get the tool description."""
        return "Get pre-built GraphQL queries and mutations for common Healthie operations"
    
    def execute(
        self,
        workflow: Optional[str] = None,
        include_variables: bool = True
    ) -> QueryTemplatesResult:
        """Get query templates for common operations.
        
        Args:
            workflow: Optional workflow filter
            include_variables: Whether to include example variables
            
        Returns:
            QueryTemplatesResult containing the templates
        """
        try:
            # Load templates from configuration
            if self._templates_cache is None:
                self._templates_cache = self.config_loader.load_queries()
            
            templates = []
            
            # Convert workflow string to enum if provided
            workflow_filter = None
            if workflow:
                try:
                    workflow_filter = WorkflowCategory(workflow)
                except ValueError:
                    available = [w.value for w in WorkflowCategory]
                    raise ToolError(
                        f"Invalid workflow: {workflow}",
                        {"available_workflows": available}
                    )
            
            # Process templates from configuration
            for category_key, category_templates in self._templates_cache.items():
                # Map category key to enum
                try:
                    category = WorkflowCategory(category_key)
                except ValueError:
                    continue  # Skip unknown categories
                
                # Apply workflow filter
                if workflow_filter and category != workflow_filter:
                    continue
                
                # Convert templates
                for template_data in category_templates:
                    template = QueryTemplate(
                        name=template_data["name"],
                        description=template_data["description"],
                        category=category,
                        query=template_data["query"],
                        variables=template_data.get("variables", {}) if include_variables else {},
                        required_variables=template_data.get("required_variables", []),
                        optional_variables=template_data.get("optional_variables", []),
                        notes=template_data.get("notes", "")
                    )
                    templates.append(template)
            
            # Generate tips
            tips = self._generate_tips()
            
            # Count by category
            category_counts = {}
            for template in templates:
                category_counts[template.category.value] = category_counts.get(template.category.value, 0) + 1
            
            return QueryTemplatesResult(
                templates=templates,
                total_count=len(templates),
                categories_available=[cat.value for cat in WorkflowCategory],
                filtered_by=workflow,
                tips=tips,
                template_counts_by_category=category_counts
            )
            
        except ConfigurationError as e:
            raise ToolError(
                "Failed to load query templates configuration",
                {"error": str(e)}
            )
        except Exception as e:
            raise ToolError(
                f"Failed to retrieve query templates: {str(e)}",
                {"workflow": workflow}
            )
    
    def _generate_tips(self) -> List[str]:
        """Generate helpful tips for using the templates.
        
        Returns:
            List of tip strings
        """
        return [
            "Always validate required variables before executing queries",
            "Use the include_variables parameter to see example values",
            "Check the notes field for important usage information",
            "Combine multiple queries in a single request for better performance",
            "Test mutations in a staging environment first"
        ]


def setup_query_templates_tool(mcp, schema_manager) -> None:
    """Set up the query templates tool.
    
    Args:
        mcp: MCP server instance
        schema_manager: Schema manager instance
    """
    tool = QueryTemplatesTool(schema_manager)
    
    @mcp.tool()
    async def query_templates(
        workflow: Optional[str] = None,
        include_variables: bool = True
    ) -> QueryTemplatesResult:
        """Get pre-built GraphQL queries and mutations for common Healthie operations.
        
        Args:
            workflow: Optional workflow filter (patient_management, appointments, clinical_data, billing)
            include_variables: Whether to include example variables with each template
            
        Returns:
            QueryTemplatesResult containing the templates
        """
        return tool.execute(workflow=workflow, include_variables=include_variables)