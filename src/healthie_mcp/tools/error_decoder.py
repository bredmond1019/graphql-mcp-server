"""Error message decoder tool for external developers."""

import re
from typing import List
from mcp.server.fastmcp import FastMCP
from ..models.external_dev_tools import (
    ErrorDecodeResult, ErrorSolution
)


def setup_error_decoder_tool(mcp: FastMCP, schema_manager) -> None:
    """Setup the error message decoder tool with the MCP server."""
    
    @mcp.tool()
    def decode_api_errors(
        error_message: str,
        include_compliance_notes: bool = True
    ) -> ErrorDecodeResult:
        """Decode Healthie API error messages into plain English with actionable solutions.
        
        This tool helps external developers understand API errors and provides
        specific solutions for common integration issues.
        
        Args:
            error_message: The error message from the Healthie API
            include_compliance_notes: Whether to include healthcare compliance guidance
                     
        Returns:
            ErrorDecodeResult with plain English explanation and solutions
        """
        try:
            # Classify error type
            error_type = _classify_error_type(error_message)
            
            # Generate plain English explanation
            plain_english = _generate_plain_english_explanation(error_message, error_type)
            
            # Generate solutions
            solutions = _generate_error_solutions(error_message, error_type)
            
            # Check if healthcare-specific
            is_healthcare_specific = _is_healthcare_specific(error_message)
            
            # Generate compliance notes if requested
            compliance_notes = None
            if include_compliance_notes and is_healthcare_specific:
                compliance_notes = _generate_compliance_notes(error_message, error_type)
            
            return ErrorDecodeResult(
                original_error=error_message,
                error_type=error_type,
                plain_english=plain_english,
                solutions=solutions,
                is_healthcare_specific=is_healthcare_specific,
                compliance_notes=compliance_notes
            )
            
        except Exception as e:
            return ErrorDecodeResult(
                original_error=error_message,
                error_type="unknown",
                plain_english="Unable to decode error message",
                solutions=[],
                is_healthcare_specific=False,
                error=f"Error decoding API error: {str(e)}"
            )


def _classify_error_type(error_message: str) -> str:
    """Classify the type of error based on the message."""
    error_lower = error_message.lower()
    
    if 'authentication' in error_lower or 'unauthorized' in error_lower:
        return "authentication"
    elif 'permission' in error_lower or 'forbidden' in error_lower:
        return "authorization"
    elif 'validation' in error_lower or 'invalid' in error_lower:
        return "validation"
    elif 'not found' in error_lower or '404' in error_lower:
        return "not_found"
    elif 'rate limit' in error_lower or 'too many requests' in error_lower:
        return "rate_limit"
    elif 'server error' in error_lower or '500' in error_lower:
        return "server_error"
    elif 'timeout' in error_lower:
        return "timeout"
    elif 'graphql' in error_lower or 'syntax' in error_lower:
        return "graphql_syntax"
    else:
        return "unknown"


def _generate_plain_english_explanation(error_message: str, error_type: str) -> str:
    """Generate a plain English explanation of the error."""
    explanations = {
        "authentication": "Your API key is missing, invalid, or expired. The server cannot verify your identity.",
        "authorization": "You don't have permission to access this resource. Your account may not have the required role or the resource belongs to another organization.",
        "validation": "The data you provided doesn't meet the required format or business rules. Some fields may be missing, invalid, or contain incorrect values.",
        "not_found": "The resource you're trying to access doesn't exist. This could be a patient, appointment, or other record that has been deleted or never existed.",
        "rate_limit": "You're making too many API requests too quickly. The server is temporarily blocking your requests to prevent overload.",
        "server_error": "Something went wrong on Healthie's servers. This is usually a temporary issue on their end.",
        "timeout": "Your request took too long to process and was cancelled. This might happen with complex queries or during high server load.",
        "graphql_syntax": "There's a syntax error in your GraphQL query or mutation. The server can't understand what you're trying to do.",
        "unknown": "An unexpected error occurred that doesn't match common patterns."
    }
    
    base_explanation = explanations.get(error_type, explanations["unknown"])
    
    # Add specific details from the error message
    if "email" in error_message.lower():
        base_explanation += " The issue seems to be related to email validation or formatting."
    elif "phone" in error_message.lower():
        base_explanation += " The issue seems to be related to phone number formatting."
    elif "date" in error_message.lower():
        base_explanation += " The issue seems to be related to date formatting or invalid dates."
    
    return base_explanation


def _generate_error_solutions(error_message: str, error_type: str) -> List[ErrorSolution]:
    """Generate specific solutions for the error."""
    solutions = []
    
    if error_type == "authentication":
        solutions.extend([
            ErrorSolution(
                problem="Invalid or missing API key",
                solution="Check that your HEALTHIE_API_KEY environment variable is set correctly",
                code_example='headers: { "Authorization": "Bearer your-api-key-here" }'
            ),
            ErrorSolution(
                problem="Expired API key",
                solution="Generate a new API key from your Healthie dashboard",
                documentation_link="https://docs.gethealthie.com/authentication"
            )
        ])
    
    elif error_type == "validation":
        if "email" in error_message.lower():
            solutions.append(ErrorSolution(
                problem="Invalid email format",
                solution="Ensure email addresses follow the format user@domain.com",
                code_example='"email": "patient@example.com"'
            ))
        
        if "phone" in error_message.lower():
            solutions.append(ErrorSolution(
                problem="Invalid phone number format",
                solution="Use international format with country code",
                code_example='"phone": "+1234567890"'
            ))
        
        if "required" in error_message.lower():
            solutions.append(ErrorSolution(
                problem="Missing required fields",
                solution="Check the API documentation for required fields and include them in your request",
                code_example="Ensure all fields marked with '!' in the schema are provided"
            ))
    
    elif error_type == "authorization":
        solutions.extend([
            ErrorSolution(
                problem="Insufficient permissions",
                solution="Contact your organization admin to grant the necessary permissions for your API key"
            ),
            ErrorSolution(
                problem="Accessing resources from another organization",
                solution="Ensure you're only accessing resources that belong to your organization"
            )
        ])
    
    elif error_type == "rate_limit":
        solutions.extend([
            ErrorSolution(
                problem="Too many requests",
                solution="Implement exponential backoff retry logic",
                code_example="""
// Retry with exponential backoff
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));
let retries = 0;
while (retries < 3) {
  try {
    const response = await makeApiCall();
    return response;
  } catch (error) {
    if (error.status === 429) {
      await delay(Math.pow(2, retries) * 1000);
      retries++;
    } else {
      throw error;
    }
  }
}"""
            )
        ])
    
    elif error_type == "graphql_syntax":
        solutions.extend([
            ErrorSolution(
                problem="GraphQL syntax error",
                solution="Validate your GraphQL query syntax using a GraphQL playground or validator"
            ),
            ErrorSolution(
                problem="Invalid field names",
                solution="Check field names against the schema - they are case-sensitive"
            )
        ])
    
    # Add general solution if no specific ones found
    if not solutions:
        solutions.append(ErrorSolution(
            problem="General error",
            solution="Check the Healthie API documentation for more details about this error"
        ))
    
    return solutions


def _is_healthcare_specific(error_message: str) -> bool:
    """Check if the error is healthcare-specific."""
    healthcare_terms = [
        'patient', 'client', 'appointment', 'provider', 'insurance', 
        'medication', 'diagnosis', 'hipaa', 'phi', 'medical'
    ]
    
    error_lower = error_message.lower()
    return any(term in error_lower for term in healthcare_terms)


def _generate_compliance_notes(error_message: str, error_type: str) -> str:
    """Generate healthcare compliance notes for the error."""
    if error_type == "authorization":
        return "HIPAA Compliance: Ensure your application properly restricts access to patient data based on user roles and permissions. Only authorized personnel should access PHI (Protected Health Information)."
    
    elif error_type == "validation" and "patient" in error_message.lower():
        return "Healthcare Data Quality: Patient data validation errors can impact care quality. Ensure all patient information is accurate and complete before submission."
    
    elif "phi" in error_message.lower() or "hipaa" in error_message.lower():
        return "HIPAA Violation Risk: This error may indicate a potential violation of HIPAA privacy rules. Review your data handling practices and ensure proper access controls are in place."
    
    else:
        return "Healthcare Best Practice: When handling healthcare data, always implement proper error handling, logging (without exposing PHI), and user notification procedures."