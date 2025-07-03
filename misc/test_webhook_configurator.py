#!/usr/bin/env python3
"""Test script for webhook_configurator tool."""

import json
from src.healthie_mcp.tools.additional.webhook_configurator import WebhookConfigurator
from src.healthie_mcp.models.webhook_configurator import WebhookConfiguratorInput, SecurityLevel, WebhookEvent

def test_endpoint_validation():
    """Test endpoint validation with a real endpoint."""
    print("🔍 Testing endpoint validation...")
    
    # Use httpbin.org as a test endpoint (it accepts POST requests)
    input_data = WebhookConfiguratorInput(
        action="validate",
        endpoint_url="https://httpbin.org/post",
        timeout_seconds=10
    )
    
    configurator = WebhookConfigurator(input_data)
    result = configurator.process_action()
    
    print(f"✅ Action: {result.action_performed}")
    print(f"✅ Valid: {result.validation_result.is_valid if result.validation_result else 'N/A'}")
    print(f"✅ Status: {result.validation_result.status_code if result.validation_result else 'N/A'}")
    print(f"✅ Response Time: {result.validation_result.response_time_ms if result.validation_result else 'N/A'}ms")
    print(f"✅ Summary: {result.summary}")
    
    if result.validation_result and result.validation_result.recommendations:
        print("📋 Recommendations:")
        for rec in result.validation_result.recommendations:
            print(f"  - {rec}")
    
    return result.validation_result.is_valid if result.validation_result else False

def test_security_generation():
    """Test security configuration generation."""
    print("\n🔒 Testing security configuration generation...")
    
    input_data = WebhookConfiguratorInput(
        action="generate_security",
        security_level=SecurityLevel.HIPAA_COMPLIANT
    )
    
    configurator = WebhookConfigurator(input_data)
    result = configurator.process_action()
    
    print(f"✅ Action: {result.action_performed}")
    print(f"✅ Security Level: {result.security_config.security_level if hasattr(result.security_config, 'security_level') else 'N/A'}")
    print(f"✅ Secret Generated: {'Yes' if result.security_config and result.security_config.signing_secret else 'No'}")
    print(f"✅ Timestamp Tolerance: {result.security_config.timestamp_tolerance_seconds if result.security_config else 'N/A'}s")
    print(f"✅ Required Headers: {len(result.security_config.required_headers) if result.security_config and result.security_config.required_headers else 0}")
    
    if result.warnings:
        print("⚠️ Warnings:")
        for warning in result.warnings:
            print(f"  - {warning}")
    
    return result.security_config is not None

def test_event_mapping():
    """Test healthcare event mapping."""
    print("\n🏥 Testing healthcare event mapping...")
    
    input_data = WebhookConfiguratorInput(
        action="map_events",
        workflow_type="patient_management"
    )
    
    configurator = WebhookConfigurator(input_data)
    result = configurator.process_action()
    
    print(f"✅ Action: {result.action_performed}")
    print(f"✅ Event Mappings: {len(result.event_mappings) if result.event_mappings else 0} workflows")
    
    if result.event_mappings:
        for workflow, events in result.event_mappings.items():
            print(f"  📋 {workflow}: {len(events)} events")
            for event in events:
                print(f"    - {event.value if hasattr(event, 'value') else event}")
    
    return result.event_mappings is not None

def test_payload_examples():
    """Test payload example generation."""
    print("\n📦 Testing payload example generation...")
    
    input_data = WebhookConfiguratorInput(
        action="get_examples",
        events=[WebhookEvent.PATIENT_CREATED, WebhookEvent.APPOINTMENT_CREATED]
    )
    
    configurator = WebhookConfigurator(input_data)
    result = configurator.process_action()
    
    print(f"✅ Action: {result.action_performed}")
    print(f"✅ Examples Generated: {len(result.payload_examples) if result.payload_examples else 0}")
    
    if result.payload_examples:
        for example in result.payload_examples:
            print(f"  📨 Event: {example.event.value if hasattr(example.event, 'value') else example.event}")
            print(f"     Headers: {len(example.headers)} headers")
            print(f"     Signature: {'Yes' if example.signature else 'No'}")
    
    return result.payload_examples is not None and len(result.payload_examples) > 0

def test_complete_configuration():
    """Test complete webhook configuration."""
    print("\n⚙️ Testing complete webhook configuration...")
    
    input_data = WebhookConfiguratorInput(
        action="configure",
        endpoint_url="https://httpbin.org/post",
        events=[WebhookEvent.PATIENT_CREATED, WebhookEvent.APPOINTMENT_UPDATED],
        security_level=SecurityLevel.ENHANCED,
        workflow_type="patient_management"
    )
    
    configurator = WebhookConfigurator(input_data)
    result = configurator.process_action()
    
    print(f"✅ Action: {result.action_performed}")
    print(f"✅ Configuration Created: {'Yes' if result.configuration else 'No'}")
    
    if result.configuration:
        print(f"  📋 Name: {result.configuration.name}")
        print(f"  🔗 Endpoint: {result.configuration.endpoint_url}")
        print(f"  📨 Events: {len(result.configuration.event_filter.events) if result.configuration.event_filter else 0}")
        print(f"  🔒 Security: {'Configured' if result.configuration.security else 'None'}")
        print(f"  🔄 Retries: {result.configuration.retry_config.get('max_retries', 'N/A') if result.configuration.retry_config else 'N/A'}")
    
    return result.configuration is not None

def test_invalid_endpoint():
    """Test with an invalid endpoint to check error handling."""
    print("\n❌ Testing invalid endpoint (should fail gracefully)...")
    
    input_data = WebhookConfiguratorInput(
        action="validate",
        endpoint_url="https://invalid-domain-that-does-not-exist.com/webhook",
        timeout_seconds=5
    )
    
    configurator = WebhookConfigurator(input_data)
    result = configurator.process_action()
    
    print(f"✅ Action: {result.action_performed}")
    print(f"✅ Failed as expected: {'Yes' if result.error or (result.validation_result and not result.validation_result.is_valid) else 'No'}")
    print(f"✅ Error: {result.error or 'Validation failed'}")
    
    return result.error is not None or (result.validation_result and not result.validation_result.is_valid)

def main():
    """Run all webhook configurator tests."""
    print("🧪 Testing Webhook Configurator Tool")
    print("=" * 50)
    
    tests = [
        ("Endpoint Validation", test_endpoint_validation),
        ("Security Generation", test_security_generation),
        ("Event Mapping", test_event_mapping),
        ("Payload Examples", test_payload_examples),
        ("Complete Configuration", test_complete_configuration),
        ("Error Handling", test_invalid_endpoint)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success, None))
        except Exception as e:
            results.append((test_name, False, str(e)))
            print(f"❌ Test failed with error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test Results Summary")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success, _ in results if success)
    
    for test_name, success, error in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if error:
            print(f"     Error: {error}")
    
    print(f"\n📊 Overall: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Webhook configurator is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main()