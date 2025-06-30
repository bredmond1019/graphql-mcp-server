# Building a Patient Dashboard Tutorial

Learn how to build a comprehensive patient dashboard using the Healthie MCP Server and React.

## 🎯 What We'll Build

A responsive patient dashboard that displays:
- Patient demographics and contact information
- Recent appointments and upcoming scheduling
- Medical history summary
- Insurance information
- Quick action buttons for common tasks

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React App     │◄──►│  Apollo Client   │◄──►│ Healthie API    │
│                 │    │                  │    │                 │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │ Dashboard   │ │    │ │ Query Cache  │ │    │ │ GraphQL     │ │
│ │ Components  │ │    │ │              │ │    │ │ Schema      │ │
│ └─────────────┘ │    │ └──────────────┘ │    │ └─────────────┘ │
│                 │    │                  │    │                 │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │ Error       │ │    │ │ Auth Handler │ │    │ │ Patient     │ │
│ │ Boundaries  │ │    │ │              │ │    │ │ Data        │ │
│ └─────────────┘ │    │ └──────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                ▲
                                │
                    ┌──────────────────┐
                    │  MCP Server      │
                    │  (Query Helper)  │
                    └──────────────────┘
```

## 📋 Prerequisites

Before starting, ensure you have:
- Node.js 18+ installed
- React development environment set up
- Healthie MCP Server running
- Basic understanding of GraphQL and React

## 🚀 Step 1: Project Setup

### Initialize React Project

```bash
# Create new React app
npx create-react-app patient-dashboard
cd patient-dashboard

# Install dependencies
npm install @apollo/client graphql react-router-dom
npm install @mui/material @emotion/react @emotion/styled  # For UI components
npm install @mui/icons-material @mui/lab
npm install date-fns  # For date handling
```

### Apollo Client Setup

First, use the MCP server to get the optimal Apollo Client configuration:

```bash
# Get code examples from MCP server
code_examples category="patient_management" language="javascript"
```

Create `src/apollo/client.js`:

```javascript
import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';

const httpLink = createHttpLink({
  uri: process.env.REACT_APP_HEALTHIE_API_URL || 'https://staging-api.gethealthie.com/graphql',
});

const authLink = setContext((_, { headers }) => {
  const token = localStorage.getItem('healthie_auth_token');
  
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : "",
      'Content-Type': 'application/json',
    }
  };
});

// Healthcare-optimized cache configuration
const cache = new InMemoryCache({
  typePolicies: {
    Patient: {
      keyFields: ['id'],
      fields: {
        appointments: {
          merge(existing = [], incoming) {
            return [...existing, ...incoming];
          }
        }
      }
    },
    Appointment: {
      keyFields: ['id']
    }
  }
});

export const apolloClient = new ApolloClient({
  link: authLink.concat(httpLink),
  cache,
  defaultOptions: {
    query: {
      fetchPolicy: 'cache-first',
      errorPolicy: 'all'
    }
  }
});
```

## 🔍 Step 2: Define GraphQL Queries

Use the MCP server to get optimal queries:

```bash
# Get query templates
query_templates workflow="patient_management"

# Get field usage recommendations
field_usage type_name="Patient" context="dashboard"
```

Create `src/queries/patientQueries.js`:

```javascript
import { gql } from '@apollo/client';

// Essential patient information for dashboard
export const GET_PATIENT_DASHBOARD = gql`
  query GetPatientDashboard($id: ID!) {
    patient(id: $id) {
      # Core identification
      id
      firstName
      lastName
      email
      phoneNumber
      dateOfBirth
      
      # Contact information
      address {
        street
        city
        state
        zipCode
      }
      
      # Recent appointments (limit for performance)
      appointments(limit: 5, orderBy: { field: START_TIME, direction: DESC }) {
        id
        startTime
        endTime
        status
        appointmentType
        provider {
          id
          firstName
          lastName
          specialty
        }
        notes
      }
      
      # Upcoming appointments
      upcomingAppointments: appointments(
        limit: 3, 
        filter: { startTimeAfter: "${new Date().toISOString()}" }
        orderBy: { field: START_TIME, direction: ASC }
      ) {
        id
        startTime
        endTime
        status
        appointmentType
        provider {
          id
          firstName
          lastName
        }
      }
      
      # Insurance information
      insuranceInfo {
        id
        provider
        memberNumber
        groupNumber
        # Note: Exclude sensitive details for dashboard view
      }
      
      # Medical summary (high-level only for dashboard)
      medicalSummary {
        primaryCareProvider {
          id
          firstName
          lastName
        }
        allergies {
          id
          allergen
          severity
        }
        # Note: Detailed medical history loaded separately for performance
      }
    }
  }
`;

// Separate query for detailed medical history (loaded on demand)
export const GET_PATIENT_MEDICAL_HISTORY = gql`
  query GetPatientMedicalHistory($id: ID!) {
    patient(id: $id) {
      id
      medicalHistory {
        id
        condition
        diagnosisDate
        status
        notes
      }
      prescriptions {
        id
        medicationName
        dosage
        frequency
        prescribedDate
        status
      }
      clinicalNotes(limit: 10) {
        id
        noteType
        createdAt
        provider {
          firstName
          lastName
        }
        # Note: Content excluded for privacy - load separately if needed
      }
    }
  }
`;

// Quick actions queries
export const UPDATE_PATIENT_CONTACT = gql`
  mutation UpdatePatientContact($id: ID!, $input: UpdatePatientInput!) {
    updatePatient(id: $id, input: $input) {
      patient {
        id
        email
        phoneNumber
        address {
          street
          city
          state
          zipCode
        }
      }
      errors
    }
  }
`;
```

## 🧱 Step 3: Build Dashboard Components

### Main Dashboard Component

Create `src/components/PatientDashboard.js`:

```javascript
import React, { useState } from 'react';
import { useQuery } from '@apollo/client';
import { useParams } from 'react-router-dom';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Tabs,
  Tab
} from '@mui/material';

import { GET_PATIENT_DASHBOARD } from '../queries/patientQueries';
import PatientHeader from './PatientHeader';
import AppointmentsList from './AppointmentsList';
import MedicalSummary from './MedicalSummary';
import InsuranceCard from './InsuranceCard';
import QuickActions from './QuickActions';

export default function PatientDashboard() {
  const { patientId } = useParams();
  const [activeTab, setActiveTab] = useState(0);
  
  const { loading, error, data, refetch } = useQuery(GET_PATIENT_DASHBOARD, {
    variables: { id: patientId },
    errorPolicy: 'all',
    notifyOnNetworkStatusChange: true
  });

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" mt={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (error && !data) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        Failed to load patient data: {error.message}
      </Alert>
    );
  }

  const patient = data?.patient;
  
  if (!patient) {
    return (
      <Alert severity="warning" sx={{ mt: 2 }}>
        Patient not found
      </Alert>
    );
  }

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Patient Header */}
      <PatientHeader patient={patient} onRefresh={refetch} />
      
      {/* Quick Actions */}
      <QuickActions patient={patient} onUpdate={refetch} />
      
      {/* Main Content Tabs */}
      <Box sx={{ mt: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="Overview" />
          <Tab label="Appointments" />
          <Tab label="Medical History" />
          <Tab label="Insurance" />
        </Tabs>
        
        {/* Tab Panels */}
        <Box sx={{ mt: 2 }}>
          {activeTab === 0 && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <AppointmentsList 
                  appointments={patient.appointments}
                  upcoming={patient.upcomingAppointments}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <MedicalSummary summary={patient.medicalSummary} />
              </Grid>
            </Grid>
          )}
          
          {activeTab === 1 && (
            <AppointmentsList 
              appointments={[...patient.appointments, ...patient.upcomingAppointments]}
              showAllDetails={true}
            />
          )}
          
          {activeTab === 2 && (
            <MedicalSummary 
              summary={patient.medicalSummary} 
              patientId={patient.id}
              detailed={true}
            />
          )}
          
          {activeTab === 3 && (
            <InsuranceCard insuranceInfo={patient.insuranceInfo} />
          )}
        </Box>
      </Box>
    </Box>
  );
}
```

### Patient Header Component

Create `src/components/PatientHeader.js`:

```javascript
import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Avatar,
  Chip,
  IconButton,
  Grid
} from '@mui/material';
import {
  Person,
  Email,
  Phone,
  LocationOn,
  Refresh
} from '@mui/icons-material';
import { format } from 'date-fns';

export default function PatientHeader({ patient, onRefresh }) {
  const getInitials = (firstName, lastName) => {
    return `${firstName?.[0] || ''}${lastName?.[0] || ''}`.toUpperCase();
  };

  const formatAddress = (address) => {
    if (!address) return 'No address on file';
    return `${address.street}, ${address.city}, ${address.state} ${address.zipCode}`;
  };

  const calculateAge = (dateOfBirth) => {
    if (!dateOfBirth) return 'Unknown';
    const today = new Date();
    const birth = new Date(dateOfBirth);
    const age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      return age - 1;
    }
    return age;
  };

  return (
    <Card elevation={2}>
      <CardContent>
        <Grid container spacing={3} alignItems="center">
          <Grid item>
            <Avatar 
              sx={{ width: 80, height: 80, bgcolor: 'primary.main' }}
            >
              {getInitials(patient.firstName, patient.lastName)}
            </Avatar>
          </Grid>
          
          <Grid item xs>
            <Box>
              <Typography variant="h4" component="h1" gutterBottom>
                {patient.firstName} {patient.lastName}
              </Typography>
              
              <Box display="flex" gap={1} mb={2}>
                <Chip 
                  icon={<Person />}
                  label={`Age ${calculateAge(patient.dateOfBirth)}`}
                  size="small"
                />
                <Chip 
                  label={`DOB: ${format(new Date(patient.dateOfBirth), 'MM/dd/yyyy')}`}
                  size="small"
                />
              </Box>
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Email fontSize="small" color="action" />
                    <Typography variant="body2">
                      {patient.email || 'No email on file'}
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Phone fontSize="small" color="action" />
                    <Typography variant="body2">
                      {patient.phoneNumber || 'No phone on file'}
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <LocationOn fontSize="small" color="action" />
                    <Typography variant="body2">
                      {formatAddress(patient.address)}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </Box>
          </Grid>
          
          <Grid item>
            <IconButton onClick={onRefresh} title="Refresh patient data">
              <Refresh />
            </IconButton>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
}
```

### Appointments List Component

Create `src/components/AppointmentsList.js`:

```javascript
import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Box,
  Divider
} from '@mui/material';
import {
  Event,
  Person,
  Schedule
} from '@mui/icons-material';
import { format, isAfter } from 'date-fns';

export default function AppointmentsList({ appointments = [], upcoming = [], showAllDetails = false }) {
  const getStatusColor = (status) => {
    const colors = {
      scheduled: 'primary',
      completed: 'success',
      cancelled: 'error',
      no_show: 'warning'
    };
    return colors[status] || 'default';
  };

  const formatAppointmentTime = (startTime, endTime) => {
    const start = new Date(startTime);
    const end = new Date(endTime);
    
    return `${format(start, 'MMM dd, yyyy')} ${format(start, 'h:mm a')} - ${format(end, 'h:mm a')}`;
  };

  const allAppointments = showAllDetails 
    ? [...appointments, ...upcoming].sort((a, b) => new Date(b.startTime) - new Date(a.startTime))
    : appointments;

  const upcomingAppointments = upcoming.filter(apt => 
    isAfter(new Date(apt.startTime), new Date())
  );

  return (
    <Box>
      {/* Upcoming Appointments */}
      {!showAllDetails && upcomingAppointments.length > 0 && (
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Upcoming Appointments
            </Typography>
            <List dense>
              {upcomingAppointments.map((appointment) => (
                <ListItem key={appointment.id}>
                  <ListItemIcon>
                    <Schedule />
                  </ListItemIcon>
                  <ListItemText
                    primary={formatAppointmentTime(appointment.startTime, appointment.endTime)}
                    secondary={`${appointment.provider.firstName} ${appointment.provider.lastName} - ${appointment.appointmentType}`}
                  />
                  <Chip
                    label={appointment.status}
                    color={getStatusColor(appointment.status)}
                    size="small"
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {/* Recent/All Appointments */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {showAllDetails ? 'All Appointments' : 'Recent Appointments'}
          </Typography>
          
          {allAppointments.length === 0 ? (
            <Typography variant="body2" color="text.secondary">
              No appointments found
            </Typography>
          ) : (
            <List>
              {allAppointments.map((appointment, index) => (
                <React.Fragment key={appointment.id}>
                  <ListItem alignItems="flex-start">
                    <ListItemIcon>
                      <Event />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Typography component="span">
                            {formatAppointmentTime(appointment.startTime, appointment.endTime)}
                          </Typography>
                          <Chip
                            label={appointment.status}
                            color={getStatusColor(appointment.status)}
                            size="small"
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Box display="flex" alignItems="center" gap={1} mt={1}>
                            <Person fontSize="small" />
                            <Typography variant="body2">
                              {appointment.provider.firstName} {appointment.provider.lastName}
                              {appointment.provider.specialty && ` - ${appointment.provider.specialty}`}
                            </Typography>
                          </Box>
                          <Typography variant="body2" sx={{ mt: 1 }}>
                            Type: {appointment.appointmentType}
                          </Typography>
                          {appointment.notes && (
                            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                              Notes: {appointment.notes}
                            </Typography>
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                  {index < allAppointments.length - 1 && <Divider variant="inset" component="li" />}
                </React.Fragment>
              ))}
            </List>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}
```

## 🔐 Step 4: HIPAA-Compliant Features

### Access Control

```javascript
// src/hooks/usePatientAccess.js
import { useState, useEffect } from 'react';

export function usePatientAccess(patientId, userRole) {
  const [accessLevel, setAccessLevel] = useState('none');
  
  useEffect(() => {
    // Determine access level based on user role and patient relationship
    const determineAccess = () => {
      if (userRole === 'admin') return 'full';
      if (userRole === 'provider') return 'clinical';
      if (userRole === 'staff') return 'basic';
      return 'none';
    };
    
    setAccessLevel(determineAccess());
  }, [patientId, userRole]);
  
  const canViewField = (fieldName) => {
    const fieldPermissions = {
      full: ['*'],
      clinical: ['demographics', 'appointments', 'medicalHistory', 'clinicalNotes'],
      basic: ['demographics', 'appointments', 'insurance'],
      none: []
    };
    
    const allowedFields = fieldPermissions[accessLevel] || [];
    return allowedFields.includes('*') || allowedFields.includes(fieldName);
  };
  
  return { accessLevel, canViewField };
}
```

### Audit Logging

```javascript
// src/utils/auditLogger.js
export class AuditLogger {
  static logPatientAccess(patientId, userId, action, fields = []) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      patientId: patientId,
      userId: userId,
      action: action,
      fieldsAccessed: fields,
      userAgent: navigator.userAgent,
      sessionId: sessionStorage.getItem('sessionId')
    };
    
    // Send to secure audit endpoint
    fetch('/api/audit/log', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(logEntry)
    }).catch(console.error);
  }
}

// Usage in components
useEffect(() => {
  if (patient) {
    AuditLogger.logPatientAccess(
      patient.id,
      currentUser.id,
      'dashboard_view',
      ['demographics', 'appointments']
    );
  }
}, [patient]);
```

## 🎨 Step 5: UI Polish & Performance

### Loading States

```javascript
// src/components/LoadingStates.js
import React from 'react';
import { Skeleton, Card, CardContent, Box } from '@mui/material';

export function PatientHeaderSkeleton() {
  return (
    <Card elevation={2}>
      <CardContent>
        <Box display="flex" gap={3} alignItems="center">
          <Skeleton variant="circular" width={80} height={80} />
          <Box flex={1}>
            <Skeleton variant="text" sx={{ fontSize: '2rem' }} width="60%" />
            <Box display="flex" gap={1} mt={1}>
              <Skeleton variant="rectangular" width={80} height={24} />
              <Skeleton variant="rectangular" width={120} height={24} />
            </Box>
            <Skeleton variant="text" width="80%" />
            <Skeleton variant="text" width="70%" />
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}

export function AppointmentListSkeleton() {
  return (
    <Card>
      <CardContent>
        <Skeleton variant="text" sx={{ fontSize: '1.5rem' }} width="40%" />
        {[1, 2, 3].map(i => (
          <Box key={i} display="flex" gap={2} mt={2}>
            <Skeleton variant="circular" width={24} height={24} />
            <Box flex={1}>
              <Skeleton variant="text" width="80%" />
              <Skeleton variant="text" width="60%" />
            </Box>
          </Box>
        ))}
      </CardContent>
    </Card>
  );
}
```

### Error Boundaries

```javascript
// src/components/ErrorBoundary.js
import React from 'react';
import { Alert, Button, Box } from '@mui/material';

class PatientDashboardError extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Log error to monitoring service
    console.error('Patient dashboard error:', error, errorInfo);
    
    // Don't log patient data for privacy
    const sanitizedError = {
      message: error.message,
      stack: error.stack,
      component: 'PatientDashboard'
    };
    
    // Send to error tracking (without PHI)
    this.logError(sanitizedError);
  }

  logError = (error) => {
    // Send to error tracking service
    fetch('/api/errors', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(error)
    }).catch(console.error);
  };

  render() {
    if (this.state.hasError) {
      return (
        <Box sx={{ p: 3 }}>
          <Alert severity="error">
            <strong>Something went wrong</strong>
            <br />
            We're sorry, but there was an error loading the patient dashboard.
            <br />
            <Button 
              onClick={() => window.location.reload()}
              sx={{ mt: 1 }}
            >
              Reload Page
            </Button>
          </Alert>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default PatientDashboardError;
```

## 🧪 Step 6: Testing

### Component Tests

```javascript
// src/components/__tests__/PatientDashboard.test.js
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MockedProvider } from '@apollo/client/testing';
import { BrowserRouter } from 'react-router-dom';
import PatientDashboard from '../PatientDashboard';
import { GET_PATIENT_DASHBOARD } from '../../queries/patientQueries';

const mockPatient = {
  id: 'patient-123',
  firstName: 'John',
  lastName: 'Doe',
  email: 'john.doe@example.com',
  phoneNumber: '+1234567890',
  dateOfBirth: '1990-01-15',
  address: {
    street: '123 Main St',
    city: 'Anytown',
    state: 'CA',
    zipCode: '12345'
  },
  appointments: [],
  upcomingAppointments: [],
  insuranceInfo: null,
  medicalSummary: null
};

const mocks = [
  {
    request: {
      query: GET_PATIENT_DASHBOARD,
      variables: { id: 'patient-123' }
    },
    result: {
      data: {
        patient: mockPatient
      }
    }
  }
];

const renderWithProviders = (component) => {
  return render(
    <BrowserRouter>
      <MockedProvider mocks={mocks} addTypename={false}>
        {component}
      </MockedProvider>
    </BrowserRouter>
  );
};

// Mock useParams
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({ patientId: 'patient-123' })
}));

describe('PatientDashboard', () => {
  test('renders patient information correctly', async () => {
    renderWithProviders(<PatientDashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('john.doe@example.com')).toBeInTheDocument();
      expect(screen.getByText('+1234567890')).toBeInTheDocument();
    });
  });

  test('shows loading state initially', () => {
    renderWithProviders(<PatientDashboard />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  test('handles patient not found', async () => {
    const errorMocks = [
      {
        request: {
          query: GET_PATIENT_DASHBOARD,
          variables: { id: 'patient-123' }
        },
        result: {
          data: { patient: null }
        }
      }
    ];

    render(
      <BrowserRouter>
        <MockedProvider mocks={errorMocks} addTypename={false}>
          <PatientDashboard />
        </MockedProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Patient not found')).toBeInTheDocument();
    });
  });
});
```

## 🚀 Step 7: Deployment & Optimization

### Environment Configuration

```javascript
// .env.production
REACT_APP_HEALTHIE_API_URL=https://api.gethealthie.com/graphql
REACT_APP_AUDIT_ENDPOINT=https://audit.yourdomain.com/api
REACT_APP_ERROR_TRACKING=https://errors.yourdomain.com
```

### Performance Optimizations

```javascript
// src/utils/performanceOptimizations.js
import { useCallback, useMemo } from 'react';

// Memoize expensive calculations
export function usePatientAge(dateOfBirth) {
  return useMemo(() => {
    if (!dateOfBirth) return null;
    const today = new Date();
    const birth = new Date(dateOfBirth);
    return today.getFullYear() - birth.getFullYear();
  }, [dateOfBirth]);
}

// Optimize appointment filtering
export function useFilteredAppointments(appointments, filter) {
  return useMemo(() => {
    if (!filter) return appointments;
    return appointments.filter(apt => 
      apt.status === filter || 
      apt.appointmentType.toLowerCase().includes(filter.toLowerCase())
    );
  }, [appointments, filter]);
}

// Debounced search
export function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = React.useState(value);

  React.useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}
```

## 📋 Summary

You've built a comprehensive patient dashboard that includes:

✅ **Healthcare-optimized GraphQL queries** using MCP server guidance  
✅ **HIPAA-compliant access controls** and audit logging  
✅ **Responsive UI** with Material-UI components  
✅ **Performance optimizations** with Apollo Client caching  
✅ **Error handling** and loading states  
✅ **Comprehensive testing** setup  

### Next Steps

1. **Add more sections:** Lab results, medications, care plans
2. **Implement real-time updates:** WebSocket subscriptions for live data
3. **Add mobile responsiveness:** PWA features for mobile access
4. **Enhance security:** Multi-factor authentication, session management
5. **Add analytics:** User interaction tracking for UX improvements

### Resources

- [Healthie API Documentation](https://docs.gethealthie.com)
- [Apollo Client Best Practices](https://www.apollographql.com/docs/react/performance/optimistic-ui/)
- [HIPAA Compliance Guidelines](https://www.hhs.gov/hipaa/for-professionals/security/guidance/index.html)
- [React Performance Optimization](https://react.dev/learn/render-and-commit)

This tutorial provides a solid foundation for building healthcare applications with proper security, performance, and user experience considerations.