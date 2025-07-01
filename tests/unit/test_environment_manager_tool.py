"""Unit tests for the Environment Manager tool."""

import pytest
from unittest.mock import Mock, MagicMock
from src.healthie_mcp.tools.environment_manager import EnvironmentManagerTool
from src.healthie_mcp.models.environment_manager import (
    EnvironmentManagerResult,
    ValidationResult,
    DeploymentStep,
    SecretManagement,
    EnvironmentTransition
)
from src.healthie_mcp.exceptions import ToolError


class TestEnvironmentManagerTool:
    """Test cases for the Environment Manager tool."""
    
    @pytest.fixture
    def mock_schema_manager(self):
        """Create a mock schema manager."""
        mock = Mock()
        mock.ensure_schema = MagicMock()
        mock.get_schema_path = MagicMock(return_value="/mock/schema.graphql")
        return mock
    
    @pytest.fixture
    def tool(self, mock_schema_manager):
        """Create an Environment Manager tool instance."""
        return EnvironmentManagerTool(mock_schema_manager)
    
    def test_tool_name_and_description(self, tool):
        """Test tool has correct name and description."""
        assert tool.get_tool_name() == "environment_manager"
        assert "environment" in tool.get_tool_description().lower()
        assert "deployment" in tool.get_tool_description().lower()
    
    def test_environment_manager_validates_configs(self, tool):
        """Test that the tool validates environment configurations."""
        # Test with a mix of valid and invalid configurations
        result = tool.execute(
            action="validate_config",
            environment="production",
            config={
                "HEALTHIE_API_URL": "https://api.gethealthie.com/graphql",
                "HEALTHIE_API_KEY": "",  # Empty API key should fail
                "REQUEST_TIMEOUT": "30",
                "MAX_RETRIES": "abc",  # Invalid number should fail
                "LOG_LEVEL": "INFO",
                "ENABLE_TELEMETRY": "true"
            }
        )
        
        assert isinstance(result, EnvironmentManagerResult)
        assert result.validation_results is not None
        assert len(result.validation_results) > 0
        
        # Check that we have both valid and invalid results
        valid_configs = [r for r in result.validation_results if r.valid]
        invalid_configs = [r for r in result.validation_results if not r.valid]
        
        assert len(valid_configs) > 0
        assert len(invalid_configs) > 0
        
        # Check specific validations
        api_key_result = next(
            (r for r in result.validation_results if r.name == "HEALTHIE_API_KEY"),
            None
        )
        assert api_key_result is not None
        assert not api_key_result.valid
        assert api_key_result.severity == "error"
        
        # Test with all valid configurations
        result = tool.execute(
            action="validate_config",
            environment="development",
            config={
                "HEALTHIE_API_URL": "https://staging-api.gethealthie.com/graphql",
                "HEALTHIE_API_KEY": "dev_test_key_123",
                "REQUEST_TIMEOUT": "60",
                "LOG_LEVEL": "DEBUG"
            }
        )
        
        assert all(r.valid for r in result.validation_results)
        assert "valid" in result.summary.lower()
    
    def test_environment_manager_provides_deployment_checklist(self, tool):
        """Test that the tool provides deployment checklists."""
        # Test production deployment checklist
        result = tool.execute(
            action="deployment_checklist",
            environment="production",
            deployment_type="initial"
        )
        
        assert isinstance(result, EnvironmentManagerResult)
        assert result.deployment_checklist is not None
        assert len(result.deployment_checklist) > 0
        
        # Check checklist structure
        steps = result.deployment_checklist
        assert all(isinstance(step, DeploymentStep) for step in steps)
        
        # Check ordering
        orders = [step.order for step in steps]
        assert orders == sorted(orders)
        
        # Check categories
        categories = {step.category for step in steps}
        assert "pre-deployment" in categories
        assert "deployment" in categories
        assert "post-deployment" in categories
        
        # Check for critical steps
        step_titles = {step.title.lower() for step in steps}
        assert any("backup" in title for title in step_titles)
        assert any("test" in title or "verify" in title for title in step_titles)
        assert any("rollback" in title for title in step_titles)
        
        # Test update deployment checklist
        result = tool.execute(
            action="deployment_checklist",
            environment="production",
            deployment_type="update"
        )
        
        update_steps = result.deployment_checklist
        assert len(update_steps) > 0
        
        # Update checklist might be different from initial
        update_titles = {step.title for step in update_steps}
        initial_titles = {step.title for step in steps}
        assert update_titles != initial_titles or len(update_titles) != len(initial_titles)
    
    def test_environment_manager_manages_secrets(self, tool):
        """Test that the tool provides secret management guidance."""
        # Test API key management
        result = tool.execute(
            action="manage_secrets",
            secret_type="api_key",
            environment="production"
        )
        
        assert isinstance(result, EnvironmentManagerResult)
        assert result.secret_recommendations is not None
        assert len(result.secret_recommendations) > 0
        
        api_key_rec = result.secret_recommendations[0]
        assert isinstance(api_key_rec, SecretManagement)
        assert api_key_rec.type == "api_key"
        assert len(api_key_rec.never_do) > 0
        assert api_key_rec.environment_separation is True
        assert "env" in api_key_rec.storage_recommendation.lower() or \
               "vault" in api_key_rec.storage_recommendation.lower()
        
        # Test multiple secret types
        result = tool.execute(
            action="manage_secrets",
            secret_type="all",
            environment="production"
        )
        
        secret_types = {rec.type for rec in result.secret_recommendations}
        assert "api_key" in secret_types
        assert "database_password" in secret_types
        assert "jwt_secret" in secret_types
        
        # Check for security best practices
        for rec in result.secret_recommendations:
            assert len(rec.access_control) > 0
            # At least one secret type should have commit warning
        
        # Check that at least one recommendation mentions not committing to version control
        commit_warnings = [
            item for rec in result.secret_recommendations 
            for item in rec.never_do 
            if "commit" in item.lower()
        ]
        assert len(commit_warnings) > 0
    
    def test_environment_manager_validates_security_settings(self, tool):
        """Test that the tool validates security settings."""
        # Test with some security issues
        result = tool.execute(
            action="validate_security",
            environment="production",
            settings={
                "ssl_enabled": True,
                "rate_limiting": True,
                "cors_configured": False,  # Should flag as issue
                "encryption_at_rest": True,
                "audit_logging": False,  # Should flag as issue for production
                "mfa_enabled": True,
                "session_timeout": 3600
            }
        )
        
        assert isinstance(result, EnvironmentManagerResult)
        assert result.security_validations is not None
        
        # Find specific security issues
        cors_result = next(
            (r for r in result.security_validations if "cors" in r.name.lower()),
            None
        )
        assert cors_result is not None
        assert not cors_result.valid
        assert cors_result.severity == "error"
        
        audit_result = next(
            (r for r in result.security_validations if "audit" in r.name.lower()),
            None
        )
        assert audit_result is not None
        assert not audit_result.valid
        
        # Test HIPAA compliance check
        result = tool.execute(
            action="validate_security",
            environment="production",
            compliance_framework="HIPAA",
            settings={
                "encryption_at_rest": True,
                "encryption_in_transit": True,
                "audit_logging": True,
                "access_controls": True,
                "phi_encryption": True,
                "backup_encryption": True
            }
        )
        
        # Should have HIPAA-specific validations
        hipaa_validations = [
            r for r in result.security_validations 
            if r.category == "compliance" or "HIPAA" in str(r.message)
        ]
        assert len(hipaa_validations) > 0
    
    def test_environment_manager_supports_staging_to_prod(self, tool):
        """Test that the tool supports staging to production transitions."""
        result = tool.execute(
            action="transition_guide",
            from_environment="staging",
            to_environment="production"
        )
        
        assert isinstance(result, EnvironmentManagerResult)
        assert result.transition_guide is not None
        
        transition = result.transition_guide
        assert isinstance(transition, EnvironmentTransition)
        assert transition.from_environment == "staging"
        assert transition.to_environment == "production"
        
        # Check comprehensive checklist
        assert len(transition.checklist) >= 10
        checklist_lower = [item.lower() for item in transition.checklist]
        
        # Should include critical items
        assert any("test" in item for item in checklist_lower)
        assert any("backup" in item for item in checklist_lower)
        assert any("config" in item for item in checklist_lower)
        assert any("monitor" in item for item in checklist_lower)
        
        # Check config changes
        assert len(transition.config_changes) > 0
        config_changes_lower = [change.lower() for change in transition.config_changes]
        assert any("api" in change and "url" in change for change in config_changes_lower)
        assert any("log" in change and "level" in change for change in config_changes_lower)
        
        # Check testing requirements
        assert len(transition.testing_requirements) > 0
        assert any("integration" in req.lower() for req in transition.testing_requirements)
        assert any("load" in req.lower() or "performance" in req.lower() 
                  for req in transition.testing_requirements)
        
        # Check rollback plan
        assert len(transition.rollback_plan) > 0
        assert transition.rollback_plan[0].lower().startswith(
            ("stop", "halt", "pause", "suspend")
        )
        
        # Test development to staging transition (should be simpler)
        result = tool.execute(
            action="transition_guide",
            from_environment="development",
            to_environment="staging"
        )
        
        dev_transition = result.transition_guide
        assert len(dev_transition.checklist) < len(transition.checklist)
        assert len(dev_transition.testing_requirements) <= len(transition.testing_requirements)
    
    def test_environment_manager_handles_invalid_inputs(self, tool):
        """Test that the tool handles invalid inputs gracefully."""
        # Invalid action
        with pytest.raises(ToolError) as exc_info:
            tool.execute(action="invalid_action")
        
        assert "Invalid action" in str(exc_info.value)
        
        # Missing required parameters
        with pytest.raises(ToolError) as exc_info:
            tool.execute(action="validate_config")
        
        assert "environment" in str(exc_info.value).lower()
        
        # Invalid environment
        with pytest.raises(ToolError) as exc_info:
            tool.execute(
                action="deployment_checklist",
                environment="invalid_env"
            )
        
        assert "Invalid environment" in str(exc_info.value)
    
    def test_environment_manager_provides_helpful_summaries(self, tool):
        """Test that the tool provides helpful summaries and next steps."""
        # Test config validation summary
        result = tool.execute(
            action="validate_config",
            environment="development",
            config={
                "HEALTHIE_API_URL": "https://staging-api.gethealthie.com/graphql",
                "HEALTHIE_API_KEY": "dev_key_123"
            }
        )
        
        assert len(result.summary) > 0
        assert len(result.next_steps) > 0
        assert any("deploy" in step.lower() for step in result.next_steps)
        
        # Test security validation with issues
        result = tool.execute(
            action="validate_security",
            environment="production",
            settings={
                "ssl_enabled": False,
                "audit_logging": False
            }
        )
        
        assert "issue" in result.summary.lower() or "problem" in result.summary.lower()
        assert any("fix" in step.lower() or "enable" in step.lower() 
                  for step in result.next_steps)