"""Data models for the Environment Manager tool."""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field


class EnvironmentType(BaseModel):
    """Represents an environment type."""
    
    name: Literal["development", "staging", "production", "test"] = Field(
        description="Name of the environment"
    )
    api_url: str = Field(
        description="API URL for this environment"
    )
    characteristics: List[str] = Field(
        description="Key characteristics of this environment"
    )


class ConfigurationItem(BaseModel):
    """Represents a configuration item to validate."""
    
    name: str = Field(
        description="Name of the configuration item"
    )
    required: bool = Field(
        description="Whether this configuration is required"
    )
    category: str = Field(
        description="Category of the configuration (e.g., 'api', 'security', 'database')"
    )
    description: str = Field(
        description="Description of what this configuration does"
    )
    validation_pattern: Optional[str] = Field(
        default=None,
        description="Regex pattern for validation if applicable"
    )
    example: Optional[str] = Field(
        default=None,
        description="Example value for this configuration"
    )
    security_sensitive: bool = Field(
        default=False,
        description="Whether this contains sensitive data"
    )


class ValidationResult(BaseModel):
    """Result of validating a configuration item."""
    
    name: str = Field(
        description="Name of the configuration item"
    )
    valid: bool = Field(
        description="Whether the configuration is valid"
    )
    message: str = Field(
        description="Validation message"
    )
    category: str = Field(
        description="Category of the configuration"
    )
    severity: Literal["error", "warning", "info"] = Field(
        description="Severity of the validation result"
    )


class DeploymentStep(BaseModel):
    """Represents a step in the deployment checklist."""
    
    order: int = Field(
        description="Order in which to perform this step"
    )
    title: str = Field(
        description="Title of the deployment step"
    )
    description: str = Field(
        description="Detailed description of what to do"
    )
    category: str = Field(
        description="Category of the step (e.g., 'pre-deployment', 'deployment', 'post-deployment')"
    )
    commands: Optional[List[str]] = Field(
        default=None,
        description="Commands to run for this step"
    )
    validation: Optional[str] = Field(
        default=None,
        description="How to validate this step was completed successfully"
    )
    rollback: Optional[str] = Field(
        default=None,
        description="How to rollback if this step fails"
    )
    environment_specific: Optional[Dict[str, str]] = Field(
        default=None,
        description="Environment-specific notes or variations"
    )


class SecretManagement(BaseModel):
    """Information about managing a secret or credential."""
    
    name: str = Field(
        description="Name of the secret"
    )
    type: str = Field(
        description="Type of secret (e.g., 'api_key', 'certificate', 'password')"
    )
    storage_recommendation: str = Field(
        description="Recommended way to store this secret"
    )
    rotation_policy: Optional[str] = Field(
        default=None,
        description="Recommended rotation policy"
    )
    access_control: List[str] = Field(
        description="Access control recommendations"
    )
    never_do: List[str] = Field(
        description="Things to never do with this secret"
    )
    environment_separation: bool = Field(
        default=True,
        description="Whether this secret should be different per environment"
    )


class SecuritySetting(BaseModel):
    """Represents a security setting to validate."""
    
    name: str = Field(
        description="Name of the security setting"
    )
    category: str = Field(
        description="Category (e.g., 'authentication', 'encryption', 'network', 'compliance')"
    )
    description: str = Field(
        description="Description of the security setting"
    )
    required_for_production: bool = Field(
        description="Whether this is required for production"
    )
    validation_check: str = Field(
        description="How to validate this setting"
    )
    remediation: Optional[str] = Field(
        default=None,
        description="How to fix if not properly configured"
    )
    compliance_frameworks: Optional[List[str]] = Field(
        default=None,
        description="Compliance frameworks this relates to (e.g., 'HIPAA', 'SOC2')"
    )


class EnvironmentTransition(BaseModel):
    """Information about transitioning between environments."""
    
    from_environment: str = Field(
        description="Source environment"
    )
    to_environment: str = Field(
        description="Target environment"
    )
    checklist: List[str] = Field(
        description="Checklist items for this transition"
    )
    data_migration: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Data migration considerations"
    )
    config_changes: List[str] = Field(
        description="Configuration changes needed"
    )
    testing_requirements: List[str] = Field(
        description="Testing requirements before transition"
    )
    rollback_plan: List[str] = Field(
        description="Steps to rollback if needed"
    )


class EnvironmentManagerResult(BaseModel):
    """Result from the Environment Manager tool."""
    
    validation_results: Optional[List[ValidationResult]] = Field(
        default=None,
        description="Results from configuration validation"
    )
    deployment_checklist: Optional[List[DeploymentStep]] = Field(
        default=None,
        description="Deployment checklist steps"
    )
    secret_recommendations: Optional[List[SecretManagement]] = Field(
        default=None,
        description="Secret management recommendations"
    )
    security_validations: Optional[List[ValidationResult]] = Field(
        default=None,
        description="Security setting validation results"
    )
    transition_guide: Optional[EnvironmentTransition] = Field(
        default=None,
        description="Environment transition guide"
    )
    summary: str = Field(
        description="Summary of the environment management action"
    )
    next_steps: List[str] = Field(
        description="Recommended next steps"
    )