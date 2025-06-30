"""GraphQL schema management for Healthie MCP server."""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import httpx
from graphql import GraphQLSchema, build_schema

logger = logging.getLogger(__name__)


class SchemaManager:
    """Manages GraphQL schema loading, caching, and validation."""

    def __init__(
        self,
        api_endpoint: str = "https://api.gethealthie.com/graphql/introspection",
        cache_dir: Optional[Path] = None,
        cache_max_age_days: int = 7,
    ):
        """Initialize the schema manager.
        
        Args:
            api_endpoint: The API endpoint to fetch schema from
            cache_dir: Directory to cache schema files (defaults to ~/.healthie-mcp/cache)
            cache_max_age_days: Maximum age of cached schema in days before refresh
        """
        self.api_endpoint = api_endpoint
        self.cache_max_age_days = cache_max_age_days
        
        if cache_dir is None:
            self.cache_dir = Path.home() / ".healthie-mcp" / "cache"
        else:
            self.cache_dir = Path(cache_dir)
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.cache_file = self.cache_dir / "schema.graphql"

    def load_schema(self, force_refresh: bool = False) -> GraphQLSchema:
        """Load GraphQL schema from cache or API.
        
        Args:
            force_refresh: Force download from API even if cache is fresh
            
        Returns:
            Parsed GraphQL schema
            
        Raises:
            Exception: If schema cannot be loaded or is invalid
        """
        # Check if we should use cached schema
        if not force_refresh and self.cache_file.exists() and not self.needs_refresh():
            logger.info("Loading schema from cache")
            schema_content = self.cache_file.read_text()
            return self._parse_schema(schema_content)
        
        # Download schema from API
        logger.info(f"Downloading schema from {self.api_endpoint}")
        schema_content = self._download_schema()
        
        # Parse and validate schema
        schema = self._parse_schema(schema_content)
        
        # Cache the schema
        self._cache_schema(schema_content)
        logger.info(f"Schema cached to {self.cache_file}")
        
        return schema

    def needs_refresh(self) -> bool:
        """Check if cached schema needs to be refreshed based on age.
        
        Returns:
            True if schema should be refreshed, False otherwise
        """
        if not self.cache_file.exists():
            return True
        
        cache_time = datetime.fromtimestamp(self.cache_file.stat().st_mtime)
        max_age = timedelta(days=self.cache_max_age_days)
        
        return datetime.now() - cache_time > max_age

    def _download_schema(self) -> str:
        """Download schema from API.
        
        Returns:
            Schema content as string
            
        Raises:
            Exception: If download fails
        """
        try:
            response = httpx.get(
                self.api_endpoint,
                timeout=30.0,
                headers={"Accept": "application/graphql", "Content-Type": "application/graphql"}
            )
            response.raise_for_status()
            
            return response.text
            
        except httpx.NetworkError as e:
            raise Exception(f"Network error downloading schema: {e}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error downloading schema: {e}")
        except Exception as e:
            raise Exception(f"Error downloading schema: {e}")

    def _parse_schema(self, schema_content: str) -> GraphQLSchema:
        """Parse and validate GraphQL schema.
        
        Args:
            schema_content: Schema content as SDL string
            
        Returns:
            Parsed GraphQL schema
            
        Raises:
            Exception: If schema is invalid
        """
        try:
            return build_schema(schema_content)
        except Exception as e:
            raise Exception(f"Invalid GraphQL schema: {e}")

    def _cache_schema(self, schema_content: str) -> None:
        """Cache schema content to file.
        
        Args:
            schema_content: Schema content to cache
        """
        self.cache_file.write_text(schema_content)

    def get_schema_content(self, force_refresh: bool = False) -> str:
        """Get the raw schema content as a string.
        
        Args:
            force_refresh: Force download from API even if cache is fresh
            
        Returns:
            Raw schema content as SDL string
        """
        # Check if we should use cached schema
        if not force_refresh and self.cache_file.exists() and not self.needs_refresh():
            logger.info("Loading schema content from cache")
            return self.cache_file.read_text()
        
        # Download schema from API
        logger.info(f"Downloading schema content from {self.api_endpoint}")
        schema_content = self._download_schema()
        
        # Validate schema (will raise if invalid)
        self._parse_schema(schema_content)
        
        # Cache the schema
        self._cache_schema(schema_content)
        logger.info(f"Schema content cached to {self.cache_file}")
        
        return schema_content