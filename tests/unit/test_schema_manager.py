"""Unit tests for GraphQL schema management."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

import pytest
import httpx
from graphql import build_schema, GraphQLSchema

from healthie_mcp.schema_manager import SchemaManager


class TestSchemaManager:
    """Test GraphQL schema loading and caching functionality."""

    @pytest.fixture
    def schema_manager(self, tmp_path):
        """Create a schema manager with a temporary cache directory."""
        return SchemaManager(cache_dir=tmp_path)

    @pytest.fixture
    def sample_schema(self):
        """Sample GraphQL schema for testing."""
        return """
        type Query {
            me: User
            patients: [Patient!]!
        }

        type User {
            id: ID!
            email: String!
            name: String
        }

        type Patient {
            id: ID!
            firstName: String!
            lastName: String!
            email: String
        }
        """

    @pytest.fixture
    def invalid_schema(self):
        """Invalid GraphQL schema for testing."""
        return """
        type Query {
            # Missing closing brace
            me: User
        """

    def test_load_schema_from_cache_when_exists(self, schema_manager, sample_schema, tmp_path):
        """Test loading schema from local cache file when it exists."""
        # Create a cached schema file
        cache_file = tmp_path / "schema.graphql"
        cache_file.write_text(sample_schema)
        
        # Load schema
        schema = schema_manager.load_schema()
        
        # Verify it's a valid GraphQL schema
        assert isinstance(schema, GraphQLSchema)
        assert schema.query_type is not None
        assert "me" in schema.query_type.fields
        assert "patients" in schema.query_type.fields

    def test_download_schema_when_cache_missing(self, schema_manager, sample_schema, tmp_path):
        """Test downloading schema from API when local cache doesn't exist."""
        # Mock httpx.get to return our sample schema
        with patch('httpx.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = sample_schema
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            # Load schema (should trigger download)
            schema = schema_manager.load_schema()
            
            # Verify download was called
            mock_get.assert_called_once()
            assert "introspection" in mock_get.call_args[0][0]
            
            # Verify schema was cached
            cache_file = tmp_path / "schema.graphql"
            assert cache_file.exists()
            assert cache_file.read_text() == sample_schema
            
            # Verify returned schema is valid
            assert isinstance(schema, GraphQLSchema)

    def test_schema_validation_and_parsing(self, schema_manager, sample_schema):
        """Test schema validation and parsing with graphql-core."""
        # Test valid schema
        parsed_schema = schema_manager._parse_schema(sample_schema)
        assert isinstance(parsed_schema, GraphQLSchema)
        assert parsed_schema.query_type.name == "Query"
        
        # Verify we can access schema fields
        user_type = parsed_schema.type_map.get("User")
        assert user_type is not None
        assert "id" in user_type.fields
        assert "email" in user_type.fields

    def test_invalid_schema_handling(self, schema_manager, invalid_schema):
        """Test error handling for invalid schemas."""
        with pytest.raises(Exception) as exc_info:
            schema_manager._parse_schema(invalid_schema)
        
        assert "Syntax Error" in str(exc_info.value) or "Expected" in str(exc_info.value)

    def test_network_error_handling(self, schema_manager, tmp_path):
        """Test error handling for network failures."""
        # Mock httpx.get to raise network error
        with patch('httpx.get') as mock_get:
            mock_get.side_effect = httpx.NetworkError("Connection failed")
            
            # Should raise exception when no cache exists
            with pytest.raises(Exception) as exc_info:
                schema_manager.load_schema()
            
            assert "Connection failed" in str(exc_info.value)

    def test_api_error_handling(self, schema_manager):
        """Test handling of API errors (non-200 responses)."""
        with patch('httpx.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Server error", request=Mock(), response=mock_response
            )
            mock_get.return_value = mock_response
            
            with pytest.raises(Exception) as exc_info:
                schema_manager.load_schema()
            
            assert "Server error" in str(exc_info.value) or "500" in str(exc_info.value)

    def test_schema_refresh_check_based_on_age(self, schema_manager, sample_schema, tmp_path):
        """Test checking if schema needs refresh based on file age."""
        cache_file = tmp_path / "schema.graphql"
        cache_file.write_text(sample_schema)
        
        # Test fresh cache (should not need refresh)
        assert not schema_manager.needs_refresh()
        
        # Mock file modification time to be old
        old_time = datetime.now() - timedelta(days=8)
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value = Mock(st_mtime=old_time.timestamp())
            assert schema_manager.needs_refresh()

    def test_force_refresh_schema(self, schema_manager, sample_schema, tmp_path):
        """Test forcing schema refresh even when cache is fresh."""
        # Create initial cache
        cache_file = tmp_path / "schema.graphql"
        cache_file.write_text("old schema content")
        
        # Mock API to return new schema
        with patch('httpx.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = sample_schema
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            # Force refresh
            schema = schema_manager.load_schema(force_refresh=True)
            
            # Verify download was called
            mock_get.assert_called_once()
            
            # Verify cache was updated
            assert cache_file.read_text() == sample_schema
            
            # Verify returned schema is valid
            assert isinstance(schema, GraphQLSchema)

    def test_custom_api_endpoint(self, sample_schema, tmp_path):
        """Test using custom API endpoint for schema download."""
        custom_endpoint = "https://api.custom.com/graphql"
        manager = SchemaManager(api_endpoint=custom_endpoint, cache_dir=tmp_path)
        
        with patch('httpx.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = sample_schema
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            manager.load_schema()
            
            # Verify custom endpoint was used
            mock_get.assert_called_once()
            assert custom_endpoint in mock_get.call_args[0][0]

    def test_schema_caching_creates_directory(self, tmp_path):
        """Test that cache directory is created if it doesn't exist."""
        cache_dir = tmp_path / "nested" / "cache" / "dir"
        manager = SchemaManager(cache_dir=cache_dir)
        
        with patch('httpx.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "type Query { test: String }"
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            manager.load_schema()
            
            # Verify directory was created
            assert cache_dir.exists()
            assert cache_dir.is_dir()

    def test_get_schema_content_returns_string(self, tmp_path, sample_schema):
        """Test that get_schema_content returns string content."""
        cache_dir = tmp_path / "cache"
        schema_manager = SchemaManager(cache_dir=cache_dir)
        
        # Mock successful API response
        with patch('httpx.get') as mock_get:
            mock_response = Mock()
            mock_response.text = sample_schema
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            # Get schema content
            content = schema_manager.get_schema_content()
            
            # Should return string content
            assert isinstance(content, str)
            assert content == sample_schema
            
            # Should also cache it
            assert schema_manager.cache_file.exists()
            assert schema_manager.cache_file.read_text() == sample_schema

    def test_get_schema_content_uses_cached_content(self, tmp_path, sample_schema):
        """Test that get_schema_content uses cached content when available."""
        cache_dir = tmp_path / "cache"
        schema_manager = SchemaManager(cache_dir=cache_dir)
        
        # Pre-populate cache
        schema_manager.cache_file.write_text(sample_schema)
        
        # Should return cached content without making API call
        with patch('httpx.get') as mock_get:
            content = schema_manager.get_schema_content()
            
            # Should not make API call
            mock_get.assert_not_called()
            
            # Should return cached content
            assert content == sample_schema