"""Workflow sequence builder tool for external developers.

This tool provides multi-step API call sequences for common healthcare workflows,
helping external developers understand the correct order of operations and
best practices for healthcare application development.
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

from ..models.external_dev_tools import (
    WorkflowSequenceResult, WorkflowSequence, WorkflowStep, WorkflowCategory
)
from ..base import BaseTool, SchemaManagerProtocol
from ..config.loader import get_config_loader
from ..exceptions import ToolError


class WorkflowConstants:
    """Constants for workflow sequence tool."""
    
    # Workflow categories mapping
    CATEGORY_PATIENT_MANAGEMENT = "patient_management"
    CATEGORY_APPOINTMENTS = "appointments"
    CATEGORY_CLINICAL_DATA = "clinical_data"
    CATEGORY_BILLING = "billing"
    CATEGORY_PROVIDER_MANAGEMENT = "provider_management"
    
    # Common workflow patterns
    WORKFLOW_PATTERNS = {
        'onboarding': 'Complete setup process for new entities',
        'booking': 'Reservation and scheduling processes',
        'submission': 'Data entry and form completion',
        'verification': 'Validation and approval processes',
        'payment': 'Financial transaction processing'
    }
    
    # Required inputs for common operations
    COMMON_INPUTS = {
        'patient_create': ['firstName', 'lastName', 'email', 'phone'],
        'appointment_create': ['clientId', 'providerId', 'startTime', 'endTime'],
        'form_submit': ['clientId', 'formId', 'responses'],
        'payment_process': ['amount', 'clientId', 'paymentMethod']
    }
    
    # Expected outputs for verification
    COMMON_OUTPUTS = {
        'entity_creation': ['id', 'status', 'createdAt'],
        'form_operations': ['status', 'submittedAt', 'completedAt'],
        'payment_operations': ['transactionId', 'status', 'amount']
    }
    
    # Prerequisites for workflows
    WORKFLOW_PREREQUISITES = {
        'patient_onboarding': ['Valid API key', 'Organization setup'],
        'appointment_booking': ['Patient exists in system', 'Provider has availability'],
        'clinical_documentation': ['Patient relationship established', 'Provider credentials verified'],
        'billing_processing': ['Patient insurance verified', 'Services documented']
    }
    
    # Estimated durations
    DURATION_ESTIMATES = {
        'simple': '1-2 minutes',
        'moderate': '3-5 minutes',
        'complex': '5-10 minutes',
        'extended': '10+ minutes'
    }


class WorkflowSequenceInput(BaseModel):
    """Input parameters for workflow sequence building."""
    
    workflow_name: Optional[str] = Field(
        None,
        description="Specific workflow to build (e.g., 'patient_onboarding', 'appointment_booking')"
    )
    
    category: Optional[str] = Field(
        None,
        description="Workflow category to filter by (patient_management, appointments, clinical_data, billing)"
    )


class WorkflowSequencesTool(BaseTool[WorkflowSequenceResult]):
    """Tool for building step-by-step workflow sequences for healthcare operations."""
    
    def __init__(self, schema_manager: SchemaManagerProtocol):
        """Initialize the tool.
        
        Args:
            schema_manager: Schema manager instance (required for consistency)
        """
        super().__init__(schema_manager)
        self.config_loader = get_config_loader()
        self._workflows_cache: Optional[List[WorkflowSequence]] = None
    
    def get_tool_name(self) -> str:
        """Get the tool name."""
        return "build_workflow_sequence"
    
    def get_tool_description(self) -> str:
        """Get the tool description."""
        return "Build step-by-step workflow sequences for complex healthcare operations"
    
    def execute(
        self,
        workflow_name: Optional[str] = None,
        category: Optional[str] = None
    ) -> WorkflowSequenceResult:
        """Build step-by-step workflow sequences for complex healthcare operations.
        
        Args:
            workflow_name: Specific workflow to build
            category: Workflow category to filter by
                     
        Returns:
            WorkflowSequenceResult with detailed workflow sequences
        """
        try:
            # Get workflow sequences based on filters
            workflows = self._get_workflow_sequences(workflow_name, category)
            
            return WorkflowSequenceResult(
                workflows=workflows,
                total_workflows=len(workflows),
                category_filter=category
            )
            
        except Exception as e:
            raise ToolError(f"Error building workflow sequences: {str(e)}")

    def _get_workflow_sequences(self, workflow_filter: Optional[str], category_filter: Optional[str]) -> List[WorkflowSequence]:
        """Get workflow sequences based on filters."""
        # Use cached workflows if available
        if self._workflows_cache is None:
            self._workflows_cache = self._build_all_workflows()
        
        workflows = list(self._workflows_cache)
        
        # Apply category filter
        if category_filter:
            workflows = self._filter_by_category(workflows, category_filter)
        
        # Apply workflow name filter
        if workflow_filter:
            workflows = self._filter_by_name(workflows, workflow_filter)
        
        return workflows
    
    def _build_all_workflows(self) -> List[WorkflowSequence]:
        """Build all available workflow sequences."""
        workflows = []
        
        # Add patient management workflows
        workflows.extend(self._build_patient_management_workflows())
        
        # Add appointment workflows
        workflows.extend(self._build_appointment_workflows())
        
        # Add clinical workflows
        workflows.extend(self._build_clinical_workflows())
        
        # Add billing workflows  
        workflows.extend(self._build_billing_workflows())
        
        return workflows
    
    def _build_patient_management_workflows(self) -> List[WorkflowSequence]:
        """Build patient management workflow sequences."""
        return [
            WorkflowSequence(
                workflow_name="Complete Patient Onboarding",
                category=WorkflowCategory.PATIENT_MANAGEMENT,
                description="Full patient registration process including demographics, insurance, and initial forms",
                steps=self._build_patient_onboarding_steps(),
                total_steps=4,
                estimated_duration=WorkflowConstants.DURATION_ESTIMATES['complex'],
                prerequisites=WorkflowConstants.WORKFLOW_PREREQUISITES['patient_onboarding'],
                notes="Complete this workflow before scheduling appointments"
            )
        ]
    
    def _build_patient_onboarding_steps(self) -> List[WorkflowStep]:
        """Build steps for patient onboarding workflow."""
        return [
            WorkflowStep(
                step_number=1,
                operation_type="mutation",
                operation_name="createClient",
                description="Create the patient record with basic demographics",
                required_inputs=WorkflowConstants.COMMON_INPUTS['patient_create'],
                expected_outputs=["client.id", "client.email"],
                graphql_example="""mutation CreatePatient($input: CreateClientInput!) {
  createClient(input: $input) {
    client {
      id
      firstName
      lastName
      email
    }
    errors { field message }
  }
}""",
                notes="Save the client.id for subsequent steps"
            ),
            WorkflowStep(
                step_number=2,
                operation_type="mutation",
                operation_name="updateClientInsurance",
                description="Add insurance information for the patient",
                required_inputs=["clientId", "insuranceInfo"],
                expected_outputs=["insurance.id", "insurance.status"],
                graphql_example="""mutation UpdateInsurance($input: UpdateInsuranceInput!) {
  updateClientInsurance(input: $input) {
    insurance {
      id
      name
      memberNumber
      status
    }
    errors { field message }
  }
}""",
                depends_on=[1],
                notes="Insurance verification may take additional time"
            ),
            WorkflowStep(
                step_number=3,
                operation_type="query",
                operation_name="getRequiredForms",
                description="Get list of required intake forms for the patient",
                required_inputs=["clientId"],
                expected_outputs=["forms.id", "forms.name", "forms.required"],
                graphql_example="""query GetRequiredForms($clientId: ID!) {
  client(id: $clientId) {
    requiredForms {
      id
      name
      formType
      required
    }
  }
}""",
                depends_on=[1]
            ),
            WorkflowStep(
                step_number=4,
                operation_type="mutation",
                operation_name="submitIntakeForm",
                description="Submit completed intake forms",
                required_inputs=WorkflowConstants.COMMON_INPUTS['form_submit'],
                expected_outputs=WorkflowConstants.COMMON_OUTPUTS['form_operations'],
                graphql_example="""mutation SubmitForm($input: SubmitFormInput!) {
  submitForm(input: $input) {
    form {
      id
      status
      submittedAt
    }
    errors { field message }
  }
}""",
                depends_on=[3],
                notes="Repeat for each required form"
            )
        ]
    
    def _build_appointment_workflows(self) -> List[WorkflowSequence]:
        """Build appointment workflow sequences."""
        return [
            WorkflowSequence(
                workflow_name="Book Appointment with Verification",
                category=WorkflowCategory.APPOINTMENTS,
                description="Complete appointment booking process with availability check and confirmation",
                steps=self._build_appointment_booking_steps(),
                total_steps=3,
                estimated_duration=WorkflowConstants.DURATION_ESTIMATES['simple'],
                prerequisites=WorkflowConstants.WORKFLOW_PREREQUISITES['appointment_booking']
            )
        ]
    
    def _build_appointment_booking_steps(self) -> List[WorkflowStep]:
        """Build steps for appointment booking workflow."""
        return [
            WorkflowStep(
                step_number=1,
                operation_type="query",
                operation_name="getProviderAvailability",
                description="Check provider availability for the requested time period",
                required_inputs=["providerId", "startDate", "endDate"],
                expected_outputs=["availableSlots"],
                graphql_example="""query GetAvailability($providerId: ID!, $startDate: Date!, $endDate: Date!) {
  provider(id: $providerId) {
    availableSlots(startDate: $startDate, endDate: $endDate) {
      startTime
      endTime
      isAvailable
    }
  }
}"""
            ),
            WorkflowStep(
                step_number=2,
                operation_type="mutation",
                operation_name="createAppointment",
                description="Create the appointment booking",
                required_inputs=WorkflowConstants.COMMON_INPUTS['appointment_create'],
                expected_outputs=["appointment.id", "appointment.status"],
                graphql_example="""mutation BookAppointment($input: CreateAppointmentInput!) {
  createAppointment(input: $input) {
    appointment {
      id
      startTime
      endTime
      status
    }
    errors { field message }
  }
}""",
                depends_on=[1]
            ),
            WorkflowStep(
                step_number=3,
                operation_type="mutation",
                operation_name="sendAppointmentConfirmation",
                description="Send confirmation email/SMS to patient",
                required_inputs=["appointmentId"],
                expected_outputs=["confirmation.sent"],
                graphql_example="""mutation SendConfirmation($appointmentId: ID!) {
  sendAppointmentConfirmation(appointmentId: $appointmentId) {
    success
    sentAt
  }
}""",
                depends_on=[2],
                notes="Optional but recommended for patient experience"
            )
        ]
    
    def _build_clinical_workflows(self) -> List[WorkflowSequence]:
        """Build clinical workflow sequences."""
        # Add clinical workflows in the future
        return []
    
    def _build_billing_workflows(self) -> List[WorkflowSequence]:
        """Build billing workflow sequences."""
        # Add billing workflows in the future
        return []
    
    def _filter_by_category(self, workflows: List[WorkflowSequence], category_filter: str) -> List[WorkflowSequence]:
        """Filter workflows by category."""
        try:
            # Convert string to enum for comparison
            target_category = WorkflowCategory(category_filter)
            return [w for w in workflows if w.category == target_category]
        except ValueError:
            # Invalid category, return empty list
            return []
    
    def _filter_by_name(self, workflows: List[WorkflowSequence], workflow_filter: str) -> List[WorkflowSequence]:
        """Filter workflows by name."""
        workflow_filter_lower = workflow_filter.lower()
        return [w for w in workflows if workflow_filter_lower in w.workflow_name.lower()]


def setup_workflow_sequence_tool(mcp: FastMCP, schema_manager) -> None:
    """Setup the workflow sequence builder tool with the MCP server."""
    tool = WorkflowSequencesTool(schema_manager)
    
    @mcp.tool()
    def build_workflow_sequence(
        workflow_name: Optional[str] = None,
        category: Optional[str] = None
    ) -> dict:
        """Build step-by-step workflow sequences for complex healthcare operations.
        
        This tool provides multi-step API call sequences for common healthcare workflows,
        helping external developers understand the correct order of operations.
        
        Args:
            workflow_name: Specific workflow to build (e.g., "patient_onboarding")
            category: Workflow category to filter by
                     
        Returns:
            WorkflowSequenceResult with detailed workflow sequences
        """
        result = tool.execute(
            workflow_name=workflow_name,
            category=category
        )
        return result.model_dump()