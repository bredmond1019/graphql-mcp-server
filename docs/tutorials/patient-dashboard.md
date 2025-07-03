# Patient Dashboard Tutorial

Learn how to build a patient dashboard with Healthie's GraphQL API.

## Overview

This tutorial covers building a basic patient dashboard that displays:
- Patient profile information
- Recent appointments
- Upcoming visits
- Basic health metrics

## Core GraphQL Queries

### 1. Get Patient Profile

```graphql
query GetPatient($id: ID!) {
  patient(id: $id) {
    id
    first_name
    last_name
    email
    phone_number
    date_of_birth
    gender
    addresses {
      line1
      line2
      city
      state
      zip
    }
    policies {
      id
      insurance_plan {
        payer_name
        name
      }
      holder_relationship
      num
    }
  }
}
```

### 2. Get Patient Appointments

```graphql
query GetPatientAppointments($patient_id: ID!, $start_date: String!, $end_date: String!) {
  appointments(patient_id: $patient_id, start_date: $start_date, end_date: $end_date) {
    id
    date
    time
    end_time
    status
    contact_type
    provider {
      id
      first_name
      last_name
      title
    }
    appointment_type {
      id
      name
      duration
    }
  }
}
```

### 3. Get Patient Metrics

```graphql
query GetPatientMetrics($patient_id: ID!) {
  patient(id: $patient_id) {
    id
    metric_entries(category: "biometrics", limit: 10) {
      id
      category
      type
      value
      created_at
      metric {
        name
        unit
      }
    }
  }
}
```

## React Implementation

### Dashboard Component

```javascript
import React, { useState, useEffect } from 'react';
import { useQuery, gql } from '@apollo/client';
import { format } from 'date-fns';

const GET_PATIENT_DASHBOARD = gql`
  query GetPatientDashboard($patient_id: ID!, $start_date: String!, $end_date: String!) {
    patient(id: $patient_id) {
      id
      first_name
      last_name
      email
      phone_number
      date_of_birth
      appointments(start_date: $start_date, end_date: $end_date, first: 10) {
        id
        date
        time
        status
        provider {
          first_name
          last_name
        }
      }
      metric_entries(category: "biometrics", limit: 5) {
        id
        type
        value
        created_at
        metric {
          name
          unit
        }
      }
    }
  }
`;

function PatientDashboard({ patientId }) {
  const today = new Date();
  const startDate = format(today, 'yyyy-MM-dd');
  const endDate = format(new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000), 'yyyy-MM-dd');

  const { loading, error, data } = useQuery(GET_PATIENT_DASHBOARD, {
    variables: { 
      patient_id: patientId,
      start_date: startDate,
      end_date: endDate
    }
  });

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  const patient = data.patient;

  return (
    <div className="dashboard">
      <h1>Welcome, {patient.first_name} {patient.last_name}</h1>
      
      <section className="profile-section">
        <h2>Profile Information</h2>
        <p>Email: {patient.email}</p>
        <p>Phone: {patient.phone_number}</p>
        <p>Date of Birth: {patient.date_of_birth}</p>
      </section>

      <section className="appointments-section">
        <h2>Upcoming Appointments</h2>
        {patient.appointments.length === 0 ? (
          <p>No upcoming appointments</p>
        ) : (
          <ul>
            {patient.appointments.map(apt => (
              <li key={apt.id}>
                {apt.date} at {apt.time} with Dr. {apt.provider.last_name}
                <span className={`status ${apt.status}`}>{apt.status}</span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="metrics-section">
        <h2>Recent Health Metrics</h2>
        {patient.metric_entries.length === 0 ? (
          <p>No recent metrics recorded</p>
        ) : (
          <ul>
            {patient.metric_entries.map(metric => (
              <li key={metric.id}>
                {metric.metric.name}: {metric.value} {metric.metric.unit}
                <span className="date">{format(new Date(metric.created_at), 'MMM dd, yyyy')}</span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

export default PatientDashboard;
```

### Apollo Client Setup

```javascript
import { ApolloClient, InMemoryCache } from '@apollo/client';

const client = new ApolloClient({
  uri: 'https://api.gethealthie.com/graphql',
  cache: new InMemoryCache(),
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY'
  }
});

// Wrap your app with ApolloProvider
import { ApolloProvider } from '@apollo/client';

function App() {
  return (
    <ApolloProvider client={client}>
      <PatientDashboard patientId="12345" />
    </ApolloProvider>
  );
}
```

## Python Implementation

```python
import requests
from datetime import datetime, timedelta

def get_patient_dashboard(patient_id, api_key):
    """Fetch patient dashboard data"""
    
    query = """
    query GetPatientDashboard($patient_id: ID!, $start_date: String!, $end_date: String!) {
      patient(id: $patient_id) {
        id
        first_name
        last_name
        email
        phone_number
        appointments(start_date: $start_date, end_date: $end_date, first: 10) {
          id
          date
          time
          status
          provider {
            first_name
            last_name
          }
        }
      }
    }
    """
    
    today = datetime.now()
    start_date = today.strftime('%Y-%m-%d')
    end_date = (today + timedelta(days=30)).strftime('%Y-%m-%d')
    
    response = requests.post(
        'https://api.gethealthie.com/graphql',
        json={
            'query': query,
            'variables': {
                'patient_id': patient_id,
                'start_date': start_date,
                'end_date': end_date
            }
        },
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    )
    
    return response.json()['data']['patient']
```

## Key Considerations

1. **Performance**: Use GraphQL fragments to avoid over-fetching
2. **Caching**: Leverage Apollo Client's cache for better performance
3. **Error Handling**: Always handle loading and error states
4. **Security**: Never expose API keys in client-side code
5. **Accessibility**: Ensure dashboard is keyboard navigable and screen reader friendly

## Using MCP Tools for Patient Dashboards

### Discover Patient Data Structure

```python
# Explore the Patient type completely
patient_type = introspect_type("Patient")
# Shows 100+ fields including relationships

# Find all patient-related queries
patient_queries = search_schema("patient", type_filter="query")
# Discovers: patient, patients, patientSearch queries
```

### Generate Dashboard Components

```python
# Get patient query templates
dashboard_templates = query_templates(workflow="patient_management")

# Generate complete dashboard code
dashboard_code = code_examples(
    operation="patient_dashboard",
    language="javascript"
)
```

### Handle Dashboard Errors

```python
# Debug common dashboard issues
error_decoder("Cannot query field 'metrics' on type 'Patient'")
# Returns: "Use 'metric_entries' with category filter instead"

# Find related data fields
relationships = search_schema("patient_id", type_filter="field")
# Shows all types that reference patients
```

## Next Steps

- Add real-time updates with GraphQL subscriptions
- Implement appointment booking directly from dashboard
- Add document upload capabilities
- Build interactive health metric charts

For more advanced features, use the MCP server tools:
- `query_templates(workflow: "patient_management")` - Get more query examples
- `field_relationships(source_type: "Patient")` - Explore related data
- `find_healthcare_patterns(category: "patient_data")` - Discover patterns
- See [Using MCP Tools](./using-mcp-tools.md) for comprehensive examples