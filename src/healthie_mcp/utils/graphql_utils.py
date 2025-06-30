"""GraphQL-related utility functions."""

import re
from typing import Optional, Dict, Any, List, Tuple
from ..constants import GRAPHQL_SCALAR_TYPES, GraphQLTypeKind


def parse_graphql_type(type_str: str) -> Dict[str, Any]:
    """Parse a GraphQL type string into its components.
    
    Args:
        type_str: GraphQL type string (e.g., "[String!]!", "ID", "User!")
        
    Returns:
        Dictionary with type information including base type, nullability, and list status
    """
    original = type_str
    is_list = '[' in type_str and ']' in type_str
    is_required = type_str.endswith('!')
    is_list_items_required = False
    
    if is_list:
        # Extract list item requirement
        match = re.match(r'\[(.+?)(!?)\](!?)', type_str)
        if match:
            base_type = match.group(1)
            is_list_items_required = match.group(2) == '!'
            is_required = match.group(3) == '!'
        else:
            base_type = type_str.strip('[]!')
    else:
        base_type = type_str.rstrip('!')
    
    return {
        'original': original,
        'base_type': base_type,
        'is_required': is_required,
        'is_list': is_list,
        'is_list_items_required': is_list_items_required,
        'is_scalar': base_type in GRAPHQL_SCALAR_TYPES
    }


def is_scalar_type(type_name: str) -> bool:
    """Check if a type is a GraphQL scalar.
    
    Args:
        type_name: The type name to check
        
    Returns:
        True if the type is a scalar, False otherwise
    """
    # Strip modifiers like ! and []
    base_type = type_name.strip('[]!')
    return base_type in GRAPHQL_SCALAR_TYPES


def extract_field_type(field_definition: str) -> str:
    """Extract the type from a GraphQL field definition.
    
    Args:
        field_definition: The field definition line
        
    Returns:
        The field type or "Unknown" if not found
    """
    # Remove arguments if present
    cleaned = re.sub(r'\([^)]*\)', '', field_definition)
    
    # Extract type after colon
    type_match = re.search(r':\s*([^!\s]+(?:\s*[!\[\]]+)*)', cleaned)
    if type_match:
        return type_match.group(1).strip()
    
    return "Unknown"


def get_line_type(line: str) -> str:
    """Determine the GraphQL construct type of a line.
    
    Args:
        line: The line to analyze (should be stripped)
        
    Returns:
        The type of GraphQL construct
    """
    if line.startswith('type '):
        return 'type'
    elif line.startswith('input '):
        return 'input'
    elif line.startswith('enum '):
        return 'enum'
    elif line.startswith('interface '):
        return 'interface'
    elif line.startswith('union '):
        return 'union'
    elif line.startswith('scalar '):
        return 'scalar'
    elif ':' in line and not line.startswith('#'):
        return 'field'
    else:
        return 'other'


def find_type_definition(schema_content: str, type_name: str) -> Optional[Dict[str, Any]]:
    """Find a type definition in the GraphQL schema.
    
    Args:
        schema_content: The full GraphQL schema content
        type_name: The name of the type to find
        
    Returns:
        Dictionary with type information or None if not found
    """
    lines = schema_content.split('\n')
    
    # Regular expressions for different type definitions
    patterns = [
        (r'type\s+' + re.escape(type_name) + r'\s*{', 'type'),
        (r'input\s+' + re.escape(type_name) + r'\s*{', 'input'),
        (r'enum\s+' + re.escape(type_name) + r'\s*{', 'enum'),
        (r'interface\s+' + re.escape(type_name) + r'\s*{', 'interface'),
        (r'union\s+' + re.escape(type_name) + r'\s*=', 'union'),
        (r'scalar\s+' + re.escape(type_name), 'scalar')
    ]
    
    for line_num, line in enumerate(lines):
        for pattern, kind in patterns:
            if re.match(pattern, line.strip()):
                # Find the end of the type definition
                end_line = line_num
                if kind != 'scalar':  # Scalars are single line
                    brace_count = 1 if kind != 'union' else 0
                    for i in range(line_num + 1, len(lines)):
                        if '{' in lines[i]:
                            brace_count += 1
                        if '}' in lines[i]:
                            brace_count -= 1
                        if brace_count == 0 or (kind == 'union' and lines[i].strip() == ''):
                            end_line = i
                            break
                
                return {
                    'name': type_name,
                    'kind': kind,
                    'start_line': line_num,
                    'end_line': end_line,
                    'content': '\n'.join(lines[line_num:end_line + 1])
                }
    
    return None


def extract_fields_from_type(type_content: str) -> List[Dict[str, str]]:
    """Extract field definitions from a GraphQL type.
    
    Args:
        type_content: The content of a type definition
        
    Returns:
        List of field definitions with name and type
    """
    fields = []
    lines = type_content.split('\n')
    
    for line in lines[1:-1]:  # Skip first and last lines (type declaration and closing brace)
        line = line.strip()
        if line and not line.startswith('#'):
            field_match = re.match(r'(\w+)\s*(?:\([^)]*\))?\s*:\s*(.+)', line)
            if field_match:
                fields.append({
                    'name': field_match.group(1),
                    'type': field_match.group(2).strip(),
                    'definition': line
                })
    
    return fields


def get_operation_type(query: str) -> Tuple[str, Optional[str]]:
    """Extract the operation type and name from a GraphQL query.
    
    Args:
        query: The GraphQL query string
        
    Returns:
        Tuple of (operation_type, operation_name)
    """
    # Remove comments
    cleaned_query = re.sub(r'#.*$', '', query, flags=re.MULTILINE)
    
    # Extract operation
    operation_match = re.match(r'^\s*(query|mutation|subscription)\s*(\w+)?\s*', cleaned_query)
    
    if operation_match:
        return operation_match.group(1), operation_match.group(2)
    else:
        # Anonymous query
        return 'query', None