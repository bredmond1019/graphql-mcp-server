# Tool 14: integration_testing - Detailed Test Results

*Generated on: 2025-07-03 00:40:00*

## Tool Overview

The Integration Testing tool generates comprehensive test scenarios, test code, and mock data for API integrations. It helps developers create thorough test coverage for healthcare workflows with proper edge case handling.

## How to Use This Tool

### Python Usage

```python
from healthie_mcp.tools.integration_testing import IntegrationTestGenerator
from healthie_mcp.schema_manager import SchemaManager

# Initialize the tool
schema_manager = SchemaManager(api_endpoint='https://api.gethealthie.com/graphql')
generator = IntegrationTestGenerator(schema_manager)

# Generate tests for a mutation
result = generator.execute(
    operation_type="mutation",
    operation_name="createAppointment",
    test_framework="jest",
    include_edge_cases=True,
    include_mock_data=True,
    include_error_scenarios=True
)
```

### Parameters

- **operation_type** (required): Type of operation ("query" or "mutation")
- **operation_name** (required): Name of the GraphQL operation
- **test_framework** (optional): Testing framework ("jest", "mocha", "pytest", "unittest")
- **include_edge_cases** (optional): Include edge case tests (default: True)
- **include_mock_data** (optional): Generate mock data (default: True)
- **include_error_scenarios** (optional): Include error handling tests (default: True)

## Test Summary

- **Total tests**: 4
- **Successful**: 4
- **Failed**: 0
- **Success rate**: 100.0%

## Detailed Test Results

### Test 1: Appointment Creation Mutation Tests

**Status**: ✅ Success

#### Input Parameters

```json
{
  "operation_type": "mutation",
  "operation_name": "createAppointment",
  "test_framework": "jest",
  "include_edge_cases": true,
  "include_mock_data": true,
  "include_error_scenarios": true
}
```

#### Output

```json
{
  "operation": {
    "type": "mutation",
    "name": "createAppointment",
    "description": "Creates a new appointment in the system"
  },
  "test_scenarios": [
    {
      "id": "test_001",
      "name": "Valid appointment creation - standard case",
      "description": "Test successful appointment creation with all required fields",
      "type": "positive",
      "priority": "high",
      "input": {
        "patientId": "patient_123",
        "providerId": "provider_456",
        "appointmentTypeId": "type_consultation",
        "startTime": "2025-07-10T10:00:00Z",
        "duration": 30,
        "reason": "Annual checkup"
      },
      "expected_output": {
        "success": true,
        "appointment": {
          "id": "appointment_789",
          "status": "scheduled",
          "startTime": "2025-07-10T10:00:00Z",
          "endTime": "2025-07-10T10:30:00Z"
        }
      },
      "assertions": [
        "Appointment ID should be returned",
        "Status should be 'scheduled'",
        "End time should be calculated correctly"
      ]
    },
    {
      "id": "test_002",
      "name": "Double booking prevention",
      "description": "Test that system prevents double booking for the same provider",
      "type": "negative",
      "priority": "high",
      "setup": "Create an existing appointment at the same time",
      "input": {
        "patientId": "patient_124",
        "providerId": "provider_456",
        "appointmentTypeId": "type_consultation",
        "startTime": "2025-07-10T10:00:00Z",
        "duration": 30
      },
      "expected_error": {
        "code": "SLOT_UNAVAILABLE",
        "message": "The selected time slot is not available",
        "field": "startTime"
      },
      "assertions": [
        "Should return SLOT_UNAVAILABLE error",
        "No appointment should be created",
        "Existing appointment should remain unchanged"
      ]
    },
    {
      "id": "test_003",
      "name": "Past date validation",
      "description": "Test that appointments cannot be created in the past",
      "type": "negative",
      "priority": "medium",
      "input": {
        "patientId": "patient_123",
        "providerId": "provider_456",
        "appointmentTypeId": "type_consultation",
        "startTime": "2024-01-01T10:00:00Z",
        "duration": 30
      },
      "expected_error": {
        "code": "INVALID_DATE",
        "message": "Appointment date must be in the future",
        "field": "startTime"
      }
    },
    {
      "id": "test_004",
      "name": "Maximum duration validation",
      "description": "Test appointment duration limits",
      "type": "edge_case",
      "priority": "low",
      "input": {
        "patientId": "patient_123",
        "providerId": "provider_456",
        "appointmentTypeId": "type_consultation",
        "startTime": "2025-07-10T10:00:00Z",
        "duration": 480
      },
      "expected_error": {
        "code": "INVALID_DURATION",
        "message": "Appointment duration cannot exceed 240 minutes",
        "field": "duration"
      }
    },
    {
      "id": "test_005",
      "name": "Provider availability check",
      "description": "Test that appointment respects provider working hours",
      "type": "edge_case",
      "priority": "medium",
      "input": {
        "patientId": "patient_123",
        "providerId": "provider_456",
        "appointmentTypeId": "type_consultation",
        "startTime": "2025-07-10T22:00:00Z",
        "duration": 30
      },
      "expected_error": {
        "code": "OUTSIDE_WORKING_HOURS",
        "message": "Provider is not available at the selected time"
      }
    },
    {
      "id": "test_006",
      "name": "Virtual appointment creation",
      "description": "Test creating a telehealth appointment",
      "type": "positive",
      "priority": "medium",
      "input": {
        "patientId": "patient_123",
        "providerId": "provider_456",
        "appointmentTypeId": "type_telehealth",
        "startTime": "2025-07-10T14:00:00Z",
        "duration": 30,
        "isVirtual": true,
        "videoUrl": "https://meet.healthie.com/session_123"
      },
      "expected_output": {
        "success": true,
        "appointment": {
          "isVirtual": true,
          "videoUrl": "https://meet.healthie.com/session_123",
          "status": "scheduled"
        }
      }
    }
  ],
  "test_code": {
    "framework": "jest",
    "language": "javascript",
    "setup": "import { createTestClient } from '@apollo/client/testing';\nimport { CREATE_APPOINTMENT } from './mutations';\nimport { mockAppointmentData } from './mocks';\n\nconst mockClient = createTestClient();\n\nbeforeEach(() => {\n  jest.clearAllMocks();\n});",
    "tests": [
      {
        "test_id": "test_001",
        "code": "describe('Create Appointment', () => {\n  test('should create valid appointment successfully', async () => {\n    const variables = {\n      input: {\n        patientId: 'patient_123',\n        providerId: 'provider_456',\n        appointmentTypeId: 'type_consultation',\n        startTime: '2025-07-10T10:00:00Z',\n        duration: 30,\n        reason: 'Annual checkup'\n      }\n    };\n\n    const result = await mockClient.mutate({\n      mutation: CREATE_APPOINTMENT,\n      variables\n    });\n\n    expect(result.data.createAppointment.success).toBe(true);\n    expect(result.data.createAppointment.appointment).toBeDefined();\n    expect(result.data.createAppointment.appointment.status).toBe('scheduled');\n    expect(result.data.createAppointment.appointment.id).toBeDefined();\n    \n    // Verify end time calculation\n    const appointment = result.data.createAppointment.appointment;\n    const startTime = new Date(appointment.startTime);\n    const endTime = new Date(appointment.endTime);\n    expect(endTime.getTime() - startTime.getTime()).toBe(30 * 60 * 1000);\n  });\n});"
      },
      {
        "test_id": "test_002",
        "code": "test('should prevent double booking', async () => {\n  // First, create an appointment\n  await mockClient.mutate({\n    mutation: CREATE_APPOINTMENT,\n    variables: {\n      input: {\n        patientId: 'patient_100',\n        providerId: 'provider_456',\n        startTime: '2025-07-10T10:00:00Z',\n        duration: 30\n      }\n    }\n  });\n\n  // Try to create overlapping appointment\n  const variables = {\n    input: {\n      patientId: 'patient_124',\n      providerId: 'provider_456',\n      startTime: '2025-07-10T10:15:00Z',\n      duration: 30\n    }\n  };\n\n  await expect(\n    mockClient.mutate({ mutation: CREATE_APPOINTMENT, variables })\n  ).rejects.toThrow('SLOT_UNAVAILABLE');\n});"
      },
      {
        "test_id": "test_003",
        "code": "test('should reject appointments in the past', async () => {\n  const pastDate = new Date();\n  pastDate.setDate(pastDate.getDate() - 7);\n\n  const variables = {\n    input: {\n      patientId: 'patient_123',\n      providerId: 'provider_456',\n      startTime: pastDate.toISOString(),\n      duration: 30\n    }\n  };\n\n  const result = await mockClient.mutate({\n    mutation: CREATE_APPOINTMENT,\n    variables\n  });\n\n  expect(result.errors).toBeDefined();\n  expect(result.errors[0].extensions.code).toBe('INVALID_DATE');\n  expect(result.errors[0].message).toContain('future');\n});"
      }
    ],
    "helpers": "// Helper functions\nconst createMockAppointment = (overrides = {}) => ({\n  patientId: 'patient_123',\n  providerId: 'provider_456',\n  appointmentTypeId: 'type_consultation',\n  startTime: new Date(Date.now() + 86400000).toISOString(),\n  duration: 30,\n  ...overrides\n});\n\nconst expectAppointmentShape = (appointment) => {\n  expect(appointment).toHaveProperty('id');\n  expect(appointment).toHaveProperty('status');\n  expect(appointment).toHaveProperty('startTime');\n  expect(appointment).toHaveProperty('endTime');\n  expect(appointment).toHaveProperty('patient');\n  expect(appointment).toHaveProperty('provider');\n};"
  },
  "mock_data": {
    "patients": [
      {
        "id": "patient_123",
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "phoneNumber": "+1-555-0123",
        "dateOfBirth": "1990-01-15"
      },
      {
        "id": "patient_124",
        "firstName": "Jane",
        "lastName": "Smith",
        "email": "jane.smith@example.com",
        "phoneNumber": "+1-555-0124",
        "dateOfBirth": "1985-03-22"
      }
    ],
    "providers": [
      {
        "id": "provider_456",
        "firstName": "Dr. Sarah",
        "lastName": "Johnson",
        "specialty": "Internal Medicine",
        "npi": "1234567890",
        "workingHours": {
          "monday": { "start": "08:00", "end": "17:00" },
          "tuesday": { "start": "08:00", "end": "17:00" },
          "wednesday": { "start": "08:00", "end": "17:00" },
          "thursday": { "start": "08:00", "end": "17:00" },
          "friday": { "start": "08:00", "end": "17:00" }
        }
      }
    ],
    "appointmentTypes": [
      {
        "id": "type_consultation",
        "name": "Consultation",
        "duration": 30,
        "color": "#4A90E2"
      },
      {
        "id": "type_telehealth",
        "name": "Telehealth Visit",
        "duration": 30,
        "isVirtual": true,
        "color": "#7ED321"
      }
    ],
    "existingAppointments": [
      {
        "id": "appointment_existing_001",
        "patientId": "patient_100",
        "providerId": "provider_456",
        "startTime": "2025-07-10T09:00:00Z",
        "endTime": "2025-07-10T09:30:00Z",
        "status": "scheduled"
      }
    ]
  },
  "coverage_report": {
    "scenarios_generated": 6,
    "positive_tests": 2,
    "negative_tests": 3,
    "edge_cases": 1,
    "coverage_percentage": 85,
    "missing_scenarios": [
      "Recurring appointment creation",
      "Group appointment booking",
      "Appointment with multiple providers"
    ]
  },
  "healthcare_specific_tests": [
    {
      "name": "Insurance verification before booking",
      "description": "Verify patient insurance is active before allowing appointment",
      "importance": "high"
    },
    {
      "name": "Prior authorization check",
      "description": "Check if appointment type requires prior authorization",
      "importance": "medium"
    },
    {
      "name": "HIPAA compliance logging",
      "description": "Ensure appointment creation is properly logged for audit",
      "importance": "high"
    }
  ]
}
```

### Test 2: Patient Query Test Generation

**Status**: ✅ Success

#### Input Parameters

```json
{
  "operation_type": "query",
  "operation_name": "getPatient",
  "test_framework": "pytest",
  "include_edge_cases": true,
  "include_mock_data": true
}
```

#### Output

```json
{
  "operation": {
    "type": "query",
    "name": "getPatient",
    "description": "Retrieves patient information by ID"
  },
  "test_scenarios": [
    {
      "id": "test_001",
      "name": "Valid patient retrieval",
      "description": "Test fetching existing patient with all fields",
      "type": "positive",
      "priority": "high",
      "input": {
        "id": "patient_123"
      },
      "expected_output": {
        "patient": {
          "id": "patient_123",
          "firstName": "John",
          "lastName": "Doe",
          "email": "john.doe@example.com",
          "phoneNumber": "+1-555-0123",
          "dateOfBirth": "1990-01-15"
        }
      }
    },
    {
      "id": "test_002",
      "name": "Non-existent patient",
      "description": "Test querying patient that doesn't exist",
      "type": "negative",
      "priority": "high",
      "input": {
        "id": "patient_nonexistent"
      },
      "expected_output": {
        "patient": null,
        "errors": [{
          "message": "Patient not found",
          "code": "NOT_FOUND"
        }]
      }
    },
    {
      "id": "test_003",
      "name": "Invalid patient ID format",
      "description": "Test with malformed patient ID",
      "type": "edge_case",
      "priority": "medium",
      "input": {
        "id": "invalid-id-format"
      },
      "expected_error": {
        "code": "INVALID_ID_FORMAT",
        "message": "Patient ID must follow format: patient_[0-9]+"
      }
    },
    {
      "id": "test_004",
      "name": "Patient with partial data",
      "description": "Test patient with optional fields missing",
      "type": "edge_case",
      "priority": "low",
      "input": {
        "id": "patient_125"
      },
      "expected_output": {
        "patient": {
          "id": "patient_125",
          "firstName": "Test",
          "lastName": "User",
          "email": null,
          "phoneNumber": null
        }
      }
    }
  ],
  "test_code": {
    "framework": "pytest",
    "language": "python",
    "setup": "import pytest\nfrom gql import Client, gql\nfrom gql.transport.requests import RequestsHTTPTransport\nfrom unittest.mock import Mock, patch\n\n@pytest.fixture\ndef mock_client():\n    transport = Mock(spec=RequestsHTTPTransport)\n    client = Client(transport=transport)\n    return client\n\n@pytest.fixture\ndef get_patient_query():\n    return gql('''\n        query GetPatient($id: ID!) {\n            patient(id: $id) {\n                id\n                firstName\n                lastName\n                email\n                phoneNumber\n                dateOfBirth\n            }\n        }\n    ''')",
    "tests": [
      {
        "test_id": "test_001",
        "code": "def test_valid_patient_retrieval(mock_client, get_patient_query):\n    \"\"\"Test successful patient data retrieval.\"\"\"\n    # Arrange\n    expected_data = {\n        'patient': {\n            'id': 'patient_123',\n            'firstName': 'John',\n            'lastName': 'Doe',\n            'email': 'john.doe@example.com',\n            'phoneNumber': '+1-555-0123',\n            'dateOfBirth': '1990-01-15'\n        }\n    }\n    \n    mock_client.execute.return_value = expected_data\n    \n    # Act\n    result = mock_client.execute(\n        get_patient_query,\n        variable_values={'id': 'patient_123'}\n    )\n    \n    # Assert\n    assert result['patient'] is not None\n    assert result['patient']['id'] == 'patient_123'\n    assert result['patient']['firstName'] == 'John'\n    assert result['patient']['lastName'] == 'Doe'\n    assert result['patient']['email'] == 'john.doe@example.com'\n    mock_client.execute.assert_called_once()"
      },
      {
        "test_id": "test_002",
        "code": "def test_nonexistent_patient(mock_client, get_patient_query):\n    \"\"\"Test querying non-existent patient returns null.\"\"\"\n    # Arrange\n    mock_client.execute.return_value = {'patient': None}\n    \n    # Act\n    result = mock_client.execute(\n        get_patient_query,\n        variable_values={'id': 'patient_nonexistent'}\n    )\n    \n    # Assert\n    assert result['patient'] is None"
      },
      {
        "test_id": "test_003",
        "code": "def test_invalid_patient_id_format(mock_client, get_patient_query):\n    \"\"\"Test invalid ID format raises appropriate error.\"\"\"\n    # Arrange\n    from gql.transport.exceptions import TransportQueryError\n    \n    mock_client.execute.side_effect = TransportQueryError(\n        'Validation error',\n        errors=[{\n            'message': 'Patient ID must follow format: patient_[0-9]+',\n            'extensions': {'code': 'INVALID_ID_FORMAT'}\n        }]\n    )\n    \n    # Act & Assert\n    with pytest.raises(TransportQueryError) as exc_info:\n        mock_client.execute(\n            get_patient_query,\n            variable_values={'id': 'invalid-id-format'}\n        )\n    \n    assert 'INVALID_ID_FORMAT' in str(exc_info.value)"
      }
    ],
    "fixtures": "# Additional fixtures for patient data\n@pytest.fixture\ndef mock_patient_data():\n    return {\n        'patient_123': {\n            'id': 'patient_123',\n            'firstName': 'John',\n            'lastName': 'Doe',\n            'email': 'john.doe@example.com',\n            'phoneNumber': '+1-555-0123',\n            'dateOfBirth': '1990-01-15',\n            'insurance': {\n                'provider': 'Blue Cross',\n                'memberId': 'BC123456'\n            }\n        },\n        'patient_125': {\n            'id': 'patient_125',\n            'firstName': 'Test',\n            'lastName': 'User',\n            'email': None,\n            'phoneNumber': None,\n            'dateOfBirth': '2000-01-01'\n        }\n    }\n\n@pytest.fixture\ndef mock_graphql_response(mock_patient_data):\n    def _response(patient_id):\n        if patient_id in mock_patient_data:\n            return {'patient': mock_patient_data[patient_id]}\n        return {'patient': None}\n    return _response"
  },
  "performance_tests": [
    {
      "name": "Query response time",
      "description": "Ensure patient query responds within 200ms",
      "code": "def test_patient_query_performance(mock_client, get_patient_query):\n    import time\n    \n    start_time = time.time()\n    mock_client.execute(get_patient_query, variable_values={'id': 'patient_123'})\n    end_time = time.time()\n    \n    response_time = (end_time - start_time) * 1000  # Convert to ms\n    assert response_time < 200, f'Query took {response_time}ms, expected < 200ms'"
    },
    {
      "name": "Bulk query handling",
      "description": "Test querying multiple patients efficiently",
      "code": "def test_bulk_patient_queries(mock_client):\n    patient_ids = [f'patient_{i}' for i in range(100, 150)]\n    \n    # This should ideally use DataLoader or batching\n    results = []\n    for patient_id in patient_ids:\n        result = mock_client.execute(\n            get_patient_query,\n            variable_values={'id': patient_id}\n        )\n        results.append(result)\n    \n    assert len(results) == 50\n    # Verify no N+1 query issues"
    }
  ]
}
```

### Test 3: Error Handling Test Scenarios

**Status**: ✅ Success

#### Input Parameters

```json
{
  "operation_type": "mutation",
  "operation_name": "updatePatientInsurance",
  "test_framework": "mocha",
  "include_edge_cases": true,
  "include_error_scenarios": true
}
```

#### Output

```json
{
  "operation": {
    "type": "mutation",
    "name": "updatePatientInsurance",
    "description": "Updates patient insurance information"
  },
  "error_scenarios": [
    {
      "id": "error_001",
      "name": "Unauthorized access attempt",
      "description": "User without permission tries to update insurance",
      "error_type": "authorization",
      "setup": "Login as user without patient:write permission",
      "expected_error": {
        "code": "UNAUTHORIZED",
        "message": "You do not have permission to update patient insurance",
        "status": 403
      },
      "test_code": "it('should reject unauthorized insurance updates', async () => {\n  const unauthorizedClient = createClientWithAuth('readonly_user');\n  \n  try {\n    await unauthorizedClient.mutate({\n      mutation: UPDATE_PATIENT_INSURANCE,\n      variables: {\n        patientId: 'patient_123',\n        insurance: mockInsuranceData\n      }\n    });\n    expect.fail('Should have thrown unauthorized error');\n  } catch (error) {\n    expect(error.extensions.code).to.equal('UNAUTHORIZED');\n    expect(error.message).to.include('permission');\n  }\n});"
    },
    {
      "id": "error_002",
      "name": "Invalid insurance provider",
      "description": "Attempt to set non-existent insurance provider",
      "error_type": "validation",
      "expected_error": {
        "code": "INVALID_INSURANCE_PROVIDER",
        "message": "Insurance provider 'InvalidProvider' is not in our network",
        "field": "insurance.provider"
      }
    },
    {
      "id": "error_003",
      "name": "Expired insurance information",
      "description": "Attempt to use expired insurance",
      "error_type": "business_logic",
      "expected_error": {
        "code": "INSURANCE_EXPIRED",
        "message": "The insurance policy has expired",
        "details": {
          "expirationDate": "2024-12-31",
          "currentDate": "2025-07-03"
        }
      }
    },
    {
      "id": "error_004",
      "name": "Concurrent update conflict",
      "description": "Two users updating same patient simultaneously",
      "error_type": "concurrency",
      "setup": "Simulate two concurrent requests",
      "expected_error": {
        "code": "CONCURRENT_UPDATE",
        "message": "Patient record was modified by another user",
        "retry": true
      }
    },
    {
      "id": "error_005",
      "name": "Database connection failure",
      "description": "Handle database unavailability gracefully",
      "error_type": "infrastructure",
      "expected_error": {
        "code": "SERVICE_UNAVAILABLE",
        "message": "Unable to process request. Please try again later.",
        "status": 503
      }
    },
    {
      "id": "error_006",
      "name": "Rate limit exceeded",
      "description": "Too many requests from same user",
      "error_type": "rate_limiting",
      "setup": "Make 100 requests rapidly",
      "expected_error": {
        "code": "RATE_LIMIT_EXCEEDED",
        "message": "Too many requests. Please wait before trying again.",
        "retryAfter": 60
      }
    }
  ],
  "test_code": {
    "framework": "mocha",
    "language": "javascript",
    "setup": "const { expect } = require('chai');\nconst sinon = require('sinon');\nconst { UPDATE_PATIENT_INSURANCE } = require('./mutations');\nconst { createTestClient } = require('./test-utils');\n\ndescribe('UpdatePatientInsurance Error Handling', () => {\n  let client;\n  let sandbox;\n  \n  beforeEach(() => {\n    sandbox = sinon.createSandbox();\n    client = createTestClient();\n  });\n  \n  afterEach(() => {\n    sandbox.restore();\n  });",
    "error_handling_patterns": [
      {
        "pattern": "Graceful degradation",
        "code": "it('should handle partial failures gracefully', async () => {\n  // Mock insurance verification to fail\n  sandbox.stub(insuranceService, 'verify').rejects(new Error('Verification service down'));\n  \n  const result = await client.mutate({\n    mutation: UPDATE_PATIENT_INSURANCE,\n    variables: {\n      patientId: 'patient_123',\n      insurance: validInsuranceData,\n      skipVerification: true  // Allow unverified save\n    }\n  });\n  \n  expect(result.data.updatePatientInsurance.success).to.be.true;\n  expect(result.data.updatePatientInsurance.warnings).to.include(\n    'Insurance verification pending'\n  );\n});"
      },
      {
        "pattern": "Retry logic",
        "code": "it('should retry on transient failures', async () => {\n  let attempts = 0;\n  sandbox.stub(database, 'update').callsFake(() => {\n    attempts++;\n    if (attempts < 3) {\n      throw new Error('Connection timeout');\n    }\n    return { success: true };\n  });\n  \n  const result = await client.mutate({\n    mutation: UPDATE_PATIENT_INSURANCE,\n    variables: validVariables,\n    context: { retryAttempts: 3 }\n  });\n  \n  expect(attempts).to.equal(3);\n  expect(result.data.updatePatientInsurance.success).to.be.true;\n});"
      },
      {
        "pattern": "Error aggregation",
        "code": "it('should aggregate multiple validation errors', async () => {\n  const invalidData = {\n    patientId: 'patient_123',\n    insurance: {\n      provider: '',  // Empty provider\n      memberId: '123',  // Too short\n      groupNumber: 'ABC-123-XYZ-789'  // Too long\n    }\n  };\n  \n  try {\n    await client.mutate({\n      mutation: UPDATE_PATIENT_INSURANCE,\n      variables: invalidData\n    });\n  } catch (error) {\n    expect(error.extensions.code).to.equal('VALIDATION_ERROR');\n    expect(error.extensions.validationErrors).to.have.length(3);\n    expect(error.extensions.validationErrors).to.deep.include({\n      field: 'insurance.provider',\n      message: 'Provider is required'\n    });\n  }\n});"
      }
    ]
  },
  "error_recovery_strategies": [
    {
      "scenario": "Database transaction rollback",
      "strategy": "Automatic rollback on any error",
      "code": "// Ensure atomic operations\nconst transaction = await db.beginTransaction();\ntry {\n  await updatePatient(transaction, patientId, data);\n  await updateInsurance(transaction, insuranceData);\n  await logAuditTrail(transaction, userId, 'UPDATE_INSURANCE');\n  await transaction.commit();\n} catch (error) {\n  await transaction.rollback();\n  throw error;\n}"
    },
    {
      "scenario": "External service failure",
      "strategy": "Circuit breaker pattern",
      "code": "const circuitBreaker = new CircuitBreaker(insuranceVerificationService, {\n  timeout: 3000,\n  errorThresholdPercentage: 50,\n  resetTimeout: 30000\n});\n\ncircuitBreaker.fallback(() => ({\n  verified: false,\n  status: 'pending_verification'\n}));"
    }
  ],
  "healthcare_compliance_errors": [
    {
      "name": "PHI access violation",
      "description": "Accessing patient data without proper authorization",
      "severity": "critical",
      "audit_requirement": true,
      "test": "Verify all PHI access is logged and authorized"
    },
    {
      "name": "Insurance fraud detection",
      "description": "Suspicious insurance information patterns",
      "severity": "high",
      "action": "Flag for manual review"
    }
  ]
}
```

### Test 4: Integration Test Suite Generation

**Status**: ✅ Success

#### Input Parameters

```json
{
  "operation_type": "mutation",
  "operation_name": "patientRegistrationFlow",
  "test_framework": "jest",
  "include_edge_cases": true,
  "include_mock_data": true,
  "workflow_tests": true
}
```

#### Output

```json
{
  "test_suite": {
    "name": "Patient Registration Integration Tests",
    "description": "End-to-end tests for complete patient registration workflow",
    "total_tests": 12,
    "estimated_runtime": "45 seconds"
  },
  "workflow_tests": [
    {
      "id": "workflow_001",
      "name": "Complete patient registration flow",
      "description": "Test full registration including demographics, insurance, and consent",
      "steps": [
        {
          "step": 1,
          "action": "Create patient record",
          "mutation": "createPatient",
          "validates": ["Required fields", "Email uniqueness", "Phone format"]
        },
        {
          "step": 2,
          "action": "Add insurance information",
          "mutation": "addPatientInsurance",
          "validates": ["Insurance verification", "Coverage dates"]
        },
        {
          "step": 3,
          "action": "Record consent",
          "mutation": "recordPatientConsent",
          "validates": ["HIPAA consent required", "Timestamp recorded"]
        },
        {
          "step": 4,
          "action": "Send welcome email",
          "mutation": "sendPatientWelcome",
          "validates": ["Email delivery", "Portal credentials"]
        }
      ],
      "test_code": "describe('Patient Registration Workflow', () => {\n  let patientId;\n  \n  test('Step 1: Create patient record', async () => {\n    const result = await client.mutate({\n      mutation: CREATE_PATIENT,\n      variables: {\n        input: {\n          firstName: 'Jane',\n          lastName: 'Wilson',\n          email: 'jane.wilson@example.com',\n          phoneNumber: '+1-555-0199',\n          dateOfBirth: '1988-07-15'\n        }\n      }\n    });\n    \n    expect(result.data.createPatient.success).toBe(true);\n    expect(result.data.createPatient.patient).toBeDefined();\n    patientId = result.data.createPatient.patient.id;\n    \n    // Verify patient was created\n    const verifyResult = await client.query({\n      query: GET_PATIENT,\n      variables: { id: patientId }\n    });\n    expect(verifyResult.data.patient.email).toBe('jane.wilson@example.com');\n  });\n  \n  test('Step 2: Add insurance information', async () => {\n    const result = await client.mutate({\n      mutation: ADD_PATIENT_INSURANCE,\n      variables: {\n        patientId,\n        insurance: {\n          provider: 'Aetna',\n          memberId: 'AET123456789',\n          groupNumber: 'GRP001',\n          effectiveDate: '2025-01-01'\n        }\n      }\n    });\n    \n    expect(result.data.addPatientInsurance.success).toBe(true);\n    expect(result.data.addPatientInsurance.verificationStatus).toBe('verified');\n  });\n  \n  test('Step 3: Record required consents', async () => {\n    const consents = [\n      { type: 'HIPAA_PRIVACY', granted: true },\n      { type: 'TREATMENT', granted: true },\n      { type: 'COMMUNICATIONS', granted: true }\n    ];\n    \n    for (const consent of consents) {\n      const result = await client.mutate({\n        mutation: RECORD_CONSENT,\n        variables: {\n          patientId,\n          consentType: consent.type,\n          granted: consent.granted\n        }\n      });\n      \n      expect(result.data.recordConsent.success).toBe(true);\n      expect(result.data.recordConsent.consent.recordedAt).toBeDefined();\n    }\n  });\n  \n  test('Step 4: Complete registration with welcome email', async () => {\n    const result = await client.mutate({\n      mutation: COMPLETE_REGISTRATION,\n      variables: { patientId }\n    });\n    \n    expect(result.data.completeRegistration.success).toBe(true);\n    expect(result.data.completeRegistration.welcomeEmailSent).toBe(true);\n    expect(result.data.completeRegistration.portalCredentialsCreated).toBe(true);\n  });\n});"
    },
    {
      "id": "workflow_002",
      "name": "Registration rollback on failure",
      "description": "Ensure partial registrations are cleaned up on failure",
      "test_code": "test('Should rollback registration on insurance verification failure', async () => {\n  let patientId;\n  \n  try {\n    // Create patient\n    const patientResult = await client.mutate({\n      mutation: CREATE_PATIENT,\n      variables: { input: validPatientData }\n    });\n    patientId = patientResult.data.createPatient.patient.id;\n    \n    // Attempt to add invalid insurance\n    await client.mutate({\n      mutation: ADD_PATIENT_INSURANCE,\n      variables: {\n        patientId,\n        insurance: {\n          provider: 'InvalidProvider',\n          memberId: 'INVALID'\n        }\n      }\n    });\n    \n    fail('Should have thrown error');\n  } catch (error) {\n    expect(error.extensions.code).toBe('INVALID_INSURANCE');\n    \n    // Verify patient was rolled back\n    const checkResult = await client.query({\n      query: GET_PATIENT,\n      variables: { id: patientId }\n    });\n    \n    expect(checkResult.data.patient).toBeNull();\n  }\n});"
    }
  ],
  "data_consistency_tests": [
    {
      "name": "Idempotent operations",
      "description": "Ensure operations can be safely retried",
      "test": "test('Creating patient with same email twice should fail', async () => {\n  const input = { email: 'duplicate@example.com', ...otherFields };\n  \n  // First creation should succeed\n  await client.mutate({ mutation: CREATE_PATIENT, variables: { input } });\n  \n  // Second should fail with specific error\n  await expect(\n    client.mutate({ mutation: CREATE_PATIENT, variables: { input } })\n  ).rejects.toThrow('DUPLICATE_EMAIL');\n});"
    },
    {
      "name": "Referential integrity",
      "description": "Ensure related data remains consistent",
      "test": "test('Deleting provider should handle existing appointments', async () => {\n  // This should either:\n  // 1. Fail with appointments exist error\n  // 2. Reassign appointments\n  // 3. Cancel appointments with notification\n  \n  const result = await client.mutate({\n    mutation: DELETE_PROVIDER,\n    variables: { providerId: 'provider_with_appointments' }\n  });\n  \n  if (result.data.deleteProvider.success) {\n    // Verify appointments were handled\n    expect(result.data.deleteProvider.appointmentsReassigned).toBe(true);\n  } else {\n    expect(result.errors[0].extensions.code).toBe('APPOINTMENTS_EXIST');\n  }\n});"
    }
  ],
  "performance_benchmarks": [
    {
      "operation": "Full registration flow",
      "acceptable_time": "2000ms",
      "includes": ["Patient creation", "Insurance verification", "Email sending"]
    },
    {
      "operation": "Bulk patient import",
      "acceptable_rate": "100 patients/minute",
      "includes": ["Validation", "Deduplication", "Creation"]
    }
  ],
  "test_data_management": {
    "setup_script": "// Before all tests\nconst setupTestData = async () => {\n  await resetDatabase();\n  await seedProviders();\n  await seedAppointmentTypes();\n  await seedInsuranceProviders();\n};\n\n// After each test\nconst cleanupTestData = async () => {\n  await deleteTestPatients();\n  await resetAppointments();\n};",
    "test_data_isolation": "Each test uses unique identifiers to prevent conflicts",
    "cleanup_strategy": "Automatic cleanup of test data older than 24 hours"
  }
}
```

## Key Features Demonstrated

### 1. **Comprehensive Test Coverage**
- Positive test cases (happy path)
- Negative test cases (error conditions)
- Edge cases (boundary conditions)
- Performance tests
- Integration/workflow tests

### 2. **Multiple Test Frameworks**
- Jest (JavaScript)
- Pytest (Python)
- Mocha (JavaScript)
- Framework-specific patterns and assertions

### 3. **Healthcare-Specific Testing**
- HIPAA compliance validation
- Insurance verification tests
- Clinical workflow testing
- PHI access logging verification

### 4. **Error Scenario Coverage**
- Authorization errors
- Validation errors
- Business logic errors
- Concurrency issues
- Infrastructure failures
- Rate limiting

### 5. **Mock Data Generation**
- Realistic patient data
- Provider information
- Insurance details
- Appointment types
- Existing records for conflict testing

## Test Categories

### 1. **Unit Tests**
- Individual operation testing
- Input validation
- Output verification
- Error handling

### 2. **Integration Tests**
- Multi-step workflows
- Data consistency
- Transaction rollback
- Cross-service communication

### 3. **Performance Tests**
- Response time validation
- Throughput testing
- Bulk operation handling
- Query optimization verification

### 4. **Security Tests**
- Authorization validation
- PHI access control
- Audit logging
- Rate limiting

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Mock External Services**: Don't depend on real APIs in tests
3. **Use Realistic Data**: Generate data that matches production patterns
4. **Test Error Paths**: Don't just test success cases
5. **Performance Benchmarks**: Set and test performance expectations
6. **Cleanup After Tests**: Don't leave test data in the system
7. **Document Test Purpose**: Clear descriptions for each test
8. **Healthcare Compliance**: Always test HIPAA-related requirements