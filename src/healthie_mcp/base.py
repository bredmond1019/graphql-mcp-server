"""Base classes and protocols for Healthie MCP tools."""

from abc import ABC, abstractmethod
from typing import Protocol, TypeVar, Generic, Any, Optional
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

# Type variable for tool results
TResult = TypeVar('TResult', bound=BaseModel)


class SchemaManagerProtocol(Protocol):
    """Protocol defining the interface for schema management."""
    
    def get_schema_content(self) -> Optional[str]:
        """Get the current GraphQL schema content."""
        ...
    
    def refresh_schema(self, force: bool = False) -> bool:
        """Refresh the schema from the API."""
        ...


class BaseTool(ABC, Generic[TResult]):
    """Base class for all MCP tools."""
    
    def __init__(self, schema_manager: SchemaManagerProtocol):
        """Initialize the tool with a schema manager.
        
        Args:
            schema_manager: The schema manager instance for accessing GraphQL schema
        """
        self.schema_manager = schema_manager
    
    @abstractmethod
    def get_tool_name(self) -> str:
        """Get the name of this tool as it will be registered with MCP.
        
        Returns:
            The tool name (e.g., "search_schema", "validate_input")
        """
        pass
    
    @abstractmethod
    def get_tool_description(self) -> str:
        """Get the description of this tool for documentation.
        
        Returns:
            A comprehensive description of what the tool does
        """
        pass
    
    @abstractmethod
    def execute(self, **kwargs: Any) -> TResult:
        """Execute the tool with the given parameters.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            The tool's result as a Pydantic model
        """
        pass
    
    def setup(self, mcp: FastMCP) -> None:
        """Register this tool with the MCP server.
        
        Args:
            mcp: The FastMCP server instance
        """
        tool_name = self.get_tool_name()
        tool_func = self.execute
        tool_func.__name__ = tool_name
        tool_func.__doc__ = self.get_tool_description()
        
        # Register with MCP
        mcp.tool()(tool_func)


class BaseSetupFunction(ABC):
    """Base class for tool setup functions following the existing pattern."""
    
    @abstractmethod
    def setup_tool(self, mcp: FastMCP, schema_manager: SchemaManagerProtocol) -> None:
        """Setup the tool with the MCP server.
        
        Args:
            mcp: The FastMCP server instance
            schema_manager: The schema manager for accessing GraphQL schema
        """
        pass


class ToolRegistry:
    """Registry for managing all available tools."""
    
    def __init__(self):
        """Initialize the tool registry."""
        self._tools: list[BaseTool] = []
        self._setup_functions: list[BaseSetupFunction] = []
    
    def register_tool(self, tool: BaseTool) -> None:
        """Register a tool instance.
        
        Args:
            tool: The tool to register
        """
        self._tools.append(tool)
    
    def register_setup_function(self, setup_func: BaseSetupFunction) -> None:
        """Register a setup function.
        
        Args:
            setup_func: The setup function to register
        """
        self._setup_functions.append(setup_func)
    
    def setup_all_tools(self, mcp: FastMCP, schema_manager: SchemaManagerProtocol) -> None:
        """Setup all registered tools with the MCP server.
        
        Args:
            mcp: The FastMCP server instance
            schema_manager: The schema manager for accessing GraphQL schema
        """
        # Setup tools using the new pattern
        for tool in self._tools:
            tool.setup(mcp)
        
        # Setup tools using the existing pattern
        for setup_func in self._setup_functions:
            setup_func.setup_tool(mcp, schema_manager)