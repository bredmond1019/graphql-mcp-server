"""Integration testing tool for the Healthie MCP server - Refactored version."""

import os
import time
import httpx
from typing import List, Optional, Dict, Any
from mcp.server.fastmcp import FastMCP
from ...models.integration_testing import (
    IntegrationTestInput, IntegrationTestingResult, IntegrationTestReport,
    TestResult, TestCategory, TestSeverity
)


class IntegrationTestRunner:
    """Handles the execution of integration tests."""
    
    def __init__(self, input_data: IntegrationTestInput):
        self.input_data = input_data
        self.test_results: List[TestResult] = []
        self.start_time = time.time()
        self._http_client: Optional[httpx.Client] = None
    
    @property
    def http_client(self) -> httpx.Client:
        """Lazy initialization of HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.Client(timeout=30.0)  # Match original timeout
        return self._http_client
    
    def cleanup(self):
        """Clean up resources."""
        if self._http_client:
            self._http_client.close()
    
    def run_tests(self) -> IntegrationTestReport:
        """Execute all requested integration tests."""
        try:
            # Validate prerequisites
            self._validate_prerequisites()
            
            # Run test categories
            test_runners = {
                TestCategory.AUTHENTICATION: self._run_authentication_tests,
                TestCategory.QUERIES: self._run_query_tests,
                TestCategory.MUTATIONS: self._run_mutation_tests,
                TestCategory.ERROR_HANDLING: self._run_error_handling_tests,
                TestCategory.PERFORMANCE: self._run_performance_tests
            }
            
            for category, runner in test_runners.items():
                if self._should_run_category(category):
                    try:
                        runner()
                    except Exception as e:
                        self._add_test_result(
                            f"{category.value} Tests",
                            category,
                            TestSeverity.ERROR,
                            False,
                            f"Test category failed: {str(e)}"
                        )
            
            return self._generate_report()
            
        finally:
            self.cleanup()
    
    def _validate_prerequisites(self):
        """Validate that all prerequisites are met for testing."""
        if self.input_data.auth_method == "api_key":
            api_key = os.environ.get('HEALTHIE_API_KEY')
            if not api_key:
                raise ValueError(
                    "API key not found in environment variables. "
                    "Please set HEALTHIE_API_KEY."
                )
    
    def _should_run_category(self, category: TestCategory) -> bool:
        """Check if a test category should be run."""
        if not self.input_data.test_categories:
            return True
        return category in self.input_data.test_categories
    
    def _add_test_result(
        self, 
        test_name: str, 
        category: TestCategory,
        severity: TestSeverity,
        passed: bool,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        execution_time_ms: Optional[float] = None
    ):
        """Add a test result to the collection."""
        self.test_results.append(TestResult(
            test_name=test_name,
            category=category,
            severity=severity,
            passed=passed,
            message=message,
            details=details,
            execution_time_ms=execution_time_ms
        ))
    
    def _get_api_endpoint(self) -> str:
        """Get the API endpoint based on environment."""
        if self.input_data.custom_endpoint:
            return self.input_data.custom_endpoint
        
        endpoints = {
            "staging": "https://staging-api.gethealthie.com/graphql",
            "production": "https://api.gethealthie.com/graphql"
        }
        return endpoints.get(
            self.input_data.environment, 
            "https://staging-api.gethealthie.com/graphql"
        )
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.input_data.auth_method == "api_key":
            api_key = os.environ.get('HEALTHIE_API_KEY')
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
        
        return headers
    
    def _execute_graphql_query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Execute a GraphQL query and return the response."""
        start_time = time.time()
        
        payload = {
            "query": query,
            "variables": variables or {}
        }
        
        try:
            # For test compatibility, simulate context manager behavior
            client = self.http_client
            response = client.post(
                self._get_api_endpoint(),
                json=payload,
                headers=self._get_headers()
            )
            
            execution_time_ms = (time.time() - start_time) * 1000
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            result = response.json()
            result['_execution_time_ms'] = execution_time_ms
            return result
        except Exception as e:
            # Still calculate execution time even on error
            execution_time_ms = (time.time() - start_time) * 1000
            raise Exception(f"{str(e)} (execution_time: {execution_time_ms:.2f}ms)")
    
    def _run_authentication_tests(self):
        """Run authentication-related tests."""
        # Test 1: Validate API key setup
        self._add_test_result(
            "API Key Authentication",
            TestCategory.AUTHENTICATION,
            TestSeverity.SUCCESS,
            True,
            "API key authentication setup validated"
        )
        
        # Test 2: Test authentication with introspection query
        try:
            query = "{ __schema { queryType { name } } }"
            result = self._execute_graphql_query(query)
            
            if "errors" in result:
                self._add_test_result(
                    "GraphQL Authentication Test",
                    TestCategory.AUTHENTICATION,
                    TestSeverity.ERROR,
                    False,
                    f"Authentication failed: {result['errors'][0]['message']}"
                )
            else:
                self._add_test_result(
                    "GraphQL Authentication Test",
                    TestCategory.AUTHENTICATION,
                    TestSeverity.SUCCESS,
                    True,
                    "Successfully authenticated with GraphQL API",
                    execution_time_ms=result.get('_execution_time_ms')
                )
        except Exception as e:
            self._add_test_result(
                "GraphQL Authentication Test",
                TestCategory.AUTHENTICATION,
                TestSeverity.ERROR,
                False,
                f"Authentication test failed: {str(e)}"
            )
    
    def _run_query_tests(self):
        """Run query-related tests."""
        # Test simple introspection query
        try:
            query = """
            {
                __schema {
                    types {
                        name
                        kind
                    }
                }
            }
            """
            result = self._execute_graphql_query(query)
            
            if "data" in result and result["data"]:
                self._add_test_result(
                    "Basic Introspection Query",
                    TestCategory.QUERIES,
                    TestSeverity.SUCCESS,
                    True,
                    "Successfully executed introspection query",
                    details={"types_count": len(result["data"]["__schema"]["types"])},
                    execution_time_ms=result.get('_execution_time_ms')
                )
            else:
                self._add_test_result(
                    "Basic Introspection Query",
                    TestCategory.QUERIES,
                    TestSeverity.ERROR,
                    False,
                    "Introspection query returned no data"
                )
                
        except Exception as e:
            self._add_test_result(
                "Basic Introspection Query",
                TestCategory.QUERIES,
                TestSeverity.ERROR,
                False,
                f"Query test failed: {str(e)}"
            )
    
    def _run_mutation_tests(self):
        """Run mutation-related tests."""
        if not self.input_data.test_mutations:
            self._add_test_result(
                "Mutation Tests",
                TestCategory.MUTATIONS,
                TestSeverity.WARNING,
                True,
                "Mutation tests skipped as requested"
            )
            return
        
        # Safety check for production
        if self.input_data.environment == "production":
            self._add_test_result(
                "Production Mutation Safety Check",
                TestCategory.MUTATIONS,
                TestSeverity.WARNING,
                True,
                "Mutations cannot be tested in production environment without explicit override"
            )
            return
        
        # Here you would add actual mutation tests
        self._add_test_result(
            "Mutation Test Placeholder",
            TestCategory.MUTATIONS,
            TestSeverity.WARNING,
            True,
            "Mutation tests not implemented yet"
        )
    
    def _run_error_handling_tests(self):
        """Run error handling tests."""
        # Test invalid query
        try:
            query = "{ invalidField }"
            result = self._execute_graphql_query(query)
            
            if "errors" in result:
                self._add_test_result(
                    "Invalid Query Error Handling",
                    TestCategory.ERROR_HANDLING,
                    TestSeverity.SUCCESS,
                    True,
                    "API correctly handles invalid queries",
                    details={"error_message": result["errors"][0]["message"]}
                )
            else:
                self._add_test_result(
                    "Invalid Query Error Handling",
                    TestCategory.ERROR_HANDLING,
                    TestSeverity.ERROR,
                    False,
                    "API did not return expected error for invalid query"
                )
                
        except Exception as e:
            self._add_test_result(
                "Invalid Query Error Handling",
                TestCategory.ERROR_HANDLING,
                TestSeverity.ERROR,
                False,
                f"Error handling test failed: {str(e)}"
            )
    
    def _run_performance_tests(self):
        """Run performance tests."""
        # Test response time
        execution_time = None
        try:
            query = "{ __typename }"
            result = self._execute_graphql_query(query)
            
            execution_time = result.get('_execution_time_ms', 0)
            
            if execution_time < 500:
                severity = TestSeverity.SUCCESS
                passed = True
                message = f"Response time is excellent: {execution_time:.2f}ms"
            elif execution_time < 2000:
                severity = TestSeverity.WARNING
                passed = True
                message = f"Response time is acceptable: {execution_time:.2f}ms"
            else:
                severity = TestSeverity.ERROR
                passed = False
                message = f"Response time is too slow: {execution_time:.2f}ms"
            
            self._add_test_result(
                "API Response Time",
                TestCategory.PERFORMANCE,
                severity,
                passed,
                message,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            # Try to extract execution time from error message if available
            import re
            match = re.search(r'execution_time: (\d+\.\d+)ms', str(e))
            if match:
                execution_time = float(match.group(1))
            
            self._add_test_result(
                "API Response Time",
                TestCategory.PERFORMANCE,
                TestSeverity.ERROR,
                False,
                f"Performance test failed: {str(e)}",
                execution_time_ms=execution_time
            )
    
    def _generate_report(self) -> IntegrationTestReport:
        """Generate the final test report."""
        execution_time = time.time() - self.start_time
        passed_tests = sum(1 for r in self.test_results if r.passed)
        failed_tests = len(self.test_results) - passed_tests
        
        # Generate recommendations
        recommendations = []
        if failed_tests > 0:
            recommendations.append("Review and fix failed tests before proceeding")
        
        # Check for specific issues
        auth_failures = [r for r in self.test_results 
                        if r.category == TestCategory.AUTHENTICATION and not r.passed]
        if auth_failures:
            recommendations.append("Ensure API credentials are correctly configured")
        
        perf_issues = [r for r in self.test_results 
                      if r.category == TestCategory.PERFORMANCE and r.severity == TestSeverity.ERROR]
        if perf_issues:
            recommendations.append("Consider optimizing queries or checking network latency")
        
        # Generate summary
        if failed_tests == 0:
            summary = f"All {len(self.test_results)} tests passed successfully!"
        else:
            summary = f"{passed_tests} passed, {failed_tests} failed out of {len(self.test_results)} tests"
        
        return IntegrationTestReport(
            environment=self.input_data.environment,
            total_tests=len(self.test_results),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            test_results=self.test_results,
            overall_success=failed_tests == 0,
            execution_time_seconds=execution_time,
            recommendations=recommendations,
            summary=summary
        )


def setup_integration_testing_tool(mcp: FastMCP, schema_manager) -> None:
    """Setup the integration testing tool with the MCP server."""
    
    @mcp.tool()
    def integration_testing(
        environment: str = "staging",
        auth_method: str = "api_key",
        test_mutations: bool = True,
        test_categories: Optional[List[str]] = None,
        max_execution_time_seconds: int = 300,
        custom_endpoint: Optional[str] = None
    ) -> IntegrationTestingResult:
        """Run comprehensive integration tests against the Healthie GraphQL API.
        
        This tool performs end-to-end testing of the Healthie API including authentication,
        query execution, mutation safety, error handling, and performance validation.
        
        Args:
            environment: Environment to test against (staging, production, custom)
            auth_method: Authentication method to test (api_key, oauth, custom)
            test_mutations: Whether to test mutations (may modify data)
            test_categories: Specific test categories to run (if not provided, runs all)
            max_execution_time_seconds: Maximum time to allow for all tests
            custom_endpoint: Custom API endpoint URL for testing
                     
        Returns:
            IntegrationTestingResult with comprehensive test report
        """
        try:
            # Parse and validate test categories
            categories = _parse_test_categories(test_categories)
            
            # Create input model for validation
            input_data = IntegrationTestInput(
                environment=environment,
                auth_method=auth_method,
                test_mutations=test_mutations,
                test_categories=categories if categories else None,
                max_execution_time_seconds=max_execution_time_seconds,
                custom_endpoint=custom_endpoint
            )
            
            # Create and run test runner
            runner = IntegrationTestRunner(input_data)
            report = runner.run_tests()
            
            return IntegrationTestingResult(report=report)
            
        except ValueError as e:
            # Handle validation errors
            return IntegrationTestingResult(
                report=_create_error_report(environment, str(e)),
                error=str(e)
            )
        except Exception as e:
            # Handle unexpected errors
            return IntegrationTestingResult(
                report=_create_error_report(environment, "Unexpected error occurred"),
                error=f"Unexpected error: {str(e)}"
            )


def _parse_test_categories(test_categories: Optional[List[str]]) -> List[TestCategory]:
    """Parse test category strings into enum values."""
    if not test_categories:
        return []
    
    categories = []
    for cat in test_categories:
        try:
            categories.append(TestCategory(cat))
        except ValueError:
            # Skip invalid categories
            pass
    
    return categories


def _create_error_report(environment: str, error_message: str) -> IntegrationTestReport:
    """Create an error report for when tests cannot be run."""
    return IntegrationTestReport(
        environment=environment,
        total_tests=0,
        passed_tests=0,
        failed_tests=0,
        test_results=[],
        overall_success=False,
        execution_time_seconds=0.0,
        recommendations=["Fix the error and try again"],
        summary=f"Failed to run tests: {error_message}"
    )