/**
 * Error Debugging Examples
 * 
 * Demonstrates how to use the error_decoder tool to transform
 * cryptic GraphQL errors into actionable solutions.
 * 
 * Combines with other MCP tools for comprehensive debugging.
 */

// Example 1: Basic Error Decoding
async function basicErrorDecoding() {
  // Common field error
  const fieldError = await mcp.error_decoder({
    error_message: "Cannot query field 'patient_name' on type 'Patient'"
  });
  
  console.log("Error Type:", fieldError.error_type);
  console.log("Plain English:", fieldError.plain_english);
  console.log("Solutions:", fieldError.possible_solutions);
  console.log("Example Fix:", fieldError.example_fix);
  
  // Returns:
  // Error Type: FIELD_NOT_FOUND
  // Plain English: The field 'patient_name' does not exist on the Patient type.
  // Solutions: ["Use 'firstName' and 'lastName' instead", ...]
  // Example Fix: query { patient { firstName lastName } }
  
  return fieldError;
}

// Example 2: Authentication Error Handling
async function handleAuthErrors() {
  const authError = await mcp.error_decoder({
    error_message: "Not authorized"
  });
  
  // Generate complete auth solution
  const solution = {
    error: authError,
    
    // Headers needed
    headers: {
      'Authorization': 'Basic YOUR_API_KEY',
      'AuthorizationSource': 'API',
      'Content-Type': 'application/json'
    },
    
    // Code example
    implementation: `
// Correct authentication setup
const client = new ApolloClient({
  uri: 'https://api.gethealthie.com/graphql',
  headers: {
    'Authorization': \`Basic \${process.env.HEALTHIE_API_KEY}\`,
    'AuthorizationSource': 'API'
  }
});
    `
  };
  
  return solution;
}

// Example 3: Validation Error Resolution
async function resolveValidationErrors() {
  const validationError = await mcp.error_decoder({
    error_message: "date_of_birth must be a valid date"
  });
  
  // Build complete validation fix
  const validationFix = {
    error: validationError,
    
    // Date formatter
    formatDate: (date) => {
      // Convert various formats to YYYY-MM-DD
      const d = new Date(date);
      return d.toISOString().split('T')[0];
    },
    
    // Validation function
    validateDate: (dateStr) => {
      const regex = /^\d{4}-\d{2}-\d{2}$/;
      if (!regex.test(dateStr)) return false;
      
      const date = new Date(dateStr);
      return date instanceof Date && !isNaN(date);
    },
    
    // Example usage
    example: `
// Correct date formatting
const patientData = {
  firstName: "John",
  lastName: "Doe",
  dateOfBirth: formatDate("01/15/1990") // Converts to "1990-01-15"
};
    `
  };
  
  return validationFix;
}

// Example 4: Complex Error Debugging Flow
async function complexErrorDebugging() {
  // Simulate complex error scenario
  const error = "Field 'InsurancePolicy.patient_name' doesn't exist. Did you mean 'InsurancePolicy.patient.name'?";
  
  // Step 1: Decode the error
  const decoded = await mcp.error_decoder({
    error_message: error
  });
  
  // Step 2: Search for correct structure
  const searchResults = await mcp.search_schema({
    search_term: "InsurancePolicy",
    type_filter: "type"
  });
  
  // Step 3: Introspect the type
  const typeInfo = await mcp.introspect_type({
    type_name: "InsurancePolicy"
  });
  
  // Step 4: Find the relationship
  const patientField = typeInfo.fields.find(f => f.name === 'patient');
  
  // Step 5: Build correct query
  const correctQuery = `
query {
  insurancePolicy(id: "123") {
    id
    policyNumber
    patient {  # This is a relationship
      firstName
      lastName
    }
  }
}
  `;
  
  return {
    error: decoded,
    correctStructure: patientField,
    fixedQuery: correctQuery
  };
}

// Example 5: Error Pattern Recognition
async function recognizeErrorPatterns() {
  // Common error patterns and their solutions
  const errorPatterns = [
    {
      pattern: "Cannot query field '(\\w+)' on type",
      type: "FIELD_NOT_FOUND",
      solution: async (match) => {
        const fieldName = match[1];
        // Search for similar fields
        const similar = await mcp.search_schema({
          search_term: fieldName,
          type_filter: "field"
        });
        return similar;
      }
    },
    {
      pattern: "Expected type '(\\w+)', found",
      type: "TYPE_MISMATCH",
      solution: async (match) => {
        const expectedType = match[1];
        // Get type information
        const typeInfo = await mcp.introspect_type({
          type_name: expectedType
        });
        return typeInfo;
      }
    },
    {
      pattern: "Variable '\\$(\\w+)' of required type",
      type: "MISSING_VARIABLE",
      solution: async (match) => {
        const variableName = match[1];
        // Get query template with variables
        const template = await mcp.query_templates({
          include_variables: true
        });
        return template;
      }
    }
  ];
  
  return errorPatterns;
}

// Example 6: Building Error Recovery System
async function buildErrorRecovery() {
  class GraphQLErrorRecovery {
    constructor() {
      this.errorCache = new Map();
    }
    
    async handleError(error) {
      // Check cache first
      if (this.errorCache.has(error.message)) {
        return this.errorCache.get(error.message);
      }
      
      // Decode error
      const decoded = await mcp.error_decoder({
        error_message: error.message
      });
      
      // Build recovery strategy
      let recovery;
      
      switch (decoded.error_type) {
        case 'FIELD_NOT_FOUND':
          recovery = await this.recoverFieldError(error, decoded);
          break;
          
        case 'AUTHENTICATION_ERROR':
          recovery = await this.recoverAuthError(error, decoded);
          break;
          
        case 'VALIDATION_ERROR':
          recovery = await this.recoverValidationError(error, decoded);
          break;
          
        default:
          recovery = decoded;
      }
      
      // Cache the recovery
      this.errorCache.set(error.message, recovery);
      
      return recovery;
    }
    
    async recoverFieldError(error, decoded) {
      // Extract field and type from error
      const match = error.message.match(/field '(\w+)' on type '(\w+)'/);
      if (!match) return decoded;
      
      const [, fieldName, typeName] = match;
      
      // Search for correct field
      const searchResults = await mcp.search_schema({
        search_term: fieldName,
        type_filter: "field"
      });
      
      // Filter by parent type
      const correctField = searchResults.matches.find(m => 
        m.parent_type === typeName
      );
      
      return {
        ...decoded,
        corrected_field: correctField?.field_name,
        automated_fix: true
      };
    }
    
    async recoverAuthError(error, decoded) {
      // Get authentication examples
      const authExample = await mcp.code_examples({
        operation: "authentication",
        language: "javascript"
      });
      
      return {
        ...decoded,
        code_example: authExample.code,
        immediate_action: "Check API key and headers"
      };
    }
    
    async recoverValidationError(error, decoded) {
      // Extract field from error
      const fieldMatch = error.message.match(/(\w+) must be/);
      const fieldName = fieldMatch?.[1];
      
      // Get validation rules
      const validationExample = {
        email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        phone: /^\+?[\d\s-()]+$/,
        date: /^\d{4}-\d{2}-\d{2}$/
      };
      
      return {
        ...decoded,
        field: fieldName,
        validation_pattern: validationExample[fieldName] || null,
        format_example: this.getFormatExample(fieldName)
      };
    }
    
    getFormatExample(fieldName) {
      const examples = {
        email: "user@example.com",
        phoneNumber: "+1234567890",
        date_of_birth: "1990-01-15",
        dateOfBirth: "1990-01-15"
      };
      
      return examples[fieldName] || "Check documentation";
    }
  }
  
  return GraphQLErrorRecovery;
}

// Example 7: Debugging GraphQL Response Errors
async function debugResponseErrors() {
  // Handle errors in GraphQL response
  const response = {
    data: {
      createPatient: {
        patient: null,
        errors: [
          {
            field: "email",
            message: "has already been taken"
          },
          {
            field: "phoneNumber",
            message: "is invalid"
          }
        ]
      }
    }
  };
  
  // Process each error
  const processedErrors = await Promise.all(
    response.data.createPatient.errors.map(async (error) => {
      const decoded = await mcp.error_decoder({
        error_message: `${error.field} ${error.message}`
      });
      
      return {
        field: error.field,
        original: error.message,
        decoded: decoded,
        userMessage: getUserFriendlyMessage(error.field, error.message)
      };
    })
  );
  
  return processedErrors;
}

function getUserFriendlyMessage(field, message) {
  const messages = {
    email: {
      "has already been taken": "This email is already registered. Try logging in instead.",
      "is invalid": "Please enter a valid email address."
    },
    phoneNumber: {
      "is invalid": "Please enter a valid phone number (e.g., +1234567890)."
    }
  };
  
  return messages[field]?.[message] || `${field}: ${message}`;
}

// Example 8: Error Monitoring and Logging
async function setupErrorMonitoring() {
  class ErrorMonitor {
    constructor() {
      this.errorLog = [];
      this.errorCounts = {};
    }
    
    async logError(error, context) {
      // Decode error
      const decoded = await mcp.error_decoder({
        error_message: error.message
      });
      
      // Create log entry
      const logEntry = {
        timestamp: new Date().toISOString(),
        error: error.message,
        decoded: decoded,
        context: context,
        stack: error.stack,
        userId: context.userId,
        operation: context.operation
      };
      
      // Add to log
      this.errorLog.push(logEntry);
      
      // Update counts
      const errorType = decoded.error_type;
      this.errorCounts[errorType] = (this.errorCounts[errorType] || 0) + 1;
      
      // Alert on critical errors
      if (this.isCritical(decoded)) {
        this.alertTeam(logEntry);
      }
      
      return logEntry;
    }
    
    isCritical(decoded) {
      const criticalTypes = ['AUTHENTICATION_ERROR', 'PERMISSION_DENIED'];
      return criticalTypes.includes(decoded.error_type);
    }
    
    alertTeam(logEntry) {
      console.error('CRITICAL ERROR:', logEntry);
      // Send to monitoring service
    }
    
    getErrorReport() {
      return {
        totalErrors: this.errorLog.length,
        errorsByType: this.errorCounts,
        recentErrors: this.errorLog.slice(-10),
        criticalErrors: this.errorLog.filter(e => 
          this.isCritical(e.decoded)
        )
      };
    }
  }
  
  return ErrorMonitor;
}

// Example 9: Automated Error Resolution
async function automatedErrorResolution() {
  // Build automated fixer for common errors
  const autoFixer = {
    async fix(query, variables, error) {
      const decoded = await mcp.error_decoder({
        error_message: error.message
      });
      
      switch (decoded.error_type) {
        case 'FIELD_NOT_FOUND':
          return this.fixFieldError(query, error);
          
        case 'TYPE_MISMATCH':
          return this.fixTypeMismatch(variables, error);
          
        case 'VALIDATION_ERROR':
          return this.fixValidation(variables, error);
          
        default:
          return null;
      }
    },
    
    fixFieldError(query, error) {
      // Extract incorrect field
      const match = error.message.match(/field '(\w+)'/);
      if (!match) return null;
      
      const incorrectField = match[1];
      
      // Common field corrections
      const corrections = {
        'patient_name': 'firstName lastName',
        'patient_id': 'id',
        'created': 'createdAt',
        'updated': 'updatedAt'
      };
      
      if (corrections[incorrectField]) {
        return query.replace(incorrectField, corrections[incorrectField]);
      }
      
      return null;
    },
    
    fixTypeMismatch(variables, error) {
      // Extract type info
      const match = error.message.match(/Expected type '(\w+)', found "(.+)"/);
      if (!match) return null;
      
      const [, expectedType, actualValue] = match;
      
      // Type converters
      const converters = {
        'Int': (val) => parseInt(val, 10),
        'Float': (val) => parseFloat(val),
        'Boolean': (val) => val === 'true' || val === true,
        'String': (val) => String(val)
      };
      
      if (converters[expectedType]) {
        // Find and fix the variable
        // This is simplified - real implementation would be more complex
        return converters[expectedType](actualValue);
      }
      
      return null;
    },
    
    fixValidation(variables, error) {
      // Common validation fixes
      const fixes = {
        'date': (val) => {
          const date = new Date(val);
          return date.toISOString().split('T')[0];
        },
        'email': (val) => val.toLowerCase().trim(),
        'phone': (val) => val.replace(/[^\d+]/g, '')
      };
      
      // Apply fix based on field type
      // This is simplified
      return variables;
    }
  };
  
  return autoFixer;
}

// Example 10: Complete Debugging Workflow
async function completeDebuggingWorkflow() {
  // Comprehensive debugging system
  
  const debugSystem = {
    async debug(operation, variables, error) {
      console.log("🔍 Debugging GraphQL Error");
      console.log("Operation:", operation);
      console.log("Error:", error.message);
      
      // Step 1: Decode error
      const decoded = await mcp.error_decoder({
        error_message: error.message
      });
      console.log("\n📊 Error Analysis:");
      console.log("Type:", decoded.error_type);
      console.log("Explanation:", decoded.plain_english);
      
      // Step 2: Search for related schema elements
      const searchTerm = this.extractSearchTerm(error.message);
      if (searchTerm) {
        const searchResults = await mcp.search_schema({
          search_term: searchTerm
        });
        console.log(`\n🔎 Found ${searchResults.total_matches} related schema elements`);
      }
      
      // Step 3: Get correct examples
      const examples = await mcp.code_examples({
        operation: this.guessOperation(operation),
        language: "javascript"
      });
      console.log("\n💡 Example implementation available");
      
      // Step 4: Generate fix
      const fix = await this.generateFix(error, decoded, operation, variables);
      console.log("\n✅ Suggested fix:");
      console.log(fix);
      
      return {
        error: decoded,
        searchResults: searchResults,
        examples: examples,
        suggestedFix: fix
      };
    },
    
    extractSearchTerm(errorMessage) {
      // Extract relevant terms from error
      const patterns = [
        /field '(\w+)'/,
        /type '(\w+)'/,
        /'(\w+)' of required type/
      ];
      
      for (const pattern of patterns) {
        const match = errorMessage.match(pattern);
        if (match) return match[1];
      }
      
      return null;
    },
    
    guessOperation(operation) {
      // Map GraphQL operation to example operation
      if (operation.includes('create')) return 'create_patient';
      if (operation.includes('update')) return 'update_patient';
      if (operation.includes('query')) return 'get_patient';
      return 'create_patient';
    },
    
    async generateFix(error, decoded, operation, variables) {
      // Generate specific fix based on error type
      const fixes = {
        FIELD_NOT_FOUND: () => this.fixFieldNotFound(error, operation),
        TYPE_MISMATCH: () => this.fixTypeMismatch(error, variables),
        VALIDATION_ERROR: () => this.fixValidation(error, variables),
        AUTHENTICATION_ERROR: () => this.fixAuthentication()
      };
      
      const fixFunction = fixes[decoded.error_type];
      return fixFunction ? await fixFunction() : decoded.example_fix;
    },
    
    async fixFieldNotFound(error, operation) {
      // Generate corrected query
      return `
// Corrected query with proper field names
${operation.replace(/patient_name/g, 'firstName lastName')}
      `;
    },
    
    fixTypeMismatch(error, variables) {
      // Show type conversion
      return `
// Convert values to correct types
const correctedVariables = {
  ...variables,
  // Add type conversions here
};
      `;
    },
    
    fixValidation(error, variables) {
      // Show validation fix
      return `
// Format data correctly
const formattedData = {
  ...variables,
  dateOfBirth: formatDate(variables.dateOfBirth), // YYYY-MM-DD
  email: variables.email.toLowerCase().trim(),
  phoneNumber: formatPhoneNumber(variables.phoneNumber)
};
      `;
    },
    
    fixAuthentication() {
      return `
// Set up authentication correctly
const headers = {
  'Authorization': 'Basic YOUR_API_KEY',
  'AuthorizationSource': 'API'
};
      `;
    }
  };
  
  return debugSystem;
}

// Practical Usage Example
async function practicalUsageExample() {
  // Real-world error handling scenario
  
  try {
    // Attempt GraphQL operation
    const result = await graphqlClient.request(
      CREATE_PATIENT_MUTATION,
      variables
    );
    
    // Check for application-level errors
    if (result.createPatient.errors?.length > 0) {
      const errors = result.createPatient.errors;
      
      // Decode each error
      const decodedErrors = await Promise.all(
        errors.map(err => mcp.error_decoder({
          error_message: `${err.field}: ${err.message}`
        }))
      );
      
      // Show user-friendly messages
      decodedErrors.forEach(decoded => {
        showUserError(decoded.plain_english);
      });
    }
    
  } catch (error) {
    // Handle transport/GraphQL errors
    const decoded = await mcp.error_decoder({
      error_message: error.message
    });
    
    console.error("Error decoded:", decoded);
    
    // Attempt automatic recovery
    if (decoded.error_type === 'FIELD_NOT_FOUND') {
      // Try to fix and retry
      const fixed = await attemptAutoFix(error);
      if (fixed) {
        return retry(fixed);
      }
    }
    
    // Show error to user
    showUserError(decoded.plain_english);
  }
}

// Export for use in other files
module.exports = {
  basicErrorDecoding,
  handleAuthErrors,
  resolveValidationErrors,
  complexErrorDebugging,
  recognizeErrorPatterns,
  buildErrorRecovery,
  debugResponseErrors,
  setupErrorMonitoring,
  automatedErrorResolution,
  completeDebuggingWorkflow,
  practicalUsageExample
};