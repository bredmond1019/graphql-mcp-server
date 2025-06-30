"""Pydantic models for schema search functionality."""

from typing import List, Optional
from pydantic import BaseModel


class SchemaMatch(BaseModel):
    """A single schema search match."""
    line_number: int
    content: str
    match_type: str  # "type", "input", "enum", "query", "mutation", "field"
    location: str  # The parent type or context where the match was found


class SchemaSearchResult(BaseModel):
    """Result from schema search operation."""
    matches: List[SchemaMatch]
    total_matches: int
    search_query: str
    type_filter: str
    error: Optional[str] = None