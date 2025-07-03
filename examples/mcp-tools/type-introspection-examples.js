/**
 * Type Introspection Examples
 * 
 * Demonstrates how to use the introspect_type tool to explore
 * GraphQL types in depth, understand relationships, and build
 * type-safe applications.
 * 
 * The Patient type has 100+ fields, User has 453 fields!
 */

// Example 1: Basic Type Introspection
async function basicTypeIntrospection() {
  // Get information about the Patient type
  const patientType = await mcp.introspect_type({
    type_name: "Patient"
  });
  
  console.log(`Patient type has ${patientType.fields.length} fields`);
  
  // Explore core fields
  const coreFields = patientType.fields.filter(field => 
    ['id', 'firstName', 'lastName', 'email', 'dateOfBirth'].includes(field.name)
  );
  
  coreFields.forEach(field => {
    console.log(`${field.name}: ${field.type} ${field.isRequired ? '(required)' : ''}`);
  });
  
  return patientType;
}

// Example 2: Complex Type Analysis
async function analyzeComplexType() {
  // User type has 453 fields!
  const userType = await mcp.introspect_type({
    type_name: "User",
    include_deprecated: true
  });
  
  // Categorize fields
  const categories = {
    personal: [],
    medical: [],
    provider: [],
    settings: [],
    relationships: [],
    timestamps: [],
    other: []
  };
  
  userType.fields.forEach(field => {
    if (['firstName', 'lastName', 'email', 'phone'].some(n => field.name.includes(n))) {
      categories.personal.push(field);
    } else if (['medical', 'allergy', 'medication'].some(n => field.name.includes(n))) {
      categories.medical.push(field);
    } else if (['npi', 'dea', 'license', 'specialty'].some(n => field.name.includes(n))) {
      categories.provider.push(field);
    } else if (['setting', 'preference', 'config'].some(n => field.name.includes(n))) {
      categories.settings.push(field);
    } else if (field.type.includes('Connection') || field.type.includes('[]')) {
      categories.relationships.push(field);
    } else if (field.name.endsWith('At')) {
      categories.timestamps.push(field);
    } else {
      categories.other.push(field);
    }
  });
  
  console.log("User type field breakdown:");
  Object.entries(categories).forEach(([category, fields]) => {
    console.log(`${category}: ${fields.length} fields`);
  });
  
  return categories;
}

// Example 3: Understanding Relationships
async function exploreRelationships() {
  const appointmentType = await mcp.introspect_type({
    type_name: "Appointment"
  });
  
  // Find all relationship fields
  const relationships = appointmentType.fields.filter(field => {
    // Object types represent relationships
    return field.type.kind === 'OBJECT' || 
           (field.type.kind === 'LIST' && field.type.ofType?.kind === 'OBJECT');
  });
  
  console.log("Appointment relationships:");
  relationships.forEach(rel => {
    const isList = rel.type.kind === 'LIST';
    const typeName = isList ? rel.type.ofType.name : rel.type.name;
    const cardinality = isList ? 'has many' : 'has one';
    console.log(`- ${rel.name}: ${cardinality} ${typeName}`);
  });
  
  // Example output:
  // - patient: has one Patient
  // - provider: has one Provider
  // - attendees: has many User
  // - location: has one Location
  // - appointmentType: has one AppointmentType
  
  return relationships;
}

// Example 4: Finding Required Fields
async function findRequiredFields() {
  // Introspect an input type
  const createPatientInput = await mcp.introspect_type({
    type_name: "CreatePatientInput"
  });
  
  // Separate required and optional fields
  const required = [];
  const optional = [];
  
  createPatientInput.fields.forEach(field => {
    if (field.type.kind === 'NON_NULL') {
      required.push({
        name: field.name,
        type: field.type.ofType.name
      });
    } else {
      optional.push({
        name: field.name,
        type: field.type.name || field.type.ofType?.name
      });
    }
  });
  
  console.log("Required fields for creating a patient:");
  required.forEach(field => {
    console.log(`- ${field.name}: ${field.type}`);
  });
  
  console.log("\nOptional fields:");
  optional.forEach(field => {
    console.log(`- ${field.name}: ${field.type}`);
  });
  
  return { required, optional };
}

// Example 5: Exploring Enums
async function exploreEnums() {
  // Get appointment status enum
  const appointmentStatus = await mcp.introspect_type({
    type_name: "AppointmentStatus"
  });
  
  console.log("Appointment Status Values:");
  appointmentStatus.enumValues.forEach(value => {
    console.log(`- ${value.name}${value.description ? `: ${value.description}` : ''}`);
  });
  
  // Common healthcare enums to explore
  const healthcareEnums = [
    "Gender",
    "ContactType",
    "InsuranceRelationship",
    "DocumentType",
    "MetricType"
  ];
  
  const enumDetails = {};
  
  for (const enumName of healthcareEnums) {
    try {
      const enumType = await mcp.introspect_type({
        type_name: enumName
      });
      enumDetails[enumName] = enumType.enumValues.map(v => v.name);
    } catch (e) {
      // Enum might not exist
    }
  }
  
  return enumDetails;
}

// Example 6: Building TypeScript Interfaces
async function generateTypeScriptInterface() {
  const patientType = await mcp.introspect_type({
    type_name: "Patient"
  });
  
  let interface = "interface Patient {\n";
  
  patientType.fields.forEach(field => {
    // Convert GraphQL types to TypeScript
    let tsType = field.type.name;
    
    // Handle common scalar mappings
    const scalarMappings = {
      'String': 'string',
      'Int': 'number',
      'Float': 'number',
      'Boolean': 'boolean',
      'ID': 'string',
      'DateTime': 'Date',
      'JSON': 'any'
    };
    
    if (scalarMappings[tsType]) {
      tsType = scalarMappings[tsType];
    }
    
    // Handle lists
    if (field.type.kind === 'LIST') {
      tsType = `${field.type.ofType.name}[]`;
    }
    
    // Handle nullability
    const optional = field.type.kind !== 'NON_NULL' ? '?' : '';
    
    interface += `  ${field.name}${optional}: ${tsType};\n`;
  });
  
  interface += "}";
  
  return interface;
}

// Example 7: Finding Deprecated Fields
async function findDeprecatedFields() {
  const types = ["Patient", "Appointment", "User", "Provider"];
  const deprecatedReport = {};
  
  for (const typeName of types) {
    const typeInfo = await mcp.introspect_type({
      type_name: typeName,
      include_deprecated: true
    });
    
    const deprecated = typeInfo.fields.filter(field => field.isDeprecated);
    
    if (deprecated.length > 0) {
      deprecatedReport[typeName] = deprecated.map(field => ({
        field: field.name,
        reason: field.deprecationReason,
        suggestion: extractAlternative(field.deprecationReason)
      }));
    }
  }
  
  return deprecatedReport;
}

function extractAlternative(reason) {
  // Extract suggested alternative from deprecation reason
  const match = reason?.match(/use (\w+) instead/i);
  return match ? match[1] : null;
}

// Example 8: Schema Documentation Generator
async function generateSchemaDocumentation() {
  const typesToDocument = [
    "Patient",
    "Appointment",
    "Provider",
    "InsurancePolicy"
  ];
  
  let documentation = "# Healthie GraphQL Schema Documentation\n\n";
  
  for (const typeName of typesToDocument) {
    const typeInfo = await mcp.introspect_type({
      type_name: typeName
    });
    
    documentation += `## ${typeName}\n\n`;
    documentation += `Total fields: ${typeInfo.fields.length}\n\n`;
    
    // Group fields by category
    documentation += "### Identity Fields\n";
    typeInfo.fields
      .filter(f => ['id', 'firstName', 'lastName', 'email'].includes(f.name))
      .forEach(f => {
        documentation += `- **${f.name}**: ${f.type}${f.description ? ` - ${f.description}` : ''}\n`;
      });
    
    documentation += "\n### Relationships\n";
    typeInfo.fields
      .filter(f => f.type.kind === 'OBJECT' || f.type.kind === 'LIST')
      .forEach(f => {
        documentation += `- **${f.name}**: ${f.type}\n`;
      });
    
    documentation += "\n---\n\n";
  }
  
  return documentation;
}

// Example 9: Type Validation Builder
async function buildValidationRules() {
  const inputType = await mcp.introspect_type({
    type_name: "CreatePatientInput"
  });
  
  const validationRules = {};
  
  inputType.fields.forEach(field => {
    const rules = [];
    
    // Required check
    if (field.type.kind === 'NON_NULL') {
      rules.push('required');
    }
    
    // Type-based validation
    if (field.name === 'email') {
      rules.push('email');
    } else if (field.name === 'phoneNumber') {
      rules.push('phone');
    } else if (field.name === 'dateOfBirth') {
      rules.push('date');
      rules.push('pastDate');
    } else if (field.type.name === 'Int') {
      rules.push('integer');
    }
    
    // Length validation
    if (field.name.includes('name') || field.name.includes('Name')) {
      rules.push('minLength:2');
      rules.push('maxLength:50');
    }
    
    validationRules[field.name] = rules;
  });
  
  // Generate validation function
  const validationFunction = `
function validatePatientInput(input) {
  const errors = {};
  
  ${Object.entries(validationRules).map(([field, rules]) => `
  // Validate ${field}
  ${rules.includes('required') ? `
  if (!input.${field}) {
    errors.${field} = '${field} is required';
  }` : ''}
  
  ${rules.includes('email') ? `
  if (input.${field} && !isValidEmail(input.${field})) {
    errors.${field} = 'Invalid email format';
  }` : ''}
  `).join('\n')}
  
  return errors;
}
  `;
  
  return { rules: validationRules, function: validationFunction };
}

// Example 10: Complete Type Explorer
async function completeTypeExplorer(typeName) {
  // Comprehensive type analysis
  const analysis = {
    basic: await mcp.introspect_type({ type_name: typeName }),
    relationships: {},
    requiredFields: [],
    optionalFields: [],
    deprecatedFields: [],
    enumFields: [],
    scalarFields: [],
    objectFields: [],
    listFields: []
  };
  
  // Analyze each field
  for (const field of analysis.basic.fields) {
    // Check if required
    if (field.type.kind === 'NON_NULL') {
      analysis.requiredFields.push(field);
    } else {
      analysis.optionalFields.push(field);
    }
    
    // Check if deprecated
    if (field.isDeprecated) {
      analysis.deprecatedFields.push(field);
    }
    
    // Categorize by type
    if (field.type.kind === 'ENUM') {
      analysis.enumFields.push(field);
    } else if (field.type.kind === 'SCALAR') {
      analysis.scalarFields.push(field);
    } else if (field.type.kind === 'OBJECT') {
      analysis.objectFields.push(field);
      analysis.relationships[field.name] = field.type.name;
    } else if (field.type.kind === 'LIST') {
      analysis.listFields.push(field);
      if (field.type.ofType?.kind === 'OBJECT') {
        analysis.relationships[field.name] = `[${field.type.ofType.name}]`;
      }
    }
  }
  
  // Generate summary
  analysis.summary = {
    totalFields: analysis.basic.fields.length,
    requiredCount: analysis.requiredFields.length,
    optionalCount: analysis.optionalFields.length,
    relationshipCount: Object.keys(analysis.relationships).length,
    deprecatedCount: analysis.deprecatedFields.length
  };
  
  return analysis;
}

// Practical Usage Example
async function practicalExample() {
  // Scenario: Building a type-safe patient form
  
  // 1. Introspect the input type
  const inputType = await mcp.introspect_type({
    type_name: "CreatePatientInput"
  });
  
  // 2. Generate form fields
  const formFields = inputType.fields.map(field => ({
    name: field.name,
    type: mapGraphQLToHTMLInputType(field.type),
    required: field.type.kind === 'NON_NULL',
    label: field.name.replace(/([A-Z])/g, ' $1').trim()
  }));
  
  // 3. Generate validation
  const validation = await buildValidationRules();
  
  // 4. Create form component
  console.log("Form fields:", formFields);
  console.log("Validation rules:", validation.rules);
  
  return { formFields, validation };
}

function mapGraphQLToHTMLInputType(graphqlType) {
  const typeName = graphqlType.name || graphqlType.ofType?.name;
  
  const mappings = {
    'String': 'text',
    'Int': 'number',
    'Float': 'number',
    'Boolean': 'checkbox',
    'Date': 'date',
    'DateTime': 'datetime-local'
  };
  
  return mappings[typeName] || 'text';
}

// Export for use in other files
module.exports = {
  basicTypeIntrospection,
  analyzeComplexType,
  exploreRelationships,
  findRequiredFields,
  exploreEnums,
  generateTypeScriptInterface,
  findDeprecatedFields,
  generateSchemaDocumentation,
  buildValidationRules,
  completeTypeExplorer,
  practicalExample
};