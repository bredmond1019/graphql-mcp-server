"""Tests for healthcare patterns detection tool."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

# Mock the MCP module before importing our modules
sys.modules['mcp'] = MagicMock()
sys.modules['mcp.server'] = MagicMock()
sys.modules['mcp.server.fastmcp'] = MagicMock()

import pytest
from healthie_mcp.tools.healthcare_patterns import setup_healthcare_patterns_tool
from healthie_mcp.models.healthcare_patterns import (
    HealthcarePattern,
    PatternCategory,
    HealthcarePatternsResult
)


class TestHealthcarePatternsToolRegistration:
    """Test healthcare patterns tool registration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_schema_manager = Mock()
        self.mock_mcp = MagicMock()
        self.registered_tools = {}
        
        # Mock the tool decorator to capture registered functions
        def mock_tool():
            def decorator(func):
                self.registered_tools[func.__name__] = func
                return func
            return decorator
        
        self.mock_mcp.tool = mock_tool
    
    def test_find_healthcare_patterns_tool_is_registered(self):
        """Test that find_healthcare_patterns tool is registered."""
        setup_healthcare_patterns_tool(self.mock_mcp, self.mock_schema_manager)
        
        assert 'find_healthcare_patterns' in self.registered_tools
        assert callable(self.registered_tools['find_healthcare_patterns'])


class TestHealthcarePatternsDetection:
    """Test healthcare pattern detection functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_schema_manager = Mock()
        self.mock_mcp = MagicMock()
        self.registered_tools = {}
        
        # Mock the tool decorator to capture registered functions
        def mock_tool():
            def decorator(func):
                self.registered_tools[func.__name__] = func
                return func
            return decorator
        
        self.mock_mcp.tool = mock_tool
    
    def get_mock_schema_content(self):
        """Mock GraphQL schema content as SDL."""
        return """
        type Query {
            patient(id: ID!): Patient
            patients(first: Int): [Patient!]!
            appointments(patientId: ID): [Appointment!]!
            formAnswers(patientId: ID): [FormAnswer!]!
        }
        
        type Mutation {
            createPatient(input: CreatePatientInput!): Patient
            updatePatient(id: ID!, input: UpdatePatientInput!): Patient
            bookAppointment(input: BookAppointmentInput!): Appointment
            cancelAppointment(id: ID!): Appointment
            createFormAnswer(input: CreateFormAnswerInput!): FormAnswer
            createPayment(input: CreatePaymentInput!): Payment
            submitClaim(input: SubmitClaimInput!): Claim
        }
        
        type Patient {
            id: ID!
            first_name: String!
            last_name: String!
            date_of_birth: String
            appointments: [Appointment!]!
        }
        
        type Appointment {
            id: ID!
            date: String!
            provider: Provider
            status: String!
        }
        
        type FormAnswer {
            id: ID!
            answer: String!
        }
        
        type Payment {
            id: ID!
            amount: Float!
        }
        
        type Claim {
            id: ID!
            status: String!
        }
        
        type Provider {
            id: ID!
            name: String!
        }
        
        input CreatePatientInput {
            first_name: String!
            last_name: String!
            date_of_birth: String
        }
        
        input UpdatePatientInput {
            first_name: String
            last_name: String
            date_of_birth: String
        }
        
        input BookAppointmentInput {
            patientId: ID!
            providerId: ID!
            date: String!
        }
        
        input CreateFormAnswerInput {
            patientId: ID!
            answer: String!
        }
        
        input CreatePaymentInput {
            patientId: ID!
            amount: Float!
        }
        
        input SubmitClaimInput {
            patientId: ID!
            amount: Float!
        }
        """
    
    def test_find_patient_management_patterns(self):
        """Test finding patient management patterns."""
        mock_schema_content = self.get_mock_schema_content()
        self.mock_schema_manager.get_schema_content.return_value = mock_schema_content
        
        setup_healthcare_patterns_tool(self.mock_mcp, self.mock_schema_manager)
        healthcare_tool = self.registered_tools['find_healthcare_patterns']
        
        result = healthcare_tool()
        
        assert isinstance(result, HealthcarePatternsResult)
        
        patient_patterns = [p for p in result.patterns if p.category == PatternCategory.PATIENT_MANAGEMENT]
        assert len(patient_patterns) > 0
        
        pattern = patient_patterns[0]
        assert pattern.category == PatternCategory.PATIENT_MANAGEMENT
        assert any("createpatient" in elem.lower() for elem in pattern.elements)
        assert any("updatepatient" in elem.lower() for elem in pattern.elements)
        assert len(pattern.recommendations) > 0
    
    def test_find_appointment_workflow_patterns(self):
        """Test finding appointment workflow patterns."""
        mock_schema_content = self.get_mock_schema_content()
        self.mock_schema_manager.get_schema_content.return_value = mock_schema_content
        
        setup_healthcare_patterns_tool(self.mock_mcp, self.mock_schema_manager)
        healthcare_tool = self.registered_tools['find_healthcare_patterns']
        
        result = healthcare_tool()
        
        appointment_patterns = [p for p in result.patterns if p.category == PatternCategory.APPOINTMENTS]
        assert len(appointment_patterns) > 0
        
        pattern = appointment_patterns[0]
        assert "appointment" in pattern.description.lower()
        assert any("bookappointment" in elem.lower() for elem in pattern.elements)
        assert any("cancelappointment" in elem.lower() for elem in pattern.elements)
        assert len(pattern.recommendations) > 0
    
    def test_find_billing_insurance_patterns(self):
        """Test finding billing and insurance patterns."""
        mock_schema_content = self.get_mock_schema_content()
        self.mock_schema_manager.get_schema_content.return_value = mock_schema_content
        
        setup_healthcare_patterns_tool(self.mock_mcp, self.mock_schema_manager)
        healthcare_tool = self.registered_tools['find_healthcare_patterns']
        
        result = healthcare_tool()
        
        billing_patterns = [p for p in result.patterns if p.category == PatternCategory.BILLING]
        assert len(billing_patterns) > 0
        
        pattern = billing_patterns[0]
        assert any("createpayment" in elem.lower() or "submitclaim" in elem.lower() for elem in pattern.elements)
        assert len(pattern.recommendations) > 0
    
    def test_find_clinical_data_patterns(self):
        """Test finding clinical data patterns."""
        mock_schema_content = self.get_mock_schema_content()
        self.mock_schema_manager.get_schema_content.return_value = mock_schema_content
        
        setup_healthcare_patterns_tool(self.mock_mcp, self.mock_schema_manager)
        healthcare_tool = self.registered_tools['find_healthcare_patterns']
        
        result = healthcare_tool()
        
        clinical_patterns = [p for p in result.patterns if p.category == PatternCategory.CLINICAL_DATA]
        assert len(clinical_patterns) > 0
        
        pattern = clinical_patterns[0]
        assert any("createformanswer" in elem.lower() or "formanswers" in elem.lower() for elem in pattern.elements)
        assert len(pattern.recommendations) > 0
    
    def test_find_provider_organization_patterns(self):
        """Test finding provider/organization patterns."""
        extended_schema = self.get_mock_schema_content() + """
        type Organization {
            id: ID!
            name: String!
            providers: [Provider!]!
        }
        
        extend type Mutation {
            createProvider(input: CreateProviderInput!): Provider
            updateOrganization(id: ID!, input: UpdateOrganizationInput!): Organization
        }
        
        input CreateProviderInput {
            name: String!
            organizationId: ID
        }
        
        input UpdateOrganizationInput {
            name: String
        }
        """
        
        self.mock_schema_manager.get_schema_content.return_value = extended_schema
        setup_healthcare_patterns_tool(self.mock_mcp, self.mock_schema_manager)
        healthcare_tool = self.registered_tools['find_healthcare_patterns']
        
        result = healthcare_tool()
        
        provider_patterns = [p for p in result.patterns if p.category == PatternCategory.PROVIDER_MANAGEMENT]
        assert len(provider_patterns) > 0
    
    def test_structured_output_format(self):
        """Test that output follows structured format."""
        mock_schema_content = self.get_mock_schema_content()
        self.mock_schema_manager.get_schema_content.return_value = mock_schema_content
        
        setup_healthcare_patterns_tool(self.mock_mcp, self.mock_schema_manager)
        healthcare_tool = self.registered_tools['find_healthcare_patterns']
        
        result = healthcare_tool()
        
        assert isinstance(result, HealthcarePatternsResult)
        assert isinstance(result.patterns, list)
        assert result.total_patterns > 0
        assert result.summary is not None
        
        for pattern in result.patterns:
            assert isinstance(pattern, HealthcarePattern)
            assert pattern.category in PatternCategory
            assert isinstance(pattern.elements, list)
            assert pattern.description
            assert isinstance(pattern.recommendations, list)
    
    def test_no_patterns_found(self):
        """Test handling when no patterns are found."""
        empty_schema = """
        type Query {
            _dummy: String
        }
        
        type Mutation {
            _dummy: String
        }
        """
        
        self.mock_schema_manager.get_schema_content.return_value = empty_schema
        setup_healthcare_patterns_tool(self.mock_mcp, self.mock_schema_manager)
        healthcare_tool = self.registered_tools['find_healthcare_patterns']
        
        result = healthcare_tool()
        
        assert isinstance(result, HealthcarePatternsResult)
        assert result.total_patterns == 0
        assert len(result.patterns) == 0
        assert "no" in result.summary.lower() and "patterns" in result.summary.lower()
    
    def test_category_specific_search(self):
        """Test searching for specific pattern categories."""
        mock_schema_content = self.get_mock_schema_content()
        self.mock_schema_manager.get_schema_content.return_value = mock_schema_content
        
        setup_healthcare_patterns_tool(self.mock_mcp, self.mock_schema_manager)
        healthcare_tool = self.registered_tools['find_healthcare_patterns']
        
        # Search only for appointment patterns
        result = healthcare_tool(category="appointments")
        
        assert all(p.category == PatternCategory.APPOINTMENTS for p in result.patterns)
        assert len(result.patterns) > 0