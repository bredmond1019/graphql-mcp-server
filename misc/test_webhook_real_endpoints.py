#!/usr/bin/env python3
"""Test webhook configurator with real webhook testing services."""

from src.healthie_mcp.tools.additional.webhook_configurator import WebhookConfigurator
from src.healthie_mcp.models.webhook_configurator import WebhookConfiguratorInput, SecurityLevel, WebhookEvent

def test_with_webhook_site():
    """Test with webhook.site (free webhook testing service)."""
    print("🌐 Testing with webhook.site...")
    
    # You can get a unique URL from https://webhook.site
    test_url = "https://webhook.site/#!/unique-id-here/create"
    
    input_data = WebhookConfiguratorInput(
        action="validate",
        endpoint_url=test_url,
        timeout_seconds=10
    )
    
    configurator = WebhookConfigurator(input_data)
    result = configurator.process_action()
    
    print(f"📋 Validation Result: {result.validation_result.is_valid if result.validation_result else 'Error'}")
    print(f"📋 Response Time: {result.validation_result.response_time_ms if result.validation_result else 'N/A'}ms")
    
def test_with_requestbin():
    """Test with RequestBin (another webhook testing service)."""
    print("🌐 Testing with RequestBin...")
    
    # You can get a URL from https://requestbin.com
    test_url = "https://en123456.x.pipedream.net/"  # Example format
    
    input_data = WebhookConfiguratorInput(
        action="validate",
        endpoint_url=test_url,
        timeout_seconds=10
    )
    
    configurator = WebhookConfigurator(input_data)
    result = configurator.process_action()
    
    print(f"📋 Validation Result: {result.validation_result.is_valid if result.validation_result else 'Error'}")

def test_localhost_endpoint():
    """Test with a localhost endpoint (if you have a local server running)."""
    print("🏠 Testing with localhost...")
    
    # This will fail unless you have a server running on localhost:3000
    input_data = WebhookConfiguratorInput(
        action="validate",
        endpoint_url="http://localhost:3000/webhooks/healthie",
        timeout_seconds=5
    )
    
    configurator = WebhookConfigurator(input_data)
    result = configurator.process_action()
    
    print(f"📋 Localhost Test: {result.validation_result.is_valid if result.validation_result else 'Failed (expected if no local server)'}")

if __name__ == "__main__":
    print("🧪 Testing Webhook Configurator with Real Endpoints")
    print("=" * 60)
    print("💡 To test with real services:")
    print("1. Go to https://webhook.site and get a unique URL")
    print("2. Replace the test_url in this script")
    print("3. Run the test to see the webhook configurator in action")
    print("=" * 60)
    
    # Test with httpbin (always available)
    print("\n🔗 Testing with httpbin.org (always available)...")
    input_data = WebhookConfiguratorInput(
        action="validate",
        endpoint_url="https://httpbin.org/post",
        timeout_seconds=10
    )
    
    configurator = WebhookConfigurator(input_data)
    result = configurator.process_action()
    
    print(f"✅ HTTPBin Test: {result.validation_result.is_valid if result.validation_result else 'Failed'}")
    print(f"✅ Status Code: {result.validation_result.status_code if result.validation_result else 'N/A'}")
    print(f"✅ SSL Valid: {result.validation_result.ssl_valid if result.validation_result else 'N/A'}")
    
    # Show security recommendations
    if result.validation_result and result.validation_result.recommendations:
        print("\n📋 Security Recommendations:")
        for rec in result.validation_result.recommendations:
            print(f"  - {rec}")