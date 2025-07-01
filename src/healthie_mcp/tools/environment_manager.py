"""Environment Manager tool for deployment and environment management."""

import re
from typing import Dict, Any, List, Optional, Literal
from mcp.server.fastmcp import FastMCP
from src.healthie_mcp.models.environment_manager import (
    EnvironmentManagerResult,
    ValidationResult,
    DeploymentStep,
    SecretManagement,
    EnvironmentTransition,
    ConfigurationItem,
    SecuritySetting
)
from src.healthie_mcp.base import BaseTool, SchemaManagerProtocol
from src.healthie_mcp.exceptions import ToolError


class EnvironmentManagerTool(BaseTool[EnvironmentManagerResult]):
    """Tool for managing environments, deployments, and security configurations."""
    
    def get_tool_name(self) -> str:
        """Get the name of this tool."""
        return "environment_manager"
    
    def get_tool_description(self) -> str:
        """Get the description of this tool."""
        return (
            "Helps with environment configuration, deployment checklists, "
            "secret management, security validation, and environment transitions. "
            "Supports development, staging, and production environments with "
            "healthcare-specific security and compliance considerations."
        )
    
    def execute(self, **kwargs) -> EnvironmentManagerResult:
        """Execute the environment management action."""
        action = kwargs.get("action")
        if not action:
            raise ToolError(
                "Missing required parameter: action",
                details={"required": ["action"]}
            )
        
        valid_actions = [
            "validate_config",
            "deployment_checklist", 
            "manage_secrets",
            "validate_security",
            "transition_guide"
        ]
        
        if action not in valid_actions:
            raise ToolError(
                f"Invalid action: {action}",
                details={"valid_actions": valid_actions}
            )
        
        if action == "validate_config":
            return self._validate_config(**kwargs)
        elif action == "deployment_checklist":
            return self._get_deployment_checklist(**kwargs)
        elif action == "manage_secrets":
            return self._manage_secrets(**kwargs)
        elif action == "validate_security":
            return self._validate_security(**kwargs)
        elif action == "transition_guide":
            return self._get_transition_guide(**kwargs)
    
    def _validate_config(self, **kwargs) -> EnvironmentManagerResult:
        """Validate environment configuration."""
        environment = kwargs.get("environment")
        if not environment:
            raise ToolError(
                "Missing required parameter: environment",
                details={"required": ["environment", "config"]}
            )
        
        config = kwargs.get("config", {})
        if not config:
            raise ToolError(
                "Missing required parameter: config",
                details={"required": ["environment", "config"]}
            )
        
        # Define configuration items to validate
        config_items = self._get_config_items(environment)
        
        validation_results = []
        for item in config_items:
            value = config.get(item.name)
            result = self._validate_config_item(item, value, environment)
            validation_results.append(result)
        
        # Check for extra configs not in our list
        known_configs = {item.name for item in config_items}
        for key in config:
            if key not in known_configs:
                validation_results.append(ValidationResult(
                    name=key,
                    valid=True,
                    message=f"Additional configuration detected",
                    category="custom",
                    severity="info"
                ))
        
        # Generate summary
        error_count = sum(1 for r in validation_results if not r.valid and r.severity == "error")
        warning_count = sum(1 for r in validation_results if not r.valid and r.severity == "warning")
        
        if error_count > 0:
            summary = f"Configuration validation failed with {error_count} errors and {warning_count} warnings"
        elif warning_count > 0:
            summary = f"Configuration valid with {warning_count} warnings"
        else:
            summary = f"All configurations valid for {environment} environment"
        
        # Next steps
        next_steps = []
        if error_count > 0:
            next_steps.append("Fix configuration errors before proceeding")
            for result in validation_results:
                if not result.valid and result.severity == "error":
                    next_steps.append(f"Fix {result.name}: {result.message}")
        else:
            next_steps.append("Run deployment checklist")
            next_steps.append("Validate security settings")
            if environment == "production":
                next_steps.append("Review secret management")
                next_steps.append("Proceed with production deployment")
            else:
                next_steps.append("Proceed with deployment")
        
        return EnvironmentManagerResult(
            validation_results=validation_results,
            summary=summary,
            next_steps=next_steps
        )
    
    def _get_config_items(self, environment: str) -> List[ConfigurationItem]:
        """Get configuration items to validate for an environment."""
        items = [
            ConfigurationItem(
                name="HEALTHIE_API_URL",
                required=True,
                category="api",
                description="Healthie GraphQL API endpoint",
                validation_pattern=r"^https://.*\.gethealthie\.com/graphql$",
                example="https://api.gethealthie.com/graphql",
                security_sensitive=False
            ),
            ConfigurationItem(
                name="HEALTHIE_API_KEY",
                required=True,
                category="api",
                description="API key for Healthie authentication",
                validation_pattern=r"^.{10,}$",  # At least 10 characters
                example="your_api_key_here",
                security_sensitive=True
            ),
            ConfigurationItem(
                name="REQUEST_TIMEOUT",
                required=False,
                category="network",
                description="HTTP request timeout in seconds",
                validation_pattern=r"^\d+$",
                example="30",
                security_sensitive=False
            ),
            ConfigurationItem(
                name="MAX_RETRIES",
                required=False,
                category="network",
                description="Maximum number of retry attempts",
                validation_pattern=r"^\d+$",
                example="3",
                security_sensitive=False
            ),
            ConfigurationItem(
                name="LOG_LEVEL",
                required=False,
                category="logging",
                description="Application log level",
                validation_pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
                example="INFO",
                security_sensitive=False
            ),
            ConfigurationItem(
                name="ENABLE_TELEMETRY",
                required=False,
                category="monitoring",
                description="Enable application telemetry",
                validation_pattern=r"^(true|false)$",
                example="true",
                security_sensitive=False
            )
        ]
        
        # Add production-specific items
        if environment == "production":
            items.extend([
                ConfigurationItem(
                    name="SSL_CERT_PATH",
                    required=True,
                    category="security",
                    description="Path to SSL certificate",
                    validation_pattern=r"^/.+\.(crt|pem)$",
                    example="/etc/ssl/certs/server.crt",
                    security_sensitive=True
                ),
                ConfigurationItem(
                    name="RATE_LIMIT",
                    required=True,
                    category="security",
                    description="API rate limit per minute",
                    validation_pattern=r"^\d+$",
                    example="60",
                    security_sensitive=False
                )
            ])
        
        return items
    
    def _validate_config_item(
        self, 
        item: ConfigurationItem, 
        value: Any,
        environment: str
    ) -> ValidationResult:
        """Validate a single configuration item."""
        # Check if required
        if item.required and not value:
            return ValidationResult(
                name=item.name,
                valid=False,
                message=f"Required configuration is missing or empty",
                category=item.category,
                severity="error"
            )
        
        # If not required and not provided, it's valid
        if not item.required and not value:
            return ValidationResult(
                name=item.name,
                valid=True,
                message="Optional configuration not provided",
                category=item.category,
                severity="info"
            )
        
        # Validate pattern if provided
        if item.validation_pattern and value:
            if not re.match(item.validation_pattern, str(value)):
                return ValidationResult(
                    name=item.name,
                    valid=False,
                    message=f"Value does not match expected pattern. Example: {item.example}",
                    category=item.category,
                    severity="error"
                )
        
        # Special validations
        if item.name == "HEALTHIE_API_URL":
            if environment == "production" and "staging" in str(value):
                return ValidationResult(
                    name=item.name,
                    valid=False,
                    message="Production environment should not use staging API URL",
                    category=item.category,
                    severity="error"
                )
            elif environment == "development" and "api.gethealthie.com" in str(value):
                return ValidationResult(
                    name=item.name,
                    valid=True,
                    message="Consider using staging API for development",
                    category=item.category,
                    severity="warning"
                )
        
        if item.name == "LOG_LEVEL" and environment == "production" and value == "DEBUG":
            return ValidationResult(
                name=item.name,
                valid=True,
                message="DEBUG logging in production may impact performance",
                category=item.category,
                severity="warning"
            )
        
        return ValidationResult(
            name=item.name,
            valid=True,
            message=f"Configuration valid",
            category=item.category,
            severity="info"
        )
    
    def _get_deployment_checklist(self, **kwargs) -> EnvironmentManagerResult:
        """Get deployment checklist for an environment."""
        environment = kwargs.get("environment")
        if not environment:
            raise ToolError(
                "Missing required parameter: environment",
                details={"required": ["environment"]}
            )
        
        valid_environments = ["development", "staging", "production", "test"]
        if environment not in valid_environments:
            raise ToolError(
                f"Invalid environment: {environment}",
                details={"valid_environments": valid_environments}
            )
        
        deployment_type = kwargs.get("deployment_type", "update")
        
        steps = []
        order = 1
        
        # Pre-deployment steps
        if deployment_type == "initial":
            steps.extend([
                DeploymentStep(
                    order=order,
                    title="Verify Infrastructure Requirements",
                    description="Ensure all infrastructure components are ready",
                    category="pre-deployment",
                    validation="Check database connectivity, Redis availability, and external service access",
                    commands=["ping database_host", "redis-cli ping"]
                ),
                DeploymentStep(
                    order=order + 1,
                    title="Create Database Schema",
                    description="Initialize database with required schema",
                    category="pre-deployment",
                    commands=["python manage.py migrate"],
                    rollback="python manage.py migrate --reverse"
                )
            ])
            order += 2
        
        # Common pre-deployment steps
        steps.extend([
            DeploymentStep(
                order=order,
                title="Backup Current State",
                description="Create backup of database and configurations",
                category="pre-deployment",
                commands=["./scripts/backup.sh"],
                validation="Verify backup file exists and is valid",
                rollback="N/A - This is a safety measure"
            ),
            DeploymentStep(
                order=order + 1,
                title="Run Pre-deployment Tests",
                description="Execute test suite to ensure code quality",
                category="pre-deployment",
                commands=["pytest tests/", "npm test"],
                validation="All tests pass with no failures"
            ),
            DeploymentStep(
                order=order + 2,
                title="Validate Environment Configuration",
                description="Ensure all required environment variables are set",
                category="pre-deployment",
                validation="Use environment_manager validate_config action",
                environment_specific={
                    "production": "Ensure production API keys and certificates are in place",
                    "staging": "Verify staging-specific configurations"
                }
            )
        ])
        order += 3
        
        # Deployment steps
        if environment == "production":
            steps.extend([
                DeploymentStep(
                    order=order,
                    title="Enable Maintenance Mode",
                    description="Put application in maintenance mode to prevent data corruption",
                    category="deployment",
                    commands=["./scripts/maintenance.sh enable"],
                    rollback="./scripts/maintenance.sh disable"
                ),
                DeploymentStep(
                    order=order + 1,
                    title="Deploy Application Code",
                    description="Deploy new application version",
                    category="deployment",
                    commands=["git pull", "docker-compose up -d"],
                    rollback="git checkout previous_version && docker-compose up -d"
                ),
                DeploymentStep(
                    order=order + 2,
                    title="Run Database Migrations",
                    description="Apply any pending database migrations",
                    category="deployment",
                    commands=["python manage.py migrate"],
                    rollback="python manage.py migrate --reverse",
                    validation="Check migration status"
                ),
                DeploymentStep(
                    order=order + 3,
                    title="Clear Caches",
                    description="Clear application and CDN caches",
                    category="deployment",
                    commands=["redis-cli FLUSHDB", "cloudflare-cli purge"],
                    validation="Verify cache is empty"
                ),
                DeploymentStep(
                    order=order + 4,
                    title="Disable Maintenance Mode",
                    description="Restore normal application access",
                    category="deployment",
                    commands=["./scripts/maintenance.sh disable"],
                    validation="Application is accessible"
                )
            ])
            order += 5
        else:
            steps.extend([
                DeploymentStep(
                    order=order,
                    title="Deploy Application Code",
                    description="Deploy new application version",
                    category="deployment",
                    commands=["git pull", "npm install", "npm run build"],
                    rollback="git checkout previous_version"
                ),
                DeploymentStep(
                    order=order + 1,
                    title="Restart Services",
                    description="Restart application services",
                    category="deployment",
                    commands=["systemctl restart app-service"],
                    validation="Service is running"
                )
            ])
            order += 2
        
        # Post-deployment steps
        steps.extend([
            DeploymentStep(
                order=order,
                title="Run Smoke Tests",
                description="Execute basic functionality tests",
                category="post-deployment",
                commands=["./scripts/smoke-tests.sh"],
                validation="All smoke tests pass",
                environment_specific={
                    "production": "Test with production data samples",
                    "staging": "Test with staging test data"
                }
            ),
            DeploymentStep(
                order=order + 1,
                title="Verify Application Health",
                description="Check application health endpoints and metrics",
                category="post-deployment",
                commands=["curl https://api/health", "check-metrics.sh"],
                validation="Health check returns 200 OK"
            ),
            DeploymentStep(
                order=order + 2,
                title="Monitor Application Logs",
                description="Watch logs for errors or warnings",
                category="post-deployment",
                validation="No critical errors in logs for 5 minutes",
                commands=["tail -f /var/log/app.log"]
            ),
            DeploymentStep(
                order=order + 3,
                title="Update Monitoring Alerts",
                description="Ensure monitoring and alerting are configured",
                category="post-deployment",
                validation="Alerts are firing correctly"
            )
        ])
        
        if environment == "production":
            steps.append(DeploymentStep(
                order=order + 4,
                title="Document Deployment",
                description="Update deployment log and notify team",
                category="post-deployment",
                validation="Deployment documented in wiki/changelog"
            ))
        
        # Prepare rollback plan
        steps.append(DeploymentStep(
            order=order + 5,
            title="Prepare Rollback Plan",
            description="Ensure rollback procedures are ready if needed",
            category="post-deployment",
            rollback="Follow rollback procedures in deployment guide",
            validation="Rollback script tested and ready"
        ))
        
        summary = f"{deployment_type.capitalize()} deployment checklist for {environment} environment"
        next_steps = [
            "Review each step carefully before proceeding",
            "Ensure all team members are aware of deployment",
            "Have rollback plan ready",
            "Monitor application after deployment"
        ]
        
        return EnvironmentManagerResult(
            deployment_checklist=steps,
            summary=summary,
            next_steps=next_steps
        )
    
    def _manage_secrets(self, **kwargs) -> EnvironmentManagerResult:
        """Provide secret management recommendations."""
        secret_type = kwargs.get("secret_type", "all")
        environment = kwargs.get("environment", "production")
        
        recommendations = []
        
        # API Key management
        if secret_type in ["api_key", "all"]:
            recommendations.append(SecretManagement(
                name="HEALTHIE_API_KEY",
                type="api_key",
                storage_recommendation="Store in environment variables or secure key management service (e.g., AWS Secrets Manager, HashiCorp Vault)",
                rotation_policy="Rotate every 90 days or immediately if compromised",
                access_control=[
                    "Limit access to production systems only",
                    "Use separate keys for each environment",
                    "Implement key-based access controls",
                    "Monitor API key usage"
                ],
                never_do=[
                    "Never commit API keys to version control",
                    "Never share keys via email or chat",
                    "Never use the same key across environments",
                    "Never log API keys in plain text"
                ],
                environment_separation=True
            ))
        
        # Database passwords
        if secret_type in ["database_password", "all"]:
            recommendations.append(SecretManagement(
                name="DATABASE_PASSWORD",
                type="database_password",
                storage_recommendation="Use environment variables or database connection pooler with encrypted credentials",
                rotation_policy="Rotate every 60 days, coordinate with DBA team",
                access_control=[
                    "Restrict to application service accounts only",
                    "Use SSL/TLS for database connections",
                    "Implement IP whitelisting for database access",
                    "Use read-only credentials where possible"
                ],
                never_do=[
                    "Never use default passwords",
                    "Never share database credentials",
                    "Never store in application code",
                    "Never use weak passwords"
                ],
                environment_separation=True
            ))
        
        # JWT secrets
        if secret_type in ["jwt_secret", "all"]:
            recommendations.append(SecretManagement(
                name="JWT_SECRET",
                type="jwt_secret",
                storage_recommendation="Generate using cryptographically secure random generator, store in environment variables",
                rotation_policy="Rotate with proper token migration strategy",
                access_control=[
                    "Only accessible to authentication service",
                    "Never expose to client-side code",
                    "Use different secrets per environment",
                    "Consider using asymmetric keys for better security"
                ],
                never_do=[
                    "Never use predictable secrets",
                    "Never reuse secrets across applications",
                    "Never expose in API responses",
                    "Never commit to version control"
                ],
                environment_separation=True
            ))
        
        # SSL certificates
        if secret_type in ["ssl_cert", "all"]:
            recommendations.append(SecretManagement(
                name="SSL_CERTIFICATE",
                type="certificate",
                storage_recommendation="Store in secure certificate store or load balancer, use Let's Encrypt for automatic renewal",
                rotation_policy="Auto-renew 30 days before expiration",
                access_control=[
                    "Limit access to system administrators",
                    "Use certificate pinning for mobile apps",
                    "Monitor certificate expiration",
                    "Implement HSTS headers"
                ],
                never_do=[
                    "Never use self-signed certificates in production",
                    "Never ignore certificate warnings",
                    "Never store private keys unencrypted",
                    "Never share private keys"
                ],
                environment_separation=True
            ))
        
        # Encryption keys
        if secret_type in ["encryption_key", "all"]:
            recommendations.append(SecretManagement(
                name="ENCRYPTION_KEY",
                type="encryption_key",
                storage_recommendation="Use hardware security module (HSM) or key management service",
                rotation_policy="Implement key rotation with re-encryption strategy",
                access_control=[
                    "Strict access control with audit logging",
                    "Use key encryption keys (KEK) for additional security",
                    "Implement key escrow for recovery",
                    "Monitor all key usage"
                ],
                never_do=[
                    "Never store encryption keys with encrypted data",
                    "Never use weak encryption algorithms",
                    "Never hardcode keys",
                    "Never transmit keys over insecure channels"
                ],
                environment_separation=True
            ))
        
        summary = f"Secret management recommendations for {secret_type} in {environment} environment"
        next_steps = [
            "Audit current secret storage practices",
            "Implement recommended storage solutions",
            "Set up secret rotation schedules",
            "Train team on secret handling best practices",
            "Implement secret scanning in CI/CD pipeline"
        ]
        
        return EnvironmentManagerResult(
            secret_recommendations=recommendations,
            summary=summary,
            next_steps=next_steps
        )
    
    def _validate_security(self, **kwargs) -> EnvironmentManagerResult:
        """Validate security settings."""
        environment = kwargs.get("environment", "production")
        settings = kwargs.get("settings", {})
        compliance_framework = kwargs.get("compliance_framework")
        
        # Define security settings to check
        security_checks = self._get_security_checks(environment, compliance_framework)
        
        validation_results = []
        for check in security_checks:
            result = self._validate_security_setting(check, settings, environment)
            validation_results.append(result)
        
        # Count issues
        error_count = sum(1 for r in validation_results if not r.valid and r.severity == "error")
        warning_count = sum(1 for r in validation_results if not r.valid and r.severity == "warning")
        
        if error_count > 0:
            summary = f"Security validation failed with {error_count} critical issues"
        elif warning_count > 0:
            summary = f"Security validation passed with {warning_count} warnings"
        else:
            summary = "All security settings validated successfully"
        
        # Next steps based on results
        next_steps = []
        if error_count > 0:
            next_steps.append("Address critical security issues immediately")
            for result in validation_results:
                if not result.valid and result.severity == "error":
                    next_steps.append(f"Fix: {result.message}")
        else:
            next_steps.append("Schedule regular security reviews")
            next_steps.append("Implement security monitoring")
            if compliance_framework:
                next_steps.append(f"Complete {compliance_framework} compliance audit")
        
        return EnvironmentManagerResult(
            security_validations=validation_results,
            summary=summary,
            next_steps=next_steps
        )
    
    def _get_security_checks(
        self, 
        environment: str,
        compliance_framework: Optional[str] = None
    ) -> List[SecuritySetting]:
        """Get security settings to check."""
        checks = [
            SecuritySetting(
                name="ssl_enabled",
                category="encryption",
                description="HTTPS/TLS encryption enabled",
                required_for_production=True,
                validation_check="Verify SSL certificate is valid and not expired",
                remediation="Enable SSL/TLS with valid certificate",
                compliance_frameworks=["HIPAA", "SOC2"]
            ),
            SecuritySetting(
                name="cors_configured",
                category="network",
                description="CORS properly configured",
                required_for_production=True,
                validation_check="Check CORS headers are restrictive",
                remediation="Configure CORS to allow only trusted origins",
                compliance_frameworks=["SOC2"]
            ),
            SecuritySetting(
                name="rate_limiting",
                category="network",
                description="API rate limiting enabled",
                required_for_production=True,
                validation_check="Verify rate limits are enforced",
                remediation="Implement rate limiting to prevent abuse",
                compliance_frameworks=["SOC2"]
            ),
            SecuritySetting(
                name="audit_logging",
                category="compliance",
                description="Comprehensive audit logging",
                required_for_production=True,
                validation_check="Verify all access is logged",
                remediation="Implement audit logging for all data access",
                compliance_frameworks=["HIPAA", "SOC2"]
            ),
            SecuritySetting(
                name="encryption_at_rest",
                category="encryption",
                description="Data encrypted at rest",
                required_for_production=True,
                validation_check="Verify database and file encryption",
                remediation="Enable encryption for all data storage",
                compliance_frameworks=["HIPAA", "SOC2"]
            ),
            SecuritySetting(
                name="mfa_enabled",
                category="authentication",
                description="Multi-factor authentication",
                required_for_production=True,
                validation_check="Verify MFA is enforced for all users",
                remediation="Enable and enforce MFA",
                compliance_frameworks=["SOC2"]
            )
        ]
        
        # Add HIPAA-specific checks
        if compliance_framework == "HIPAA":
            checks.extend([
                SecuritySetting(
                    name="phi_encryption",
                    category="compliance",
                    description="PHI encryption in transit and at rest",
                    required_for_production=True,
                    validation_check="Verify all PHI is encrypted",
                    remediation="Implement field-level encryption for PHI",
                    compliance_frameworks=["HIPAA"]
                ),
                SecuritySetting(
                    name="access_controls",
                    category="compliance",
                    description="Role-based access controls for PHI",
                    required_for_production=True,
                    validation_check="Verify RBAC implementation",
                    remediation="Implement granular access controls",
                    compliance_frameworks=["HIPAA"]
                ),
                SecuritySetting(
                    name="backup_encryption",
                    category="compliance",
                    description="Encrypted backups",
                    required_for_production=True,
                    validation_check="Verify backup encryption",
                    remediation="Encrypt all backup data",
                    compliance_frameworks=["HIPAA"]
                ),
                SecuritySetting(
                    name="encryption_in_transit",
                    category="encryption",
                    description="All data encrypted in transit",
                    required_for_production=True,
                    validation_check="Verify TLS 1.2+ for all connections",
                    remediation="Enforce TLS 1.2 or higher",
                    compliance_frameworks=["HIPAA"]
                )
            ])
        
        return checks
    
    def _validate_security_setting(
        self,
        check: SecuritySetting,
        settings: Dict[str, Any],
        environment: str
    ) -> ValidationResult:
        """Validate a single security setting."""
        setting_value = settings.get(check.name)
        
        # Check if required for production
        if environment == "production" and check.required_for_production:
            if setting_value is None:
                return ValidationResult(
                    name=check.name,
                    valid=False,
                    message=f"{check.description} is required for production. {check.remediation}",
                    category=check.category,
                    severity="error"
                )
            elif setting_value is False:
                return ValidationResult(
                    name=check.name,
                    valid=False,
                    message=f"{check.description} must be enabled for production. {check.remediation}",
                    category=check.category,
                    severity="error"
                )
        
        # Validate specific settings
        if check.name == "ssl_enabled" and setting_value is True:
            return ValidationResult(
                name=check.name,
                valid=True,
                message="SSL/TLS properly configured",
                category=check.category,
                severity="info"
            )
        
        if check.name == "session_timeout":
            if isinstance(setting_value, (int, float)):
                if setting_value > 3600:  # 1 hour
                    return ValidationResult(
                        name=check.name,
                        valid=True,
                        message="Session timeout may be too long for healthcare applications",
                        category="authentication",
                        severity="warning"
                    )
        
        # Default validation
        if setting_value is True:
            return ValidationResult(
                name=check.name,
                valid=True,
                message=f"{check.description} is properly configured",
                category=check.category,
                severity="info"
            )
        elif setting_value is False:
            severity = "error" if environment == "production" else "warning"
            return ValidationResult(
                name=check.name,
                valid=False,
                message=f"{check.description} should be enabled. {check.remediation}",
                category=check.category,
                severity=severity
            )
        else:
            return ValidationResult(
                name=check.name,
                valid=False,
                message=f"{check.description} configuration not found",
                category=check.category,
                severity="warning"
            )
    
    def _get_transition_guide(self, **kwargs) -> EnvironmentManagerResult:
        """Get guide for transitioning between environments."""
        from_env = kwargs.get("from_environment")
        to_env = kwargs.get("to_environment")
        
        if not from_env or not to_env:
            raise ToolError(
                "Missing required parameters",
                details={"required": ["from_environment", "to_environment"]}
            )
        
        valid_environments = ["development", "staging", "production"]
        if from_env not in valid_environments or to_env not in valid_environments:
            raise ToolError(
                "Invalid environment specified",
                details={"valid_environments": valid_environments}
            )
        
        # Create transition guide based on environments
        if from_env == "staging" and to_env == "production":
            transition = self._staging_to_production_guide()
        elif from_env == "development" and to_env == "staging":
            transition = self._development_to_staging_guide()
        else:
            transition = self._generic_transition_guide(from_env, to_env)
        
        summary = f"Transition guide from {from_env} to {to_env}"
        next_steps = [
            "Review and complete all checklist items",
            "Perform thorough testing before transition",
            "Have rollback plan ready",
            "Monitor closely after transition"
        ]
        
        return EnvironmentManagerResult(
            transition_guide=transition,
            summary=summary,
            next_steps=next_steps
        )
    
    def _staging_to_production_guide(self) -> EnvironmentTransition:
        """Guide for staging to production transition."""
        return EnvironmentTransition(
            from_environment="staging",
            to_environment="production",
            checklist=[
                "Complete all testing in staging environment",
                "Perform load testing to verify performance",
                "Review and update all configuration values",
                "Verify all integrations work with production endpoints",
                "Create complete backup of current production",
                "Update DNS and load balancer configurations",
                "Prepare monitoring and alerting rules",
                "Schedule deployment during maintenance window",
                "Notify all stakeholders of deployment",
                "Prepare incident response team",
                "Document all changes in deployment log",
                "Verify compliance requirements are met",
                "Test disaster recovery procedures",
                "Review security configurations",
                "Ensure all secrets are properly managed"
            ],
            config_changes=[
                "Update HEALTHIE_API_URL to production endpoint",
                "Change LOG_LEVEL from DEBUG to INFO or WARNING",
                "Update database connection strings",
                "Configure production SSL certificates",
                "Set production rate limits",
                "Update external service endpoints",
                "Configure production backup schedules"
            ],
            testing_requirements=[
                "Full integration test suite",
                "Load and performance testing",
                "Security penetration testing",
                "Compliance validation testing",
                "User acceptance testing",
                "Failover and recovery testing",
                "API compatibility testing"
            ],
            rollback_plan=[
                "Stop deployment immediately if critical issues found",
                "Switch load balancer back to previous version",
                "Restore database from backup if needed",
                "Revert configuration changes",
                "Clear caches and restart services",
                "Notify team of rollback",
                "Investigate root cause",
                "Document lessons learned"
            ],
            data_migration={
                "strategy": "blue-green deployment",
                "validation": "Compare data checksums",
                "rollback": "Keep previous version running until verified"
            }
        )
    
    def _development_to_staging_guide(self) -> EnvironmentTransition:
        """Guide for development to staging transition."""
        return EnvironmentTransition(
            from_environment="development",
            to_environment="staging",
            checklist=[
                "Merge feature branches to staging branch",
                "Run full test suite",
                "Update staging configurations",
                "Deploy to staging environment",
                "Run smoke tests",
                "Verify integrations with staging services",
                "Test with staging data",
                "Document any issues found"
            ],
            config_changes=[
                "Update API URLs to staging endpoints",
                "Adjust log levels for debugging",
                "Configure staging database",
                "Update feature flags"
            ],
            testing_requirements=[
                "Unit tests",
                "Integration tests",
                "Basic load testing",
                "API contract testing"
            ],
            rollback_plan=[
                "Revert to previous staging version",
                "Clear staging caches",
                "Reset staging database if needed",
                "Document issues for fixing"
            ]
        )
    
    def _generic_transition_guide(self, from_env: str, to_env: str) -> EnvironmentTransition:
        """Generic transition guide."""
        return EnvironmentTransition(
            from_environment=from_env,
            to_environment=to_env,
            checklist=[
                f"Review differences between {from_env} and {to_env}",
                "Update configuration files",
                "Run tests appropriate for target environment",
                "Deploy application",
                "Verify deployment success",
                "Monitor for issues"
            ],
            config_changes=[
                "Update environment-specific variables",
                "Adjust service endpoints",
                "Update credentials and secrets"
            ],
            testing_requirements=[
                "Smoke tests",
                "Integration tests",
                "Environment-specific tests"
            ],
            rollback_plan=[
                "Revert to previous version",
                "Restore configurations",
                "Document and fix issues"
            ]
        )


def setup_environment_manager_tool(
    mcp: FastMCP,
    schema_manager: SchemaManagerProtocol
) -> None:
    """Set up the Environment Manager tool in the MCP server.
    
    Args:
        mcp: The FastMCP server instance
        schema_manager: The schema manager instance
    """
    tool = EnvironmentManagerTool(schema_manager)
    
    @mcp.tool(
        name=tool.get_tool_name(),
        description=tool.get_tool_description()
    )
    async def environment_manager(
        action: str,
        environment: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        deployment_type: Optional[str] = None,
        secret_type: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
        compliance_framework: Optional[str] = None,
        from_environment: Optional[str] = None,
        to_environment: Optional[str] = None
    ) -> Dict[str, Any]:
        """Manage environment configurations, deployments, and security.
        
        Args:
            action: The action to perform (validate_config, deployment_checklist, 
                   manage_secrets, validate_security, transition_guide)
            environment: Target environment (development, staging, production)
            config: Configuration values to validate (for validate_config)
            deployment_type: Type of deployment (initial, update) for checklist
            secret_type: Type of secret to manage (api_key, database_password, all)
            settings: Security settings to validate
            compliance_framework: Compliance framework to check against (e.g., HIPAA)
            from_environment: Source environment for transitions
            to_environment: Target environment for transitions
            
        Returns:
            Environment management results with recommendations
        """
        result = tool.execute(
            action=action,
            environment=environment,
            config=config,
            deployment_type=deployment_type,
            secret_type=secret_type,
            settings=settings,
            compliance_framework=compliance_framework,
            from_environment=from_environment,
            to_environment=to_environment
        )
        return result.model_dump(mode="json", exclude_none=True)