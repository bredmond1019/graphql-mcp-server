# Clinical Integration Tutorial

Learn how to integrate clinical data with Healthie's GraphQL API.

## Overview

This tutorial covers essential clinical data operations:
- Creating and managing clinical notes
- Recording vital signs and metrics
- Working with lab results
- Managing care plans

## Key GraphQL Operations

### 1. Create Clinical Note

```graphql
mutation CreateClinicalNote($input: createEntryInput!) {
  createEntry(input: $input) {
    entry {
      id
      category
      description
      created_by {
        id
        first_name
        last_name
      }
      patient {
        id
        first_name
        last_name
      }
      form_answer_group {
        id
        form_answers {
          label
          answer
        }
      }
    }
    messages
  }
}
```

### 2. Record Vital Signs

```graphql
mutation RecordVitals($input: createMetricEntryInput!) {
  createMetricEntry(input: $input) {
    metric_entry {
      id
      category
      type
      value
      created_at
      metric {
        id
        name
        unit
      }
      patient {
        id
        first_name
        last_name
      }
    }
    messages
  }
}
```

### 3. Get Patient Clinical History

```graphql
query GetClinicalHistory($patient_id: ID!, $category: String) {
  entries(patient_id: $patient_id, category: $category, first: 20) {
    id
    category
    description
    created_at
    created_by {
      id
      first_name
      last_name
      title
    }
    form_answer_group {
      form_answers {
        label
        answer
      }
    }
  }
}
```

## JavaScript Implementation

### Clinical Note Creation

```javascript
import { gql, useMutation } from '@apollo/client';

const CREATE_SOAP_NOTE = gql`
  mutation CreateSOAPNote($input: createEntryInput!) {
    createEntry(input: $input) {
      entry {
        id
        category
        description
        form_answer_group {
          form_answers {
            label
            answer
          }
        }
      }
      messages
    }
  }
`;

function SOAPNoteForm({ patientId, providerId }) {
  const [createNote] = useMutation(CREATE_SOAP_NOTE);
  
  const handleSubmit = async (soapData) => {
    try {
      const { data } = await createNote({
        variables: {
          input: {
            patient_id: patientId,
            created_by_id: providerId,
            category: "clinical_note",
            description: "SOAP Note",
            form_answer_group: {
              form_answers: [
                { label: "Subjective", answer: soapData.subjective },
                { label: "Objective", answer: soapData.objective },
                { label: "Assessment", answer: soapData.assessment },
                { label: "Plan", answer: soapData.plan }
              ]
            }
          }
        }
      });
      
      if (data.createEntry.messages?.length > 0) {
        console.error('Validation errors:', data.createEntry.messages);
        return null;
      }
      
      return data.createEntry.entry;
    } catch (error) {
      console.error('Error creating SOAP note:', error);
      throw error;
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields for SOAP note */}
    </form>
  );
}
```

### Vital Signs Recording

```javascript
const RECORD_VITALS = gql`
  mutation RecordVitals($input: createMetricEntryInput!) {
    createMetricEntry(input: $input) {
      metric_entry {
        id
        value
        created_at
      }
      messages
    }
  }
`;

async function recordVitalSigns(patientId, vitals) {
  const vitalEntries = [
    { type: "blood_pressure_systolic", value: vitals.systolic },
    { type: "blood_pressure_diastolic", value: vitals.diastolic },
    { type: "heart_rate", value: vitals.heartRate },
    { type: "temperature", value: vitals.temperature },
    { type: "respiratory_rate", value: vitals.respiratoryRate },
    { type: "oxygen_saturation", value: vitals.oxygenSaturation }
  ];
  
  const promises = vitalEntries.map(vital => 
    client.mutate({
      mutation: RECORD_VITALS,
      variables: {
        input: {
          patient_id: patientId,
          category: "biometrics",
          type: vital.type,
          value: vital.value.toString()
        }
      }
    })
  );
  
  return Promise.all(promises);
}
```

## Python Implementation

```python
import requests
from datetime import datetime

def create_clinical_note(patient_id, provider_id, note_data, api_key):
    """Create a clinical note (SOAP format)"""
    
    query = """
    mutation CreateClinicalNote($input: createEntryInput!) {
      createEntry(input: $input) {
        entry {
          id
          category
          description
          created_at
        }
        messages
      }
    }
    """
    
    variables = {
        "input": {
            "patient_id": patient_id,
            "created_by_id": provider_id,
            "category": "clinical_note",
            "description": "SOAP Note",
            "form_answer_group": {
                "form_answers": [
                    {"label": "Subjective", "answer": note_data.get("subjective", "")},
                    {"label": "Objective", "answer": note_data.get("objective", "")},
                    {"label": "Assessment", "answer": note_data.get("assessment", "")},
                    {"label": "Plan", "answer": note_data.get("plan", "")}
                ]
            }
        }
    }
    
    response = requests.post(
        'https://api.gethealthie.com/graphql',
        json={'query': query, 'variables': variables},
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    )
    
    return response.json()['data']['createEntry']['entry']

def record_vital_signs(patient_id, vitals, api_key):
    """Record patient vital signs"""
    
    query = """
    mutation RecordVital($input: createMetricEntryInput!) {
      createMetricEntry(input: $input) {
        metric_entry {
          id
          value
          created_at
        }
        messages
      }
    }
    """
    
    vital_mappings = {
        'systolic': 'blood_pressure_systolic',
        'diastolic': 'blood_pressure_diastolic',
        'heart_rate': 'heart_rate',
        'temperature': 'temperature',
        'respiratory_rate': 'respiratory_rate',
        'oxygen_saturation': 'oxygen_saturation'
    }
    
    results = []
    for vital_key, vital_type in vital_mappings.items():
        if vital_key in vitals:
            response = requests.post(
                'https://api.gethealthie.com/graphql',
                json={
                    'query': query,
                    'variables': {
                        'input': {
                            'patient_id': patient_id,
                            'category': 'biometrics',
                            'type': vital_type,
                            'value': str(vitals[vital_key])
                        }
                    }
                },
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
            )
            results.append(response.json())
    
    return results
```

## Common Clinical Categories

Healthie supports various clinical data categories:
- `clinical_note` - General clinical notes
- `biometrics` - Vital signs and measurements
- `lab_result` - Laboratory test results
- `medication` - Medication records
- `assessment` - Clinical assessments
- `care_plan` - Treatment plans

## Best Practices

1. **Data Validation**: Always validate clinical data before submission
2. **Audit Trail**: Track who created/modified clinical records
3. **Privacy**: Ensure HIPAA compliance when handling clinical data
4. **Standardization**: Use standard medical terminologies when possible
5. **Error Handling**: Implement robust error handling for clinical operations

## Next Steps

- Implement FHIR resource mappings for interoperability
- Add medical coding (ICD-10, CPT) support
- Build clinical decision support features
- Create templates for common clinical workflows

For advanced clinical features, use the MCP server tools:
- `find_healthcare_patterns(category: "clinical_data")` - Explore clinical patterns
- `query_templates(workflow: "clinical_documentation")` - Get clinical query templates
- `compliance_checker(context: "clinical_data")` - Check HIPAA compliance