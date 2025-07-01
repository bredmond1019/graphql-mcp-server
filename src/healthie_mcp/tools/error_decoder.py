"""Error message decoder tool for external developers."""

import re
from typing import List, Dict, Any, Optional
from ..models.external_dev_tools import (
    ErrorDecodeResult, ErrorSolution
)
from ..base import BaseTool, SchemaManagerProtocol
from ..config.loader import ConfigLoader
from ..exceptions import ToolError
from pydantic import BaseModel, Field


class ErrorDecoderInput(BaseModel):
    """Input for error decoder tool."""
    error_message: str = Field(description="The error message to decode")
    include_compliance_notes: bool = Field(True, description="Include healthcare compliance guidance")


class ErrorDecoderConstants:
    """Constants for error decoding."""
    
    # Error type classification patterns
    ERROR_PATTERNS = {
        "authentication": ["authentication", "unauthorized", "invalid api key", "expired token"],
        "authorization": ["permission", "forbidden", "access denied", "not authorized"],
        "validation": ["validation", "invalid", "required field", "format error"],
        "not_found": ["not found", "404", "resource not found", "does not exist"],
        "rate_limit": ["rate limit", "too many requests", "429", "quota exceeded"],
        "server_error": ["server error", "500", "internal error", "service unavailable"],
        "timeout": ["timeout", "request timeout", "took too long"],
        "graphql_syntax": ["graphql", "syntax", "parse error", "query error"],
        "network": ["connection", "network", "dns", "timeout", "unreachable"]
    }
    
    # Plain English explanations
    ERROR_EXPLANATIONS = {
        "authentication": "Your API key is missing, invalid, or expired. The server cannot verify your identity.",
        "authorization": "You don't have permission to access this resource. Your account may not have the required role or the resource belongs to another organization.",
        "validation": "The data you provided doesn't meet the required format or business rules. Some fields may be missing, invalid, or contain incorrect values.",
        "not_found": "The resource you're trying to access doesn't exist. This could be a patient, appointment, or other record that has been deleted or never existed.",
        "rate_limit": "You're making too many API requests too quickly. The server is temporarily blocking your requests to prevent overload.",
        "server_error": "Something went wrong on Healthie's servers. This is usually a temporary issue on their end.",
        "timeout": "Your request took too long to process and was cancelled. This might happen with complex queries or during high server load.",
        "graphql_syntax": "There's a syntax error in your GraphQL query or mutation. The server can't understand what you're trying to do.",
        "network": "There's a connection issue between your application and the Healthie API servers.",
        "unknown": "An unexpected error occurred that doesn't match common patterns."
    }
    
    # Healthcare-specific terms
    HEALTHCARE_TERMS = [
        'patient', 'client', 'appointment', 'provider', 'insurance', 
        'medication', 'diagnosis', 'hipaa', 'phi', 'medical', 'healthcare',
        'clinical', 'billing', 'claim', 'treatment', 'care', 'hospital'
    ]
    
    # Field-specific error hints
    FIELD_ERROR_HINTS = {
        "email": " The issue seems to be related to email validation or formatting.",
        "phone": " The issue seems to be related to phone number formatting.",
        "date": " The issue seems to be related to date formatting or invalid dates.",
        "password": " The issue seems to be related to password requirements.",
        "id": " The issue seems to be related to invalid or missing ID values."
    }


class ErrorDecoderTool(BaseTool[ErrorDecodeResult]):
    """Tool for decoding API error messages into actionable solutions."""
    
    def __init__(self, schema_manager: SchemaManagerProtocol):
        """Initialize the error decoder tool."""
        super().__init__(schema_manager)
        self.config_loader = ConfigLoader()
        self._error_config: Optional[Dict[str, Any]] = None
    
    def get_tool_name(self) -> str:
        """Get the tool name."""
        return "error_decoder"
    
    def get_tool_description(self) -> str:
        """Get the tool description."""
        return (
            "Decode Healthie API error messages into plain English with actionable solutions "
            "and healthcare compliance guidance for external developers"
        )
    
    def execute(self, input_data: ErrorDecoderInput) -> ErrorDecodeResult:
        """Decode the error message and provide solutions.
        
        Args:
            input_data: Input containing error message and options
            
        Returns:
            ErrorDecodeResult with decoded error and solutions
        """
        try:
            # Load configuration if available
            self._ensure_config_loaded()
            
            # Classify error type
            error_type = self._classify_error_type(input_data.error_message)
            
            # Generate plain English explanation
            plain_english = self._generate_plain_english_explanation(
                input_data.error_message, error_type
            )
            
            # Generate solutions
            solutions = self._generate_error_solutions(input_data.error_message, error_type)
            
            # Check if healthcare-specific
            is_healthcare_specific = self._is_healthcare_specific(input_data.error_message)
            
            # Generate compliance notes if requested
            compliance_notes = None
            if input_data.include_compliance_notes and is_healthcare_specific:
                compliance_notes = self._generate_compliance_notes(
                    input_data.error_message, error_type
                )
            
            return ErrorDecodeResult(
                original_error=input_data.error_message,
                error_type=error_type,
                plain_english=plain_english,
                solutions=solutions,
                is_healthcare_specific=is_healthcare_specific,
                compliance_notes=compliance_notes
            )
            
        except Exception as e:
            return ErrorDecodeResult(
                original_error=input_data.error_message,
                error_type="unknown",
                plain_english="Unable to decode error message",
                solutions=[],
                is_healthcare_specific=False,
                error=f"Error decoding API error: {str(e)}"
            )
    
    def _ensure_config_loaded(self) -> None:
        """Ensure error configuration is loaded."""
        if self._error_config is None:
            try:
                self._error_config = self.config_loader.load_errors()
            except Exception:
                # Use default configuration if loading fails
                self._error_config = {}
    
    def _classify_error_type(self, error_message: str) -> str:
        """Classify the type of error based on the message.
        
        Args:
            error_message: The error message to classify
            
        Returns:
            Error type string
        """
        error_lower = error_message.lower()
        
        # Check configuration patterns first
        config_patterns = self._error_config.get("patterns", {})
        for error_type, patterns in config_patterns.items():
            if any(pattern.lower() in error_lower for pattern in patterns):
                return error_type
        
        # Fall back to built-in patterns
        for error_type, patterns in ErrorDecoderConstants.ERROR_PATTERNS.items():
            if any(pattern in error_lower for pattern in patterns):
                return error_type
        
        return "unknown"
    
    def _generate_plain_english_explanation(self, error_message: str, error_type: str) -> str:
        """Generate a plain English explanation of the error.
        
        Args:
            error_message: The original error message
            error_type: The classified error type
            
        Returns:
            Plain English explanation
        """
        # Check configuration explanations first
        config_explanations = self._error_config.get("explanations", {})
        base_explanation = config_explanations.get(
            error_type, 
            ErrorDecoderConstants.ERROR_EXPLANATIONS.get(
                error_type, ErrorDecoderConstants.ERROR_EXPLANATIONS["unknown"]
            )
        )
        
        # Add field-specific hints
        error_lower = error_message.lower()
        for field, hint in ErrorDecoderConstants.FIELD_ERROR_HINTS.items():
            if field in error_lower:
                base_explanation += hint
                break
        
        return base_explanation
    
    def _generate_error_solutions(self, error_message: str, error_type: str) -> List[ErrorSolution]:
        """Generate specific solutions for the error.
        
        Args:
            error_message: The original error message
            error_type: The classified error type
            
        Returns:
            List of ErrorSolution objects
        """
        solutions = []
        
        # Check for configuration solutions first
        config_solutions = self._error_config.get("solutions", {}).get(error_type, [])
        for solution_data in config_solutions:
            solution = ErrorSolution(
                problem=solution_data.get("problem", ""),
                solution=solution_data.get("solution", ""),
                code_example=solution_data.get("code_example"),
                documentation_link=solution_data.get("documentation_link")
            )
            solutions.append(solution)
        
        # Add built-in solutions if no config solutions found
        if not solutions:
            solutions.extend(self._get_builtin_solutions(error_message, error_type))
        
        # Add field-specific solutions
        solutions.extend(self._get_field_specific_solutions(error_message))
        
        # Add general solution if no specific ones found
        if not solutions:
            solutions.append(ErrorSolution(
                problem="General error",
                solution="Check the Healthie API documentation for more details about this error",
                documentation_link="https://docs.gethealthie.com/"
            ))
        
        return solutions
    
    def _get_builtin_solutions(self, error_message: str, error_type: str) -> List[ErrorSolution]:
        """Get built-in solutions for common error types.
        
        Args:
            error_message: The original error message
            error_type: The classified error type
            
        Returns:
            List of built-in ErrorSolution objects
        """
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
            solutions.append(ErrorSolution(
                problem="Too many requests",
                solution="Implement exponential backoff retry logic",
                code_example="""// Retry with exponential backoff
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
            ))
        
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
        
        return solutions
    
    def _get_field_specific_solutions(self, error_message: str) -> List[ErrorSolution]:
        """Get solutions specific to field validation errors.
        
        Args:
            error_message: The original error message
            
        Returns:
            List of field-specific ErrorSolution objects
        """
        solutions = []
        error_lower = error_message.lower()
        
        if "email" in error_lower and "invalid" in error_lower:
            solutions.append(ErrorSolution(
                problem="Invalid email format",
                solution="Ensure email addresses follow the format user@domain.com",
                code_example='"email": "patient@example.com"'
            ))
        
        if "phone" in error_lower and "invalid" in error_lower:
            solutions.append(ErrorSolution(
                problem="Invalid phone number format",
                solution="Use international format with country code",
                code_example='"phone": "+1234567890"'
            ))
        
        if "required" in error_lower:
            solutions.append(ErrorSolution(
                problem="Missing required fields",
                solution="Check the API documentation for required fields and include them in your request",
                code_example="Ensure all fields marked with '!' in the schema are provided"
            ))
        
        return solutions
    
    def _is_healthcare_specific(self, error_message: str) -> bool:
        """Check if the error is healthcare-specific.
        
        Args:
            error_message: The error message to check
            
        Returns:
            True if healthcare-specific, False otherwise
        """
        error_lower = error_message.lower()
        return any(term in error_lower for term in ErrorDecoderConstants.HEALTHCARE_TERMS)
    
    def _generate_compliance_notes(self, error_message: str, error_type: str) -> str:
        """Generate healthcare compliance notes for the error.
        
        Args:
            error_message: The original error message
            error_type: The classified error type
            
        Returns:
            Compliance notes string
        """
        # Check configuration compliance notes first
        config_compliance = self._error_config.get("compliance_notes", {})
        if error_type in config_compliance:
            return config_compliance[error_type]
        
        # Built-in compliance notes
        if error_type == "authorization":
            return ("HIPAA Compliance: Ensure your application properly restricts access to patient data "
                   "based on user roles and permissions. Only authorized personnel should access PHI "
                   "(Protected Health Information).")
        
        elif error_type == "validation" and "patient" in error_message.lower():
            return ("Healthcare Data Quality: Patient data validation errors can impact care quality. "
                   "Ensure all patient information is accurate and complete before submission.")
        
        elif "phi" in error_message.lower() or "hipaa" in error_message.lower():
            return ("HIPAA Violation Risk: This error may indicate a potential violation of HIPAA privacy rules. "
                   "Review your data handling practices and ensure proper access controls are in place.")
        
        else:
            return ("Healthcare Best Practice: When handling healthcare data, always implement proper error "
                   "handling, logging (without exposing PHI), and user notification procedures.")


def setup_error_decoder_tool(mcp, schema_manager: SchemaManagerProtocol):
    """Setup the error decoder tool."""
    tool = ErrorDecoderTool(schema_manager)

    @mcp.tool(name=tool.get_tool_name())
    def error_decoder(
        error_message: str,
        include_compliance_notes: bool = True
    ) -> dict:
        """Decode Healthie API error messages into plain English with actionable solutions.
        
        This tool helps external developers understand API errors and provides
        specific solutions for common integration issues.
        
        Args:
            error_message: The error message from the Healthie API
            include_compliance_notes: Whether to include healthcare compliance guidance
                     
        Returns:
            ErrorDecodeResult with plain English explanation and solutions
        """
        input_data = ErrorDecoderInput(
            error_message=error_message,
            include_compliance_notes=include_compliance_notes
        )

        result = tool.execute(input_data)
        return result.model_dump()

