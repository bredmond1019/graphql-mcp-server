# Appointment Scheduling Tutorial

Learn how to implement appointment scheduling with Healthie's GraphQL API.

## Overview

This tutorial covers the essentials of building an appointment system:
- Fetching provider availability  
- Creating appointments
- Managing appointment status
- Handling conflicts

## Key GraphQL Operations

### 1. Check Provider Availability

```graphql
query GetAvailability($provider_id: ID!, $start_date: String!, $end_date: String!) {
  provider(id: $provider_id) {
    id
    first_name
    last_name
    availabilities(start_date: $start_date, end_date: $end_date) {
      id
      date
      start_time
      end_time
      is_available
    }
  }
}
```

### 2. Create Appointment

```graphql
mutation CreateAppointment($input: createAppointmentInput!) {
  createAppointment(input: $input) {
    appointment {
      id
      date
      time
      end_time
      contact_type
      attendees {
        id
        first_name
        last_name
        email
      }
      location {
        id
        name
        line1
      }
    }
    messages
  }
}
```

### 3. Update Appointment Status

```graphql
mutation UpdateAppointment($id: ID!, $input: updateAppointmentInput!) {
  updateAppointment(id: $id, input: $input) {
    appointment {
      id
      status
      cancellation_note
    }
    messages
  }
}
```

## JavaScript Implementation

```javascript
import { ApolloClient, InMemoryCache, gql } from '@apollo/client';

const client = new ApolloClient({
  uri: 'https://api.gethealthie.com/graphql',
  cache: new InMemoryCache(),
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY'
  }
});

// Book an appointment
async function bookAppointment(appointmentData) {
  const CREATE_APPOINTMENT = gql`
    mutation CreateAppointment($input: createAppointmentInput!) {
      createAppointment(input: $input) {
        appointment {
          id
          date
          time
          contact_type
          attendees {
            first_name
            last_name
          }
        }
        messages
      }
    }
  `;

  try {
    const { data } = await client.mutate({
      mutation: CREATE_APPOINTMENT,
      variables: {
        input: {
          date: appointmentData.date,
          time: appointmentData.time,
          end_time: appointmentData.end_time,
          contact_type: appointmentData.contact_type || "video_call",
          attendee_ids: [appointmentData.patient_id],
          provider_id: appointmentData.provider_id,
          appointment_type_id: appointmentData.appointment_type_id
        }
      }
    });

    if (data.createAppointment.messages?.length > 0) {
      console.error('Validation errors:', data.createAppointment.messages);
      return null;
    }

    return data.createAppointment.appointment;
  } catch (error) {
    console.error('Error creating appointment:', error);
    throw error;
  }
}

// Get provider's appointments
async function getProviderAppointments(providerId, date) {
  const GET_APPOINTMENTS = gql`
    query GetProviderAppointments($provider_id: ID!, $date: String!) {
      appointments(provider_id: $provider_id, date: $date) {
        id
        date
        time
        end_time
        status
        contact_type
        attendees {
          id
          first_name
          last_name
        }
      }
    }
  `;

  const { data } = await client.query({
    query: GET_APPOINTMENTS,
    variables: { provider_id: providerId, date: date }
  });

  return data.appointments;
}
```

## Python Implementation

```python
import requests
from datetime import datetime, timedelta

HEALTHIE_API_URL = "https://api.gethealthie.com/graphql"
API_KEY = "YOUR_API_KEY"

def create_appointment(appointment_data):
    """Create a new appointment in Healthie"""
    
    query = """
    mutation CreateAppointment($input: createAppointmentInput!) {
      createAppointment(input: $input) {
        appointment {
          id
          date
          time
          end_time
          contact_type
          attendees {
            id
            first_name
            last_name
          }
        }
        messages
      }
    }
    """
    
    variables = {
        "input": {
            "date": appointment_data["date"],
            "time": appointment_data["time"],
            "end_time": appointment_data["end_time"],
            "contact_type": appointment_data.get("contact_type", "video_call"),
            "attendee_ids": [appointment_data["patient_id"]],
            "provider_id": appointment_data["provider_id"],
            "appointment_type_id": appointment_data.get("appointment_type_id")
        }
    }
    
    response = requests.post(
        HEALTHIE_API_URL,
        json={"query": query, "variables": variables},
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
    )
    
    result = response.json()
    
    if "errors" in result:
        raise Exception(f"GraphQL errors: {result['errors']}")
    
    return result["data"]["createAppointment"]["appointment"]

def check_availability(provider_id, date):
    """Check provider availability for a specific date"""
    
    query = """
    query CheckAvailability($provider_id: ID!, $date: String!) {
      provider(id: $provider_id) {
        availabilities(date: $date) {
          id
          date
          start_time
          end_time
          is_available
        }
        appointments(date: $date) {
          time
          end_time
          status
        }
      }
    }
    """
    
    response = requests.post(
        HEALTHIE_API_URL,
        json={
            "query": query,
            "variables": {"provider_id": provider_id, "date": date}
        },
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
    )
    
    return response.json()["data"]["provider"]
```

## Common Appointment Types

Healthie supports various contact types for appointments:
- `video_call` - Telehealth video appointments
- `phone_call` - Phone consultations  
- `in_person` - Office visits
- `chat` - Asynchronous chat sessions

## Error Handling

Always check the `messages` field in mutations for validation errors:

```javascript
if (data.createAppointment.messages?.length > 0) {
  // Handle validation errors
  data.createAppointment.messages.forEach(msg => {
    console.error(`Validation error: ${msg}`);
  });
}
```

## Using MCP Tools for Appointments

### Discover Appointment Schema

```python
# Find all appointment-related operations
apt_search = search_schema("appointment")
# Returns 96+ appointment mutations and types

# Get detailed appointment type info
apt_type = introspect_type("Appointment")
# Shows all 98 fields with relationships
```

### Generate Appointment Code

```python
# Get tested appointment templates
templates = query_templates(workflow="appointments")

# Generate booking implementation
booking_code = code_examples(
    operation="book_appointment",
    language="javascript"
)
```

### Debug Common Issues

```python
# When you get errors
error_decoder("Cannot query field 'appointmentDate' on type 'Appointment'")
# Returns: "Use 'date' instead of 'appointmentDate'"
```

## Next Steps

- Implement appointment reminders using Healthie's notification system
- Add recurring appointment support
- Build a calendar UI to visualize appointments
- Set up webhook notifications for appointment changes

For more details, use the MCP server tools:
- `query_templates(workflow: "appointments")` - Get pre-built queries
- `find_healthcare_patterns(category: "appointments")` - Explore appointment patterns
- `field_relationships(source_type: "Appointment")` - Understand related fields
- See [Using MCP Tools](./using-mcp-tools.md) for comprehensive examples