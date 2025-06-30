"""Data models for webhook configurator tool."""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, validator


class WebhookEvent(str, Enum):
    """Supported webhook events in Healthie."""
    PATIENT_CREATED = "patient_created"
    PATIENT_UPDATED = "patient_updated"
    APPOINTMENT_CREATED = "appointment_created"
    APPOINTMENT_UPDATED = "appointment_updated"
    APPOINTMENT_CANCELLED = "appointment_cancelled"
    FORM_SUBMITTED = "form_submitted"
    PAYMENT_COMPLETED = "payment_completed"
    PAYMENT_FAILED = "payment_failed"
    DOCUMENT_UPLOADED = "document_uploaded"
    TASK_COMPLETED = "task_completed"
    CHAT_MESSAGE_CREATED = "chat_message_created"
    CARE_PLAN_UPDATED = "care_plan_updated"


class SecurityLevel(str, Enum):
    """Security configuration levels for webhooks."""
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    HIPAA_COMPLIANT = "hipaa_compliant"


class ValidationResult(BaseModel):
    """Result of webhook endpoint validation."""
    
    is_valid: bool = Field(description="Whether the endpoint is valid")
    status_code: Optional[int] = Field(default=None, description="HTTP status code received")
    response_time_ms: Optional[float] = Field(default=None, description="Response time in milliseconds")
    ssl_valid: bool = Field(default=False, description="Whether SSL certificate is valid")
    headers_valid: bool = Field(default=False, description="Whether required headers are present")
    error_message: Optional[str] = Field(default=None, description="Error message if validation failed")
    security_issues: List[str] = Field(default_factory=list, description="Security issues found")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")


class WebhookSecurity(BaseModel):
    """Security configuration for webhooks."""
    
    signing_secret: str = Field(description="Secret key for webhook signature verification")
    signature_header: str = Field(default="X-Healthie-Signature", description="Header name for signature")
    timestamp_header: str = Field(default="X-Healthie-Timestamp", description="Header name for timestamp")
    timestamp_tolerance_seconds: int = Field(default=300, description="Allowed timestamp tolerance")
    required_headers: List[str] = Field(default_factory=list, description="Required headers for verification")
    ip_whitelist: Optional[List[str]] = Field(default=None, description="Allowed IP addresses")
    user_agent_pattern: Optional[str] = Field(default=None, description="Expected user agent pattern")


class EventFilter(BaseModel):
    """Configuration for filtering webhook events."""
    
    events: List[WebhookEvent] = Field(description="Events to include")
    conditions: Optional[Dict[str, Any]] = Field(default=None, description="Additional filtering conditions")
    patient_tags: Optional[List[str]] = Field(default=None, description="Filter by patient tags")
    provider_ids: Optional[List[str]] = Field(default=None, description="Filter by provider IDs")
    location_ids: Optional[List[str]] = Field(default=None, description="Filter by location IDs")


class WebhookConfiguration(BaseModel):
    """Complete webhook configuration."""
    
    name: str = Field(description="Descriptive name for the webhook")
    endpoint_url: HttpUrl = Field(description="Webhook endpoint URL")
    security: WebhookSecurity = Field(description="Security configuration")
    event_filter: EventFilter = Field(description="Event filtering configuration")
    retry_config: Dict[str, Any] = Field(default_factory=dict, description="Retry configuration")
    active: bool = Field(default=True, description="Whether webhook is active")
    description: Optional[str] = Field(default=None, description="Webhook description")


class PayloadExample(BaseModel):
    """Example webhook payload for an event."""
    
    event: WebhookEvent = Field(description="Event type")
    headers: Dict[str, str] = Field(description="Example headers")
    payload: Dict[str, Any] = Field(description="Example payload data")
    signature: str = Field(description="Example signature")
    timestamp: str = Field(description="Example timestamp")


class WebhookConfiguratorInput(BaseModel):
    """Input parameters for webhook configurator."""
    
    action: str = Field(
        description="Action to perform: validate, configure, generate_security, map_events, get_examples, or check_ssl"
    )
    
    endpoint_url: Optional[HttpUrl] = Field(
        default=None,
        description="Webhook endpoint URL to validate or configure"
    )
    
    events: Optional[List[WebhookEvent]] = Field(
        default=None,
        description="Events to configure or get examples for"
    )
    
    security_level: SecurityLevel = Field(
        default=SecurityLevel.STANDARD,
        description="Security level for configuration"
    )
    
    existing_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Existing webhook configuration to modify"
    )
    
    workflow_type: Optional[str] = Field(
        default=None,
        description="Healthcare workflow type (patient_management, appointments, billing, etc.)"
    )
    
    custom_headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="Custom headers to include in validation"
    )
    
    timeout_seconds: int = Field(
        default=10,
        description="Timeout for endpoint validation requests"
    )

    @validator('action')
    def validate_action(cls, v):
        valid_actions = {
            'validate', 'configure', 'generate_security', 
            'map_events', 'get_examples', 'check_ssl'
        }
        if v not in valid_actions:
            raise ValueError(f"Action must be one of: {', '.join(valid_actions)}")
        return v


class WebhookConfiguratorResult(BaseModel):
    """Result of webhook configurator tool execution."""
    
    action_performed: str = Field(description="Action that was performed")
    
    # Validation results
    validation_result: Optional[ValidationResult] = Field(
        default=None, 
        description="Endpoint validation results"
    )
    
    # Configuration results
    configuration: Optional[WebhookConfiguration] = Field(
        default=None,
        description="Generated webhook configuration"
    )
    
    # Security configuration
    security_config: Optional[WebhookSecurity] = Field(
        default=None,
        description="Generated security configuration"
    )
    
    # Event mapping results
    event_mappings: Optional[Dict[str, List[WebhookEvent]]] = Field(
        default=None,
        description="Event mappings for workflows"
    )
    
    # Payload examples
    payload_examples: Optional[List[PayloadExample]] = Field(
        default=None,
        description="Example payloads for events"
    )
    
    # SSL/TLS check results
    ssl_details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="SSL/TLS certificate details"
    )
    
    # General results
    recommendations: List[str] = Field(
        default_factory=list,
        description="Recommendations for webhook setup"
    )
    
    warnings: List[str] = Field(
        default_factory=list,
        description="Warnings about configuration"
    )
    
    error: Optional[str] = Field(
        default=None,
        description="Error message if operation failed"
    )
    
    summary: str = Field(
        description="Summary of the operation performed"
    )