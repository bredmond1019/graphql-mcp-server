"""
Custom assertion helpers for Healthie MCP Server tests.

This module provides custom assertion functions that make tests more readable
and provide better error messages for common test scenarios.
"""

from typing import Any, Dict, List, Optional
import json


def assert_graphql_response_valid(response: Dict[str, Any]) -> None:
    """Assert that a GraphQL response has the expected structure."""
    assert isinstance(response, dict), "Response must be a dictionary"
    assert "data" in response or "errors" in response, "Response must contain 'data' or 'errors'"
    
    if "errors" in response:
        assert isinstance(response["errors"], list), "Errors must be a list"
        for error in response["errors"]:
            assert "message" in error, "Each error must have a message"


def assert_mcp_tool_response_valid(response: Dict[str, Any]) -> None:
    """Assert that an MCP tool response has the expected structure."""
    assert isinstance(response, dict), "MCP response must be a dictionary"
    # Add more specific MCP response validation as needed


def assert_schema_type_exists(schema: Dict[str, Any], type_name: str) -> None:
    """Assert that a GraphQL schema contains a specific type."""
    assert "data" in schema, "Schema must have 'data' field"
    assert "__schema" in schema["data"], "Schema data must have '__schema' field"
    assert "types" in schema["data"]["__schema"], "Schema must have 'types' field"
    
    type_names = [t["name"] for t in schema["data"]["__schema"]["types"]]
    assert type_name in type_names, f"Type '{type_name}' not found in schema. Available types: {type_names}"


def assert_schema_field_exists(schema: Dict[str, Any], type_name: str, field_name: str) -> None:
    """Assert that a GraphQL schema type contains a specific field."""
    assert_schema_type_exists(schema, type_name)
    
    # Find the type
    schema_type = None
    for t in schema["data"]["__schema"]["types"]:
        if t["name"] == type_name:
            schema_type = t
            break
    
    assert schema_type is not None, f"Type '{type_name}' not found"
    assert "fields" in schema_type, f"Type '{type_name}' has no fields"
    
    field_names = [f["name"] for f in schema_type["fields"]]
    assert field_name in field_names, f"Field '{field_name}' not found in type '{type_name}'. Available fields: {field_names}"


def assert_json_structure_matches(actual: Any, expected_structure: Dict[str, Any]) -> None:
    """Assert that a JSON object matches an expected structure."""
    def check_structure(actual_val: Any, expected_val: Any, path: str = "root") -> None:
        if isinstance(expected_val, dict):
            assert isinstance(actual_val, dict), f"Expected dict at {path}, got {type(actual_val)}"
            for key, expected_sub in expected_val.items():
                assert key in actual_val, f"Missing key '{key}' at {path}"
                check_structure(actual_val[key], expected_sub, f"{path}.{key}")
        elif isinstance(expected_val, list):
            assert isinstance(actual_val, list), f"Expected list at {path}, got {type(actual_val)}"
            if expected_val:  # If template list is not empty
                for i, item in enumerate(actual_val):
                    check_structure(item, expected_val[0], f"{path}[{i}]")
        elif isinstance(expected_val, type):
            assert isinstance(actual_val, expected_val), f"Expected {expected_val} at {path}, got {type(actual_val)}"
        # For primitive values, we just check the type unless it's a specific value
    
    check_structure(actual, expected_structure)


def assert_error_contains_message(error: Exception, expected_message: str) -> None:
    """Assert that an exception contains a specific message."""
    error_message = str(error)
    assert expected_message.lower() in error_message.lower(), \
        f"Expected error message to contain '{expected_message}', got: {error_message}"


def assert_list_contains_items(actual_list: List[Any], expected_items: List[Any]) -> None:
    """Assert that a list contains all expected items."""
    assert isinstance(actual_list, list), "First argument must be a list"
    
    for expected_item in expected_items:
        assert expected_item in actual_list, \
            f"Expected item '{expected_item}' not found in list: {actual_list}"


def assert_dict_contains_keys(actual_dict: Dict[str, Any], expected_keys: List[str]) -> None:
    """Assert that a dictionary contains all expected keys."""
    assert isinstance(actual_dict, dict), "First argument must be a dictionary"
    
    for expected_key in expected_keys:
        assert expected_key in actual_dict, \
            f"Expected key '{expected_key}' not found in dict. Available keys: {list(actual_dict.keys())}"