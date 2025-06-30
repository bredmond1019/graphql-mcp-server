"""Custom exceptions for the Healthie MCP server."""

from typing import Optional, Dict, Any


class HealthieMCPError(Exception):
    """Base exception for all Healthie MCP errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize the error with a message and optional details.
        
        Args:
            message: The error message
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary for API responses.
        
        Returns:
            Dictionary representation of the error
        """
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }


class SchemaError(HealthieMCPError):
    """Errors related to GraphQL schema operations."""
    pass


class SchemaNotFoundError(SchemaError):
    """Raised when the GraphQL schema is not available."""
    
    def __init__(self, message: str = "GraphQL schema not available"):
        super().__init__(message)


class SchemaParseError(SchemaError):
    """Raised when the GraphQL schema cannot be parsed."""
    
    def __init__(self, message: str = "Failed to parse GraphQL schema", parse_error: Optional[str] = None):
        details = {"parse_error": parse_error} if parse_error else {}
        super().__init__(message, details)


class ValidationError(HealthieMCPError):
    """Errors related to input validation."""
    pass


class InvalidMutationError(ValidationError):
    """Raised when a mutation is not found in the schema."""
    
    def __init__(self, mutation_name: str):
        super().__init__(
            f"Mutation '{mutation_name}' not found in schema",
            {"mutation_name": mutation_name}
        )


class InvalidInputError(ValidationError):
    """Raised when input data is invalid."""
    
    def __init__(self, field: str, reason: str):
        super().__init__(
            f"Invalid input for field '{field}': {reason}",
            {"field": field, "reason": reason}
        )


class ToolError(HealthieMCPError):
    """Errors related to tool execution."""
    pass


class ToolExecutionError(ToolError):
    """Raised when a tool fails to execute."""
    
    def __init__(self, tool_name: str, reason: str):
        super().__init__(
            f"Tool '{tool_name}' failed to execute: {reason}",
            {"tool_name": tool_name, "reason": reason}
        )


class ConfigurationError(HealthieMCPError):
    """Errors related to configuration."""
    pass


class MissingConfigurationError(ConfigurationError):
    """Raised when required configuration is missing."""
    
    def __init__(self, config_key: str):
        super().__init__(
            f"Missing required configuration: {config_key}",
            {"config_key": config_key}
        )


class InvalidConfigurationError(ConfigurationError):
    """Raised when configuration values are invalid."""
    
    def __init__(self, config_key: str, value: Any, reason: str):
        super().__init__(
            f"Invalid configuration for '{config_key}': {reason}",
            {"config_key": config_key, "value": str(value), "reason": reason}
        )


class NetworkError(HealthieMCPError):
    """Errors related to network operations."""
    pass


class APIConnectionError(NetworkError):
    """Raised when connection to the Healthie API fails."""
    
    def __init__(self, endpoint: str, reason: str):
        super().__init__(
            f"Failed to connect to {endpoint}: {reason}",
            {"endpoint": endpoint, "reason": reason}
        )


class APIResponseError(NetworkError):
    """Raised when the API returns an unexpected response."""
    
    def __init__(self, status_code: int, response_body: Optional[str] = None):
        super().__init__(
            f"API returned status code {status_code}",
            {"status_code": status_code, "response_body": response_body}
        )