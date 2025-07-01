"""Input validation helper tool for external developers.

This tool validates GraphQL mutation inputs against schema requirements
and healthcare best practices, helping developers catch errors before
making API calls.
"""

import re
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field

from ..models.external_dev_tools import (
    InputValidationResult, ValidationIssue
)
from ..base import BaseTool, SchemaManagerProtocol
from ..config.loader import get_config_loader
from ..exceptions import ToolError


class ValidationConstants:
    """Constants for input validation tool."""
    
    # Validation issue types
    ISSUE_REQUIRED = "required"
    ISSUE_UNKNOWN_FIELD = "unknown_field"
    ISSUE_INVALID_TYPE = "invalid_type"
    ISSUE_HEALTHCARE_SPECIFIC = "healthcare_specific"
    
    # Severity levels
    SEVERITY_ERROR = "error"
    SEVERITY_WARNING = "warning"
    
    # Scalar types
    SCALAR_TYPES = {
        'String', 'Int', 'Float', 'Boolean', 'ID', 'Date', 'DateTime',
        'Time', 'JSON', 'Upload', 'BigInt', 'Decimal'
    }
    
    # Type validators
    TYPE_VALIDATORS = {
        'String': lambda v: isinstance(v, str),
        'Int': lambda v: isinstance(v, int),
        'Float': lambda v: isinstance(v, (int, float)),
        'Boolean': lambda v: isinstance(v, bool),
        'ID': lambda v: isinstance(v, (str, int)),
        'JSON': lambda v: True,  # JSON can be any valid JSON value
    }
    
    # Healthcare field patterns
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PHONE_PATTERN = r'^(\+?1[-\s]?)?(\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4})$'
    DATE_PATTERN = r'^\d{4}-\d{2}-\d{2}$'
    DATETIME_PATTERN = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$'
    
    # Healthcare field identifiers
    EMAIL_FIELDS = {'email'}
    PHONE_FIELDS = {'phone', 'telephone', 'mobile'}
    DATE_BIRTH_FIELDS = {'dateofbirth', 'birthdate', 'dob'}
    MRN_FIELDS = {'mrn', 'medicalnumber', 'recordnumber'}
    
    # Date format
    DATE_FORMAT = '%Y-%m-%d'
    
    # Minimum lengths
    MIN_MRN_LENGTH = 3
    
    # Validation suggestions
    SUGGESTIONS_BY_MUTATION = {
        'create': "For create operations, ensure all required fields are provided",
        'patient': "Patient data should include email and phone for communication",
        'client': "Patient data should include email and phone for communication",
        'appointment': "Verify appointment time conflicts before creating"
    }
    
    # Field-specific suggestions
    FIELD_SUGGESTIONS = {
        'email': "Valid email addresses are required for patient communications",
        'phone': "Include country code in phone numbers for SMS notifications"
    }


class InputValidationInput(BaseModel):
    """Input parameters for input validation."""
    
    mutation_name: str = Field(
        description="Name of the GraphQL mutation to validate against"
    )
    
    input_data: Dict[str, Any] = Field(
        description="The input data object to validate"
    )
    
    strict_mode: bool = Field(
        False,
        description="Enable strict validation including healthcare-specific rules"
    )


class InputValidationTool(BaseTool[InputValidationResult]):
    """Tool for validating GraphQL mutation inputs against schema and healthcare rules."""
    
    def __init__(self, schema_manager: SchemaManagerProtocol):
        """Initialize the tool.
        
        Args:
            schema_manager: Schema manager instance for accessing GraphQL schema
        """
        super().__init__(schema_manager)
        self.config_loader = get_config_loader()
    
    def get_tool_name(self) -> str:
        """Get the tool name."""
        return "validate_mutation_input"
    
    def get_tool_description(self) -> str:
        """Get the tool description."""
        return "Validate GraphQL mutation input against schema requirements and healthcare best practices"
    
    def execute(
        self,
        mutation_name: str,
        input_data: Dict[str, Any],
        strict_mode: bool = False
    ) -> InputValidationResult:
        """Validate GraphQL mutation input against schema requirements.
        
        Args:
            mutation_name: Name of the GraphQL mutation to validate against
            input_data: The input data object to validate
            strict_mode: Enable strict validation including healthcare-specific rules
                     
        Returns:
            InputValidationResult with validation issues and suggestions
        """
        try:
            # Validate inputs
            if not mutation_name:
                return InputValidationResult(
                    is_valid=False,
                    issues=[],
                    total_errors=0,
                    total_warnings=0,
                    suggestions=[],
                    error="Mutation name is required"
                )
            if not isinstance(input_data, dict):
                return InputValidationResult(
                    is_valid=False,
                    issues=[],
                    total_errors=0,
                    total_warnings=0,
                    suggestions=[],
                    error="Input data must be a dictionary"
                )
            
            schema_content = self.schema_manager.get_schema_content()
            if not schema_content:
                return InputValidationResult(
                    is_valid=False,
                    issues=[],
                    total_errors=0,
                    total_warnings=0,
                    suggestions=[],
                    error="Schema not available. Please check your configuration."
                )
            
            # Find mutation definition
            mutation_def = self._find_mutation_definition(schema_content, mutation_name)
            if not mutation_def:
                return InputValidationResult(
                    is_valid=False,
                    issues=[],
                    total_errors=0,
                    total_warnings=0,
                    suggestions=[],
                    error=f"Mutation '{mutation_name}' not found in schema"
                )
            
            # Validate input against mutation definition
            issues = self._validate_input_data(input_data, mutation_def, schema_content, strict_mode)
            
            # Generate suggestions
            suggestions = self._generate_validation_suggestions(issues, mutation_name, input_data)
            
            # Count issues by severity
            errors = [issue for issue in issues if issue.severity == ValidationConstants.SEVERITY_ERROR]
            warnings = [issue for issue in issues if issue.severity == ValidationConstants.SEVERITY_WARNING]
            
            return InputValidationResult(
                is_valid=len(errors) == 0,
                issues=issues,
                total_errors=len(errors),
                total_warnings=len(warnings),
                suggestions=suggestions
            )
            
        except Exception as e:
            return InputValidationResult(
                is_valid=False,
                issues=[],
                total_errors=0,
                total_warnings=0,
                suggestions=[],
                error=f"Error validating mutation input: {str(e)}"
            )

    def _find_mutation_definition(self, schema_content: str, mutation_name: str) -> Optional[Dict[str, Any]]:
        """Find the definition of a specific mutation in the schema."""
        lines = schema_content.split('\n')
        in_mutation_type = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Check if we're entering the Mutation type
            if re.match(r'type\s+Mutation\s*{', line):
                in_mutation_type = True
                continue
            
            # Check if we're leaving the Mutation type
            if in_mutation_type and line == '}':
                break
            
            # Look for the specific mutation
            if in_mutation_type:
                mutation_match = re.match(rf'\s*{re.escape(mutation_name)}\s*\(([^)]*)\)\s*:\s*(.+)', line)
                if mutation_match:
                    args_str = mutation_match.group(1)
                    return_type = mutation_match.group(2)
                    
                    # Parse arguments
                    args = self._parse_mutation_arguments(args_str)
                    
                    return {
                        'name': mutation_name,
                        'arguments': args,
                        'return_type': return_type.strip(),
                        'line_number': i + 1
                    }
        
        return None

    def _parse_mutation_arguments(self, args_str: str) -> List[Dict[str, Any]]:
        """Parse mutation arguments string into structured data."""
        if not args_str.strip():
            return []
        
        args = []
        # Simple argument parsing - handles basic cases
        arg_parts = re.split(r',\s*(?=\w+\s*:)', args_str)
        
        for arg_part in arg_parts:
            arg_match = re.match(r'(\w+)\s*:\s*(.+)', arg_part.strip())
            if arg_match:
                arg_name = arg_match.group(1)
                arg_type = arg_match.group(2).strip()
                
                args.append({
                    'name': arg_name,
                    'type': arg_type,
                    'required': arg_type.endswith('!'),
                    'is_input_type': not self._is_scalar_type(arg_type.rstrip('!'))
                })
        
        return args

    def _validate_input_data(
        self,
        input_data: Dict[str, Any], 
        mutation_def: Dict[str, Any], 
        schema_content: str, 
        strict_mode: bool
    ) -> List[ValidationIssue]:
        """Validate input data against mutation definition."""
        issues = []
        
        # Check for required arguments
        for arg in mutation_def['arguments']:
            if arg['required'] and arg['name'] not in input_data:
                issues.append(ValidationIssue(
                    field_path=arg['name'],
                    issue_type=ValidationConstants.ISSUE_REQUIRED,
                    message=f"Required argument '{arg['name']}' is missing",
                    severity=ValidationConstants.SEVERITY_ERROR,
                    suggestion=f"Add '{arg['name']}' to your input data"
                ))
        
        # Validate each provided input
        for field_name, field_value in input_data.items():
            arg_def = next((arg for arg in mutation_def['arguments'] if arg['name'] == field_name), None)
            
            if not arg_def:
                issues.append(ValidationIssue(
                    field_path=field_name,
                    issue_type=ValidationConstants.ISSUE_UNKNOWN_FIELD,
                    message=f"Unknown argument '{field_name}' for mutation '{mutation_def['name']}'",
                    severity=ValidationConstants.SEVERITY_WARNING,
                    suggestion=f"Remove '{field_name}' or check the mutation definition"
                ))
                continue
            
            # Validate input type structure
            if arg_def['is_input_type']:
                input_type_issues = self._validate_input_type(
                    field_value, arg_def['type'], field_name, schema_content, strict_mode
                )
                issues.extend(input_type_issues)
            else:
                # Validate scalar type
                scalar_issues = self._validate_scalar_value(field_value, arg_def['type'], field_name)
                issues.extend(scalar_issues)
        
        return issues

    def _validate_input_type(
        self,
        input_value: Any, 
        input_type: str, 
        field_path: str, 
        schema_content: str, 
        strict_mode: bool
    ) -> List[ValidationIssue]:
        """Validate input against a specific input type definition."""
        issues = []
        
        if not isinstance(input_value, dict):
            issues.append(ValidationIssue(
                field_path=field_path,
                issue_type=ValidationConstants.ISSUE_INVALID_TYPE,
                message=f"Expected object for input type '{input_type}', got {type(input_value).__name__}",
                severity=ValidationConstants.SEVERITY_ERROR
            ))
            return issues
        
        # Find input type definition
        input_type_def = self._find_input_type_definition(schema_content, input_type.rstrip('!'))
        if not input_type_def:
            return issues
        
        # Validate required fields
        for field_def in input_type_def['fields']:
            field_name = field_def['name']
            full_path = f"{field_path}.{field_name}"
            
            if field_def['required'] and field_name not in input_value:
                issues.append(ValidationIssue(
                    field_path=full_path,
                    issue_type=ValidationConstants.ISSUE_REQUIRED,
                    message=f"Required field '{field_name}' is missing",
                    severity=ValidationConstants.SEVERITY_ERROR,
                    suggestion=f"Add '{field_name}' to your input object"
                ))
        
        # Validate provided fields
        for field_name, field_value in input_value.items():
            field_def = next((f for f in input_type_def['fields'] if f['name'] == field_name), None)
            full_path = f"{field_path}.{field_name}"
            
            if not field_def:
                issues.append(ValidationIssue(
                    field_path=full_path,
                    issue_type=ValidationConstants.ISSUE_UNKNOWN_FIELD,
                    message=f"Unknown field '{field_name}' in input type '{input_type}'",
                    severity=ValidationConstants.SEVERITY_WARNING
                ))
                continue
            
            # Validate field value
            if self._is_scalar_type(field_def['type']):
                scalar_issues = self._validate_scalar_value(field_value, field_def['type'], full_path)
                issues.extend(scalar_issues)
            
            # Healthcare-specific validation
            if strict_mode:
                healthcare_issues = self._validate_healthcare_specific(field_name, field_value, full_path)
                issues.extend(healthcare_issues)
        
        return issues

    def _find_input_type_definition(self, schema_content: str, input_type: str) -> Optional[Dict[str, Any]]:
        """Find the definition of a specific input type."""
        lines = schema_content.split('\n')
        in_input_type = False
        fields = []
        
        for line in lines:
            line = line.strip()
            
            # Check if we're entering the target input type
            if re.match(rf'input\s+{re.escape(input_type)}\s*{{', line):
                in_input_type = True
                continue
            
            # Check if we're leaving the input type
            if in_input_type and line == '}':
                break
            
            # Extract field if we're in the input type
            if in_input_type and line and not line.startswith('#'):
                field_match = re.match(r'\s*(\w+)\s*:\s*(.+)', line)
                if field_match:
                    field_name = field_match.group(1)
                    field_type = field_match.group(2).strip()
                    
                    fields.append({
                        'name': field_name,
                        'type': field_type,
                        'required': field_type.endswith('!')
                    })
        
        return {'name': input_type, 'fields': fields} if fields else None

    def _validate_scalar_value(self, value: Any, scalar_type: str, field_path: str) -> List[ValidationIssue]:
        """Validate a scalar value against its expected type."""
        issues = []
        base_type = scalar_type.rstrip('!')
        
        # Create type validators with custom date/datetime validation
        type_validators = dict(ValidationConstants.TYPE_VALIDATORS)
        type_validators.update({
            'Date': lambda v: isinstance(v, str) and self._is_valid_date(v),
            'DateTime': lambda v: isinstance(v, str) and self._is_valid_datetime(v),
        })
        
        validator = type_validators.get(base_type)
        if validator and not validator(value):
            issues.append(ValidationIssue(
                field_path=field_path,
                issue_type=ValidationConstants.ISSUE_INVALID_TYPE,
                message=f"Expected {base_type}, got {type(value).__name__}",
                severity=ValidationConstants.SEVERITY_ERROR,
                suggestion=f"Convert value to {base_type} type"
            ))
        
        return issues

    def _validate_healthcare_specific(self, field_name: str, field_value: Any, field_path: str) -> List[ValidationIssue]:
        """Validate healthcare-specific field requirements."""
        issues = []
        field_lower = field_name.lower()
        
        # Email validation
        if any(email_field in field_lower for email_field in ValidationConstants.EMAIL_FIELDS):
            if isinstance(field_value, str) and not self._is_valid_email(field_value):
                issues.append(ValidationIssue(
                    field_path=field_path,
                    issue_type=ValidationConstants.ISSUE_HEALTHCARE_SPECIFIC,
                    message="Invalid email format",
                    severity=ValidationConstants.SEVERITY_ERROR,
                    suggestion="Provide a valid email address (required for patient communications)"
                ))
        
        # Phone number validation
        if any(phone_field in field_lower for phone_field in ValidationConstants.PHONE_FIELDS):
            if isinstance(field_value, str) and not self._is_valid_phone(field_value):
                issues.append(ValidationIssue(
                    field_path=field_path,
                    issue_type=ValidationConstants.ISSUE_HEALTHCARE_SPECIFIC,
                    message="Phone number should include country code",
                    severity=ValidationConstants.SEVERITY_WARNING,
                    suggestion="Format: +1234567890 (required for appointment reminders)"
                ))
        
        # Date of birth validation
        if any(dob_field in field_lower.replace('_', '') for dob_field in ValidationConstants.DATE_BIRTH_FIELDS):
            if isinstance(field_value, str):
                if not self._is_valid_date(field_value):
                    issues.append(ValidationIssue(
                        field_path=field_path,
                        issue_type=ValidationConstants.ISSUE_HEALTHCARE_SPECIFIC,
                        message="Invalid date format for date of birth",
                        severity=ValidationConstants.SEVERITY_ERROR,
                        suggestion="Use YYYY-MM-DD format"
                    ))
                elif self._is_future_date(field_value):
                    issues.append(ValidationIssue(
                        field_path=field_path,
                        issue_type=ValidationConstants.ISSUE_HEALTHCARE_SPECIFIC,
                        message="Date of birth cannot be in the future",
                        severity=ValidationConstants.SEVERITY_ERROR,
                        suggestion="Provide a valid past date"
                    ))
        
        # Medical record number validation
        if any(mrn_field in field_lower.replace('_', '') for mrn_field in ValidationConstants.MRN_FIELDS):
            if not isinstance(field_value, str) or len(field_value) < ValidationConstants.MIN_MRN_LENGTH:
                issues.append(ValidationIssue(
                    field_path=field_path,
                    issue_type=ValidationConstants.ISSUE_HEALTHCARE_SPECIFIC,
                    message=f"Medical record number should be at least {ValidationConstants.MIN_MRN_LENGTH} characters",
                    severity=ValidationConstants.SEVERITY_WARNING,
                    suggestion="Provide a valid medical record number"
                ))
        
        return issues

    def _is_scalar_type(self, type_name: str) -> bool:
        """Check if a type is a GraphQL scalar."""
        return type_name.rstrip('![]') in ValidationConstants.SCALAR_TYPES
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format."""
        return re.match(ValidationConstants.EMAIL_PATTERN, email) is not None
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Validate phone number format."""
        return re.match(ValidationConstants.PHONE_PATTERN, phone) is not None
    
    def _is_valid_date(self, date_str: str) -> bool:
        """Validate date format (YYYY-MM-DD)."""
        return re.match(ValidationConstants.DATE_PATTERN, date_str) is not None
    
    def _is_valid_datetime(self, datetime_str: str) -> bool:
        """Validate datetime format (ISO 8601)."""
        return re.match(ValidationConstants.DATETIME_PATTERN, datetime_str) is not None
    
    def _is_future_date(self, date_str: str) -> bool:
        """Check if date is in the future."""
        try:
            date_obj = datetime.strptime(date_str, ValidationConstants.DATE_FORMAT)
            return date_obj > datetime.now()
        except ValueError:
            return False
    
    def _generate_validation_suggestions(
        self,
        issues: List[ValidationIssue], 
        mutation_name: str, 
        input_data: Dict[str, Any]
    ) -> List[str]:
        """Generate helpful suggestions based on validation issues."""
        suggestions = []
        
        # Count issues by severity
        error_count = len([i for i in issues if i.severity == ValidationConstants.SEVERITY_ERROR])
        warning_count = len([i for i in issues if i.severity == ValidationConstants.SEVERITY_WARNING])
        
        if error_count > 0:
            suggestions.append(f"Fix {error_count} error(s) before submitting the mutation")
        
        if warning_count > 0:
            suggestions.append(f"Consider addressing {warning_count} warning(s) for better data quality")
        
        # Add mutation-specific suggestions
        mutation_lower = mutation_name.lower()
        for keyword, suggestion in ValidationConstants.SUGGESTIONS_BY_MUTATION.items():
            if keyword in mutation_lower:
                suggestions.append(suggestion)
        
        # Add field-specific suggestions
        for field_keyword, suggestion in ValidationConstants.FIELD_SUGGESTIONS.items():
            if any(field_keyword in issue.field_path for issue in issues):
                suggestions.append(suggestion)
        
        return suggestions[:5]  # Limit to 5 suggestions


def setup_input_validation_tool(mcp, schema_manager) -> None:
    """Setup the input validation helper tool with the MCP server."""
    tool = InputValidationTool(schema_manager)
    
    @mcp.tool()
    def validate_mutation_input(
        mutation_name: str,
        input_data: Dict[str, Any],
        strict_mode: bool = False
    ) -> InputValidationResult:
        """Validate GraphQL mutation input against schema requirements and healthcare best practices.
        
        This tool helps external developers validate their mutation inputs before making
        API calls, reducing failed requests and improving data quality.
        
        Args:
            mutation_name: Name of the GraphQL mutation to validate against
            input_data: The input data object to validate
            strict_mode: Enable strict validation including healthcare-specific rules
                     
        Returns:
            InputValidationResult with validation issues and suggestions
        """
        return tool.execute(
            mutation_name=mutation_name,
            input_data=input_data,
            strict_mode=strict_mode
        )