# Tool 3: code_examples - Detailed Test Results

*Generated on: 2025-07-02 23:42:56*

## Tool Overview

The Code Examples tool generates complete, runnable code examples in Python, TypeScript, or cURL for interacting with the Healthie API. Examples include authentication and error handling.
## How to Use This Tool

### Python Usage

```python
from healthie_mcp.tools.code_examples import CodeExamplesTool, CodeExamplesInput
from healthie_mcp.schema_manager import SchemaManager

# Initialize the tool
schema_manager = SchemaManager(api_endpoint='https://api.gethealthie.com/graphql')
tool = CodeExamplesTool(schema_manager)

# Get Python examples
input_data = CodeExamplesInput(
    operation_name="patient",
    language="python",
    include_authentication=True,
    include_error_handling=True
)
result = tool.execute(input_data)

# Get TypeScript examples
input_data = CodeExamplesInput(
    operation_name="createAppointment",
    language="typescript",
    include_authentication=True,
    include_error_handling=True
)
result = tool.execute(input_data)
```

### Parameters

- **operation_name** (required): The GraphQL operation name
- **language** (required): One of "python", "typescript", or "curl"
- **include_authentication** (optional): Include auth code (default: True)
- **include_error_handling** (optional): Include error handling (default: True)

## Test Summary

- **Total tests**: 2
- **Successful**: 2
- **Failed**: 0
- **Success rate**: 100.0%

## Detailed Test Results

### Test 1: Python patient examples

**Status**: ✅ Success

#### Input Parameters

```json
{
  "operation_name": "patient",
  "language": "python",
  "include_authentication": true,
  "include_error_handling": true
}
```

#### Output

```json
{
  "operation_name": "patient",
  "language": "python",
  "authentication_included": true,
  "error_handling_included": true,
  "examples": [
    {
      "title": "Basic Patient Query with Authentication",
      "description": "Simple example of fetching a patient by ID",
      "code": "import httpx\nfrom typing import Dict, Any\n\ndef get_patient(patient_id: str, api_key: str) -> Dict[str, Any]:\n    \"\"\"Fetch a patient by ID from Healthie API\"\"\"\n    \n    headers = {\n        \"Authorization\": f\"Bearer {api_key}\",\n        \"Content-Type\": \"application/json\"\n    }\n    \n    query = \"\"\"\n    query GetPatient($id: ID!) {\n        patient(id: $id) {\n            id\n            firstName\n            lastName\n            email\n            dateOfBirth\n        }\n    }\n    \"\"\"\n    \n    variables = {\"id\": patient_id}\n    \n    try:\n        response = httpx.post(\n            \"https://api.gethealthie.com/graphql\",\n            json={\"query\": query, \"variables\": variables},\n            headers=headers\n        )\n        response.raise_for_status()\n        \n        data = response.json()\n        if \"errors\" in data:\n            raise Exception(f\"GraphQL errors: {data['errors']}\")\n            \n        return data[\"data\"][\"patient\"]\n        \n    except httpx.HTTPError as e:\n        print(f\"HTTP error occurred: {e}\")\n        raise\n    except Exception as e:\n        print(f\"An error occurred: {e}\")\n        raise\n\n# Usage\npatient = get_patient(\"123\", \"your-api-key\")\nprint(f\"Patient: {patient['firstName']} {patient['lastName']}\")"
    },
    {
      "title": "Advanced Patient Query with Error Handling",
      "description": "Comprehensive example with retry logic and detailed error handling",
      "code": "import httpx\nimport time\nfrom typing import Dict, Any, Optional\nfrom dataclasses import dataclass\n\n@dataclass\nclass PatientData:\n    id: str\n    first_name: str\n    last_name: str\n    email: Optional[str]\n    date_of_birth: Optional[str]\n\nclass HealthieClient:\n    def __init__(self, api_key: str, base_url: str = \"https://api.gethealthie.com/graphql\"):\n        self.api_key = api_key\n        self.base_url = base_url\n        self.client = httpx.Client(\n            headers={\n                \"Authorization\": f\"Bearer {api_key}\",\n                \"Content-Type\": \"application/json\"\n            }\n        )\n    \n    def get_patient(self, patient_id: str, max_retries: int = 3) -> PatientData:\n        \"\"\"Fetch patient with automatic retry on failure\"\"\"\n        \n        query = \"\"\"\n        query GetPatient($id: ID!) {\n            patient(id: $id) {\n                id\n                firstName\n                lastName\n                email\n                dateOfBirth\n            }\n        }\n        \"\"\"\n        \n        for attempt in range(max_retries):\n            try:\n                response = self.client.post(\n                    self.base_url,\n                    json={\"query\": query, \"variables\": {\"id\": patient_id}}\n                )\n                \n                if response.status_code == 429:  # Rate limited\n                    retry_after = int(response.headers.get(\"Retry-After\", 60))\n                    time.sleep(retry_after)\n                    continue\n                \n                response.raise_for_status()\n                data = response.json()\n                \n                if \"errors\" in data:\n                    error_msg = data[\"errors\"][0][\"message\"]\n                    if \"not found\" in error_msg.lower():\n                        raise ValueError(f\"Patient {patient_id} not found\")\n                    raise Exception(f\"GraphQL error: {error_msg}\")\n                \n                patient_data = data[\"data\"][\"patient\"]\n                return PatientData(\n                    id=patient_data[\"id\"],\n                    first_name=patient_data[\"firstName\"],\n                    last_name=patient_data[\"lastName\"],\n                    email=patient_data.get(\"email\"),\n                    date_of_birth=patient_data.get(\"dateOfBirth\")\n                )\n                \n            except httpx.HTTPError as e:\n                if attempt == max_retries - 1:\n                    raise\n                time.sleep(2 ** attempt)  # Exponential backoff\n        \n        raise Exception(\"Max retries exceeded\")\n\n# Usage\nclient = HealthieClient(\"your-api-key\")\ntry:\n    patient = client.get_patient(\"123\")\n    print(f\"Patient: {patient.first_name} {patient.last_name}\")\nexcept ValueError as e:\n    print(f\"Patient not found: {e}\")\nexcept Exception as e:\n    print(f\"Error fetching patient: {e}\")"
    }
  ]
}
```


---

### Test 2: TypeScript createAppointment examples

**Status**: ✅ Success

#### Input Parameters

```json
{
  "operation_name": "createAppointment",
  "language": "typescript",
  "include_authentication": true,
  "include_error_handling": true
}
```

#### Output

```json
{
  "operation_name": "createAppointment",
  "language": "typescript",
  "authentication_included": true,
  "error_handling_included": true,
  "examples": [
    {
      "title": "Create Appointment with TypeScript",
      "description": "TypeScript example using fetch API",
      "code": "interface CreateAppointmentInput {\n  patientId: string;\n  providerId: string;\n  scheduledAt: string;\n  duration: number;\n  type: string;\n  notes?: string;\n}\n\ninterface AppointmentResponse {\n  id: string;\n  scheduledAt: string;\n  status: string;\n  patient: {\n    id: string;\n    firstName: string;\n    lastName: string;\n  };\n  provider: {\n    id: string;\n    firstName: string;\n    lastName: string;\n  };\n}\n\nasync function createAppointment(\n  input: CreateAppointmentInput,\n  apiKey: string\n): Promise<AppointmentResponse> {\n  const query = `\n    mutation CreateAppointment($input: CreateAppointmentInput!) {\n      createAppointment(input: $input) {\n        appointment {\n          id\n          scheduledAt\n          status\n          patient {\n            id\n            firstName\n            lastName\n          }\n          provider {\n            id\n            firstName\n            lastName\n          }\n        }\n        errors {\n          field\n          message\n        }\n      }\n    }\n  `;\n\n  try {\n    const response = await fetch('https://api.gethealthie.com/graphql', {\n      method: 'POST',\n      headers: {\n        'Content-Type': 'application/json',\n        'Authorization': `Bearer ${apiKey}`,\n      },\n      body: JSON.stringify({\n        query,\n        variables: { input },\n      }),\n    });\n\n    if (!response.ok) {\n      throw new Error(`HTTP error! status: ${response.status}`);\n    }\n\n    const data = await response.json();\n\n    if (data.errors) {\n      throw new Error(`GraphQL errors: ${JSON.stringify(data.errors)}`);\n    }\n\n    if (data.data.createAppointment.errors?.length > 0) {\n      const errors = data.data.createAppointment.errors\n        .map((e: any) => `${e.field}: ${e.message}`)\n        .join(', ');\n      throw new Error(`Validation errors: ${errors}`);\n    }\n\n    return data.data.createAppointment.appointment;\n  } catch (error) {\n    console.error('Error creating appointment:', error);\n    throw error;\n  }\n}\n\n// Usage\nconst newAppointment = await createAppointment(\n  {\n    patientId: '123',\n    providerId: '456',\n    scheduledAt: '2024-01-15T10:00:00Z',\n    duration: 30,\n    type: 'consultation',\n    notes: 'Initial consultation',\n  },\n  'your-api-key'\n);\n\nconsole.log(`Appointment created: ${newAppointment.id}`);"
    }
  ]
}
```


---

