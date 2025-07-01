"""
Unit tests for the Compliance Checker Tool.

This module tests the compliance checking functionality using TDD methodology.
All tests should initially fail until the tool is implemented.
"""

import pytest
from unittest.mock import Mock, patch
from typing import List

from src.healthie_mcp.tools.compliance_checker import ComplianceCheckerTool
from src.healthie_mcp.models.compliance_checker import (
    ComplianceCheckerInput,
    ComplianceCheckerResult,
    ComplianceLevel,
    RegulatoryFramework,
    PHICategory,
    AuditRequirement,
    ComplianceViolation,
    PHIExposureRisk,
    DataHandlingPractice,
    AuditRequirementCheck,
    StateRegulation
)
from src.healthie_mcp.base import SchemaManagerProtocol


class TestComplianceCheckerTool:
    """Test cases for the Compliance Checker Tool."""

    @pytest.fixture
    def mock_schema_manager(self):
        """Create a mock schema manager."""
        mock = Mock(spec=SchemaManagerProtocol)
        mock.get_schema_content.return_value = "type Patient { id: ID! name: String ssn: String }"
        return mock

    @pytest.fixture 
    def compliance_checker(self, mock_schema_manager):
        """Create a ComplianceCheckerTool instance."""
        tool = ComplianceCheckerTool(mock_schema_manager)
        # Clear cache to avoid test interference
        tool.config_loader.clear_cache()
        return tool

    @pytest.mark.unit
    def test_compliance_checker_validates_hipaa_queries(self, compliance_checker):
        """Test that the tool validates HIPAA compliance in GraphQL queries."""
        # Test query with potential PHI exposure
        phi_query = """
        query GetPatient($id: ID!) {
            patient(id: $id) {
                id
                name
                ssn
                dateOfBirth
                address
                phoneNumber
                email
            }
        }
        """
        
        input_data = ComplianceCheckerInput(
            query=phi_query,
            operation_type="query",
            frameworks=[RegulatoryFramework.HIPAA]
        )
        
        result = compliance_checker.execute(input_data)
        
        assert isinstance(result, ComplianceCheckerResult)
        assert result.overall_compliance in [ComplianceLevel.WARNING, ComplianceLevel.VIOLATION]
        assert len(result.violations) > 0
        assert any(v.framework == RegulatoryFramework.HIPAA for v in result.violations)
        assert any("ssn" in v.field.lower() for v in result.violations if v.field)

    @pytest.mark.unit
    def test_compliance_checker_checks_data_handling(self, compliance_checker):
        """Test that the tool checks data handling practices for compliance."""
        input_data = ComplianceCheckerInput(
            data_handling_context="patient_portal",
            frameworks=[RegulatoryFramework.HIPAA, RegulatoryFramework.HITECH]
        )
        
        result = compliance_checker.execute(input_data)
        
        assert isinstance(result, ComplianceCheckerResult)
        assert len(result.data_handling) > 0
        
        # Should check encryption practices
        encryption_check = next(
            (p for p in result.data_handling if "encryption" in p.practice.lower()), 
            None
        )
        assert encryption_check is not None
        assert encryption_check.framework in [RegulatoryFramework.HIPAA, RegulatoryFramework.HITECH]

    @pytest.mark.unit
    def test_compliance_checker_provides_regulatory_guidance(self, compliance_checker):
        """Test that the tool provides comprehensive regulatory guidance."""
        input_data = ComplianceCheckerInput(
            query="query { patients { id name } }",
            frameworks=[RegulatoryFramework.HIPAA, RegulatoryFramework.GDPR]
        )
        
        result = compliance_checker.execute(input_data)
        
        assert isinstance(result, ComplianceCheckerResult)
        assert len(result.recommendations) > 0
        assert len(result.next_steps) > 0
        assert len(result.resources) > 0
        
        # Should provide framework-specific guidance
        assert len(result.frameworks_checked) >= 2
        assert RegulatoryFramework.HIPAA in result.frameworks_checked
        assert RegulatoryFramework.GDPR in result.frameworks_checked

    @pytest.mark.unit
    def test_compliance_checker_identifies_phi_exposure(self, compliance_checker):
        """Test that the tool identifies PHI exposure risks."""
        # Query with various types of PHI
        phi_query = """
        query GetPatientDetails($id: ID!) {
            patient(id: $id) {
                socialSecurityNumber
                medicalRecordNumber
                diagnoses
                medications
                insuranceId
                emergencyContactPhone
            }
        }
        """
        
        input_data = ComplianceCheckerInput(
            query=phi_query,
            check_phi_exposure=True,
            frameworks=[RegulatoryFramework.HIPAA]
        )
        
        result = compliance_checker.execute(input_data)
        
        assert isinstance(result, ComplianceCheckerResult)
        assert len(result.phi_risks) > 0
        
        # Should identify different PHI categories
        phi_categories = {risk.category for risk in result.phi_risks}
        assert PHICategory.DIRECT_IDENTIFIERS in phi_categories
        assert PHICategory.SENSITIVE_HEALTH_DATA in phi_categories
        
        # Should provide mitigation strategies
        for risk in result.phi_risks:
            assert len(risk.mitigation) > 0
            assert len(risk.fields) > 0

    @pytest.mark.unit
    def test_compliance_checker_validates_audit_requirements(self, compliance_checker):
        """Test that the tool validates audit requirements."""
        input_data = ComplianceCheckerInput(
            query="mutation { updatePatient(id: \"123\", input: { name: \"John\" }) { id } }",
            operation_type="mutation",
            check_audit_requirements=True,
            frameworks=[RegulatoryFramework.HIPAA]
        )
        
        result = compliance_checker.execute(input_data)
        
        assert isinstance(result, ComplianceCheckerResult)
        assert len(result.audit_requirements) > 0
        
        # Should check key audit requirements
        audit_types = {req.requirement for req in result.audit_requirements}
        assert AuditRequirement.ACCESS_LOGGING in audit_types
        assert AuditRequirement.AUTHORIZATION in audit_types
        
        # Should provide implementation guidance
        for requirement in result.audit_requirements:
            assert len(requirement.implementation_guide) > 0
            assert len(requirement.evidence_needed) > 0

    @pytest.mark.unit
    def test_compliance_checker_supports_state_regulations(self, compliance_checker):
        """Test that the tool supports state-specific regulations."""
        input_data = ComplianceCheckerInput(
            query="query { patients { id name email } }",
            state="CA",  # California has strict privacy laws
            frameworks=[RegulatoryFramework.STATE_PRIVACY]
        )
        
        result = compliance_checker.execute(input_data)
        
        assert isinstance(result, ComplianceCheckerResult)
        assert len(result.state_regulations) > 0
        
        # Should include California-specific regulations
        ca_regulation = next(
            (reg for reg in result.state_regulations if reg.state == "CA"), 
            None
        )
        assert ca_regulation is not None
        assert len(ca_regulation.requirements) > 0
        assert len(ca_regulation.compliance_notes) > 0

    @pytest.mark.unit
    def test_compliance_checker_handles_compliant_query(self, compliance_checker):
        """Test that the tool correctly identifies compliant queries."""
        # Simple query with minimal PHI exposure
        compliant_query = """
        query GetAppointments {
            appointments {
                id
                startTime
                status
            }
        }
        """
        
        input_data = ComplianceCheckerInput(
            query=compliant_query,
            frameworks=[RegulatoryFramework.HIPAA]
        )
        
        result = compliance_checker.execute(input_data)
        
        assert isinstance(result, ComplianceCheckerResult)
        assert result.overall_compliance in [ComplianceLevel.COMPLIANT, ComplianceLevel.WARNING]
        assert len(result.violations) == 0 or all(
            v.severity != ComplianceLevel.VIOLATION for v in result.violations
        )

    @pytest.mark.unit
    def test_compliance_checker_handles_multiple_frameworks(self, compliance_checker):
        """Test that the tool can check against multiple regulatory frameworks."""
        input_data = ComplianceCheckerInput(
            query="query { patients { id name } }",
            frameworks=[
                RegulatoryFramework.HIPAA,
                RegulatoryFramework.HITECH,
                RegulatoryFramework.SOC2
            ]
        )
        
        result = compliance_checker.execute(input_data)
        
        assert isinstance(result, ComplianceCheckerResult)
        assert len(result.frameworks_checked) == 3
        
        # Should have framework-specific checks
        frameworks_in_violations = {v.framework for v in result.violations}
        frameworks_in_data_handling = {p.framework for p in result.data_handling}
        
        # At least one framework should have generated checks
        assert len(frameworks_in_violations | frameworks_in_data_handling) > 0

    @pytest.mark.unit
    def test_compliance_checker_handles_empty_input(self, compliance_checker):
        """Test that the tool handles empty or minimal input gracefully."""
        input_data = ComplianceCheckerInput()
        
        result = compliance_checker.execute(input_data)
        
        assert isinstance(result, ComplianceCheckerResult)
        assert result.overall_compliance in [ComplianceLevel.WARNING, ComplianceLevel.COMPLIANT]
        assert len(result.recommendations) > 0  # Should provide general guidance

    @pytest.mark.unit
    def test_compliance_checker_provides_detailed_recommendations(self, compliance_checker):
        """Test that the tool provides detailed, actionable recommendations."""
        input_data = ComplianceCheckerInput(
            query="query { patients { ssn medicalRecordNumber } }",
            frameworks=[RegulatoryFramework.HIPAA]
        )
        
        result = compliance_checker.execute(input_data)
        
        assert isinstance(result, ComplianceCheckerResult)
        assert len(result.recommendations) > 0
        assert len(result.next_steps) > 0
        
        # Recommendations should be specific and actionable
        for recommendation in result.recommendations:
            assert len(recommendation) > 20  # Should be detailed
            
        for step in result.next_steps:
            assert len(step) > 10  # Should be specific

    @pytest.mark.unit
    def test_compliance_checker_tool_registration(self, compliance_checker):
        """Test that the tool is properly registered with correct metadata."""
        assert compliance_checker.get_tool_name() == "compliance_checker"
        
        description = compliance_checker.get_tool_description()
        assert "compliance" in description.lower()
        assert "hipaa" in description.lower()
        assert "phi" in description.lower()

    @pytest.mark.unit
    def test_compliance_checker_configuration_loading(self, compliance_checker):
        """Test that the tool loads configuration correctly."""
        # This test verifies that the tool can load its configuration
        # without errors and that required config sections exist
        
        # The tool should not raise exceptions during initialization
        assert compliance_checker is not None
        
        # Configuration should be accessible through the tool
        # (Implementation details will depend on the actual config structure)
        assert hasattr(compliance_checker, 'config_loader')