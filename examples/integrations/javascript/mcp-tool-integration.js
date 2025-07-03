/**
 * MCP Tool Integration for JavaScript/React
 * 
 * This example shows how to integrate the 5 core MCP tools
 * into your JavaScript/React application for faster development.
 * 
 * Prerequisites:
 * - MCP server running locally or accessible
 * - Apollo Client or similar GraphQL client
 */

import { ApolloClient, InMemoryCache, gql } from '@apollo/client';

// MCP Client setup (example - adjust to your MCP client library)
class MCPClient {
  constructor(serverUrl) {
    this.serverUrl = serverUrl;
  }

  async callTool(toolName, params) {
    // This would be your actual MCP client implementation
    // For now, showing the pattern
    const response = await fetch(`${this.serverUrl}/tools/${toolName}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    return response.json();
  }

  // Tool-specific methods
  async searchSchema(params) {
    return this.callTool('search_schema', params);
  }

  async queryTemplates(params) {
    return this.callTool('query_templates', params);
  }

  async codeExamples(params) {
    return this.callTool('code_examples', params);
  }

  async introspectType(params) {
    return this.callTool('introspect_type', params);
  }

  async errorDecoder(params) {
    return this.callTool('error_decoder', params);
  }
}

// Initialize MCP client
const mcp = new MCPClient('http://localhost:5000'); // Adjust URL

// Initialize GraphQL client
const graphqlClient = new ApolloClient({
  uri: 'https://api.gethealthie.com/graphql',
  cache: new InMemoryCache(),
  headers: {
    'Authorization': `Basic ${process.env.REACT_APP_HEALTHIE_API_KEY}`,
    'AuthorizationSource': 'API'
  }
});

/**
 * Example 1: Building a Patient Registration Form
 * Uses all 5 MCP tools together
 */
export async function buildPatientRegistrationForm() {
  try {
    // Step 1: Search for patient creation operations
    console.log('🔍 Searching for patient operations...');
    const searchResults = await mcp.searchSchema({
      search_term: 'createPatient',
      type_filter: 'mutation'
    });
    
    console.log(`Found ${searchResults.total_matches} matches`);

    // Step 2: Get the mutation template
    console.log('📝 Getting patient creation template...');
    const templates = await mcp.queryTemplates({
      workflow: 'patient_management',
      include_variables: true
    });
    
    const createPatientTemplate = templates.templates.find(t => 
      t.name.includes('CreatePatient')
    );

    // Step 3: Introspect the input type
    console.log('🔎 Exploring CreatePatientInput type...');
    const inputType = await mcp.introspectType({
      type_name: 'CreatePatientInput'
    });
    
    // Find required fields
    const requiredFields = inputType.fields.filter(f => 
      f.type.kind === 'NON_NULL'
    );
    
    console.log(`Found ${requiredFields.length} required fields`);

    // Step 4: Generate the React component
    console.log('⚡ Generating React component...');
    const componentCode = await mcp.codeExamples({
      operation: 'create_patient',
      language: 'javascript'
    });

    // Step 5: Prepare error handlers
    const commonErrors = [
      'email already exists',
      'invalid date format',
      'phone number is invalid'
    ];
    
    const errorHandlers = {};
    for (const error of commonErrors) {
      const decoded = await mcp.errorDecoder({
        error_message: error
      });
      errorHandlers[error] = decoded;
    }

    return {
      mutation: createPatientTemplate.query,
      variables: createPatientTemplate.variables,
      requiredFields: requiredFields,
      componentCode: componentCode.code,
      errorHandlers: errorHandlers
    };

  } catch (error) {
    console.error('Error building form:', error);
    throw error;
  }
}

/**
 * Example 2: Smart GraphQL Query Builder
 * Uses search_schema and query_templates
 */
export class SmartQueryBuilder {
  constructor(mcp) {
    this.mcp = mcp;
    this.cache = new Map();
  }

  async buildQuery(operation, options = {}) {
    const cacheKey = `${operation}-${JSON.stringify(options)}`;
    
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    // Search for the operation
    const searchResults = await this.mcp.searchSchema({
      search_term: operation,
      type_filter: options.type || 'query'
    });

    if (searchResults.total_matches === 0) {
      throw new Error(`Operation '${operation}' not found`);
    }

    // Get template if available
    const templates = await this.mcp.queryTemplates({
      workflow: options.workflow || 'all',
      include_variables: true
    });

    const template = templates.templates.find(t => 
      t.name.toLowerCase().includes(operation.toLowerCase())
    );

    const result = {
      operation: searchResults.matches[0],
      template: template,
      query: template?.query || this.generateBasicQuery(operation)
    };

    this.cache.set(cacheKey, result);
    return result;
  }

  generateBasicQuery(operation) {
    return `
      query ${operation}($id: ID!) {
        ${operation}(id: $id) {
          id
          # Add more fields as needed
        }
      }
    `;
  }
}

/**
 * Example 3: Error-Resilient GraphQL Client
 * Uses error_decoder for automatic error handling
 */
export class ResilientGraphQLClient {
  constructor(apolloClient, mcp) {
    this.client = apolloClient;
    this.mcp = mcp;
  }

  async query(query, variables) {
    try {
      const result = await this.client.query({
        query: gql(query),
        variables
      });
      
      return result.data;
      
    } catch (error) {
      // Decode the error
      const decoded = await this.mcp.errorDecoder({
        error_message: error.message
      });
      
      // Attempt automatic recovery
      if (decoded.error_type === 'FIELD_NOT_FOUND') {
        const corrected = await this.correctFieldError(query, error);
        if (corrected) {
          return this.query(corrected, variables);
        }
      }
      
      // Enhance error with decoded information
      error.decoded = decoded;
      error.solutions = decoded.possible_solutions;
      error.example = decoded.example_fix;
      
      throw error;
    }
  }

  async correctFieldError(query, error) {
    // Extract field name from error
    const match = error.message.match(/field '(\w+)'/);
    if (!match) return null;
    
    const incorrectField = match[1];
    
    // Search for correct field
    const search = await this.mcp.searchSchema({
      search_term: incorrectField,
      type_filter: 'field'
    });
    
    if (search.matches.length > 0) {
      const correctField = search.matches[0].field_name;
      return query.replace(incorrectField, correctField);
    }
    
    return null;
  }
}

/**
 * Example 4: Type-Safe Form Generator
 * Uses introspect_type to generate forms
 */
export class FormGenerator {
  constructor(mcp) {
    this.mcp = mcp;
  }

  async generateForm(typeName) {
    // Introspect the type
    const type = await this.mcp.introspectType({
      type_name: typeName
    });

    // Generate form fields
    const formFields = type.fields.map(field => ({
      name: field.name,
      label: this.humanize(field.name),
      type: this.mapToInputType(field.type),
      required: field.type.kind === 'NON_NULL',
      validation: this.generateValidation(field)
    }));

    // Generate React form component
    const formComponent = this.generateReactForm(typeName, formFields);
    
    return {
      fields: formFields,
      component: formComponent
    };
  }

  humanize(fieldName) {
    return fieldName
      .replace(/([A-Z])/g, ' $1')
      .replace(/^./, str => str.toUpperCase())
      .trim();
  }

  mapToInputType(graphqlType) {
    const type = graphqlType.name || graphqlType.ofType?.name;
    
    const mapping = {
      'String': 'text',
      'Int': 'number',
      'Float': 'number',
      'Boolean': 'checkbox',
      'Date': 'date',
      'DateTime': 'datetime-local',
      'Email': 'email'
    };
    
    return mapping[type] || 'text';
  }

  generateValidation(field) {
    const rules = [];
    
    if (field.type.kind === 'NON_NULL') {
      rules.push({ required: true });
    }
    
    if (field.name.includes('email')) {
      rules.push({ pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/ });
    }
    
    if (field.name.includes('phone')) {
      rules.push({ pattern: /^[\d\s-()]+$/ });
    }
    
    return rules;
  }

  generateReactForm(typeName, fields) {
    return `
import React from 'react';
import { useForm } from 'react-hook-form';

export function ${typeName}Form({ onSubmit }) {
  const { register, handleSubmit, formState: { errors } } = useForm();

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      ${fields.map(field => `
      <div className="form-group">
        <label htmlFor="${field.name}">${field.label}</label>
        <input
          id="${field.name}"
          type="${field.type}"
          {...register("${field.name}", {
            required: ${field.required}
          })}
        />
        {errors.${field.name} && <span>This field is required</span>}
      </div>
      `).join('')}
      
      <button type="submit">Submit</button>
    </form>
  );
}
    `;
  }
}

/**
 * Example 5: Development Workflow Helper
 * Combines all tools for rapid development
 */
export class DevelopmentHelper {
  constructor(mcp, graphqlClient) {
    this.mcp = mcp;
    this.graphqlClient = graphqlClient;
    this.queryBuilder = new SmartQueryBuilder(mcp);
    this.resilientClient = new ResilientGraphQLClient(graphqlClient, mcp);
    this.formGenerator = new FormGenerator(mcp);
  }

  async implementFeature(featureName) {
    console.log(`🚀 Implementing ${featureName} feature...`);
    
    // 1. Discovery phase
    const discovery = await this.discoverFeature(featureName);
    
    // 2. Generate code
    const code = await this.generateFeatureCode(featureName, discovery);
    
    // 3. Prepare error handling
    const errorHandling = await this.prepareErrorHandling(featureName);
    
    return {
      discovery,
      code,
      errorHandling
    };
  }

  async discoverFeature(featureName) {
    const [types, queries, mutations] = await Promise.all([
      this.mcp.searchSchema({ search_term: featureName, type_filter: 'type' }),
      this.mcp.searchSchema({ search_term: featureName, type_filter: 'query' }),
      this.mcp.searchSchema({ search_term: featureName, type_filter: 'mutation' })
    ]);
    
    return {
      types: types.matches,
      queries: queries.matches,
      mutations: mutations.matches
    };
  }

  async generateFeatureCode(featureName, discovery) {
    const code = {};
    
    // Generate queries
    if (discovery.queries.length > 0) {
      const queryTemplate = await this.mcp.queryTemplates({
        workflow: this.guessWorkflow(featureName)
      });
      code.queries = queryTemplate;
    }
    
    // Generate mutations
    if (discovery.mutations.length > 0) {
      const mutationCode = await this.mcp.codeExamples({
        operation: this.guessOperation(featureName),
        language: 'javascript'
      });
      code.mutations = mutationCode;
    }
    
    // Generate forms
    if (discovery.types.length > 0) {
      const mainType = discovery.types[0].type_name;
      code.forms = await this.formGenerator.generateForm(mainType);
    }
    
    return code;
  }

  async prepareErrorHandling(featureName) {
    const commonErrors = [
      `${featureName} not found`,
      `Invalid ${featureName}`,
      `${featureName} already exists`
    ];
    
    const handlers = {};
    
    for (const error of commonErrors) {
      handlers[error] = await this.mcp.errorDecoder({
        error_message: error
      });
    }
    
    return handlers;
  }

  guessWorkflow(featureName) {
    if (featureName.includes('patient')) return 'patient_management';
    if (featureName.includes('appointment')) return 'appointments';
    if (featureName.includes('clinical')) return 'clinical_data';
    if (featureName.includes('billing')) return 'billing';
    return 'all';
  }

  guessOperation(featureName) {
    if (featureName.includes('create')) return 'create_patient';
    if (featureName.includes('update')) return 'update_patient';
    if (featureName.includes('book')) return 'book_appointment';
    return 'create_patient';
  }
}

/**
 * Example Usage
 */
export async function exampleUsage() {
  // Initialize helper
  const helper = new DevelopmentHelper(mcp, graphqlClient);
  
  // Implement a complete feature
  const patientFeature = await helper.implementFeature('patient');
  
  console.log('Feature implementation complete!');
  console.log('Types found:', patientFeature.discovery.types.length);
  console.log('Queries generated:', patientFeature.code.queries?.templates.length);
  console.log('Forms created:', patientFeature.code.forms ? 'Yes' : 'No');
  
  // Use the resilient client
  const resilientClient = new ResilientGraphQLClient(graphqlClient, mcp);
  
  try {
    const patient = await resilientClient.query(
      patientFeature.code.queries.templates[0].query,
      { id: '123' }
    );
    console.log('Patient data:', patient);
  } catch (error) {
    console.error('Error:', error.message);
    console.log('Solutions:', error.solutions);
    console.log('Example fix:', error.example);
  }
}

// Export everything for use in your app
export {
  MCPClient,
  buildPatientRegistrationForm,
  SmartQueryBuilder,
  ResilientGraphQLClient,
  FormGenerator,
  DevelopmentHelper
};