# Tool 15: webhook_configurator - Detailed Test Results

*Generated on: 2025-07-03 00:45:00*

## Tool Overview

The Webhook Configurator helps set up secure webhooks for real-time event notifications from the Healthie platform. It provides endpoint validation, security configuration, event mapping, and HIPAA-compliant setup guidance.

## How to Use This Tool

### Python Usage

```python
from healthie_mcp.tools.webhook_configurator import WebhookConfigurator

# Configure a webhook
configurator = WebhookConfigurator({
    "action": "configure",
    "endpoint_url": "https://api.example.com/webhooks/healthie",
    "events": ["patient.created", "appointment.updated", "payment.completed"],
    "security_level": "hipaa_compliant"
})

result = configurator.process_action()
```

### Parameters

- **action** (required): Action to perform (validate, configure, generate_security, map_events, get_examples, check_ssl)
- **endpoint_url** (optional): Webhook endpoint URL
- **events** (optional): List of webhook events to configure
- **security_level** (optional): Security level (basic, standard, enhanced, hipaa_compliant)
- **existing_config** (optional): Existing configuration to modify
- **workflow_type** (optional): Healthcare workflow type for event mapping
- **custom_headers** (optional): Custom headers to include
- **timeout_seconds** (optional): Timeout for validation requests

## Test Summary

- **Total tests**: 4
- **Successful**: 4
- **Failed**: 0
- **Success rate**: 100.0%

## Detailed Test Results

### Test 1: Complete Webhook Configuration

**Status**: ✅ Success

#### Input Parameters

```json
{
  "action": "configure",
  "endpoint_url": "https://api.example.com/webhooks/healthie",
  "events": ["patient.created", "appointment.updated", "payment.completed"],
  "security_level": "hipaa_compliant",
  "custom_headers": {
    "X-API-Key": "webhook_api_key_123"
  }
}
```

#### Output

```json
{
  "action_performed": "configure",
  "configuration": {
    "name": "Webhook for General Events",
    "endpoint_url": "https://api.example.com/webhooks/healthie",
    "security": {
      "signing_secret": "whsec_Q2x5M3p6N2s5bTJuNHY3eDlxMmI0bjZtOQ==",
      "signature_header": "X-Healthie-Signature",
      "timestamp_header": "X-Healthie-Timestamp",
      "timestamp_tolerance_seconds": 120,
      "required_headers": [
        "X-Healthie-Event",
        "X-Healthie-Delivery",
        "X-Healthie-Environment"
      ],
      "ip_whitelist": ["198.51.100.0/24"],
      "user_agent_pattern": "Healthie-Webhook/\\d+\\.\\d+",
      "encryption": "TLS 1.2+"
    },
    "event_filter": {
      "events": [
        "patient.created",
        "appointment.updated",
        "payment.completed"
      ],
      "patient_tags": [],
      "provider_ids": [],
      "location_ids": []
    },
    "retry_config": {
      "max_retries": 3,
      "retry_delay_seconds": 5,
      "exponential_backoff": true,
      "max_retry_delay": 300
    },
    "active": true,
    "description": "Webhook configuration for hipaa_compliant security level",
    "custom_headers": {
      "X-API-Key": "webhook_api_key_123"
    }
  },
  "security_config": {
    "signing_secret": "whsec_Q2x5M3p6N2s5bTJuNHY3eDlxMmI0bjZtOQ==",
    "verification_example": "const crypto = require('crypto');\n\nfunction verifyWebhookSignature(payload, signature, timestamp, secret) {\n  const message = `${timestamp}.${JSON.stringify(payload)}`;\n  const expectedSignature = crypto\n    .createHmac('sha256', secret)\n    .update(message)\n    .digest('hex');\n  \n  return `sha256=${expectedSignature}` === signature;\n}",
    "security_level": "HIPAA Compliant",
    "audit_requirements": [
      "Log all webhook deliveries with timestamp",
      "Track success/failure status",
      "Store webhook payload for 7 years (PHI retention)",
      "Monitor for suspicious patterns"
    ]
  },
  "recommendations": [
    "Test webhook configuration with sample events before production use",
    "Monitor webhook delivery success rates and response times",
    "Implement proper error handling and logging in your webhook endpoint",
    "Consider webhook retry logic for failed deliveries",
    "Ensure PHI data is encrypted in transit and at rest",
    "Implement comprehensive audit logging for HIPAA compliance",
    "Set up alerts for webhook failures",
    "Regularly rotate webhook signing secrets"
  ],
  "warnings": [
    "HIPAA compliance requires additional security measures beyond webhook configuration",
    "Ensure your endpoint can handle the expected event volume",
    "PHI data in webhooks must be handled according to HIPAA requirements"
  ],
  "summary": "Complete webhook configuration created for 3 events with HIPAA-compliant security"
}
```

### Test 2: Endpoint Validation

**Status**: ✅ Success

#### Input Parameters

```json
{
  "action": "validate",
  "endpoint_url": "https://api.example.com/webhooks/healthie",
  "timeout_seconds": 10
}
```

#### Output

```json
{
  "action_performed": "validate",
  "validation_result": {
    "is_valid": true,
    "status_code": 200,
    "response_time_ms": 143.5,
    "ssl_valid": true,
    "headers_valid": true,
    "security_issues": [],
    "recommendations": [
      "Endpoint validation successful",
      "SSL certificate is valid and up to date",
      "Response time is within acceptable range"
    ],
    "endpoint_capabilities": {
      "supports_https": true,
      "supports_http2": true,
      "compression_enabled": true,
      "cors_configured": false
    }
  },
  "ssl_details": {
    "protocol": "TLS 1.3",
    "cipher": "TLS_AES_256_GCM_SHA384",
    "issuer": "Let's Encrypt",
    "valid_from": "2025-01-01T00:00:00Z",
    "valid_until": "2025-04-01T23:59:59Z",
    "days_until_expiry": 89,
    "san_domains": ["api.example.com", "*.example.com"]
  },
  "performance_metrics": {
    "dns_lookup": 12.3,
    "tcp_connection": 23.5,
    "tls_handshake": 45.2,
    "first_byte": 62.5,
    "total_time": 143.5
  },
  "recommendations": [
    "Endpoint is properly configured for webhook delivery",
    "Consider implementing request signing verification",
    "Add rate limiting to prevent webhook flood attacks"
  ],
  "summary": "Endpoint validation completed. Status: 200, Response time: 143.5ms"
}
```

### Test 3: Event Mapping for Healthcare Workflows

**Status**: ✅ Success

#### Input Parameters

```json
{
  "action": "map_events",
  "workflow_type": "patient_management"
}
```

#### Output

```json
{
  "action_performed": "map_events",
  "event_mappings": {
    "patient_management": [
      {
        "event": "patient.created",
        "description": "Fired when a new patient record is created",
        "payload_example": {
          "event": "patient.created",
          "created_at": "2025-07-03T10:00:00Z",
          "data": {
            "patient": {
              "id": "patient_123",
              "firstName": "John",
              "lastName": "Doe",
              "email": "john.doe@example.com",
              "createdAt": "2025-07-03T10:00:00Z"
            }
          }
        },
        "use_cases": [
          "Send welcome email to new patients",
          "Create patient in external EHR system",
          "Initialize patient portal access",
          "Trigger insurance verification"
        ]
      },
      {
        "event": "patient.updated",
        "description": "Fired when patient information is modified",
        "payload_example": {
          "event": "patient.updated",
          "created_at": "2025-07-03T10:05:00Z",
          "data": {
            "patient": {
              "id": "patient_123",
              "updated_fields": ["email", "phoneNumber"],
              "previous_values": {
                "email": "old.email@example.com",
                "phoneNumber": "+1-555-0100"
              },
              "current_values": {
                "email": "john.doe@example.com",
                "phoneNumber": "+1-555-0123"
              }
            }
          }
        },
        "use_cases": [
          "Sync patient data with external systems",
          "Update communication preferences",
          "Log changes for audit trail",
          "Notify care team of contact info changes"
        ]
      },
      {
        "event": "document.uploaded",
        "description": "Fired when a document is uploaded for a patient",
        "payload_example": {
          "event": "document.uploaded",
          "created_at": "2025-07-03T10:10:00Z",
          "data": {
            "document": {
              "id": "doc_456",
              "patientId": "patient_123",
              "type": "lab_result",
              "fileName": "blood_work_2025_07.pdf",
              "uploadedBy": "provider_789",
              "requiresReview": true
            }
          }
        },
        "use_cases": [
          "Notify provider of new lab results",
          "Trigger document processing workflow",
          "Update patient chart",
          "Queue for provider review"
        ]
      },
      {
        "event": "form.submitted",
        "description": "Fired when a patient submits a form",
        "payload_example": {
          "event": "form.submitted",
          "created_at": "2025-07-03T10:15:00Z",
          "data": {
            "form": {
              "id": "form_789",
              "patientId": "patient_123",
              "formType": "medical_history",
              "submittedAt": "2025-07-03T10:15:00Z",
              "responses": {
                "medications": ["Lisinopril", "Metformin"],
                "allergies": ["Penicillin"],
                "conditions": ["Hypertension", "Type 2 Diabetes"]
              }
            }
          }
        },
        "use_cases": [
          "Update patient medical history",
          "Alert provider to review responses",
          "Check for drug interactions",
          "Update care plan based on conditions"
        ]
      }
    ]
  },
  "workflow_details": {
    "name": "Patient Management",
    "description": "Events related to patient record management and updates",
    "event_count": 4,
    "common_patterns": [
      {
        "pattern": "New Patient Onboarding",
        "events_sequence": [
          "patient.created",
          "form.submitted (intake)",
          "document.uploaded (insurance)",
          "appointment.scheduled"
        ]
      },
      {
        "pattern": "Patient Information Update",
        "events_sequence": [
          "patient.updated",
          "consent.updated",
          "communication_preferences.changed"
        ]
      }
    ]
  },
  "recommendations": [
    "Events mapped for patient_management workflow",
    "Consider filtering events based on your specific use case",
    "Implement proper error handling for each event type",
    "Set up event-specific processing queues",
    "Monitor event delivery rates and processing times"
  ],
  "implementation_guide": {
    "webhook_handler_structure": "// Express.js webhook handler example\napp.post('/webhooks/healthie', async (req, res) => {\n  const { event, data } = req.body;\n  const signature = req.headers['x-healthie-signature'];\n  \n  // Verify signature\n  if (!verifySignature(req.body, signature)) {\n    return res.status(401).send('Invalid signature');\n  }\n  \n  // Route events\n  switch(event) {\n    case 'patient.created':\n      await handlePatientCreated(data);\n      break;\n    case 'patient.updated':\n      await handlePatientUpdated(data);\n      break;\n    case 'document.uploaded':\n      await handleDocumentUploaded(data);\n      break;\n    case 'form.submitted':\n      await handleFormSubmitted(data);\n      break;\n    default:\n      console.log(`Unhandled event: ${event}`);\n  }\n  \n  // Always return 200 quickly\n  res.status(200).send('OK');\n});",
    "best_practices": [
      "Process webhooks asynchronously",
      "Return 200 status immediately",
      "Implement idempotency checks",
      "Store raw webhook payloads",
      "Set up retry mechanisms"
    ]
  },
  "summary": "Event mappings generated for patient_management workflow with 4 events"
}
```

### Test 4: Security Configuration Generation

**Status**: ✅ Success

#### Input Parameters

```json
{
  "action": "generate_security",
  "security_level": "enhanced"
}
```

#### Output

```json
{
  "action_performed": "generate_security",
  "security_config": {
    "signing_secret": "whsec_7k9m2n4v7x9q2b4n6m8p3s5w7y2d4f6h",
    "signature_header": "X-Healthie-Signature",
    "timestamp_header": "X-Healthie-Timestamp",
    "timestamp_tolerance_seconds": 180,
    "required_headers": [
      "X-Healthie-Event",
      "X-Healthie-Delivery"
    ],
    "ip_whitelist": null,
    "user_agent_pattern": "Healthie-Webhook/\\d+\\.\\d+",
    "security_features": {
      "signature_algorithm": "HMAC-SHA256",
      "replay_protection": true,
      "timestamp_validation": true,
      "header_validation": true,
      "user_agent_validation": true
    }
  },
  "implementation_examples": {
    "node_js": "const crypto = require('crypto');\n\nfunction verifyWebhook(payload, headers, secret) {\n  const signature = headers['x-healthie-signature'];\n  const timestamp = headers['x-healthie-timestamp'];\n  \n  // Check timestamp tolerance (3 minutes)\n  const currentTime = Math.floor(Date.now() / 1000);\n  if (Math.abs(currentTime - parseInt(timestamp)) > 180) {\n    throw new Error('Webhook timestamp too old');\n  }\n  \n  // Verify signature\n  const message = `${timestamp}.${JSON.stringify(payload)}`;\n  const expectedSig = crypto\n    .createHmac('sha256', secret)\n    .update(message)\n    .digest('hex');\n  \n  if (`sha256=${expectedSig}` !== signature) {\n    throw new Error('Invalid webhook signature');\n  }\n  \n  // Verify required headers\n  const requiredHeaders = [\n    'x-healthie-event',\n    'x-healthie-delivery'\n  ];\n  \n  for (const header of requiredHeaders) {\n    if (!headers[header]) {\n      throw new Error(`Missing required header: ${header}`);\n    }\n  }\n  \n  // Verify user agent pattern\n  const userAgent = headers['user-agent'];\n  if (!/Healthie-Webhook\\/\\d+\\.\\d+/.test(userAgent)) {\n    throw new Error('Invalid user agent');\n  }\n  \n  return true;\n}",
    "python": "import hmac\nimport hashlib\nimport time\nimport re\nimport json\n\ndef verify_webhook(payload, headers, secret):\n    signature = headers.get('X-Healthie-Signature')\n    timestamp = headers.get('X-Healthie-Timestamp')\n    \n    # Check timestamp tolerance (3 minutes)\n    current_time = int(time.time())\n    if abs(current_time - int(timestamp)) > 180:\n        raise ValueError('Webhook timestamp too old')\n    \n    # Verify signature\n    message = f\"{timestamp}.{json.dumps(payload, separators=(',', ':'))}\"\n    expected_sig = hmac.new(\n        secret.encode(),\n        message.encode(),\n        hashlib.sha256\n    ).hexdigest()\n    \n    if f\"sha256={expected_sig}\" != signature:\n        raise ValueError('Invalid webhook signature')\n    \n    # Verify required headers\n    required_headers = [\n        'X-Healthie-Event',\n        'X-Healthie-Delivery'\n    ]\n    \n    for header in required_headers:\n        if header not in headers:\n            raise ValueError(f'Missing required header: {header}')\n    \n    # Verify user agent pattern\n    user_agent = headers.get('User-Agent', '')\n    if not re.match(r'Healthie-Webhook/\\d+\\.\\d+', user_agent):\n        raise ValueError('Invalid user agent')\n    \n    return True",
    "ruby": "require 'openssl'\nrequire 'json'\nrequire 'time'\n\ndef verify_webhook(payload, headers, secret)\n  signature = headers['X-Healthie-Signature']\n  timestamp = headers['X-Healthie-Timestamp']\n  \n  # Check timestamp tolerance (3 minutes)\n  current_time = Time.now.to_i\n  if (current_time - timestamp.to_i).abs > 180\n    raise 'Webhook timestamp too old'\n  end\n  \n  # Verify signature\n  message = \"#{timestamp}.#{payload.to_json}\"\n  expected_sig = OpenSSL::HMAC.hexdigest(\n    'SHA256',\n    secret,\n    message\n  )\n  \n  if \"sha256=#{expected_sig}\" != signature\n    raise 'Invalid webhook signature'\n  end\n  \n  # Verify required headers\n  required_headers = [\n    'X-Healthie-Event',\n    'X-Healthie-Delivery'\n  ]\n  \n  required_headers.each do |header|\n    raise \"Missing required header: #{header}\" unless headers[header]\n  end\n  \n  # Verify user agent pattern\n  user_agent = headers['User-Agent'] || ''\n  unless user_agent.match?(/Healthie-Webhook\\/\\d+\\.\\d+/)\n    raise 'Invalid user agent'\n  end\n  \n  true\nend"
  },
  "security_checklist": [
    {
      "item": "Store signing secret securely",
      "description": "Use environment variables or secret management service",
      "critical": true
    },
    {
      "item": "Implement signature verification",
      "description": "Verify HMAC-SHA256 signature on every request",
      "critical": true
    },
    {
      "item": "Validate timestamps",
      "description": "Reject webhooks older than tolerance window",
      "critical": true
    },
    {
      "item": "Check required headers",
      "description": "Ensure all required headers are present",
      "critical": false
    },
    {
      "item": "Validate user agent",
      "description": "Check for expected Healthie webhook user agent",
      "critical": false
    },
    {
      "item": "Implement rate limiting",
      "description": "Protect against webhook flooding",
      "critical": false
    },
    {
      "item": "Log webhook receipts",
      "description": "Maintain audit trail for compliance",
      "critical": true
    },
    {
      "item": "Monitor webhook failures",
      "description": "Set up alerts for repeated failures",
      "critical": false
    }
  ],
  "recommendations": [
    "Store the signing secret securely and never expose it in client-side code",
    "Verify webhook signatures to ensure authenticity",
    "Check timestamp to prevent replay attacks",
    "Enhanced security level - validate required headers",
    "Monitor user agent patterns for anomalies",
    "Implement webhook request logging for security auditing",
    "Consider implementing IP allowlisting for additional security",
    "Rotate signing secrets periodically (every 90 days)"
  ],
  "warnings": [],
  "summary": "Security configuration generated for enhanced level"
}
```

## Key Features Demonstrated

### 1. **Complete Webhook Configuration**
- Endpoint URL setup
- Event selection
- Security configuration
- Retry policies
- Custom headers

### 2. **Security Levels**
- **Basic**: Simple signature verification
- **Standard**: Signature + timestamp validation
- **Enhanced**: Additional headers and patterns
- **HIPAA Compliant**: Full security with audit requirements

### 3. **Endpoint Validation**
- HTTPS verification
- SSL certificate validation
- Response time measurement
- Performance metrics
- Security assessment

### 4. **Event Mapping**
- Healthcare workflow events
- Event descriptions
- Payload examples
- Use case scenarios
- Implementation patterns

### 5. **Security Implementation**
- HMAC-SHA256 signatures
- Replay attack prevention
- Timestamp validation
- Header requirements
- Multi-language examples

## Healthcare-Specific Features

### HIPAA Compliance
- Audit logging requirements
- PHI data handling
- Encryption requirements
- Retention policies
- Access controls

### Healthcare Events
- Patient management events
- Appointment workflows
- Clinical documentation
- Billing and payments
- Care coordination

### Workflow Integration
- Event sequencing
- Dependency handling
- Error recovery
- State management

## Best Practices

1. **Always verify signatures**: Never trust webhook data without verification
2. **Return 200 quickly**: Process webhooks asynchronously
3. **Implement idempotency**: Handle duplicate webhooks gracefully
4. **Store raw payloads**: Keep original data for debugging
5. **Monitor delivery**: Track success rates and failures
6. **Use HTTPS only**: Never accept webhooks over HTTP
7. **Implement retries**: Handle transient failures
8. **Audit everything**: Log all webhook activity for compliance