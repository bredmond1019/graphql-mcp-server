"""Configuration data loader for Healthie MCP server.

This module provides utilities for loading configuration data from YAML files.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from functools import lru_cache
import logging

from ..exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Loads and manages configuration data from YAML files."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize the configuration loader.
        
        Args:
            config_dir: Directory containing configuration files. 
                       Defaults to config/data relative to this file.
        """
        if config_dir is None:
            config_dir = Path(__file__).parent / "data"
        
        self.config_dir = Path(config_dir)
        
        if not self.config_dir.exists():
            raise ConfigurationError(
                f"Configuration directory not found: {self.config_dir}",
                {"suggested_path": str(self.config_dir.absolute())}
            )
    
    @lru_cache(maxsize=32)
    def load_file(self, filename: str) -> Dict[str, Any]:
        """Load a single YAML configuration file.
        
        Args:
            filename: Name of the file to load (with or without .yaml extension)
            
        Returns:
            Dictionary containing the loaded configuration data
            
        Raises:
            ConfigurationError: If file cannot be loaded or parsed
        """
        # Add .yaml extension if not present
        if not filename.endswith(('.yaml', '.yml')):
            filename = f"{filename}.yaml"
        
        filepath = self.config_dir / filename
        
        if not filepath.exists():
            raise ConfigurationError(
                f"Configuration file not found: {filename}",
                {"searched_path": str(filepath.absolute())}
            )
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            if data is None:
                return {}
                
            return data
            
        except yaml.YAMLError as e:
            raise ConfigurationError(
                f"Failed to parse YAML file: {filename}",
                {"error": str(e), "file": str(filepath)}
            )
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load configuration file: {filename}",
                {"error": str(e), "file": str(filepath)}
            )
    
    def load_queries(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load GraphQL query templates.
        
        Returns:
            Dictionary mapping categories to lists of query templates
        """
        return self.load_file("queries")
    
    def load_patterns(self) -> Dict[str, Any]:
        """Load healthcare patterns configuration.
        
        Returns:
            Dictionary containing pattern definitions and keywords
        """
        return self.load_file("patterns")
    
    def load_errors(self) -> Dict[str, Any]:
        """Load error messages and solutions.
        
        Returns:
            Dictionary containing error configurations
        """
        return self.load_file("errors")
    
    def load_validation(self) -> Dict[str, Any]:
        """Load validation rules and patterns.
        
        Returns:
            Dictionary containing validation configurations
        """
        return self.load_file("validation")
    
    def load_workflows(self) -> Dict[str, Any]:
        """Load workflow sequences.
        
        Returns:
            Dictionary containing workflow definitions
        """
        return self.load_file("workflows")
    
    def load_fields(self) -> Dict[str, Any]:
        """Load field relationships and usage patterns.
        
        Returns:
            Dictionary containing field configurations
        """
        return self.load_file("fields")
    
    def load_performance(self) -> Dict[str, Any]:
        """Load performance thresholds and rules.
        
        Returns:
            Dictionary containing performance configurations
        """
        return self.load_file("performance")
    
    def load_examples(self) -> Dict[str, Any]:
        """Load code examples.
        
        Returns:
            Dictionary containing code examples for different languages
        """
        return self.load_file("examples")
    
    def clear_cache(self):
        """Clear the loaded configuration cache."""
        self.load_file.cache_clear()
        logger.info("Configuration cache cleared")
    
    def get_all_files(self) -> List[str]:
        """Get list of all available configuration files.
        
        Returns:
            List of configuration file names (without paths)
        """
        yaml_files = list(self.config_dir.glob("*.yaml"))
        yaml_files.extend(self.config_dir.glob("*.yml"))
        
        return [f.name for f in yaml_files]


# Global instance
_default_loader: Optional[ConfigLoader] = None


def get_config_loader() -> ConfigLoader:
    """Get the default configuration loader instance.
    
    Returns:
        The global ConfigLoader instance
    """
    global _default_loader
    if _default_loader is None:
        _default_loader = ConfigLoader()
    return _default_loader


def load_config(filename: str) -> Dict[str, Any]:
    """Convenience function to load a configuration file.
    
    Args:
        filename: Name of the configuration file to load
        
    Returns:
        Dictionary containing the configuration data
    """
    return get_config_loader().load_file(filename)