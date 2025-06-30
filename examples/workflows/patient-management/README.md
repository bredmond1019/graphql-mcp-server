# Patient Management Workflow Examples

This directory contains complete examples for managing patient data throughout the entire patient lifecycle.

## 🎯 What You'll Learn

- Patient registration and onboarding
- Profile management and updates
- Patient search and filtering
- Medical record management
- HIPAA-compliant data handling
- Validation and error handling

## 📁 Files in This Directory

### Core Workflow Files
- **`patient-registration.js`** - Complete patient registration form with validation
- **`patient-search.js`** - Advanced patient search and filtering
- **`patient-dashboard.js`** - Comprehensive patient information dashboard
- **`profile-management.js`** - Patient profile updates and medical history

### Supporting Files
- **`validation-rules.js`** - Healthcare-specific validation patterns
- **`error-handling.js`** - Patient management error scenarios
- **`test-data.js`** - Sample patient data for testing
- **`README.md`** - This documentation

## 🚀 Quick Start

### 1. Basic Patient Registration

```javascript
// From patient-registration.js
import { PatientRegistration } from './patient-registration';

// Simple registration form
function App() {
  return (
    <PatientRegistration
      onSuccess={(patient) => {
        console.log('Patient registered:', patient);
        // Redirect to patient dashboard
        navigate(`/patients/${patient.id}`);
      }}
      onError={(error) => {
        console.error('Registration failed:', error);
        // Show user-friendly error message
      }}
    />
  );
}
```

### 2. Patient Search

```javascript
// From patient-search.js
import { PatientSearch } from './patient-search';

// Search with multiple criteria
function PatientDirectory() {
  const handleSearch = (results) => {
    setPatients(results);
  };

  return (
    <PatientSearch
      searchFields={['name', 'email', 'phone', 'medicalRecordNumber']}
      onResults={handleSearch}
      maxResults={50}
    />
  );
}
```

### 3. Patient Dashboard

```javascript
// From patient-dashboard.js
import { PatientDashboard } from './patient-dashboard';

// Complete patient information view
function PatientView({ patientId }) {
  return (
    <PatientDashboard 
      patientId={patientId}
      showSections={['demographics', 'appointments', 'medicalHistory', 'insurance']}
      editable={true}
    />
  );
}
```

## 🏥 Healthcare Context

### Patient Data Categories

**Demographics**
- Name, date of birth, gender
- Contact information (phone, email, address)
- Emergency contacts
- Language preferences

**Medical Information**
- Medical record number
- Primary care provider
- Medical history and conditions
- Allergies and medications
- Insurance information

**Compliance Fields**
- Consent for treatment
- HIPAA authorization
- Communication preferences
- Data sharing permissions

### HIPAA Considerations

All examples in this directory follow HIPAA best practices:

```javascript
// Example of HIPAA-compliant field access
const PatientData = {
  // Always check permissions before accessing PHI
  getPatientInfo: (patientId, userRole, requestedFields) => {
    const allowedFields = getPermittedFields(userRole);
    const filteredFields = requestedFields.filter(field => 
      allowedFields.includes(field)
    );
    
    return queryPatient(patientId, filteredFields);
  },
  
  // Log all PHI access for audit trails
  logAccess: (userId, patientId, accessType, fields) => {
    auditLog.record({
      timestamp: new Date(),
      userId,
      patientId,
      action: accessType,
      fieldsAccessed: fields,
      ipAddress: getClientIP()
    });
  }
};
```

## 🔧 Implementation Patterns

### 1. Validation-First Approach

```javascript
// Always validate before API calls
const createPatient = async (patientData) => {
  // Client-side validation first
  const validation = validatePatientData(patientData);
  if (!validation.isValid) {
    throw new ValidationError(validation.errors);
  }
  
  // Server-side validation through GraphQL
  try {
    const result = await graphqlClient.mutate({
      mutation: CREATE_PATIENT,
      variables: { input: patientData }
    });
    
    if (result.data.createPatient.errors?.length > 0) {
      throw new ServerValidationError(result.data.createPatient.errors);
    }
    
    return result.data.createPatient.patient;
    
  } catch (error) {
    // Handle different error types appropriately
    handlePatientError(error);
  }
};
```

### 2. Progressive Data Loading

```javascript
// Load patient data efficiently
const PatientDashboard = ({ patientId }) => {
  // Essential data first (for immediate display)
  const { data: essential } = useQuery(PATIENT_ESSENTIALS, {
    variables: { id: patientId }
  });
  
  // Secondary data (for tabs/sections)
  const { data: appointments } = useQuery(PATIENT_APPOINTMENTS, {
    variables: { patientId },
    skip: !essential // Wait for essential data
  });
  
  // Detailed data (loaded on demand)
  const [loadMedicalHistory, { data: medicalHistory }] = useLazyQuery(
    PATIENT_MEDICAL_HISTORY
  );
  
  return (
    <div>
      <PatientHeader patient={essential?.patient} />
      
      <Tabs>
        <Tab label="Appointments">
          <AppointmentsList appointments={appointments?.appointments} />
        </Tab>
        
        <Tab label="Medical History" onSelect={() => 
          loadMedicalHistory({ variables: { patientId }})
        }>
          <MedicalHistory history={medicalHistory?.medicalHistory} />
        </Tab>
      </Tabs>
    </div>
  );
};
```

### 3. Error Recovery Patterns

```javascript
// Comprehensive error handling for patient operations
const PatientErrorHandler = {
  handleRegistrationError: (error) => {
    if (error.message.includes('email already exists')) {
      return {
        type: 'DUPLICATE_EMAIL',
        message: 'A patient with this email already exists.',
        action: 'Try searching for the existing patient or use a different email.',
        recoverable: true
      };
    }
    
    if (error.message.includes('invalid date of birth')) {
      return {
        type: 'INVALID_DOB',
        message: 'Please enter a valid date of birth.',
        action: 'Use MM/DD/YYYY format and ensure the date is in the past.',
        recoverable: true
      };
    }
    
    // Generic error handling
    return {
      type: 'UNKNOWN_ERROR',
      message: 'Registration failed. Please try again.',
      action: 'If the problem persists, contact support.',
      recoverable: false
    };
  }
};
```

## 📊 Example Use Cases

### Healthcare Clinic Registration
- New patient intake forms
- Insurance verification
- Medical history collection
- Provider assignment

### Hospital Patient Management
- Admission and discharge workflows
- Room and bed management
- Care team assignments
- Family contact management

### Telehealth Platform
- Remote patient onboarding
- Virtual visit preparation
- Digital consent management
- Technology access verification

### Specialty Practice
- Referral patient intake
- Specialized medical history forms
- Insurance pre-authorization
- Follow-up care coordination

## 🧪 Testing Examples

Each workflow includes comprehensive tests:

```javascript
// Example test for patient registration
describe('Patient Registration', () => {
  test('successful registration with valid data', async () => {
    const validPatientData = {
      firstName: 'John',
      lastName: 'Doe',
      email: 'john.doe@example.com',
      dateOfBirth: '1990-01-01',
      phoneNumber: '+1234567890'
    };
    
    const result = await createPatient(validPatientData);
    
    expect(result).toHaveProperty('id');
    expect(result.email).toBe(validPatientData.email);
    expect(result.firstName).toBe(validPatientData.firstName);
  });
  
  test('registration fails with duplicate email', async () => {
    const duplicateEmailData = {
      firstName: 'Jane',
      lastName: 'Smith', 
      email: 'existing@example.com', // Already exists
      dateOfBirth: '1985-05-15',
      phoneNumber: '+0987654321'
    };
    
    await expect(createPatient(duplicateEmailData))
      .rejects
      .toThrow('email already exists');
  });
});
```

## 🎓 Learning Progression

### Beginner
1. Start with `patient-registration.js` for basic GraphQL mutations
2. Review `validation-rules.js` for healthcare data validation
3. Try `patient-search.js` for query patterns

### Intermediate  
1. Study `patient-dashboard.js` for complex data loading
2. Implement `profile-management.js` for update operations
3. Add comprehensive error handling patterns

### Advanced
1. Customize validation rules for your specific use case
2. Implement role-based access control
3. Add audit logging and compliance features
4. Optimize performance for large patient databases

## 💡 Tips for Implementation

1. **Start with validation** - Healthcare data has strict requirements
2. **Think mobile-first** - Many users will access on mobile devices  
3. **Plan for offline** - Healthcare settings may have connectivity issues
4. **Consider accessibility** - Healthcare apps must be accessible to all users
5. **Test with real data** - Use realistic patient scenarios for testing
6. **Plan for scale** - Large healthcare organizations have thousands of patients

Ready to build patient management features? Start with the basic registration example and build up to the full dashboard implementation!