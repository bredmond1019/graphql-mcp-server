"""
Healthie GraphQL Client for Python Applications

What it demonstrates:
- Complete Python client for Healthie GraphQL API
- Authentication and error handling
- Healthcare-specific data validation
- HIPAA-compliant logging and error handling
- Async and sync operation support

Healthcare considerations:
- Secure credential management
- PHI data handling best practices
- Audit logging for compliance
- Medical data validation

Prerequisites:
- requests or httpx for HTTP client
- python-dotenv for environment variables
- pydantic for data validation
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path

import httpx
import requests
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging for healthcare compliance
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('healthie_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class HealthieConfig:
    """Configuration for Healthie API client"""
    
    # API settings
    api_url: str = os.getenv('HEALTHIE_API_URL', 'https://staging-api.gethealthie.com/graphql')
    api_key: str = os.getenv('HEALTHIE_API_KEY', '')
    
    # Timeout settings
    timeout: int = 30
    max_retries: int = 3
    
    # Security settings
    verify_ssl: bool = True
    enable_audit_logging: bool = True
    
    # Performance settings
    connection_pool_size: int = 10
    keep_alive_timeout: int = 5


class PatientInput(BaseModel):
    """Patient input validation model"""
    
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    date_of_birth: str = Field(..., regex=r'^\d{4}-\d{2}-\d{2}$')
    phone_number: Optional[str] = Field(None, regex=r'^\+?1?[0-9]{10}$')
    gender: Optional[str] = Field(None, regex=r'^(male|female|other|prefer_not_to_say)$')
    
    # Address information
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = Field(None, regex=r'^[A-Z]{2}$')
    zip_code: Optional[str] = Field(None, regex=r'^[0-9]{5}(-[0-9]{4})?$')
    
    # Healthcare specific
    medical_record_number: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_member_number: Optional[str] = None
    
    # Consent and preferences
    consent_for_treatment: bool = False
    hipaa_authorization: bool = False
    
    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        """Ensure date of birth is in the past"""
        from datetime import datetime
        try:
            dob = datetime.strptime(v, '%Y-%m-%d')
            if dob >= datetime.now():
                raise ValueError('Date of birth must be in the past')
            return v
        except ValueError as e:
            raise ValueError(f'Invalid date format: {e}')
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Clean and validate phone number"""
        if v:
            # Remove all non-digit characters
            cleaned = ''.join(filter(str.isdigit, v))
            # Add country code if missing
            if len(cleaned) == 10:
                cleaned = '1' + cleaned
            elif len(cleaned) == 11 and cleaned.startswith('1'):
                pass
            else:
                raise ValueError('Phone number must be 10 digits (US format)')
            return '+' + cleaned
        return v


class AppointmentInput(BaseModel):
    """Appointment input validation model"""
    
    patient_id: str = Field(..., min_length=1)
    provider_id: str = Field(..., min_length=1)
    start_time: str = Field(..., regex=r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.*$')
    end_time: str = Field(..., regex=r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.*$')
    appointment_type: str = Field(..., min_length=1)
    notes: Optional[str] = Field(None, max_length=1000)
    
    @validator('start_time', 'end_time')
    def validate_datetime(cls, v):
        """Validate datetime format"""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError('Invalid datetime format. Use ISO 8601 format.')
    
    @validator('end_time')
    def validate_end_after_start(cls, v, values):
        """Ensure end time is after start time"""
        if 'start_time' in values:
            start = datetime.fromisoformat(values['start_time'].replace('Z', '+00:00'))
            end = datetime.fromisoformat(v.replace('Z', '+00:00'))
            if end <= start:
                raise ValueError('End time must be after start time')
        return v


class HealthieAPIError(Exception):
    """Base exception for Healthie API errors"""
    
    def __init__(self, message: str, error_code: str = None, details: Dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)


class HealthieAuthenticationError(HealthieAPIError):
    """Authentication related errors"""
    pass


class HealthieValidationError(HealthieAPIError):
    """Data validation errors"""
    pass


class HealthieClient:
    """
    Healthie GraphQL API Client
    
    Provides both sync and async methods for interacting with Healthie's GraphQL API.
    Includes healthcare-specific validation, error handling, and audit logging.
    """
    
    def __init__(self, config: HealthieConfig = None):
        self.config = config or HealthieConfig()
        self.session = None
        self.async_client = None
        
        # Audit logging setup
        if self.config.enable_audit_logging:
            self.audit_logger = logging.getLogger('healthie.audit')
            audit_handler = logging.FileHandler('healthie_audit.log')
            audit_formatter = logging.Formatter(
                '%(asctime)s - AUDIT - %(message)s'
            )
            audit_handler.setFormatter(audit_formatter)
            self.audit_logger.addHandler(audit_handler)
            self.audit_logger.setLevel(logging.INFO)
    
    def __enter__(self):
        """Context manager entry"""
        self.session = requests.Session()
        self.session.headers.update(self._get_headers())
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            self.session.close()
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.async_client = httpx.AsyncClient(
            timeout=self.config.timeout,
            verify=self.config.verify_ssl,
            limits=httpx.Limits(
                max_connections=self.config.connection_pool_size,
                max_keepalive_connections=self.config.connection_pool_size
            )
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.async_client:
            await self.async_client.aclose()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'HealthiePythonClient/1.0'
        }
        
        if self.config.api_key:
            headers['Authorization'] = f'Bearer {self.config.api_key}'
        
        return headers
    
    def _log_audit_event(self, operation: str, variables: Dict = None, user_id: str = None):
        """Log API access for HIPAA compliance"""
        if not self.config.enable_audit_logging:
            return
        
        # Sanitize variables to remove PHI
        sanitized_vars = {}
        if variables:
            for key, value in variables.items():
                if key in ['id', 'patient_id', 'provider_id']:
                    sanitized_vars[key] = 'REDACTED'
                elif isinstance(value, str) and len(value) > 50:
                    sanitized_vars[key] = 'LARGE_VALUE'
                else:
                    sanitized_vars[key] = type(value).__name__
        
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'operation': operation,
            'user_id': user_id or 'unknown',
            'variables': sanitized_vars,
            'client': 'python'
        }
        
        self.audit_logger.info(json.dumps(audit_entry))
    
    def _handle_graphql_errors(self, response_data: Dict) -> None:
        """Handle GraphQL errors from API response"""
        if 'errors' in response_data:
            errors = response_data['errors']
            error_messages = []
            
            for error in errors:
                message = error.get('message', 'Unknown error')
                extensions = error.get('extensions', {})
                error_code = extensions.get('code')
                
                # Handle specific error types
                if error_code == 'AUTHENTICATION_ERROR':
                    raise HealthieAuthenticationError(
                        message=message,
                        error_code=error_code,
                        details=extensions
                    )
                elif error_code == 'VALIDATION_ERROR':
                    raise HealthieValidationError(
                        message=message,
                        error_code=error_code,
                        details=extensions
                    )
                
                error_messages.append(message)
            
            if error_messages:
                raise HealthieAPIError(
                    message='; '.join(error_messages),
                    details={'errors': errors}
                )
    
    def execute_query(self, query: str, variables: Dict = None, user_id: str = None) -> Dict:
        """
        Execute GraphQL query (synchronous)
        
        Args:
            query: GraphQL query string
            variables: Query variables
            user_id: User ID for audit logging
            
        Returns:
            GraphQL response data
            
        Raises:
            HealthieAPIError: API errors
            HealthieAuthenticationError: Authentication errors
            HealthieValidationError: Validation errors
        """
        if not self.session:
            raise HealthieAPIError("Client not initialized. Use context manager.")
        
        # Log audit event
        self._log_audit_event(
            operation=self._extract_operation_name(query),
            variables=variables,
            user_id=user_id
        )
        
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        try:
            response = self.session.post(
                self.config.api_url,
                json=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            response_data = response.json()
            self._handle_graphql_errors(response_data)
            
            return response_data.get('data', {})
            
        except requests.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            raise HealthieAPIError(f"Request failed: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            raise HealthieAPIError(f"Invalid response format: {e}")
    
    async def execute_query_async(self, query: str, variables: Dict = None, user_id: str = None) -> Dict:
        """
        Execute GraphQL query (asynchronous)
        
        Args:
            query: GraphQL query string
            variables: Query variables
            user_id: User ID for audit logging
            
        Returns:
            GraphQL response data
        """
        if not self.async_client:
            raise HealthieAPIError("Async client not initialized. Use async context manager.")
        
        # Log audit event
        self._log_audit_event(
            operation=self._extract_operation_name(query),
            variables=variables,
            user_id=user_id
        )
        
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        try:
            response = await self.async_client.post(
                self.config.api_url,
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            
            response_data = response.json()
            self._handle_graphql_errors(response_data)
            
            return response_data.get('data', {})
            
        except httpx.RequestError as e:
            logger.error(f"HTTP request failed: {e}")
            raise HealthieAPIError(f"Request failed: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            raise HealthieAPIError(f"Invalid response format: {e}")
    
    def _extract_operation_name(self, query: str) -> str:
        """Extract operation name from GraphQL query"""
        # Simple extraction - in production, use proper GraphQL parsing
        lines = query.strip().split('\n')
        first_line = lines[0].strip()
        
        if first_line.startswith('query') or first_line.startswith('mutation'):
            parts = first_line.split()
            if len(parts) > 1:
                return parts[1].split('(')[0]
        
        return 'unknown_operation'
    
    # High-level methods for common operations
    
    def create_patient(self, patient_data: PatientInput, user_id: str = None) -> Dict:
        """
        Create a new patient
        
        Args:
            patient_data: Validated patient information
            user_id: User ID for audit logging
            
        Returns:
            Created patient data
        """
        mutation = """
        mutation CreatePatient($input: CreatePatientInput!) {
            createPatient(input: $input) {
                patient {
                    id
                    email
                    firstName
                    lastName
                    dateOfBirth
                    phoneNumber
                    medicalRecordNumber
                }
                errors
            }
        }
        """
        
        variables = {
            'input': patient_data.dict(exclude_none=True)
        }
        
        result = self.execute_query(mutation, variables, user_id)
        
        if result.get('createPatient', {}).get('errors'):
            errors = result['createPatient']['errors']
            raise HealthieValidationError(
                message="Patient creation failed",
                details={'validation_errors': errors}
            )
        
        return result.get('createPatient', {}).get('patient', {})
    
    def get_patient(self, patient_id: str, user_id: str = None) -> Dict:
        """
        Get patient by ID
        
        Args:
            patient_id: Patient identifier
            user_id: User ID for audit logging
            
        Returns:
            Patient data
        """
        query = """
        query GetPatient($id: ID!) {
            patient(id: $id) {
                id
                email
                firstName
                lastName
                dateOfBirth
                phoneNumber
                medicalRecordNumber
                appointments {
                    id
                    startTime
                    endTime
                    status
                }
            }
        }
        """
        
        variables = {'id': patient_id}
        result = self.execute_query(query, variables, user_id)
        
        patient = result.get('patient')
        if not patient:
            raise HealthieAPIError(f"Patient with ID {patient_id} not found")
        
        return patient
    
    def search_patients(self, search_criteria: Dict, user_id: str = None) -> List[Dict]:
        """
        Search for patients
        
        Args:
            search_criteria: Search parameters (name, email, etc.)
            user_id: User ID for audit logging
            
        Returns:
            List of matching patients
        """
        query = """
        query SearchPatients($criteria: PatientSearchInput!) {
            searchPatients(criteria: $criteria) {
                id
                email
                firstName
                lastName
                dateOfBirth
                phoneNumber
            }
        }
        """
        
        variables = {'criteria': search_criteria}
        result = self.execute_query(query, variables, user_id)
        
        return result.get('searchPatients', [])
    
    def create_appointment(self, appointment_data: AppointmentInput, user_id: str = None) -> Dict:
        """
        Create a new appointment
        
        Args:
            appointment_data: Validated appointment information
            user_id: User ID for audit logging
            
        Returns:
            Created appointment data
        """
        mutation = """
        mutation CreateAppointment($input: CreateAppointmentInput!) {
            createAppointment(input: $input) {
                appointment {
                    id
                    startTime
                    endTime
                    status
                    patient {
                        id
                        firstName
                        lastName
                    }
                    provider {
                        id
                        firstName
                        lastName
                    }
                }
                errors
            }
        }
        """
        
        variables = {
            'input': appointment_data.dict(exclude_none=True)
        }
        
        result = self.execute_query(mutation, variables, user_id)
        
        if result.get('createAppointment', {}).get('errors'):
            errors = result['createAppointment']['errors']
            raise HealthieValidationError(
                message="Appointment creation failed",
                details={'validation_errors': errors}
            )
        
        return result.get('createAppointment', {}).get('appointment', {})


# Utility functions

def load_test_patients() -> List[PatientInput]:
    """Load test patient data for development"""
    test_data = [
        {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'date_of_birth': '1990-01-15',
            'phone_number': '5551234567',
            'gender': 'male',
            'consent_for_treatment': True,
            'hipaa_authorization': True
        },
        {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'date_of_birth': '1985-07-22',
            'phone_number': '5559876543',
            'gender': 'female',
            'consent_for_treatment': True,
            'hipaa_authorization': True
        }
    ]
    
    return [PatientInput(**data) for data in test_data]


# Example usage
if __name__ == "__main__":
    # Example: Create a patient synchronously
    config = HealthieConfig()
    
    with HealthieClient(config) as client:
        # Create a test patient
        patient_data = PatientInput(
            first_name="Test",
            last_name="Patient",
            email="test.patient@example.com",
            date_of_birth="1995-03-10",
            phone_number="5551112222",
            consent_for_treatment=True,
            hipaa_authorization=True
        )
        
        try:
            patient = client.create_patient(patient_data, user_id="admin_user")
            print(f"Created patient: {patient['id']}")
            
            # Get the patient back
            retrieved_patient = client.get_patient(patient['id'], user_id="admin_user")
            print(f"Retrieved patient: {retrieved_patient['firstName']} {retrieved_patient['lastName']}")
            
        except HealthieAPIError as e:
            print(f"API Error: {e.message}")
            if e.details:
                print(f"Details: {e.details}")
    
    # Example: Async usage
    async def async_example():
        config = HealthieConfig()
        
        async with HealthieClient(config) as client:
            # Search for patients
            search_results = await client.execute_query_async(
                """
                query SearchPatients($email: String!) {
                    searchPatients(criteria: { email: $email }) {
                        id
                        firstName
                        lastName
                        email
                    }
                }
                """,
                variables={'email': 'test.patient@example.com'},
                user_id="admin_user"
            )
            
            print(f"Found {len(search_results.get('searchPatients', []))} patients")
    
    # Run async example
    # asyncio.run(async_example())