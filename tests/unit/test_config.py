"""Unit tests for configuration management."""
import os
import pytest
from unittest.mock import patch
from pydantic_core import ValidationError
from healthie_mcp.exceptions import InvalidConfigurationError

from healthie_mcp.config import Settings, get_settings


class TestConfig:
    """Test configuration loading and validation."""
    
    def test_default_configuration(self):
        """Test that default values are set correctly."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            
            assert str(settings.healthie_api_url) == "https://staging-api.gethealthie.com/graphql"
            assert settings.healthie_api_key is None
            assert str(settings.schema_dir) == "schemas"
            assert settings.cache_enabled is True
            assert settings.log_level == "INFO"
    
    def test_load_from_environment_variables(self):
        """Test loading configuration from environment variables."""
        env_vars = {
            "HEALTHIE_API_URL": "https://api.example.com/graphql",
            "HEALTHIE_API_KEY": "test-api-key-123",
            "SCHEMA_DIR": "/custom/schema/path",
            "CACHE_ENABLED": "false",
            "LOG_LEVEL": "DEBUG"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            
            assert str(settings.healthie_api_url) == "https://api.example.com/graphql"
            assert settings.healthie_api_key == "test-api-key-123"
            assert str(settings.schema_dir) == "/custom/schema/path"
            assert settings.cache_enabled is False
            assert settings.log_level == "DEBUG"
    
    def test_partial_environment_variables(self):
        """Test that partial env vars work with defaults for others."""
        env_vars = {
            "HEALTHIE_API_KEY": "partial-test-key",
            "LOG_LEVEL": "WARNING"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            
            assert str(settings.healthie_api_url) == "https://staging-api.gethealthie.com/graphql"
            assert settings.healthie_api_key == "partial-test-key"
            assert str(settings.schema_dir) == "schemas"
            assert settings.cache_enabled is True
            assert settings.log_level == "WARNING"
    
    def test_invalid_boolean_configuration(self):
        """Test that invalid boolean values raise validation errors."""
        env_vars = {
            "CACHE_ENABLED": "not-a-boolean"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            assert "CACHE_ENABLED" in str(exc_info.value)
    
    def test_invalid_log_level(self):
        """Test that invalid log levels raise validation errors."""
        env_vars = {
            "LOG_LEVEL": "INVALID_LEVEL"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(InvalidConfigurationError) as exc_info:
                Settings()
            
            assert "log_level" in str(exc_info.value)
    
    def test_empty_api_url_validation(self):
        """Test that empty API URL raises validation error."""
        env_vars = {
            "HEALTHIE_API_URL": ""
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            assert "HEALTHIE_API_URL" in str(exc_info.value)
    
    def test_invalid_url_format(self):
        """Test that invalid URL format raises validation error."""
        env_vars = {
            "HEALTHIE_API_URL": "not-a-valid-url"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            assert "healthie_api_url" in str(exc_info.value).lower()
    
    def test_get_settings_singleton(self):
        """Test that get_settings returns the same instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1 is settings2
    
    def test_case_sensitive_boolean_values(self):
        """Test that boolean parsing handles different cases."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("1", True),
            ("false", False),
            ("False", False),
            ("FALSE", False),
            ("0", False),
        ]
        
        for value, expected in test_cases:
            with patch.dict(os.environ, {"CACHE_ENABLED": value}, clear=True):
                settings = Settings()
                assert settings.cache_enabled is expected
    
    def test_schema_dir_path_validation(self):
        """Test schema directory path handling."""
        test_cases = [
            ("./schemas", "schemas"),  # Path() normalizes ./schemas to schemas
            ("/absolute/path", "/absolute/path"),
            ("relative/path", "relative/path"),
            ("~/user/path", "~/user/path"),
        ]
        
        for input_path, expected_path in test_cases:
            with patch.dict(os.environ, {"SCHEMA_DIR": input_path}, clear=True):
                settings = Settings()
                assert str(settings.schema_dir) == expected_path
    
    def test_api_key_optional(self):
        """Test that API key is truly optional."""
        # Test with no API key
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.healthie_api_key is None
        
        # Test with empty string API key (should be None)
        with patch.dict(os.environ, {"HEALTHIE_API_KEY": ""}, clear=True):
            settings = Settings()
            assert settings.healthie_api_key is None
        
        # Test with whitespace API key (should be None)
        with patch.dict(os.environ, {"HEALTHIE_API_KEY": "   "}, clear=True):
            settings = Settings()
            assert settings.healthie_api_key is None
    
    def test_production_api_url(self):
        """Test setting production API URL."""
        env_vars = {
            "HEALTHIE_API_URL": "https://api.gethealthie.com/graphql"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert str(settings.healthie_api_url) == "https://api.gethealthie.com/graphql"