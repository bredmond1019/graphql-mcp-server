"""Data models for integration testing tool."""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class TestSeverity(str, Enum):
    """Test result severity levels."""
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class TestCategory(str, Enum):
    """Categories of integration tests."""
    AUTHENTICATION = "authentication"
    QUERIES = "queries"
    MUTATIONS = "mutations"
    ERROR_HANDLING = "error_handling"
    PERFORMANCE = "performance"
    SECURITY = "security"


class TestResult(BaseModel):
    """Individual test result."""
    
    test_name: str = Field(description="Name of the test")
    category: TestCategory = Field(description="Test category")
    severity: TestSeverity = Field(description="Test result severity")
    passed: bool = Field(description="Whether the test passed")
    message: str = Field(description="Test result message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional test details")
    execution_time_ms: Optional[float] = Field(default=None, description="Test execution time in milliseconds")


class IntegrationTestInput(BaseModel):
    """Input parameters for integration testing."""
    
    environment: str = Field(
        default="staging",
        description="Environment to test against (staging, production, custom)"
    )
    
    auth_method: str = Field(
        default="api_key",
        description="Authentication method to test (api_key, oauth, custom)"
    )
    
    test_mutations: bool = Field(
        default=True,
        description="Whether to test mutations (may modify data)"
    )
    
    test_categories: Optional[List[TestCategory]] = Field(
        default=None,
        description="Specific test categories to run (if not provided, runs all)"
    )
    
    max_execution_time_seconds: int = Field(
        default=300,
        description="Maximum time to allow for all tests"
    )
    
    custom_endpoint: Optional[str] = Field(
        default=None,
        description="Custom API endpoint URL for testing"
    )


class IntegrationTestReport(BaseModel):
    """Comprehensive integration test report."""
    
    environment: str = Field(description="Environment tested")
    total_tests: int = Field(description="Total number of tests run")
    passed_tests: int = Field(description="Number of tests that passed")
    failed_tests: int = Field(description="Number of tests that failed")
    test_results: List[TestResult] = Field(description="Individual test results")
    overall_success: bool = Field(description="Whether all critical tests passed")
    execution_time_seconds: float = Field(description="Total execution time")
    recommendations: List[str] = Field(description="Recommendations based on test results")
    summary: str = Field(description="Executive summary of test results")


class IntegrationTestingResult(BaseModel):
    """Result of integration testing tool execution."""
    
    report: IntegrationTestReport = Field(description="Detailed test report")
    error: Optional[str] = Field(default=None, description="Error message if testing failed")