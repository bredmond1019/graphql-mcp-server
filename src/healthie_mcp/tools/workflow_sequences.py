"""Workflow sequence builder tool for external developers."""

from typing import Optional, List
from mcp.server.fastmcp import FastMCP
from ..models.external_dev_tools import (
    WorkflowSequenceResult, WorkflowSequence, WorkflowStep, WorkflowCategory
)


def setup_workflow_sequence_tool(mcp: FastMCP, schema_manager) -> None:
    """Setup the workflow sequence builder tool with the MCP server."""
    
    @mcp.tool()
    def build_workflow_sequence(
        workflow_name: Optional[str] = None,
        category: Optional[str] = None
    ) -> WorkflowSequenceResult:
        """Build step-by-step workflow sequences for complex healthcare operations.
        
        This tool provides multi-step API call sequences for common healthcare workflows,
        helping external developers understand the correct order of operations.
        
        Args:
            workflow_name: Specific workflow to build (e.g., "patient_onboarding")
            category: Workflow category to filter by
                     
        Returns:
            WorkflowSequenceResult with detailed workflow sequences
        """
        try:
            # Get workflow sequences based on filters
            workflows = _get_workflow_sequences(workflow_name, category)
            
            return WorkflowSequenceResult(
                workflows=workflows,
                total_workflows=len(workflows),
                category_filter=category
            )
            
        except Exception as e:
            return WorkflowSequenceResult(
                workflows=[],
                total_workflows=0,
                category_filter=category,
                error=f"Error building workflow sequences: {str(e)}"
            )


def _get_workflow_sequences(workflow_filter: Optional[str], category_filter: Optional[str]) -> List[WorkflowSequence]:
    """Get workflow sequences based on filters."""
    workflows = []
    
    # Patient Management Workflows
    if not category_filter or category_filter == WorkflowCategory.PATIENT_MANAGEMENT.value:
        workflows.extend([
            WorkflowSequence(
                workflow_name="Complete Patient Onboarding",
                category=WorkflowCategory.PATIENT_MANAGEMENT,
                description="Full patient registration process including demographics, insurance, and initial forms",
                steps=[
                    WorkflowStep(
                        step_number=1,
                        operation_type="mutation",
                        operation_name="createClient",
                        description="Create the patient record with basic demographics",
                        required_inputs=["firstName", "lastName", "email", "phone"],
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
                        required_inputs=["clientId", "formId", "responses"],
                        expected_outputs=["form.status", "form.submittedAt"],
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
                ],
                total_steps=4,
                estimated_duration="5-10 minutes",
                prerequisites=["Valid API key", "Organization setup"],
                notes="Complete this workflow before scheduling appointments"
            )
        ])
    
    # Appointment Workflows
    if not category_filter or category_filter == WorkflowCategory.APPOINTMENTS.value:
        workflows.extend([
            WorkflowSequence(
                workflow_name="Book Appointment with Verification",
                category=WorkflowCategory.APPOINTMENTS,
                description="Complete appointment booking process with availability check and confirmation",
                steps=[
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
                        required_inputs=["clientId", "providerId", "startTime", "endTime"],
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
                ],
                total_steps=3,
                estimated_duration="1-2 minutes",
                prerequisites=["Patient exists in system", "Provider has availability"]
            )
        ])
    
    # Filter by specific workflow name if provided
    if workflow_filter:
        workflows = [w for w in workflows if workflow_filter.lower() in w.workflow_name.lower()]
    
    return workflows