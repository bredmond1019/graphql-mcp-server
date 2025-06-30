"""Validation utility functions."""

import re
from datetime import datetime
from typing import Optional
from ..constants import EMAIL_REGEX, PHONE_REGEX, DATE_FORMAT, DATETIME_FORMAT


def validate_email(email: str) -> bool:
    """Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email format, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    return re.match(EMAIL_REGEX, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number format (supports US numbers).
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid phone format, False otherwise
    """
    if not phone or not isinstance(phone, str):
        return False
    return re.match(PHONE_REGEX, phone) is not None


def validate_date(date_str: str) -> bool:
    """Validate date format (YYYY-MM-DD).
    
    Args:
        date_str: Date string to validate
        
    Returns:
        True if valid date format, False otherwise
    """
    if not date_str or not isinstance(date_str, str):
        return False
    
    try:
        datetime.strptime(date_str, DATE_FORMAT)
        return True
    except ValueError:
        return False


def validate_datetime(datetime_str: str) -> bool:
    """Validate datetime format (ISO 8601).
    
    Args:
        datetime_str: Datetime string to validate
        
    Returns:
        True if valid datetime format, False otherwise
    """
    if not datetime_str or not isinstance(datetime_str, str):
        return False
    
    # Support various ISO 8601 formats
    formats = [
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%S.%fZ'
    ]
    
    for fmt in formats:
        try:
            datetime.strptime(datetime_str.replace('Z', ''), fmt.replace('Z', ''))
            return True
        except ValueError:
            continue
    
    return False


def is_future_date(date_str: str) -> bool:
    """Check if a date is in the future.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        True if date is in the future, False otherwise
    """
    try:
        date_obj = datetime.strptime(date_str, DATE_FORMAT).date()
        return date_obj > datetime.now().date()
    except ValueError:
        return False


def validate_required_fields(data: dict, required_fields: list[str]) -> list[str]:
    """Validate that all required fields are present in data.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        
    Returns:
        List of missing field names
    """
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
    return missing_fields


def validate_field_types(data: dict, field_types: dict[str, type]) -> list[tuple[str, str]]:
    """Validate that fields have the correct types.
    
    Args:
        data: Dictionary to validate
        field_types: Dictionary mapping field names to expected types
        
    Returns:
        List of (field_name, error_message) tuples for invalid fields
    """
    errors = []
    for field, expected_type in field_types.items():
        if field in data and data[field] is not None:
            if not isinstance(data[field], expected_type):
                actual_type = type(data[field]).__name__
                expected_type_name = expected_type.__name__
                errors.append((field, f"Expected {expected_type_name}, got {actual_type}"))
    return errors


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """Sanitize a string value for safe use.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return str(value)
    
    # Remove control characters
    sanitized = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
    
    # Trim whitespace
    sanitized = sanitized.strip()
    
    # Truncate if needed
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized