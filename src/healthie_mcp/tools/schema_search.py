"""Schema search tool for the Healthie MCP server."""

import re
from typing import Optional, List
from mcp.server.fastmcp import FastMCP
from ..models.schema_search import SchemaSearchResult, SchemaMatch


def setup_schema_search_tool(mcp: FastMCP, schema_manager) -> None:
    """Setup the schema search tool with the MCP server."""
    
    @mcp.tool()
    def search_schema(query: str, type_filter: Optional[str] = "any", context_lines: int = 3) -> SchemaSearchResult:
        """Search the Healthie GraphQL schema for types, fields, queries, or mutations.
        
        This tool searches through the GraphQL schema content using regex patterns
        and returns matching lines with context. It's much more efficient than
        browsing the entire schema manually.
        
        Args:
            query: Search query (supports regex patterns)
            type_filter: Filter by GraphQL construct type (query, mutation, type, input, enum, interface, union, scalar, any)
            context_lines: Number of context lines to show around matches (default: 3)
            
        Returns:
            SchemaSearchResult with structured search results
        """
        try:
            schema_content = schema_manager.get_schema_content()
            if not schema_content:
                return SchemaSearchResult(
                    matches=[],
                    total_matches=0,
                    search_query=query,
                    type_filter=type_filter,
                    error="Schema not available. Please check your configuration."
                )
            
            if not query.strip():
                return SchemaSearchResult(
                    matches=[],
                    total_matches=0,
                    search_query=query,
                    type_filter=type_filter,
                    error="Search query cannot be empty."
                )
            
            # Validate type filter
            valid_filters = {"any", "query", "mutation", "type", "input", "enum", "interface", "union", "scalar"}
            if type_filter not in valid_filters:
                return SchemaSearchResult(
                    matches=[],
                    total_matches=0,
                    search_query=query,
                    type_filter=type_filter,
                    error=f"Invalid type_filter '{type_filter}'. Must be one of: {', '.join(valid_filters)}"
                )
            
            # Perform the search
            lines = schema_content.split('\n')
            matches: List[SchemaMatch] = []
            
            try:
                pattern = re.compile(query, re.IGNORECASE)
            except re.error as e:
                return SchemaSearchResult(
                    matches=[],
                    total_matches=0,
                    search_query=query,
                    type_filter=type_filter,
                    error=f"Invalid regex pattern: {e}"
                )
            
            # Track current context (type/query/mutation we're in)
            current_context = None
            
            for line_num, line in enumerate(lines):
                line_stripped = line.strip()
                
                # Update context based on GraphQL definitions
                if line_stripped.startswith('type '):
                    current_context = line_stripped.split()[1]
                elif line_stripped.startswith('input '):
                    current_context = line_stripped.split()[1]
                elif line_stripped.startswith('enum '):
                    current_context = line_stripped.split()[1]
                elif line_stripped.startswith('interface '):
                    current_context = line_stripped.split()[1]
                elif line_stripped.startswith('union '):
                    current_context = line_stripped.split()[1]
                elif line_stripped == '}':
                    current_context = None
                
                # Apply type filter if specified
                if type_filter != "any":
                    line_type = _get_line_type(line_stripped)
                    # For specific type filters, check if we're in the right context
                    if type_filter in ["query", "mutation"]:
                        if current_context != type_filter.capitalize():
                            continue
                    elif line_type != type_filter and line_type != "field":
                        continue
                
                # Check if line matches the pattern
                if pattern.search(line):
                    start_line = max(0, line_num - context_lines)
                    end_line = min(len(lines), line_num + context_lines + 1)
                    
                    context_text = []
                    for i in range(start_line, end_line):
                        prefix = ">>> " if i == line_num else "   "
                        context_text.append(f"{prefix}{lines[i]}")
                    
                    # Determine match type
                    match_type = _get_line_type(line_stripped)
                    if match_type == "field" and current_context:
                        # If it's a field, check if we're in Query or Mutation
                        if current_context == "Query":
                            match_type = "query"
                        elif current_context == "Mutation":
                            match_type = "mutation"
                    
                    match = SchemaMatch(
                        line_number=line_num + 1,
                        content='\n'.join(context_text),
                        match_type=match_type,
                        location=current_context or "Root"
                    )
                    matches.append(match)
            
            return SchemaSearchResult(
                matches=matches,
                total_matches=len(matches),
                search_query=query,
                type_filter=type_filter
            )
            
        except Exception as e:
            return SchemaSearchResult(
                matches=[],
                total_matches=0,
                search_query=query,
                type_filter=type_filter,
                error=f"Error searching schema: {str(e)}"
            )


def _get_line_type(line: str) -> str:
    """Determine the GraphQL construct type of a line."""
    line = line.strip()
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