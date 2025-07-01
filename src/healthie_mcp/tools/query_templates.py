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


class QueryTemplateConstants:
    """Constants for query template tool."""
    
    # Template usage tips
    TEMPLATE_TIPS = [
        "Always validate required variables before executing queries",
        "Use the include_variables parameter to see example values", 
        "Check the notes field for important usage information",
        "Combine multiple queries in a single request for better performance",
        "Test mutations in a staging environment first",
        "Use fragments to reduce query complexity and improve maintainability",
        "Consider query depth limits when building nested queries",
        "Apply appropriate pagination for large result sets"
    ]
    
    # Required template fields for validation
    REQUIRED_TEMPLATE_FIELDS = {"name", "description", "query"}
    
    # Optional template fields with defaults
    OPTIONAL_TEMPLATE_FIELDS = {
        "variables": {},
        "required_variables": [],
        "optional_variables": [],
        "notes": ""
    }


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
            self._ensure_templates_loaded()
            
            # Validate and convert workflow filter
            workflow_filter = self._validate_workflow(workflow)
            
            # Process templates
            templates = self._process_templates(workflow_filter, include_variables)
            
            # Generate result
            return self._build_result(templates, workflow)
            
        except ConfigurationError as e:
            raise ToolError(
                "Failed to load query templates configuration",
                {"error": str(e)}
            )
        except ToolError:
            raise
        except Exception as e:
            raise ToolError(
                f"Failed to retrieve query templates: {str(e)}",
                {"workflow": workflow}
            )
    
    def _ensure_templates_loaded(self) -> None:
        """Ensure templates are loaded from configuration."""
        if self._templates_cache is None:
            self._templates_cache = self.config_loader.load_queries()
    
    def _validate_workflow(self, workflow: Optional[str]) -> Optional[WorkflowCategory]:
        """Validate workflow parameter and convert to enum.
        
        Args:
            workflow: Workflow string to validate
            
        Returns:
            WorkflowCategory enum or None if no workflow specified
            
        Raises:
            ToolError: If workflow is invalid
        """
        if not workflow:
            return None
            
        try:
            return WorkflowCategory(workflow)
        except ValueError:
            available = [w.value for w in WorkflowCategory]
            raise ToolError(
                f"Invalid workflow: {workflow}",
                {"available_workflows": available}
            )
    
    def _process_templates(
        self, 
        workflow_filter: Optional[WorkflowCategory], 
        include_variables: bool
    ) -> List[QueryTemplate]:
        """Process templates from configuration data.
        
        Args:
            workflow_filter: Optional workflow to filter by
            include_variables: Whether to include variables
            
        Returns:
            List of processed QueryTemplate objects
        """
        templates = []
        
        for category_key, category_templates in self._templates_cache.items():
            category = self._parse_category(category_key)
            if not category:
                continue
                
            # Apply workflow filter
            if workflow_filter and category != workflow_filter:
                continue
            
            # Process templates in this category
            for template_data in category_templates:
                if self._is_valid_template_data(template_data):
                    template = self._create_template(template_data, category, include_variables)
                    templates.append(template)
        
        return templates
    
    def _parse_category(self, category_key: str) -> Optional[WorkflowCategory]:
        """Parse category key to WorkflowCategory enum.
        
        Args:
            category_key: Category key from configuration
            
        Returns:
            WorkflowCategory enum or None if invalid
        """
        try:
            return WorkflowCategory(category_key)
        except ValueError:
            return None
    
    def _is_valid_template_data(self, template_data: Dict[str, Any]) -> bool:
        """Validate template data has required fields.
        
        Args:
            template_data: Template data to validate
            
        Returns:
            True if valid, False otherwise
        """
        return (isinstance(template_data, dict) and 
                QueryTemplateConstants.REQUIRED_TEMPLATE_FIELDS.issubset(template_data.keys()))
    
    def _create_template(
        self, 
        template_data: Dict[str, Any], 
        category: WorkflowCategory, 
        include_variables: bool
    ) -> QueryTemplate:
        """Create QueryTemplate object from data.
        
        Args:
            template_data: Raw template data
            category: Template category
            include_variables: Whether to include variables
            
        Returns:
            QueryTemplate object
        """
        return QueryTemplate(
            name=template_data["name"],
            description=template_data["description"],
            category=category,
            query=template_data["query"],
            variables=template_data.get("variables", {}) if include_variables else {},
            required_variables=template_data.get("required_variables", []),
            optional_variables=template_data.get("optional_variables", []),
            notes=template_data.get("notes", "")
        )
    
    def _build_result(self, templates: List[QueryTemplate], workflow: Optional[str]) -> QueryTemplatesResult:
        """Build the final result object.
        
        Args:
            templates: Processed templates
            workflow: Original workflow filter
            
        Returns:
            QueryTemplatesResult object
        """
        # Count templates by category
        category_counts = {}
        for template in templates:
            category_counts[template.category.value] = category_counts.get(template.category.value, 0) + 1
        
        return QueryTemplatesResult(
            templates=templates,
            total_count=len(templates),
            categories_available=[cat.value for cat in WorkflowCategory],
            filtered_by=workflow,
            tips=self._get_template_tips(),
            template_counts_by_category=category_counts
        )
    
    def _get_template_tips(self) -> List[str]:
        """Get helpful tips for using the templates.
        
        Returns:
            List of tip strings
        """
        return QueryTemplateConstants.TEMPLATE_TIPS


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