"""Webhook configurator tool for the Healthie MCP server - Refactored version."""

import os
import time
import ssl
import secrets
import hashlib
import hmac
import httpx
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
from mcp.server.fastmcp import FastMCP
from ..models.webhook_configurator import (
    WebhookConfiguratorInput, WebhookConfiguratorResult, ValidationResult,
    WebhookEvent, SecurityLevel, WebhookSecurity, EventFilter,
    WebhookConfiguration, PayloadExample
)


class WebhookConfigurator:
    """Manages webhook configuration, validation, and security for Healthie API."""
    
    # Workflow to event mappings
    WORKFLOW_MAPPINGS = {
        "patient_management": [
            WebhookEvent.PATIENT_CREATED,
            WebhookEvent.PATIENT_UPDATED,
            WebhookEvent.DOCUMENT_UPLOADED,
            WebhookEvent.FORM_SUBMITTED
        ],
        "appointments": [
            WebhookEvent.APPOINTMENT_CREATED,
            WebhookEvent.APPOINTMENT_UPDATED,
            WebhookEvent.APPOINTMENT_CANCELLED
        ],
        "billing": [
            WebhookEvent.PAYMENT_COMPLETED,
            WebhookEvent.PAYMENT_FAILED
        ],
        "clinical_data": [
            WebhookEvent.FORM_SUBMITTED,
            WebhookEvent.CARE_PLAN_UPDATED,
            WebhookEvent.TASK_COMPLETED
        ],
        "communication": [
            WebhookEvent.CHAT_MESSAGE_CREATED
        ]
    }
    
    # Security configuration defaults
    SECURITY_DEFAULTS = {
        SecurityLevel.BASIC: {
            "timestamp_tolerance": 600,  # 10 minutes
            "required_headers": [],
            "user_agent_pattern": None,
            "ip_whitelist": None
        },
        SecurityLevel.STANDARD: {
            "timestamp_tolerance": 300,  # 5 minutes
            "required_headers": [],
            "user_agent_pattern": None,
            "ip_whitelist": None
        },
        SecurityLevel.ENHANCED: {
            "timestamp_tolerance": 180,  # 3 minutes
            "required_headers": ["X-Healthie-Event", "X-Healthie-Delivery"],
            "user_agent_pattern": "Healthie-Webhook/\\d+\\.\\d+",
            "ip_whitelist": None
        },
        SecurityLevel.HIPAA_COMPLIANT: {
            "timestamp_tolerance": 120,  # 2 minutes
            "required_headers": ["X-Healthie-Event", "X-Healthie-Delivery", "X-Healthie-Environment"],
            "user_agent_pattern": "Healthie-Webhook/\\d+\\.\\d+",
            "ip_whitelist": ["198.51.100.0/24"]  # Example IP range
        }
    }
    
    def __init__(self, input_data: WebhookConfiguratorInput):
        self.input_data = input_data
    
    def process_action(self) -> WebhookConfiguratorResult:
        """Process the requested webhook action."""
        action_handlers = {
            "validate": self._validate_webhook_endpoint,
            "check_ssl": self._check_ssl_configuration,
            "generate_security": self._generate_security_configuration,
            "map_events": self._map_events_to_workflows,
            "get_examples": self._get_payload_examples,
            "configure": self._create_complete_configuration
        }
        
        handler = action_handlers.get(self.input_data.action)
        if not handler:
            return WebhookConfiguratorResult(
                action_performed=self.input_data.action,
                error=f"Unknown action: {self.input_data.action}",
                summary="Action not recognized"
            )
        
        try:
            return handler()
        except Exception as e:
            return WebhookConfiguratorResult(
                action_performed=self.input_data.action,
                error=f"Operation failed: {str(e)}",
                summary="Unexpected error occurred"
            )
    
    def _validate_webhook_endpoint(self) -> WebhookConfiguratorResult:
        """Validate webhook endpoint connectivity and configuration."""
        if not self.input_data.endpoint_url:
            return WebhookConfiguratorResult(
                action_performed="validate",
                error="Endpoint URL is required for validation",
                summary="Validation failed - missing endpoint URL"
            )
        
        # Parse URL for basic validation
        parsed_url = urlparse(str(self.input_data.endpoint_url))
        if parsed_url.scheme not in ['http', 'https']:
            return self._create_url_scheme_error(parsed_url.scheme)
        
        # Test endpoint connectivity
        headers = self._build_validation_headers()
        test_payload = self._create_test_payload()
        
        try:
            return self._perform_endpoint_test(headers, test_payload, parsed_url)
        except httpx.TimeoutException:
            return self._create_timeout_error()
        except httpx.ConnectError:
            return self._create_connection_error()
        except ssl.SSLError as e:
            return self._create_ssl_error(str(e))
        except Exception as e:
            return self._create_generic_error(str(e))
    
    def _create_url_scheme_error(self, scheme: str) -> WebhookConfiguratorResult:
        """Create error result for invalid URL scheme."""
        return WebhookConfiguratorResult(
            action_performed="validate",
            validation_result=ValidationResult(
                is_valid=False,
                error_message="Invalid URL scheme. Use http or https.",
                security_issues=["Non-secure protocol"] if scheme == 'http' else [],
                recommendations=["Use HTTPS for secure webhook delivery"]
            ),
            summary="Endpoint validation failed - invalid URL scheme"
        )
    
    def _build_validation_headers(self) -> Dict[str, str]:
        """Build headers for endpoint validation."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Healthie-Webhook-Validator/1.0"
        }
        
        # Add custom headers if provided
        if self.input_data.custom_headers:
            headers.update(self.input_data.custom_headers)
        
        return headers
    
    def _create_test_payload(self) -> Dict[str, Any]:
        """Create test payload for validation."""
        return {
            "event": "test_validation",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {"validation": True}
        }
    
    def _perform_endpoint_test(
        self, 
        headers: Dict[str, str], 
        test_payload: Dict[str, Any], 
        parsed_url
    ) -> WebhookConfiguratorResult:
        """Perform the actual endpoint test."""
        start_time = time.time()
        
        with httpx.Client() as client:
            response = client.post(
                str(self.input_data.endpoint_url),
                json=test_payload,
                headers=headers,
                timeout=self.input_data.timeout_seconds
            )
        
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Analyze response
        ssl_valid = parsed_url.scheme == 'https'
        headers_valid = True  # Basic validation passed
        security_issues = []
        recommendations = []
        
        if parsed_url.scheme == 'http':
            security_issues.append("Using HTTP instead of HTTPS")
            recommendations.append("Use HTTPS to encrypt webhook data in transit")
        
        if response.status_code not in [200, 201, 202, 204]:
            recommendations.append(f"Endpoint returned {response.status_code}. Consider returning 200-202 for successful webhook receipt")
        
        if response_time > 5000:  # 5 seconds
            recommendations.append("Endpoint response time is slow. Consider optimizing webhook processing")
        
        validation_result = ValidationResult(
            is_valid=True,
            status_code=response.status_code,
            response_time_ms=response_time,
            ssl_valid=ssl_valid,
            headers_valid=headers_valid,
            security_issues=security_issues,
            recommendations=recommendations
        )
        
        return WebhookConfiguratorResult(
            action_performed="validate",
            validation_result=validation_result,
            recommendations=recommendations,
            summary=f"Endpoint validation completed. Status: {response.status_code}, Response time: {response_time:.1f}ms"
        )
    
    def _create_timeout_error(self) -> WebhookConfiguratorResult:
        """Create error result for timeout."""
        return WebhookConfiguratorResult(
            action_performed="validate",
            validation_result=ValidationResult(
                is_valid=False,
                error_message="Request timeout occurred",
                security_issues=[],
                recommendations=[
                    "Ensure endpoint responds within timeout period",
                    "Consider increasing timeout or optimizing endpoint performance"
                ]
            ),
            recommendations=[
                "Ensure endpoint responds within timeout period",
                "Consider increasing timeout or optimizing endpoint performance"
            ],
            summary="Endpoint validation failed - request timed out"
        )
    
    def _create_connection_error(self) -> WebhookConfiguratorResult:
        """Create error result for connection failure."""
        return WebhookConfiguratorResult(
            action_performed="validate",
            validation_result=ValidationResult(
                is_valid=False,
                error_message="Connection failed",
                security_issues=[],
                recommendations=[
                    "Verify endpoint URL is correct and accessible",
                    "Check firewall and network configuration",
                    "Ensure endpoint server is running"
                ]
            ),
            recommendations=[
                "Verify endpoint URL is correct and accessible",
                "Check firewall and network configuration"
            ],
            summary="Endpoint validation failed - connection error"
        )
    
    def _create_ssl_error(self, error_message: str) -> WebhookConfiguratorResult:
        """Create error result for SSL issues."""
        return WebhookConfiguratorResult(
            action_performed="validate",
            validation_result=ValidationResult(
                is_valid=False,
                ssl_valid=False,
                error_message=f"SSL error: {error_message}",
                security_issues=["SSL certificate validation failed"],
                recommendations=[
                    "Verify SSL certificate is valid and not expired",
                    "Ensure certificate chain is complete",
                    "Check certificate matches domain name"
                ]
            ),
            summary="Endpoint validation failed - SSL error"
        )
    
    def _create_generic_error(self, error_message: str) -> WebhookConfiguratorResult:
        """Create error result for generic errors."""
        return WebhookConfiguratorResult(
            action_performed="validate",
            validation_result=ValidationResult(
                is_valid=False,
                error_message=error_message,
                security_issues=[],
                recommendations=["Check endpoint configuration and try again"]
            ),
            summary="Endpoint validation failed - unexpected error"
        )
    
    def _check_ssl_configuration(self) -> WebhookConfiguratorResult:
        """Check SSL/TLS configuration for webhook endpoint."""
        if not self.input_data.endpoint_url:
            return WebhookConfiguratorResult(
                action_performed="check_ssl",
                error="Endpoint URL is required for SSL check",
                summary="SSL check failed - missing endpoint URL"
            )
        
        parsed_url = urlparse(str(self.input_data.endpoint_url))
        if parsed_url.scheme != 'https':
            return self._create_non_https_ssl_result(parsed_url.scheme)
        
        # Attempt SSL connection
        try:
            return self._test_ssl_connection()
        except ssl.SSLError as e:
            return self._create_ssl_connection_error(str(e))
        except Exception as e:
            return WebhookConfiguratorResult(
                action_performed="check_ssl",
                error=f"SSL check failed: {str(e)}",
                summary="SSL check failed - unexpected error"
            )
    
    def _create_non_https_ssl_result(self, scheme: str) -> WebhookConfiguratorResult:
        """Create result for non-HTTPS endpoint."""
        return WebhookConfiguratorResult(
            action_performed="check_ssl",
            ssl_details={"scheme": scheme},
            validation_result=ValidationResult(
                is_valid=False,
                ssl_valid=False,
                security_issues=["Endpoint not using HTTPS"],
                recommendations=["Use HTTPS for secure webhook delivery"]
            ),
            summary="SSL check failed - endpoint not using HTTPS"
        )
    
    def _test_ssl_connection(self) -> WebhookConfiguratorResult:
        """Test SSL connection to endpoint."""
        with httpx.Client() as client:
            response = client.post(str(self.input_data.endpoint_url), timeout=self.input_data.timeout_seconds)
        
        ssl_details = {
            "protocol": "HTTPS",
            "status": "Valid",
            "verified": True
        }
        
        return WebhookConfiguratorResult(
            action_performed="check_ssl",
            ssl_details=ssl_details,
            validation_result=ValidationResult(
                is_valid=True,
                ssl_valid=True,
                security_issues=[],
                recommendations=["SSL configuration appears valid"]
            ),
            summary="SSL check completed - certificate appears valid"
        )
    
    def _create_ssl_connection_error(self, error_message: str) -> WebhookConfiguratorResult:
        """Create error result for SSL connection failure."""
        ssl_details = {
            "protocol": "HTTPS",
            "status": "Invalid",
            "error": error_message,
            "verified": False
        }
        
        return WebhookConfiguratorResult(
            action_performed="check_ssl",
            ssl_details=ssl_details,
            validation_result=ValidationResult(
                is_valid=False,
                ssl_valid=False,
                security_issues=["SSL certificate validation failed"],
                recommendations=[
                    "Verify SSL certificate is valid and not expired",
                    "Ensure certificate chain is complete",
                    "Check certificate matches domain name"
                ]
            ),
            summary="SSL check failed - certificate validation error"
        )
    
    def _generate_security_configuration(self) -> WebhookConfiguratorResult:
        """Generate security configuration for webhook."""
        # Generate signing secret
        signing_secret = secrets.token_urlsafe(32)
        
        # Get security defaults for the level
        security_defaults = self.SECURITY_DEFAULTS[self.input_data.security_level]
        
        # Create base security configuration
        security_config = WebhookSecurity(
            signing_secret=signing_secret,
            signature_header="X-Healthie-Signature",
            timestamp_header="X-Healthie-Timestamp",
            timestamp_tolerance_seconds=security_defaults["timestamp_tolerance"],
            required_headers=security_defaults["required_headers"],
            ip_whitelist=security_defaults["ip_whitelist"],
            user_agent_pattern=security_defaults["user_agent_pattern"]
        )
        
        # Generate recommendations and warnings
        recommendations, warnings = self._get_security_recommendations()
        
        return WebhookConfiguratorResult(
            action_performed="generate_security",
            security_config=security_config,
            recommendations=recommendations,
            warnings=warnings,
            summary=f"Security configuration generated for {self.input_data.security_level.value} level"
        )
    
    def _get_security_recommendations(self) -> tuple[List[str], List[str]]:
        """Get security recommendations and warnings based on level."""
        base_recommendations = [
            "Store the signing secret securely and never expose it in client-side code",
            "Verify webhook signatures to ensure authenticity",
            "Check timestamp to prevent replay attacks"
        ]
        
        warnings = []
        level_recommendations = []
        
        if self.input_data.security_level == SecurityLevel.BASIC:
            level_recommendations.append("Basic security level - consider upgrading for production use")
        elif self.input_data.security_level == SecurityLevel.ENHANCED:
            level_recommendations.extend([
                "Enhanced security level - validate required headers",
                "Monitor user agent patterns for anomalies"
            ])
        elif self.input_data.security_level == SecurityLevel.HIPAA_COMPLIANT:
            level_recommendations.extend([
                "HIPAA-compliant security level configured",
                "Implement comprehensive audit logging for all webhook receipts",
                "Encrypt webhook data at rest if storing for processing",
                "Ensure webhook processing follows HIPAA security requirements",
                "Consider additional IP restrictions based on your infrastructure"
            ])
            warnings.append("HIPAA compliance requires additional security measures beyond webhook configuration")
        
        return base_recommendations + level_recommendations, warnings
    
    def _map_events_to_workflows(self) -> WebhookConfiguratorResult:
        """Map webhook events to healthcare workflows."""
        # If specific workflow requested, return that mapping
        if self.input_data.workflow_type:
            if self.input_data.workflow_type in self.WORKFLOW_MAPPINGS:
                event_mappings = {self.input_data.workflow_type: self.WORKFLOW_MAPPINGS[self.input_data.workflow_type]}
                recommendations = [
                    f"Events mapped for {self.input_data.workflow_type} workflow",
                    "Consider filtering events based on your specific use case",
                    "Implement proper error handling for each event type"
                ]
            else:
                # Return all mappings if workflow not found
                event_mappings = self.WORKFLOW_MAPPINGS
                recommendations = [
                    f"Workflow '{self.input_data.workflow_type}' not found, returning all available mappings",
                    "Choose events that match your integration requirements"
                ]
        else:
            # Return all mappings
            event_mappings = self.WORKFLOW_MAPPINGS
            recommendations = [
                "All workflow event mappings provided",
                "Select specific workflows relevant to your integration"
            ]
        
        return WebhookConfiguratorResult(
            action_performed="map_events",
            event_mappings=event_mappings,
            recommendations=recommendations,
            summary=f"Event mappings generated for healthcare workflows"
        )
    
    def _get_payload_examples(self) -> WebhookConfiguratorResult:
        """Generate payload examples for webhook events."""
        if not self.input_data.events:
            return WebhookConfiguratorResult(
                action_performed="get_examples",
                error="Events list is required for payload examples",
                summary="Payload examples failed - no events specified"
            )
        
        examples = []
        signing_secret = "example_secret_key_123"
        
        for event in self.input_data.events:
            example = self._create_payload_example(event, signing_secret)
            examples.append(example)
        
        recommendations = [
            "Verify webhook signatures using HMAC-SHA256",
            "Check timestamp to prevent replay attacks",
            "Handle each event type appropriately in your application",
            "Return 2xx status codes for successful webhook processing"
        ]
        
        return WebhookConfiguratorResult(
            action_performed="get_examples",
            payload_examples=examples,
            recommendations=recommendations,
            summary=f"Generated {len(examples)} payload examples for requested events"
        )
    
    def _create_payload_example(self, event: WebhookEvent, signing_secret: str) -> PayloadExample:
        """Create a payload example for a specific event."""
        timestamp = datetime.utcnow().isoformat()
        
        # Generate example payload based on event type
        payload_data = self._generate_event_payload(event, timestamp)
        
        # Generate signature
        payload_string = str(payload_data)
        signature = hmac.new(
            signing_secret.encode(),
            payload_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return PayloadExample(
            event=event,
            headers={
                "Content-Type": "application/json",
                "X-Healthie-Signature": f"sha256={signature}",
                "X-Healthie-Timestamp": timestamp,
                "X-Healthie-Event": event.value,
                "X-Healthie-Delivery": f"delivery_{secrets.token_hex(8)}"
            },
            payload=payload_data,
            signature=f"sha256={signature}",
            timestamp=timestamp
        )
    
    def _generate_event_payload(self, event: WebhookEvent, timestamp: str) -> Dict[str, Any]:
        """Generate payload data for specific event types."""
        if event == WebhookEvent.PATIENT_CREATED:
            return {
                "event": "patient_created",
                "patient_id": "pat_123456789",
                "timestamp": timestamp,
                "data": {
                    "id": "pat_123456789",
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                    "phone": "+1-555-0123",
                    "date_of_birth": "1990-01-15",
                    "created_at": timestamp
                }
            }
        elif event == WebhookEvent.APPOINTMENT_CREATED:
            return {
                "event": "appointment_created",
                "appointment_id": "apt_987654321",
                "timestamp": timestamp,
                "data": {
                    "id": "apt_987654321",
                    "patient_id": "pat_123456789",
                    "provider_id": "prov_456789123",
                    "start_time": "2024-07-01T10:00:00Z",
                    "end_time": "2024-07-01T11:00:00Z",
                    "status": "scheduled",
                    "appointment_type": "consultation",
                    "created_at": timestamp
                }
            }
        else:
            # Generic example for other events
            return {
                "event": event.value,
                "id": f"obj_{secrets.token_hex(8)}",
                "timestamp": timestamp,
                "data": {
                    "event_type": event.value,
                    "occurred_at": timestamp
                }
            }
    
    def _create_complete_configuration(self) -> WebhookConfiguratorResult:
        """Create a complete webhook configuration."""
        if not self.input_data.endpoint_url:
            return WebhookConfiguratorResult(
                action_performed="configure",
                error="Endpoint URL is required for configuration",
                summary="Configuration failed - missing endpoint URL"
            )
        
        # Generate security configuration
        security_result = self._generate_security_configuration()
        if security_result.error:
            return WebhookConfiguratorResult(
                action_performed="configure",
                error=f"Security configuration failed: {security_result.error}",
                summary="Configuration failed during security setup"
            )
        
        # Determine events to configure
        events_to_configure = self._determine_events_to_configure()
        
        # Create event filter
        event_filter = self._create_event_filter(events_to_configure)
        
        # Create complete configuration
        configuration = WebhookConfiguration(
            name=f"Webhook for {self.input_data.workflow_type or 'General'} Events",
            endpoint_url=self.input_data.endpoint_url,
            security=security_result.security_config,
            event_filter=event_filter,
            retry_config={
                "max_retries": 3,
                "retry_delay_seconds": 5,
                "exponential_backoff": True
            },
            active=True,
            description=f"Webhook configuration for {self.input_data.security_level.value} security level"
        )
        
        recommendations = self._get_configuration_recommendations(event_filter)
        
        return WebhookConfiguratorResult(
            action_performed="configure",
            configuration=configuration,
            security_config=security_result.security_config,
            recommendations=recommendations,
            warnings=security_result.warnings,
            summary=f"Complete webhook configuration created for {len(events_to_configure)} events"
        )
    
    def _determine_events_to_configure(self) -> List[WebhookEvent]:
        """Determine which events to configure based on input."""
        events_to_configure = self.input_data.events or []
        
        if self.input_data.workflow_type and not events_to_configure:
            # Map workflow to events
            if self.input_data.workflow_type in self.WORKFLOW_MAPPINGS:
                events_to_configure = self.WORKFLOW_MAPPINGS[self.input_data.workflow_type]
        
        return events_to_configure
    
    def _create_event_filter(self, events_to_configure: List[WebhookEvent]) -> EventFilter:
        """Create event filter with configuration and existing settings."""
        event_filter = EventFilter(events=events_to_configure)
        
        # Merge with existing configuration if provided
        if self.input_data.existing_config:
            existing_filter = self.input_data.existing_config.get("event_filter", {})
            if "patient_tags" in existing_filter:
                event_filter.patient_tags = existing_filter["patient_tags"]
            if "provider_ids" in existing_filter:
                event_filter.provider_ids = existing_filter["provider_ids"]
            if "location_ids" in existing_filter:
                event_filter.location_ids = existing_filter["location_ids"]
        
        return event_filter
    
    def _get_configuration_recommendations(self, event_filter: EventFilter) -> List[str]:
        """Get recommendations for complete configuration."""
        recommendations = [
            "Test webhook configuration with sample events before production use",
            "Monitor webhook delivery success rates and response times",
            "Implement proper error handling and logging in your webhook endpoint",
            "Consider webhook retry logic for failed deliveries"
        ]
        
        # Add filtering recommendations if filters are configured
        if event_filter.patient_tags or event_filter.provider_ids or event_filter.location_ids:
            recommendations.append("Event filtering is configured - verify filter criteria match your requirements")
        
        return recommendations


def setup_webhook_configurator_tool(mcp: FastMCP, schema_manager) -> None:
    """Setup the webhook configurator tool with the MCP server."""
    
    @mcp.tool()
    def webhook_configurator(
        action: str,
        endpoint_url: Optional[str] = None,
        events: Optional[List[str]] = None,
        security_level: str = "standard",
        existing_config: Optional[Dict[str, Any]] = None,
        workflow_type: Optional[str] = None,
        custom_headers: Optional[Dict[str, str]] = None,
        timeout_seconds: int = 10
    ) -> WebhookConfiguratorResult:
        """Configure, validate, and manage webhook integrations for Healthie API.
        
        This tool helps external customers set up secure webhook endpoints for receiving
        real-time notifications from the Healthie platform. It provides comprehensive
        validation, security configuration, event mapping, and payload examples.
        
        Args:
            action: Action to perform (validate, configure, generate_security, map_events, get_examples, check_ssl)
            endpoint_url: Webhook endpoint URL to validate or configure
            events: List of webhook events to configure or get examples for
            security_level: Security level for configuration (basic, standard, enhanced, hipaa_compliant)
            existing_config: Existing webhook configuration to modify
            workflow_type: Healthcare workflow type (patient_management, appointments, billing, etc.)
            custom_headers: Custom headers to include in validation
            timeout_seconds: Timeout for endpoint validation requests
                     
        Returns:
            WebhookConfiguratorResult with validation results, configurations, and recommendations
        """
        try:
            # Parse webhook events if provided
            webhook_events = []
            if events:
                for event in events:
                    try:
                        webhook_events.append(WebhookEvent(event))
                    except ValueError:
                        pass  # Skip invalid events
            
            # Parse security level
            try:
                sec_level = SecurityLevel(security_level)
            except ValueError:
                sec_level = SecurityLevel.STANDARD
            
            # Create input model for validation
            input_data = WebhookConfiguratorInput(
                action=action,
                endpoint_url=endpoint_url,
                events=webhook_events if webhook_events else None,
                security_level=sec_level,
                existing_config=existing_config,
                workflow_type=workflow_type,
                custom_headers=custom_headers,
                timeout_seconds=timeout_seconds
            )
            
            # Create configurator and process action
            configurator = WebhookConfigurator(input_data)
            return configurator.process_action()
            
        except Exception as e:
            # Return error in structured format
            return WebhookConfiguratorResult(
                action_performed=action,
                error=f"Webhook configurator failed: {str(e)}",
                summary="Operation failed due to error"
            )