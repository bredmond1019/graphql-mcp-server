/**
 * Code Generation Examples
 * 
 * Demonstrates how to use the code_examples tool to generate
 * working code in JavaScript, Python, and cURL for common operations.
 * 
 * All generated code includes error handling and best practices.
 */

// Example 1: Generate JavaScript/React Code
async function generateJavaScriptCode() {
  // Generate patient creation code
  const patientCode = await mcp.code_examples({
    operation: "create_patient",
    language: "javascript"
  });
  
  console.log("Generated React Component:");
  console.log(patientCode.code);
  
  // The generated code includes:
  // - Apollo Client setup
  // - GraphQL mutation
  // - React component with form handling
  // - Error handling
  // - Loading states
  
  return patientCode;
}

// Example 2: Generate Python Implementation
async function generatePythonCode() {
  // Generate appointment booking code
  const appointmentCode = await mcp.code_examples({
    operation: "book_appointment",
    language: "python"
  });
  
  console.log("Generated Python Function:");
  console.log(appointmentCode.code);
  
  // The generated code includes:
  // - Requests library usage
  // - Proper authentication headers
  // - Error handling
  // - Type hints
  // - Docstrings
  
  return appointmentCode;
}

// Example 3: Generate cURL Commands
async function generateCurlCommands() {
  // Generate patient query cURL
  const curlCode = await mcp.code_examples({
    operation: "get_patient",
    language: "curl"
  });
  
  console.log("Generated cURL Command:");
  console.log(curlCode.code);
  
  // The generated command includes:
  // - Correct endpoint
  // - Authentication headers
  // - GraphQL query structure
  // - Variable substitution
  
  return curlCode;
}

// Example 4: Generate Multiple Language Versions
async function generateMultiLanguageSDK() {
  const operations = [
    "create_patient",
    "update_patient",
    "get_patient",
    "search_patients",
    "book_appointment",
    "cancel_appointment"
  ];
  
  const languages = ["javascript", "python", "curl"];
  const sdk = {};
  
  for (const operation of operations) {
    sdk[operation] = {};
    
    for (const language of languages) {
      const code = await mcp.code_examples({
        operation: operation,
        language: language
      });
      
      sdk[operation][language] = code.code;
    }
  }
  
  return sdk;
}

// Example 5: Custom Code Generation Patterns
async function customizeGeneratedCode() {
  // Get base code
  const baseCode = await mcp.code_examples({
    operation: "create_patient",
    language: "javascript"
  });
  
  // Customize for your needs
  let customCode = baseCode.code;
  
  // Add custom error handling
  customCode = customCode.replace(
    "console.error('Error creating patient:', error);",
    `console.error('Error creating patient:', error);
    // Custom error tracking
    trackError('patient_creation_failed', error);
    // Show user-friendly message
    showNotification('Failed to create patient. Please try again.');`
  );
  
  // Add custom success handling
  customCode = customCode.replace(
    "console.log('Patient created:', data.createPatient.patient);",
    `console.log('Patient created:', data.createPatient.patient);
    // Custom success tracking
    trackEvent('patient_created', { patientId: data.createPatient.patient.id });
    // Redirect to patient profile
    navigate(\`/patients/\${data.createPatient.patient.id}\`);`
  );
  
  return customCode;
}

// Example 6: Generate TypeScript Code
async function generateTypeScriptCode() {
  // Get JavaScript code as base
  const jsCode = await mcp.code_examples({
    operation: "create_patient",
    language: "javascript"
  });
  
  // Convert to TypeScript
  let tsCode = jsCode.code;
  
  // Add type definitions
  const typeDefinitions = `
interface CreatePatientInput {
  firstName: string;
  lastName: string;
  email: string;
  dateOfBirth: string;
  phoneNumber?: string;
  gender?: 'male' | 'female' | 'other';
}

interface Patient {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  dateOfBirth: string;
  createdAt: string;
}

interface CreatePatientResponse {
  createPatient: {
    patient: Patient;
    errors?: Array<{
      field: string;
      message: string;
    }>;
  };
}
`;
  
  // Add types to the code
  tsCode = typeDefinitions + '\n' + tsCode;
  
  // Update function signatures
  tsCode = tsCode.replace(
    "const handleSubmit = async (formData) => {",
    "const handleSubmit = async (formData: CreatePatientInput): Promise<void> => {"
  );
  
  tsCode = tsCode.replace(
    "const { data } = await createPatient({",
    "const { data } = await createPatient<CreatePatientResponse>({"
  );
  
  return tsCode;
}

// Example 7: Generate Test Code
async function generateTestCode() {
  // Get the implementation code
  const implementation = await mcp.code_examples({
    operation: "create_patient",
    language: "javascript"
  });
  
  // Generate corresponding test code
  const testCode = `
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MockedProvider } from '@apollo/client/testing';
import { CreatePatientForm } from './CreatePatientForm';

const CREATE_PATIENT_MOCK = {
  request: {
    query: CREATE_PATIENT,
    variables: {
      input: {
        firstName: "John",
        lastName: "Doe",
        email: "john.doe@test.com",
        dateOfBirth: "1990-01-01",
        phoneNumber: "+1234567890"
      }
    }
  },
  result: {
    data: {
      createPatient: {
        patient: {
          id: "123",
          firstName: "John",
          lastName: "Doe",
          email: "john.doe@test.com"
        },
        errors: null
      }
    }
  }
};

describe('CreatePatientForm', () => {
  it('successfully creates a patient', async () => {
    const onSuccess = jest.fn();
    
    render(
      <MockedProvider mocks={[CREATE_PATIENT_MOCK]}>
        <CreatePatientForm onSuccess={onSuccess} />
      </MockedProvider>
    );
    
    // Fill form
    fireEvent.change(screen.getByLabelText('First Name'), {
      target: { value: 'John' }
    });
    fireEvent.change(screen.getByLabelText('Last Name'), {
      target: { value: 'Doe' }
    });
    fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: 'john.doe@test.com' }
    });
    
    // Submit
    fireEvent.click(screen.getByText('Create Patient'));
    
    // Verify success
    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalledWith({
        id: "123",
        firstName: "John",
        lastName: "Doe",
        email: "john.doe@test.com"
      });
    });
  });
  
  it('handles validation errors', async () => {
    // Test validation error handling
  });
});
`;
  
  return testCode;
}

// Example 8: Generate API Client Class
async function generateAPIClient() {
  // Generate a complete API client from multiple operations
  const operations = [
    "create_patient",
    "get_patient",
    "update_patient",
    "search_patients"
  ];
  
  let clientClass = `
import axios from 'axios';

class HealthieAPIClient {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseURL = 'https://api.gethealthie.com/graphql';
    
    this.client = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Authorization': \`Basic \${apiKey}\`,
        'AuthorizationSource': 'API',
        'Content-Type': 'application/json'
      }
    });
  }
  
  async query(query, variables = {}) {
    try {
      const response = await this.client.post('', {
        query,
        variables
      });
      
      if (response.data.errors) {
        throw new GraphQLError(response.data.errors);
      }
      
      return response.data.data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }
`;
  
  // Add methods for each operation
  for (const operation of operations) {
    const code = await mcp.code_examples({
      operation: operation,
      language: "javascript"
    });
    
    // Extract the GraphQL query from generated code
    const queryMatch = code.code.match(/gql`([^`]+)`/);
    if (queryMatch) {
      const methodName = operation.replace(/_([a-z])/g, (g) => g[1].toUpperCase());
      
      clientClass += `
  
  async ${methodName}(input) {
    const query = \`${queryMatch[1]}\`;
    const variables = { input };
    const result = await this.query(query, variables);
    return result.${operation};
  }
`;
    }
  }
  
  clientClass += `
}

export default HealthieAPIClient;
`;
  
  return clientClass;
}

// Example 9: Generate Documentation from Code
async function generateDocumentation() {
  const operations = [
    "create_patient",
    "book_appointment",
    "create_clinical_note"
  ];
  
  let documentation = "# Healthie API Code Examples\n\n";
  
  for (const operation of operations) {
    documentation += `## ${operation.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}\n\n`;
    
    // Get code for all languages
    for (const language of ["javascript", "python", "curl"]) {
      const code = await mcp.code_examples({
        operation: operation,
        language: language
      });
      
      documentation += `### ${language.charAt(0).toUpperCase() + language.slice(1)}\n\n`;
      documentation += "```" + language + "\n";
      documentation += code.code;
      documentation += "\n```\n\n";
    }
  }
  
  return documentation;
}

// Example 10: Generate Integration Examples
async function generateIntegrationExamples() {
  // Generate code that shows how different operations work together
  
  // 1. Patient Registration Flow
  const createPatient = await mcp.code_examples({
    operation: "create_patient",
    language: "javascript"
  });
  
  const createAppointment = await mcp.code_examples({
    operation: "book_appointment",
    language: "javascript"
  });
  
  // Combine into registration flow
  const registrationFlow = `
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function PatientRegistrationFlow() {
  const navigate = useNavigate();
  const [patientId, setPatientId] = useState(null);
  const [step, setStep] = useState('patient');
  
  // Step 1: Create Patient
  ${createPatient.code}
  
  // Step 2: Book Initial Appointment
  ${createAppointment.code}
  
  const handlePatientCreated = (patient) => {
    setPatientId(patient.id);
    setStep('appointment');
  };
  
  const handleAppointmentBooked = (appointment) => {
    // Complete flow
    navigate(\`/patients/\${patientId}/welcome\`);
  };
  
  return (
    <div>
      {step === 'patient' && (
        <CreatePatientForm onSuccess={handlePatientCreated} />
      )}
      {step === 'appointment' && (
        <BookAppointmentForm 
          patientId={patientId}
          onSuccess={handleAppointmentBooked} 
        />
      )}
    </div>
  );
}
`;
  
  return registrationFlow;
}

// Practical Usage Example
async function practicalUsageExample() {
  // Scenario: Building a patient portal
  
  // 1. Generate authentication code
  const authCode = await mcp.code_examples({
    operation: "authenticate_user",
    language: "javascript"
  });
  
  // 2. Generate patient dashboard code
  const dashboardCode = await mcp.code_examples({
    operation: "get_patient_dashboard",
    language: "javascript"
  });
  
  // 3. Generate appointment management code
  const appointmentCode = await mcp.code_examples({
    operation: "manage_appointments",
    language: "javascript"
  });
  
  // 4. Combine into portal structure
  const portalStructure = {
    auth: authCode,
    dashboard: dashboardCode,
    appointments: appointmentCode
  };
  
  // 5. Generate corresponding Python backend
  const backendCode = await mcp.code_examples({
    operation: "patient_portal_api",
    language: "python"
  });
  
  return {
    frontend: portalStructure,
    backend: backendCode
  };
}

// Export for use in other files
module.exports = {
  generateJavaScriptCode,
  generatePythonCode,
  generateCurlCommands,
  generateMultiLanguageSDK,
  customizeGeneratedCode,
  generateTypeScriptCode,
  generateTestCode,
  generateAPIClient,
  generateDocumentation,
  generateIntegrationExamples,
  practicalUsageExample
};