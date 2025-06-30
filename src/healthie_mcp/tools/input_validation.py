"""Input validation helper tool for external developers."""

import re
import json
from typing import Optional, Dict, Any, List
from mcp.server.fastmcp import FastMCP
from ..models.external_dev_tools import (
    InputValidationResult, ValidationIssue
)


def setup_input_validation_tool(mcp: FastMCP, schema_manager) -> None:
    """Setup the input validation helper tool with the MCP server."""
    
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
        try:
            schema_content = schema_manager.get_schema_content()
            if not schema_content:
                raise ValueError("Schema not available. Please check your configuration.")
            
            # Find mutation definition
            mutation_def = _find_mutation_definition(schema_content, mutation_name)
            if not mutation_def:
                raise ValueError(f"Mutation '{mutation_name}' not found in schema")
            
            # Validate input against mutation definition
            issues = _validate_input_data(input_data, mutation_def, schema_content, strict_mode)
            
            # Generate suggestions
            suggestions = _generate_validation_suggestions(issues, mutation_name, input_data)
            
            # Count issues by severity
            errors = [issue for issue in issues if issue.severity == "error"]
            warnings = [issue for issue in issues if issue.severity == "warning"]
            
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


def _find_mutation_definition(schema_content: str, mutation_name: str) -> Optional[Dict[str, Any]]:
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
                args = _parse_mutation_arguments(args_str)
                
                return {
                    'name': mutation_name,
                    'arguments': args,
                    'return_type': return_type.strip(),
                    'line_number': i + 1
                }
    
    return None


def _parse_mutation_arguments(args_str: str) -> List[Dict[str, Any]]:
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
                'is_input_type': not _is_scalar_type(arg_type.rstrip('!'))
            })
    
    return args


def _validate_input_data(
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
                issue_type="required",
                message=f"Required argument '{arg['name']}' is missing",
                severity="error",
                suggestion=f"Add '{arg['name']}' to your input data"
            ))
    
    # Validate each provided input
    for field_name, field_value in input_data.items():
        arg_def = next((arg for arg in mutation_def['arguments'] if arg['name'] == field_name), None)
        
        if not arg_def:
            issues.append(ValidationIssue(
                field_path=field_name,
                issue_type="unknown_field",
                message=f"Unknown argument '{field_name}' for mutation '{mutation_def['name']}'",
                severity="warning",
                suggestion=f"Remove '{field_name}' or check the mutation definition"
            ))
            continue
        
        # Validate input type structure
        if arg_def['is_input_type']:
            input_type_issues = _validate_input_type(
                field_value, arg_def['type'], field_name, schema_content, strict_mode
            )
            issues.extend(input_type_issues)
        else:
            # Validate scalar type
            scalar_issues = _validate_scalar_value(field_value, arg_def['type'], field_name)
            issues.extend(scalar_issues)
    
    return issues


def _validate_input_type(
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
            issue_type="invalid_type",
            message=f"Expected object for input type '{input_type}', got {type(input_value).__name__}",
            severity="error"
        ))
        return issues
    
    # Find input type definition
    input_type_def = _find_input_type_definition(schema_content, input_type.rstrip('!'))
    if not input_type_def:
        return issues
    
    # Validate required fields
    for field_def in input_type_def['fields']:
        field_name = field_def['name']
        full_path = f"{field_path}.{field_name}"
        
        if field_def['required'] and field_name not in input_value:
            issues.append(ValidationIssue(
                field_path=full_path,
                issue_type="required",
                message=f"Required field '{field_name}' is missing",
                severity="error",
                suggestion=f"Add '{field_name}' to your input object"
            ))
    
    # Validate provided fields
    for field_name, field_value in input_value.items():
        field_def = next((f for f in input_type_def['fields'] if f['name'] == field_name), None)
        full_path = f"{field_path}.{field_name}"
        
        if not field_def:
            issues.append(ValidationIssue(
                field_path=full_path,
                issue_type="unknown_field",
                message=f"Unknown field '{field_name}' in input type '{input_type}'",
                severity="warning"
            ))
            continue
        
        # Validate field value
        if _is_scalar_type(field_def['type']):
            scalar_issues = _validate_scalar_value(field_value, field_def['type'], full_path)
            issues.extend(scalar_issues)
        
        # Healthcare-specific validation
        if strict_mode:
            healthcare_issues = _validate_healthcare_specific(field_name, field_value, full_path)
            issues.extend(healthcare_issues)
    
    return issues


def _find_input_type_definition(schema_content: str, input_type: str) -> Optional[Dict[str, Any]]:
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


def _validate_scalar_value(value: Any, scalar_type: str, field_path: str) -> List[ValidationIssue]:
    """Validate a scalar value against its expected type."""
    issues = []
    base_type = scalar_type.rstrip('!')
    
    type_validators = {
        'String': lambda v: isinstance(v, str),
        'Int': lambda v: isinstance(v, int),
        'Float': lambda v: isinstance(v, (int, float)),
        'Boolean': lambda v: isinstance(v, bool),
        'ID': lambda v: isinstance(v, (str, int)),
        'Date': lambda v: isinstance(v, str) and _is_valid_date(v),
        'DateTime': lambda v: isinstance(v, str) and _is_valid_datetime(v),
        'JSON': lambda v: True,  # JSON can be any valid JSON value
    }
    
    validator = type_validators.get(base_type)
    if validator and not validator(value):
        issues.append(ValidationIssue(
            field_path=field_path,
            issue_type="invalid_type",
            message=f"Expected {base_type}, got {type(value).__name__}",
            severity="error",
            suggestion=f"Convert value to {base_type} type"
        ))
    
    return issues


def _validate_healthcare_specific(field_name: str, field_value: Any, field_path: str) -> List[ValidationIssue]:
    """Validate healthcare-specific field requirements."""
    issues = []
    field_lower = field_name.lower()
    
    # Email validation for healthcare
    if 'email' in field_lower and isinstance(field_value, str):
        if not _is_valid_email(field_value):
            issues.append(ValidationIssue(
                field_path=field_path,
                issue_type="healthcare_specific",
                message="Invalid email format",
                severity="error",
                suggestion="Provide a valid email address (required for patient communications)"
            ))
    
    # Phone number validation
    if 'phone' in field_lower and isinstance(field_value, str):
        if not _is_valid_phone(field_value):
            issues.append(ValidationIssue(
                field_path=field_path,
                issue_type="healthcare_specific",
                message="Phone number should include country code",
                severity="warning",
                suggestion="Format: +1234567890 (required for appointment reminders)"
            ))
    
    # Date of birth validation
    if 'dateofbirth' in field_lower.replace('_', '') and isinstance(field_value, str):
        if not _is_valid_date(field_value):
            issues.append(ValidationIssue(
                field_path=field_path,
                issue_type="healthcare_specific",
                message="Invalid date format for date of birth",
                severity="error",
                suggestion="Use YYYY-MM-DD format"
            ))
        elif _is_future_date(field_value):
            issues.append(ValidationIssue(
                field_path=field_path,
                issue_type="healthcare_specific",
                message="Date of birth cannot be in the future",
                severity="error",
                suggestion="Provide a valid past date"
            ))
    
    # Medical record number validation
    if 'mrn' in field_lower or 'medicalnumber' in field_lower.replace('_', ''):
        if not isinstance(field_value, str) or len(field_value) < 3:
            issues.append(ValidationIssue(
                field_path=field_path,
                issue_type="healthcare_specific",
                message="Medical record number should be at least 3 characters",
                severity="warning",
                suggestion="Provide a valid medical record number"
            ))
    
    return issues


def _is_scalar_type(type_name: str) -> bool:
    """Check if a type is a GraphQL scalar."""
    scalar_types = {
        'String', 'Int', 'Float', 'Boolean', 'ID', 'Date', 'DateTime', 
        'Time', 'JSON', 'Upload', 'BigInt', 'Decimal'
    }
    return type_name.rstrip('![]') in scalar_types


def _is_valid_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def _is_valid_phone(phone: str) -> bool:
    """Validate phone number format."""
    # Allow various phone formats but prefer international format
    pattern = r'^(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$'
    return re.match(pattern, phone) is not None


def _is_valid_date(date_str: str) -> bool:
    """Validate date format (YYYY-MM-DD)."""
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    return re.match(pattern, date_str) is not None


def _is_valid_datetime(datetime_str: str) -> bool:
    """Validate datetime format (ISO 8601)."""
    pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$'
    return re.match(pattern, datetime_str) is not None


def _is_future_date(date_str: str) -> bool:
    """Check if date is in the future."""
    try:
        from datetime import datetime
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj > datetime.now()
    except ValueError:
        return False


def _generate_validation_suggestions(
    issues: List[ValidationIssue], 
    mutation_name: str, 
    input_data: Dict[str, Any]
) -> List[str]:
    """Generate helpful suggestions based on validation issues."""
    suggestions = []
    
    # Count issues by type
    error_count = len([i for i in issues if i.severity == "error"])
    warning_count = len([i for i in issues if i.severity == "warning"])
    
    if error_count > 0:
        suggestions.append(f"Fix {error_count} error(s) before submitting the mutation")
    
    if warning_count > 0:
        suggestions.append(f"Consider addressing {warning_count} warning(s) for better data quality")
    
    # Mutation-specific suggestions
    if 'create' in mutation_name.lower():
        suggestions.append("For create operations, ensure all required fields are provided")
    
    if 'patient' in mutation_name.lower() or 'client' in mutation_name.lower():
        suggestions.append("Patient data should include email and phone for communication")
    
    if 'appointment' in mutation_name.lower():
        suggestions.append("Verify appointment time conflicts before creating")
    
    # Field-specific suggestions
    if any('email' in issue.field_path for issue in issues):
        suggestions.append("Valid email addresses are required for patient communications")
    
    if any('phone' in issue.field_path for issue in issues):
        suggestions.append("Include country code in phone numbers for SMS notifications")
    
    return suggestions[:5]  # Limit to 5 suggestions