"""Utility modules for the Healthie MCP server."""

from .graphql_utils import (
    parse_graphql_type,
    is_scalar_type,
    extract_field_type,
    get_line_type,
    find_type_definition
)

from .validation_utils import (
    validate_email,
    validate_phone,
    validate_date,
    validate_datetime,
    is_future_date
)

from .text_utils import (
    pluralize,
    camel_to_snake,
    snake_to_camel,
    truncate_text
)

__all__ = [
    # GraphQL utilities
    "parse_graphql_type",
    "is_scalar_type",
    "extract_field_type",
    "get_line_type",
    "find_type_definition",
    
    # Validation utilities
    "validate_email",
    "validate_phone",
    "validate_date",
    "validate_datetime",
    "is_future_date",
    
    # Text utilities
    "pluralize",
    "camel_to_snake",
    "snake_to_camel",
    "truncate_text"
]