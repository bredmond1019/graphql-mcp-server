/**
 * Query Templates Examples
 * 
 * Demonstrates how to use the query_templates tool to get pre-built,
 * tested GraphQL queries for common healthcare workflows.
 * 
 * All templates are production-ready and follow best practices.
 */

// Example 1: Get All Available Templates
async function getAllTemplates() {
  const templates = await mcp.query_templates({
    workflow: "all"
  });
  
  console.log(`Found ${templates.templates.length} templates across all workflows`);
  
  // Templates are organized by workflow:
  // - patient_management
  // - appointments
  // - clinical_data
  // - billing
  // - provider_management
  
  return templates;
}

// Example 2: Patient Management Templates
async function getPatientTemplates() {
  const templates = await mcp.query_templates({
    workflow: "patient_management",
    include_variables: true
  });
  
  // Returns templates like:
  // - Create Patient
  // - Update Patient
  // - Search Patients
  // - Archive Patient
  
  // Example template returned:
  const createPatientTemplate = templates.templates[0];
  console.log("Create Patient Mutation:");
  console.log(createPatientTemplate.query);
  
  if (createPatientTemplate.variables) {
    console.log("\nExample Variables:");
    console.log(JSON.stringify(createPatientTemplate.variables, null, 2));
  }
  
  return createPatientTemplate;
}

// Example 3: Appointment Booking Workflow
async function getAppointmentWorkflow() {
  const templates = await mcp.query_templates({
    workflow: "appointments",
    include_variables: true
  });
  
  // Complete booking workflow templates:
  const workflow = {
    checkAvailability: templates.templates.find(t => 
      t.name.includes("availability")
    ),
    bookAppointment: templates.templates.find(t => 
      t.name.includes("create") || t.name.includes("book")
    ),
    updateAppointment: templates.templates.find(t => 
      t.name.includes("update")
    ),
    cancelAppointment: templates.templates.find(t => 
      t.name.includes("cancel")
    )
  };
  
  return workflow;
}

// Example 4: Clinical Documentation Templates
async function getClinicalTemplates() {
  const templates = await mcp.query_templates({
    workflow: "clinical_data",
    include_variables: true
  });
  
  // Clinical templates include:
  // - Create Clinical Note
  // - Update Clinical Note
  // - Sign Clinical Note
  // - Create Assessment
  // - Record Vitals
  
  // Example: SOAP Note Template
  const soapNoteTemplate = templates.templates.find(t => 
    t.name.toLowerCase().includes("clinical") || 
    t.name.toLowerCase().includes("note")
  );
  
  return soapNoteTemplate;
}

// Example 5: Building Complex Queries from Templates
async function buildComplexQuery() {
  // Get multiple templates
  const patientTemplate = await mcp.query_templates({
    workflow: "patient_management"
  });
  
  const appointmentTemplate = await mcp.query_templates({
    workflow: "appointments"
  });
  
  // Combine templates into a single query
  const complexQuery = `
    query GetPatientWithAppointments($patientId: ID!, $startDate: String!, $endDate: String!) {
      patient(id: $patientId) {
        id
        firstName
        lastName
        email
        
        # From appointment template
        appointments(startDate: $startDate, endDate: $endDate) {
          id
          date
          time
          status
          provider {
            firstName
            lastName
          }
        }
      }
    }
  `;
  
  return complexQuery;
}

// Example 6: Template Customization
async function customizeTemplate() {
  // Get base template
  const templates = await mcp.query_templates({
    workflow: "patient_management",
    include_variables: true
  });
  
  const createPatient = templates.templates.find(t => 
    t.name.includes("Create")
  );
  
  // Customize the template
  let customizedQuery = createPatient.query;
  
  // Add custom fields
  customizedQuery = customizedQuery.replace(
    "email",
    "email\n      middleName\n      preferredName"
  );
  
  // Add address fields
  customizedQuery = customizedQuery.replace(
    "}",
    `  addresses {
        line1
        line2
        city
        state
        zipCode
      }
    }`
  );
  
  return customizedQuery;
}

// Example 7: Workflow-Specific Variables
async function getWorkflowVariables() {
  // Get templates with variables for different workflows
  const workflows = [
    "patient_management",
    "appointments",
    "clinical_data",
    "billing"
  ];
  
  const workflowVariables = {};
  
  for (const workflow of workflows) {
    const templates = await mcp.query_templates({
      workflow: workflow,
      include_variables: true
    });
    
    // Extract all unique variable structures
    workflowVariables[workflow] = templates.templates
      .filter(t => t.variables)
      .map(t => ({
        operation: t.name,
        variables: t.variables
      }));
  }
  
  return workflowVariables;
}

// Example 8: Error-Safe Template Usage
async function safeTemplateUsage() {
  try {
    // Get template
    const templates = await mcp.query_templates({
      workflow: "appointments",
      include_variables: true
    });
    
    const bookingTemplate = templates.templates[0];
    
    // Validate template has required parts
    if (!bookingTemplate.query) {
      throw new Error("Template missing query");
    }
    
    // Use template with error handling
    const result = await graphqlClient.request(
      bookingTemplate.query,
      bookingTemplate.variables || {}
    );
    
    // Check for GraphQL errors in response
    if (result.errors) {
      console.error("GraphQL errors:", result.errors);
      // Use error_decoder tool here
    }
    
    return result;
    
  } catch (error) {
    console.error("Template usage error:", error);
    // Fallback logic
  }
}

// Example 9: Template-Based Code Generation
async function generateCodeFromTemplate() {
  // Get a template
  const templates = await mcp.query_templates({
    workflow: "patient_management",
    include_variables: true
  });
  
  const createPatientTemplate = templates.templates[0];
  
  // Generate TypeScript interface from template
  const generateInterface = (variables) => {
    let interface = "interface CreatePatientInput {\n";
    
    Object.entries(variables.input).forEach(([key, value]) => {
      const type = typeof value === 'string' ? 'string' : 
                   typeof value === 'number' ? 'number' : 
                   typeof value === 'boolean' ? 'boolean' : 'any';
      interface += `  ${key}: ${type};\n`;
    });
    
    interface += "}";
    return interface;
  };
  
  // Generate React hook from template
  const generateHook = (template) => {
    return `
import { gql, useMutation } from '@apollo/client';

const ${template.name.toUpperCase()}_MUTATION = gql\`
${template.query}
\`;

export function use${template.name}() {
  const [mutate, { data, loading, error }] = useMutation(
    ${template.name.toUpperCase()}_MUTATION
  );
  
  const execute = async (variables) => {
    try {
      const result = await mutate({ variables });
      return result.data;
    } catch (err) {
      console.error('${template.name} error:', err);
      throw err;
    }
  };
  
  return { execute, data, loading, error };
}
    `;
  };
  
  return {
    interface: generateInterface(createPatientTemplate.variables),
    hook: generateHook(createPatientTemplate)
  };
}

// Example 10: Template Library Builder
async function buildTemplateLibrary() {
  // Build a complete template library for your app
  const workflows = [
    "patient_management",
    "appointments", 
    "clinical_data",
    "billing",
    "provider_management"
  ];
  
  const library = {};
  
  for (const workflow of workflows) {
    const templates = await mcp.query_templates({
      workflow: workflow,
      include_variables: true
    });
    
    library[workflow] = templates.templates.reduce((acc, template) => {
      // Organize by operation type
      const operationType = template.name.includes("Create") ? "create" :
                           template.name.includes("Update") ? "update" :
                           template.name.includes("Delete") ? "delete" :
                           template.name.includes("Get") ? "query" : "other";
      
      if (!acc[operationType]) acc[operationType] = [];
      acc[operationType].push(template);
      
      return acc;
    }, {});
  }
  
  // Save to file for reuse
  const fs = require('fs');
  fs.writeFileSync(
    './graphql-templates.json',
    JSON.stringify(library, null, 2)
  );
  
  return library;
}

// Practical Usage Example
async function practicalExample() {
  // Scenario: Implement patient registration
  
  // 1. Get the template
  const templates = await mcp.query_templates({
    workflow: "patient_management",
    include_variables: true
  });
  
  const createPatient = templates.templates.find(t => 
    t.name.includes("Create")
  );
  
  // 2. Use in your application
  const createNewPatient = async (patientData) => {
    // Merge your data with template variables
    const variables = {
      input: {
        ...createPatient.variables.input,
        ...patientData
      }
    };
    
    // Execute query
    const result = await graphqlClient.request(
      createPatient.query,
      variables
    );
    
    return result.createPatient.patient;
  };
  
  // 3. Use the function
  const newPatient = await createNewPatient({
    firstName: "John",
    lastName: "Doe",
    email: "john.doe@example.com",
    dateOfBirth: "1990-01-01",
    phoneNumber: "+1234567890"
  });
  
  console.log("Created patient:", newPatient.id);
}

// Export for use in other files
module.exports = {
  getAllTemplates,
  getPatientTemplates,
  getAppointmentWorkflow,
  getClinicalTemplates,
  buildComplexQuery,
  customizeTemplate,
  getWorkflowVariables,
  safeTemplateUsage,
  generateCodeFromTemplate,
  buildTemplateLibrary,
  practicalExample
};