"""Schema search tool for the Healthie MCP server - Refactored version."""

import re
from typing import Optional, List, Tuple
from mcp.server.fastmcp import FastMCP
from ..models.schema_search import SchemaSearchResult, SchemaMatch


class SchemaSearcher:
    """Handles searching through GraphQL schema content."""
    
    # Valid filter types
    VALID_FILTERS = {"any", "query", "mutation", "type", "input", "enum", "interface", "union", "scalar"}
    
    # GraphQL construct prefixes
    CONSTRUCT_PREFIXES = {
        'type ': 'type',
        'input ': 'input',
        'enum ': 'enum',
        'interface ': 'interface',
        'union ': 'union',
        'scalar ': 'scalar'
    }
    
    def __init__(self, schema_content: str):
        self.schema_content = schema_content
        self.lines = schema_content.split('\n')
        self.current_context = None
    
    def search(
        self, 
        query: str, 
        type_filter: str = "any", 
        context_lines: int = 3
    ) -> SchemaSearchResult:
        """Execute the search with the given parameters."""
        # Validate inputs
        error = self._validate_inputs(query, type_filter)
        if error:
            return self._create_error_result(query, type_filter, error)
        
        try:
            # Compile the regex pattern
            pattern = re.compile(query, re.IGNORECASE)
        except re.error as e:
            return self._create_error_result(
                query, type_filter, f"Invalid regex pattern: {e}"
            )
        
        # Find all matches
        matches = self._find_matches(pattern, type_filter, context_lines)
        
        return SchemaSearchResult(
            matches=matches,
            total_matches=len(matches),
            search_query=query,
            type_filter=type_filter
        )
    
    def _validate_inputs(self, query: str, type_filter: str) -> Optional[str]:
        """Validate search inputs and return error message if invalid."""
        if not self.schema_content:
            return "Schema not available. Please check your configuration."
        
        if not query.strip():
            return "Search query cannot be empty."
        
        if type_filter not in self.VALID_FILTERS:
            return f"Invalid type_filter '{type_filter}'. Must be one of: {', '.join(self.VALID_FILTERS)}"
        
        return None
    
    def _find_matches(
        self, 
        pattern: re.Pattern, 
        type_filter: str, 
        context_lines: int
    ) -> List[SchemaMatch]:
        """Find all matches in the schema."""
        matches = []
        self.current_context = None
        
        for line_num, line in enumerate(self.lines):
            # Update context tracking
            self._update_context(line)
            
            # Skip lines that don't match the type filter
            if not self._should_process_line(line, type_filter):
                continue
            
            # Check if line matches the pattern
            if pattern.search(line):
                match = self._create_match(line_num, line, context_lines)
                matches.append(match)
        
        return matches
    
    def _update_context(self, line: str) -> None:
        """Update the current context based on GraphQL definitions."""
        line_stripped = line.strip()
        
        # Check for construct definitions
        for prefix, construct_type in self.CONSTRUCT_PREFIXES.items():
            if line_stripped.startswith(prefix):
                # Extract the name of the type/input/etc.
                self.current_context = line_stripped.split()[1]
                return
        
        # Reset context when we exit a block
        if line_stripped == '}':
            self.current_context = None
    
    def _should_process_line(self, line: str, type_filter: str) -> bool:
        """Determine if a line should be processed based on the type filter."""
        if type_filter == "any":
            return True
        
        line_stripped = line.strip()
        line_type = self._get_line_type(line_stripped)
        
        # Special handling for query/mutation filters
        if type_filter in ["query", "mutation"]:
            # Only process if we're in the right context
            return self.current_context == type_filter.capitalize()
        
        # For other filters, check the line type
        # Allow fields within matching contexts
        return line_type == type_filter or (line_type == "field" and self.current_context)
    
    def _create_match(self, line_num: int, line: str, context_lines: int) -> SchemaMatch:
        """Create a SchemaMatch object for a matched line."""
        # Get context lines
        start_line = max(0, line_num - context_lines)
        end_line = min(len(self.lines), line_num + context_lines + 1)
        
        # Build context text with highlighting
        context_text = []
        for i in range(start_line, end_line):
            prefix = ">>> " if i == line_num else "   "
            context_text.append(f"{prefix}{self.lines[i]}")
        
        # Determine match type
        match_type = self._determine_match_type(line.strip())
        
        return SchemaMatch(
            line_number=line_num + 1,  # 1-indexed for user display
            content='\n'.join(context_text),
            match_type=match_type,
            location=self.current_context or "Root"
        )
    
    def _determine_match_type(self, line: str) -> str:
        """Determine the type of the matched line."""
        line_type = self._get_line_type(line)
        
        # If it's a field, check if we're in Query or Mutation context
        if line_type == "field" and self.current_context:
            if self.current_context == "Query":
                return "query"
            elif self.current_context == "Mutation":
                return "mutation"
        
        return line_type
    
    def _get_line_type(self, line: str) -> str:
        """Determine the GraphQL construct type of a line."""
        # Check for construct definitions
        for prefix, construct_type in self.CONSTRUCT_PREFIXES.items():
            if line.startswith(prefix):
                return construct_type
        
        # Check if it's a field definition
        if ':' in line and not line.startswith('#'):
            return 'field'
        
        return 'other'
    
    def _create_error_result(
        self, 
        query: str, 
        type_filter: str, 
        error: str
    ) -> SchemaSearchResult:
        """Create an error result."""
        return SchemaSearchResult(
            matches=[],
            total_matches=0,
            search_query=query,
            type_filter=type_filter,
            error=error
        )


def setup_schema_search_tool(mcp: FastMCP, schema_manager) -> None:
    """Setup the schema search tool with the MCP server."""
    
    @mcp.tool()
    def search_schema(
        query: str, 
        type_filter: Optional[str] = "any", 
        context_lines: int = 3
    ) -> SchemaSearchResult:
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
            # Get schema content from manager
            schema_content = schema_manager.get_schema_content()
            if not schema_content:
                return SchemaSearchResult(
                    matches=[],
                    total_matches=0,
                    search_query=query,
                    type_filter=type_filter,
                    error="Schema not available. Please check your configuration."
                )
            
            # Create searcher and execute search
            searcher = SchemaSearcher(schema_content)
            return searcher.search(query, type_filter, context_lines)
            
        except Exception as e:
            # Handle unexpected errors
            return SchemaSearchResult(
                matches=[],
                total_matches=0,
                search_query=query,
                type_filter=type_filter,
                error=f"Error searching schema: {str(e)}"
            )