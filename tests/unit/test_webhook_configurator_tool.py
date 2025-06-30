"""Unit tests for webhook configurator MCP tool functionality."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

# Mock the MCP module before importing our modules
sys.modules['mcp'] = MagicMock()
sys.modules['mcp.server'] = MagicMock()
sys.modules['mcp.server.fastmcp'] = MagicMock()

from healthie_mcp.models.webhook_configurator import (
    WebhookConfiguratorInput, WebhookConfiguratorResult, ValidationResult,
    WebhookEvent, SecurityLevel, WebhookSecurity, EventFilter, 
    WebhookConfiguration, PayloadExample
)


class TestWebhookConfiguratorTool:
    """Test suite for webhook configurator MCP tool functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_schema_manager = Mock()
        self.mock_mcp = MagicMock()
        self.registered_tools = {}
        
        # Mock the tool decorator to capture registered functions
        def mock_tool():
            def decorator(func):
                self.registered_tools[func.__name__] = func
                return func
            return decorator
        
        self.mock_mcp.tool = mock_tool

    def test_webhook_configurator_validates_endpoint_basic(self):
        """Test that webhook configurator validates endpoint connectivity."""
        # Import the setup function (this will fail initially)
        from healthie_mcp.tools.webhook_configurator import setup_webhook_configurator_tool
        
        # Setup the tool
        setup_webhook_configurator_tool(self.mock_mcp, self.mock_schema_manager)
        
        # Get the registered function
        assert 'webhook_configurator' in self.registered_tools
        config_func = self.registered_tools['webhook_configurator']
        
        # Test input for endpoint validation
        test_input = WebhookConfiguratorInput(
            action="validate",
            endpoint_url="https://example.com/webhook",
            timeout_seconds=5
        )
        
        # Mock successful HTTP response
        with patch('httpx.Client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.elapsed.total_seconds.return_value = 0.5
            mock_response.headers = {'content-type': 'application/json'}
            mock_client.return_value.__enter__.return_value.post.return_value = mock_response
            
            result = config_func(**test_input.model_dump())
            
            # Should return successful validation
            assert isinstance(result, WebhookConfiguratorResult)
            assert result.error is None
            assert result.validation_result is not None
            assert result.validation_result.is_valid is True
            assert result.validation_result.status_code == 200
            assert result.validation_result.response_time_ms is not None

    def test_webhook_configurator_detects_ssl_issues(self):
        """Test that webhook configurator detects SSL/TLS issues."""
        from healthie_mcp.tools.webhook_configurator import setup_webhook_configurator_tool
        
        setup_webhook_configurator_tool(self.mock_mcp, self.mock_schema_manager)
        config_func = self.registered_tools['webhook_configurator']
        
        test_input = WebhookConfiguratorInput(
            action="check_ssl",
            endpoint_url="https://expired.badssl.com/",
            timeout_seconds=10
        )
        
        # Mock SSL error
        with patch('httpx.Client') as mock_client:
            import ssl
            mock_client.return_value.__enter__.return_value.post.side_effect = ssl.SSLError("Certificate expired")
            
            result = config_func(**test_input.model_dump())
            
            assert isinstance(result, WebhookConfiguratorResult)
            assert result.ssl_details is not None
            assert result.validation_result is not None
            assert result.validation_result.ssl_valid is False
            assert len(result.validation_result.security_issues) > 0

    def test_webhook_configurator_generates_security_config_basic(self):
        """Test that webhook configurator generates basic security configuration."""
        from healthie_mcp.tools.webhook_configurator import setup_webhook_configurator_tool
        
        setup_webhook_configurator_tool(self.mock_mcp, self.mock_schema_manager)
        config_func = self.registered_tools['webhook_configurator']
        
        test_input = WebhookConfiguratorInput(
            action="generate_security",
            security_level=SecurityLevel.BASIC,
            endpoint_url="https://example.com/webhook"
        )
        
        result = config_func(**test_input.model_dump())
        
        assert isinstance(result, WebhookConfiguratorResult)
        assert result.error is None
        assert result.security_config is not None
        assert isinstance(result.security_config, WebhookSecurity)
        assert len(result.security_config.signing_secret) > 0
        assert result.security_config.signature_header is not None
        assert result.security_config.timestamp_tolerance_seconds > 0

    def test_webhook_configurator_generates_hipaa_compliant_security(self):
        """Test that webhook configurator generates HIPAA-compliant security."""
        from healthie_mcp.tools.webhook_configurator import setup_webhook_configurator_tool
        
        setup_webhook_configurator_tool(self.mock_mcp, self.mock_schema_manager)
        config_func = self.registered_tools['webhook_configurator']
        
        test_input = WebhookConfiguratorInput(
            action="generate_security",
            security_level=SecurityLevel.HIPAA_COMPLIANT,
            endpoint_url="https://example.com/webhook"
        )
        
        result = config_func(**test_input.model_dump())
        
        assert isinstance(result, WebhookConfiguratorResult)
        assert result.error is None
        assert result.security_config is not None
        
        # HIPAA compliant should have stricter requirements
        assert result.security_config.timestamp_tolerance_seconds <= 300
        assert len(result.security_config.required_headers) > 0
        assert result.security_config.ip_whitelist is not None or result.security_config.user_agent_pattern is not None
        
        # Should have HIPAA-specific recommendations
        hipaa_recommendations = [r for r in result.recommendations if 'HIPAA' in r or 'compliance' in r.lower()]
        assert len(hipaa_recommendations) > 0

    def test_webhook_configurator_maps_events_to_patient_workflow(self):
        """Test that webhook configurator maps events to patient management workflow."""
        from healthie_mcp.tools.webhook_configurator import setup_webhook_configurator_tool
        
        setup_webhook_configurator_tool(self.mock_mcp, self.mock_schema_manager)
        config_func = self.registered_tools['webhook_configurator']
        
        test_input = WebhookConfiguratorInput(
            action="map_events",
            workflow_type="patient_management"
        )
        
        result = config_func(**test_input.model_dump())
        
        assert isinstance(result, WebhookConfiguratorResult)
        assert result.error is None
        assert result.event_mappings is not None
        assert "patient_management" in result.event_mappings
        
        # Should include patient-related events
        patient_events = result.event_mappings["patient_management"]
        expected_events = [WebhookEvent.PATIENT_CREATED, WebhookEvent.PATIENT_UPDATED]
        for event in expected_events:
            assert event in patient_events

    def test_webhook_configurator_maps_events_to_appointment_workflow(self):
        """Test that webhook configurator maps events to appointment workflow."""
        from healthie_mcp.tools.webhook_configurator import setup_webhook_configurator_tool
        
        setup_webhook_configurator_tool(self.mock_mcp, self.mock_schema_manager)
        config_func = self.registered_tools['webhook_configurator']
        
        test_input = WebhookConfiguratorInput(
            action="map_events",
            workflow_type="appointments"
        )
        
        result = config_func(**test_input.model_dump())
        
        assert isinstance(result, WebhookConfiguratorResult)
        assert result.event_mappings is not None
        assert "appointments" in result.event_mappings
        
        # Should include appointment-related events
        appointment_events = result.event_mappings["appointments"]
        expected_events = [
            WebhookEvent.APPOINTMENT_CREATED, 
            WebhookEvent.APPOINTMENT_UPDATED,
            WebhookEvent.APPOINTMENT_CANCELLED
        ]
        for event in expected_events:
            assert event in appointment_events

    def test_webhook_configurator_provides_payload_examples(self):
        """Test that webhook configurator provides payload examples for events."""
        from healthie_mcp.tools.webhook_configurator import setup_webhook_configurator_tool
        
        setup_webhook_configurator_tool(self.mock_mcp, self.mock_schema_manager)
        config_func = self.registered_tools['webhook_configurator']
        
        test_input = WebhookConfiguratorInput(
            action="get_examples",
            events=[WebhookEvent.PATIENT_CREATED, WebhookEvent.APPOINTMENT_CREATED]
        )
        
        result = config_func(**test_input.model_dump())
        
        assert isinstance(result, WebhookConfiguratorResult)
        assert result.error is None
        assert result.payload_examples is not None
        assert len(result.payload_examples) == 2
        
        # Check example structure
        for example in result.payload_examples:
            assert isinstance(example, PayloadExample)
            assert example.event in [WebhookEvent.PATIENT_CREATED, WebhookEvent.APPOINTMENT_CREATED]
            assert example.headers is not None
            assert example.payload is not None
            assert example.signature is not None
            assert example.timestamp is not None

    def test_webhook_configurator_creates_complete_configuration(self):
        """Test that webhook configurator creates complete webhook configuration."""
        from healthie_mcp.tools.webhook_configurator import setup_webhook_configurator_tool
        
        setup_webhook_configurator_tool(self.mock_mcp, self.mock_schema_manager)
        config_func = self.registered_tools['webhook_configurator']
        
        test_input = WebhookConfiguratorInput(
            action="configure",
            endpoint_url="https://example.com/webhook",
            events=[WebhookEvent.PATIENT_CREATED, WebhookEvent.APPOINTMENT_CREATED],
            security_level=SecurityLevel.STANDARD,
            workflow_type="patient_management"
        )
        
        result = config_func(**test_input.model_dump())
        
        assert isinstance(result, WebhookConfiguratorResult)
        assert result.error is None
        assert result.configuration is not None
        
        config = result.configuration
        assert isinstance(config, WebhookConfiguration)
        assert str(config.endpoint_url) == "https://example.com/webhook"
        assert config.security is not None
        assert config.event_filter is not None
        assert WebhookEvent.PATIENT_CREATED in config.event_filter.events
        assert config.active is True

    def test_webhook_configurator_handles_invalid_endpoint(self):
        """Test that webhook configurator handles invalid endpoints gracefully."""
        from healthie_mcp.tools.webhook_configurator import setup_webhook_configurator_tool
        
        setup_webhook_configurator_tool(self.mock_mcp, self.mock_schema_manager)
        config_func = self.registered_tools['webhook_configurator']
        
        test_input = WebhookConfiguratorInput(
            action="validate",
            endpoint_url="https://nonexistent.example.invalid/webhook",
            timeout_seconds=5
        )
        
        # Mock connection error
        with patch('httpx.Client') as mock_client:
            import httpx
            mock_client.return_value.__enter__.return_value.post.side_effect = httpx.ConnectError("Connection failed")
            
            result = config_func(**test_input.model_dump())
            
            assert isinstance(result, WebhookConfiguratorResult)
            assert result.validation_result is not None
            assert result.validation_result.is_valid is False
            assert result.validation_result.error_message is not None
            assert len(result.recommendations) > 0

    def test_webhook_configurator_validates_event_filtering(self):
        """Test that webhook configurator validates event filtering configuration."""
        from healthie_mcp.tools.webhook_configurator import setup_webhook_configurator_tool
        
        setup_webhook_configurator_tool(self.mock_mcp, self.mock_schema_manager)
        config_func = self.registered_tools['webhook_configurator']
        
        # Test with specific filtering conditions
        existing_config = {
            "event_filter": {
                "events": ["patient_created", "patient_updated"],
                "patient_tags": ["high_priority"],
                "provider_ids": ["provider_123"]
            }
        }
        
        test_input = WebhookConfiguratorInput(
            action="configure",
            endpoint_url="https://example.com/webhook",
            existing_config=existing_config,
            events=[WebhookEvent.PATIENT_CREATED]
        )
        
        result = config_func(**test_input.model_dump())
        
        assert isinstance(result, WebhookConfiguratorResult)
        assert result.error is None
        assert result.configuration is not None
        
        # Should preserve and validate filtering
        event_filter = result.configuration.event_filter
        assert event_filter.patient_tags == ["high_priority"]
        assert event_filter.provider_ids == ["provider_123"]
        
        # Should have recommendations about filtering
        filter_recommendations = [r for r in result.recommendations if 'filter' in r.lower()]
        assert len(filter_recommendations) > 0

    def test_webhook_configurator_requires_valid_action(self):
        """Test that webhook configurator requires valid action parameter."""
        from healthie_mcp.tools.webhook_configurator import setup_webhook_configurator_tool
        
        setup_webhook_configurator_tool(self.mock_mcp, self.mock_schema_manager)
        config_func = self.registered_tools['webhook_configurator']
        
        # Test with invalid action
        with pytest.raises(ValueError, match="Action must be one of"):
            WebhookConfiguratorInput(
                action="invalid_action",
                endpoint_url="https://example.com/webhook"
            )

    def test_webhook_configurator_handles_timeout_gracefully(self):
        """Test that webhook configurator handles timeout scenarios gracefully."""
        from healthie_mcp.tools.webhook_configurator import setup_webhook_configurator_tool
        
        setup_webhook_configurator_tool(self.mock_mcp, self.mock_schema_manager)
        config_func = self.registered_tools['webhook_configurator']
        
        test_input = WebhookConfiguratorInput(
            action="validate",
            endpoint_url="https://httpbin.org/delay/15",  # Will timeout
            timeout_seconds=2
        )
        
        # Mock timeout error
        with patch('httpx.Client') as mock_client:
            import httpx
            mock_client.return_value.__enter__.return_value.post.side_effect = httpx.TimeoutException("Request timed out")
            
            result = config_func(**test_input.model_dump())
            
            assert isinstance(result, WebhookConfiguratorResult)
            assert result.validation_result is not None
            assert result.validation_result.is_valid is False
            assert "timeout" in result.validation_result.error_message.lower()
            
            # Should provide timeout-specific recommendations
            timeout_recommendations = [r for r in result.recommendations if 'timeout' in r.lower()]
            assert len(timeout_recommendations) > 0