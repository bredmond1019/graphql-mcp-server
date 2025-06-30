"""Webhook configurator tool for the Healthie MCP server."""

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
            
            # Route to appropriate handler based on action
            if input_data.action == "validate":
                return _validate_webhook_endpoint(input_data)
            elif input_data.action == "check_ssl":
                return _check_ssl_configuration(input_data)
            elif input_data.action == "generate_security":
                return _generate_security_configuration(input_data)
            elif input_data.action == "map_events":
                return _map_events_to_workflows(input_data)
            elif input_data.action == "get_examples":
                return _get_payload_examples(input_data)
            elif input_data.action == "configure":
                return _create_complete_configuration(input_data)
            else:
                return WebhookConfiguratorResult(
                    action_performed=input_data.action,
                    error=f"Unknown action: {input_data.action}",
                    summary="Action not recognized"
                )
            
        except Exception as e:
            # Return error in structured format
            return WebhookConfiguratorResult(
                action_performed=action,
                error=f"Webhook configurator failed: {str(e)}",
                summary="Operation failed due to error"
            )


def _validate_webhook_endpoint(input_data: WebhookConfiguratorInput) -> WebhookConfiguratorResult:
    """Validate webhook endpoint connectivity and configuration."""
    if not input_data.endpoint_url:
        return WebhookConfiguratorResult(
            action_performed="validate",
            error="Endpoint URL is required for validation",
            summary="Validation failed - missing endpoint URL"
        )
    
    # Parse URL for basic validation
    parsed_url = urlparse(str(input_data.endpoint_url))
    if parsed_url.scheme not in ['http', 'https']:
        return WebhookConfiguratorResult(
            action_performed="validate",
            validation_result=ValidationResult(
                is_valid=False,
                error_message="Invalid URL scheme. Use http or https.",
                security_issues=["Non-secure protocol"] if parsed_url.scheme == 'http' else [],
                recommendations=["Use HTTPS for secure webhook delivery"]
            ),
            summary="Endpoint validation failed - invalid URL scheme"
        )
    
    # Test endpoint connectivity
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Healthie-Webhook-Validator/1.0"
    }
    
    # Add custom headers if provided
    if input_data.custom_headers:
        headers.update(input_data.custom_headers)
    
    # Test payload for validation
    test_payload = {
        "event": "test_validation",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {"validation": True}
    }
    
    try:
        start_time = time.time()
        with httpx.Client() as client:
            response = client.post(
                str(input_data.endpoint_url),
                json=test_payload,
                headers=headers,
                timeout=input_data.timeout_seconds
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
        
    except httpx.TimeoutException:
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
    
    except httpx.ConnectError as e:
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
    
    except ssl.SSLError as e:
        return WebhookConfiguratorResult(
            action_performed="validate",
            validation_result=ValidationResult(
                is_valid=False,
                ssl_valid=False,
                error_message=f"SSL error: {str(e)}",
                security_issues=["SSL certificate validation failed"],
                recommendations=[
                    "Verify SSL certificate is valid and not expired",
                    "Ensure certificate chain is complete",
                    "Check certificate matches domain name"
                ]
            ),
            summary="Endpoint validation failed - SSL error"
        )
    
    except Exception as e:
        return WebhookConfiguratorResult(
            action_performed="validate",
            validation_result=ValidationResult(
                is_valid=False,
                error_message=str(e),
                security_issues=[],
                recommendations=["Check endpoint configuration and try again"]
            ),
            summary="Endpoint validation failed - unexpected error"
        )


def _check_ssl_configuration(input_data: WebhookConfiguratorInput) -> WebhookConfiguratorResult:
    """Check SSL/TLS configuration for webhook endpoint."""
    if not input_data.endpoint_url:
        return WebhookConfiguratorResult(
            action_performed="check_ssl",
            error="Endpoint URL is required for SSL check",
            summary="SSL check failed - missing endpoint URL"
        )
    
    parsed_url = urlparse(str(input_data.endpoint_url))
    if parsed_url.scheme != 'https':
        return WebhookConfiguratorResult(
            action_performed="check_ssl",
            ssl_details={"scheme": parsed_url.scheme},
            validation_result=ValidationResult(
                is_valid=False,
                ssl_valid=False,
                security_issues=["Endpoint not using HTTPS"],
                recommendations=["Use HTTPS for secure webhook delivery"]
            ),
            summary="SSL check failed - endpoint not using HTTPS"
        )
    
    # Attempt SSL connection
    try:
        with httpx.Client() as client:
            response = client.post(str(input_data.endpoint_url), timeout=input_data.timeout_seconds)
        
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
        
    except ssl.SSLError as e:
        ssl_details = {
            "protocol": "HTTPS",
            "status": "Invalid",
            "error": str(e),
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
    
    except Exception as e:
        return WebhookConfiguratorResult(
            action_performed="check_ssl",
            error=f"SSL check failed: {str(e)}",
            summary="SSL check failed - unexpected error"
        )


def _generate_security_configuration(input_data: WebhookConfiguratorInput) -> WebhookConfiguratorResult:
    """Generate security configuration for webhook."""
    # Generate signing secret
    signing_secret = secrets.token_urlsafe(32)
    
    # Base security configuration
    security_config = WebhookSecurity(
        signing_secret=signing_secret,
        signature_header="X-Healthie-Signature",
        timestamp_header="X-Healthie-Timestamp",
        timestamp_tolerance_seconds=300,
        required_headers=[],
        ip_whitelist=None,
        user_agent_pattern=None
    )
    
    recommendations = [
        "Store the signing secret securely and never expose it in client-side code",
        "Verify webhook signatures to ensure authenticity",
        "Check timestamp to prevent replay attacks"
    ]
    
    warnings = []
    
    # Adjust configuration based on security level
    if input_data.security_level == SecurityLevel.BASIC:
        security_config.timestamp_tolerance_seconds = 600  # 10 minutes
        recommendations.append("Basic security level - consider upgrading for production use")
        
    elif input_data.security_level == SecurityLevel.ENHANCED:
        security_config.timestamp_tolerance_seconds = 180  # 3 minutes
        security_config.required_headers = ["X-Healthie-Event", "X-Healthie-Delivery"]
        security_config.user_agent_pattern = "Healthie-Webhook/\\d+\\.\\d+"
        recommendations.extend([
            "Enhanced security level - validate required headers",
            "Monitor user agent patterns for anomalies"
        ])
        
    elif input_data.security_level == SecurityLevel.HIPAA_COMPLIANT:
        security_config.timestamp_tolerance_seconds = 120  # 2 minutes
        security_config.required_headers = ["X-Healthie-Event", "X-Healthie-Delivery", "X-Healthie-Environment"]
        security_config.user_agent_pattern = "Healthie-Webhook/\\d+\\.\\d+"
        security_config.ip_whitelist = ["198.51.100.0/24"]  # Example IP range
        recommendations.extend([
            "HIPAA-compliant security level configured",
            "Implement comprehensive audit logging for all webhook receipts",
            "Encrypt webhook data at rest if storing for processing",
            "Ensure webhook processing follows HIPAA security requirements",
            "Consider additional IP restrictions based on your infrastructure"
        ])
        warnings.append("HIPAA compliance requires additional security measures beyond webhook configuration")
    
    return WebhookConfiguratorResult(
        action_performed="generate_security",
        security_config=security_config,
        recommendations=recommendations,
        warnings=warnings,
        summary=f"Security configuration generated for {input_data.security_level.value} level"
    )


def _map_events_to_workflows(input_data: WebhookConfiguratorInput) -> WebhookConfiguratorResult:
    """Map webhook events to healthcare workflows."""
    # Define workflow to event mappings
    workflow_mappings = {
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
    
    # If specific workflow requested, return that mapping
    if input_data.workflow_type:
        if input_data.workflow_type in workflow_mappings:
            event_mappings = {input_data.workflow_type: workflow_mappings[input_data.workflow_type]}
            recommendations = [
                f"Events mapped for {input_data.workflow_type} workflow",
                "Consider filtering events based on your specific use case",
                "Implement proper error handling for each event type"
            ]
        else:
            # Return all mappings if workflow not found
            event_mappings = workflow_mappings
            recommendations = [
                f"Workflow '{input_data.workflow_type}' not found, returning all available mappings",
                "Choose events that match your integration requirements"
            ]
    else:
        # Return all mappings
        event_mappings = workflow_mappings
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


def _get_payload_examples(input_data: WebhookConfiguratorInput) -> WebhookConfiguratorResult:
    """Generate payload examples for webhook events."""
    if not input_data.events:
        return WebhookConfiguratorResult(
            action_performed="get_examples",
            error="Events list is required for payload examples",
            summary="Payload examples failed - no events specified"
        )
    
    examples = []
    signing_secret = "example_secret_key_123"
    
    for event in input_data.events:
        timestamp = datetime.utcnow().isoformat()
        
        # Generate example payload based on event type
        if event == WebhookEvent.PATIENT_CREATED:
            payload_data = {
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
            payload_data = {
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
            payload_data = {
                "event": event.value,
                "id": f"obj_{secrets.token_hex(8)}",
                "timestamp": timestamp,
                "data": {
                    "event_type": event.value,
                    "occurred_at": timestamp
                }
            }
        
        # Generate signature
        payload_string = str(payload_data)
        signature = hmac.new(
            signing_secret.encode(),
            payload_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        example = PayloadExample(
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


def _create_complete_configuration(input_data: WebhookConfiguratorInput) -> WebhookConfiguratorResult:
    """Create a complete webhook configuration."""
    if not input_data.endpoint_url:
        return WebhookConfiguratorResult(
            action_performed="configure",
            error="Endpoint URL is required for configuration",
            summary="Configuration failed - missing endpoint URL"
        )
    
    # Generate security configuration
    security_result = _generate_security_configuration(input_data)
    if security_result.error:
        return WebhookConfiguratorResult(
            action_performed="configure",
            error=f"Security configuration failed: {security_result.error}",
            summary="Configuration failed during security setup"
        )
    
    # Determine events to configure
    events_to_configure = input_data.events or []
    if input_data.workflow_type and not events_to_configure:
        # Map workflow to events
        mapping_result = _map_events_to_workflows(input_data)
        if mapping_result.event_mappings and input_data.workflow_type in mapping_result.event_mappings:
            events_to_configure = mapping_result.event_mappings[input_data.workflow_type]
    
    # Create event filter
    event_filter = EventFilter(events=events_to_configure)
    
    # Merge with existing configuration if provided
    if input_data.existing_config:
        existing_filter = input_data.existing_config.get("event_filter", {})
        if "patient_tags" in existing_filter:
            event_filter.patient_tags = existing_filter["patient_tags"]
        if "provider_ids" in existing_filter:
            event_filter.provider_ids = existing_filter["provider_ids"]
        if "location_ids" in existing_filter:
            event_filter.location_ids = existing_filter["location_ids"]
    
    # Create complete configuration
    configuration = WebhookConfiguration(
        name=f"Webhook for {input_data.workflow_type or 'General'} Events",
        endpoint_url=input_data.endpoint_url,
        security=security_result.security_config,
        event_filter=event_filter,
        retry_config={
            "max_retries": 3,
            "retry_delay_seconds": 5,
            "exponential_backoff": True
        },
        active=True,
        description=f"Webhook configuration for {input_data.security_level.value} security level"
    )
    
    recommendations = [
        "Test webhook configuration with sample events before production use",
        "Monitor webhook delivery success rates and response times",
        "Implement proper error handling and logging in your webhook endpoint",
        "Consider webhook retry logic for failed deliveries"
    ]
    
    # Add filtering recommendations if filters are configured
    if event_filter.patient_tags or event_filter.provider_ids or event_filter.location_ids:
        recommendations.append("Event filtering is configured - verify filter criteria match your requirements")
    
    return WebhookConfiguratorResult(
        action_performed="configure",
        configuration=configuration,
        security_config=security_result.security_config,
        recommendations=recommendations,
        warnings=security_result.warnings,
        summary=f"Complete webhook configuration created for {len(events_to_configure)} events"
    )