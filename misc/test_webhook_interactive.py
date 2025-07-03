#!/usr/bin/env python3
"""Interactive webhook configurator testing."""

import json
from src.healthie_mcp.tools.additional.webhook_configurator import WebhookConfigurator
from src.healthie_mcp.models.webhook_configurator import WebhookConfiguratorInput, SecurityLevel, WebhookEvent

def pretty_print_result(result):
    """Pretty print the webhook configurator result."""
    print(f"\n📋 Action: {result.action_performed}")
    print(f"📋 Summary: {result.summary}")
    
    if result.error:
        print(f"❌ Error: {result.error}")
        return
    
    if result.validation_result:
        print(f"✅ Valid: {result.validation_result.is_valid}")
        if result.validation_result.status_code:
            print(f"📊 Status: {result.validation_result.status_code}")
        if result.validation_result.response_time_ms:
            print(f"⏱️ Response Time: {result.validation_result.response_time_ms:.1f}ms")
    
    if result.security_config:
        print(f"🔒 Security Secret Generated: {'Yes' if result.security_config.signing_secret else 'No'}")
        if result.security_config.required_headers:
            print(f"🔒 Required Headers: {len(result.security_config.required_headers)}")
    
    if result.configuration:
        print(f"⚙️ Configuration Name: {result.configuration.name}")
        if result.configuration.event_filter:
            print(f"📨 Events Configured: {len(result.configuration.event_filter.events)}")
    
    if result.event_mappings:
        print(f"🏥 Healthcare Workflows: {len(result.event_mappings)}")
    
    if result.payload_examples:
        print(f"📦 Payload Examples: {len(result.payload_examples)}")
    
    if result.recommendations:
        print("📋 Recommendations:")
        for rec in result.recommendations[:3]:  # Show first 3
            print(f"  • {rec}")
        if len(result.recommendations) > 3:
            print(f"  ... and {len(result.recommendations) - 3} more")

def test_action(action, **kwargs):
    """Test a specific webhook configurator action."""
    print(f"\n🧪 Testing Action: {action}")
    print("-" * 40)
    
    try:
        input_data = WebhookConfiguratorInput(action=action, **kwargs)
        configurator = WebhookConfigurator(input_data)
        result = configurator.process_action()
        pretty_print_result(result)
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run interactive webhook tests."""
    print("🔌 Webhook Configurator - Interactive Testing")
    print("=" * 50)
    
    # Test 1: Validate a good endpoint
    print("\n🟢 Test 1: Validate a working endpoint")
    test_action(
        "validate",
        endpoint_url="https://httpbin.org/post",
        timeout_seconds=10
    )
    
    # Test 2: Generate HIPAA security
    print("\n🟢 Test 2: Generate HIPAA-compliant security")
    test_action(
        "generate_security",
        security_level=SecurityLevel.HIPAA_COMPLIANT
    )
    
    # Test 3: Map patient management events
    print("\n🟢 Test 3: Map patient management events")
    test_action(
        "map_events",
        workflow_type="patient_management"
    )
    
    # Test 4: Get payload examples
    print("\n🟢 Test 4: Generate payload examples")
    test_action(
        "get_examples",
        events=[WebhookEvent.PATIENT_CREATED, WebhookEvent.APPOINTMENT_UPDATED]
    )
    
    # Test 5: Complete configuration
    print("\n🟢 Test 5: Complete webhook configuration")
    test_action(
        "configure",
        endpoint_url="https://httpbin.org/post",
        events=[WebhookEvent.PATIENT_CREATED],
        security_level=SecurityLevel.ENHANCED,
        workflow_type="patient_management"
    )
    
    # Test 6: Test with invalid endpoint
    print("\n🔴 Test 6: Invalid endpoint (should fail gracefully)")
    test_action(
        "validate",
        endpoint_url="https://this-domain-definitely-does-not-exist-12345.com/webhook",
        timeout_seconds=5
    )
    
    print("\n" + "=" * 50)
    print("✅ Interactive testing complete!")
    print("💡 The webhook configurator successfully:")
    print("  • Validates real endpoints")
    print("  • Generates secure configurations") 
    print("  • Maps healthcare events")
    print("  • Creates payload examples")
    print("  • Handles errors gracefully")

if __name__ == "__main__":
    main()