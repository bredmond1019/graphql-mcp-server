/**
 * Search Schema Examples
 * 
 * Demonstrates how to use the search_schema tool to find types, fields,
 * mutations, and queries in the Healthie GraphQL schema.
 * 
 * The search_schema tool searches through 925k+ characters instantly.
 */

// Example 1: Basic Search
async function basicSearch() {
  // Search for anything patient-related
  const patientResults = await mcp.search_schema({
    search_term: "patient"
  });
  
  console.log(`Found ${patientResults.total_matches} patient-related items`);
  
  // Results include:
  // - Types: Patient, PatientDemographics, PatientInsurance
  // - Fields: patient_id, patient_name, patient_email
  // - Mutations: createPatient, updatePatient, archivePatient
  // - Queries: patient, patients, patientSearch
}

// Example 2: Filtered Search
async function filteredSearch() {
  // Find only mutations
  const mutations = await mcp.search_schema({
    search_term: "appointment",
    type_filter: "mutation"
  });
  
  console.log("Appointment mutations found:");
  mutations.matches.forEach(match => {
    console.log(`- ${match.content}`);
  });
  
  // Found 96 appointment mutations including:
  // - createAppointment
  // - updateAppointment
  // - cancelAppointment
  // - rescheduleAppointment
}

// Example 3: Finding Types
async function findTypes() {
  // Search for insurance-related types
  const insuranceTypes = await mcp.search_schema({
    search_term: "insurance",
    type_filter: "type"
  });
  
  // Returns types like:
  // - InsurancePlan
  // - InsurancePolicy
  // - InsuranceClaim
  // - InsuranceVerification
  
  return insuranceTypes.matches.map(m => m.type_name);
}

// Example 4: Healthcare Pattern Discovery
async function discoverHealthcarePatterns() {
  // Find medical identifiers
  const npiFields = await mcp.search_schema({
    search_term: "npi"
  });
  
  const deaFields = await mcp.search_schema({
    search_term: "dea"
  });
  
  // Find clinical terminology
  const icdCodes = await mcp.search_schema({
    search_term: "icd"
  });
  
  const cptCodes = await mcp.search_schema({
    search_term: "cpt"
  });
  
  return {
    medical_identifiers: {
      npi: npiFields.total_matches,
      dea: deaFields.total_matches
    },
    clinical_codes: {
      icd: icdCodes.total_matches,
      cpt: cptCodes.total_matches
    }
  };
}

// Example 5: Finding Field Relationships
async function findFieldRelationships() {
  // Find all ID fields to understand relationships
  const idFields = await mcp.search_schema({
    search_term: "_id",
    type_filter: "field"
  });
  
  // Groups results by type
  const relationships = {};
  
  idFields.matches.forEach(match => {
    const fieldName = match.field_name;
    if (fieldName.endsWith('_id')) {
      const relatedType = fieldName.replace('_id', '');
      relationships[relatedType] = (relationships[relatedType] || 0) + 1;
    }
  });
  
  return relationships;
  // Example output:
  // {
  //   patient: 42,      // 42 types have patient_id field
  //   provider: 38,     // 38 types have provider_id field
  //   appointment: 15,  // 15 types have appointment_id field
  // }
}

// Example 6: Smart Query Building
async function buildQueryFromSearch() {
  // Step 1: Find the query
  const patientQuery = await mcp.search_schema({
    search_term: "patient",
    type_filter: "query"
  });
  
  // Step 2: Find the type
  const patientType = await mcp.search_schema({
    search_term: "Patient",
    type_filter: "type"
  });
  
  // Step 3: Find common fields
  const fields = await mcp.search_schema({
    search_term: "Patient {",
    type_filter: "field"
  });
  
  // Build a query based on findings
  const query = `
    query GetPatient($id: ID!) {
      patient(id: $id) {
        id
        firstName
        lastName
        email
        dateOfBirth
      }
    }
  `;
  
  return query;
}

// Example 7: Debugging Field Names
async function debugFieldName(incorrectField) {
  // When you get "Cannot query field X" error
  
  // Example: Looking for "patient_name" which doesn't exist
  const searchTerm = incorrectField.replace('_', '').replace('-', '');
  
  const results = await mcp.search_schema({
    search_term: searchTerm,
    type_filter: "field"
  });
  
  // Find the closest match
  const suggestions = results.matches
    .filter(m => m.parent_type === "Patient")
    .map(m => m.field_name);
  
  console.log(`Did you mean: ${suggestions.join(', ')}?`);
  // Output: "Did you mean: firstName, lastName?"
}

// Example 8: Discovering Enums
async function discoverEnums() {
  // Find status enums
  const statusEnums = await mcp.search_schema({
    search_term: "Status",
    type_filter: "type"
  });
  
  // Common enums found:
  // - AppointmentStatus
  // - ClaimStatus
  // - TaskStatus
  // - DocumentStatus
  
  // Find the values for a specific enum
  const appointmentStatus = await mcp.search_schema({
    search_term: "AppointmentStatus {"
  });
  
  return appointmentStatus;
}

// Example 9: Performance - Batch Searches
async function batchSearchOperations() {
  const domains = ['patient', 'appointment', 'insurance', 'provider'];
  
  // Run searches in parallel for performance
  const results = await Promise.all(
    domains.map(domain => 
      mcp.search_schema({
        search_term: domain,
        type_filter: "mutation"
      })
    )
  );
  
  // Combine results
  const operations = {};
  domains.forEach((domain, index) => {
    operations[domain] = results[index].total_matches;
  });
  
  return operations;
}

// Example 10: Building a Feature Map
async function mapFeature(featureName) {
  // Comprehensive feature discovery
  
  const featureMap = {
    types: await mcp.search_schema({
      search_term: featureName,
      type_filter: "type"
    }),
    
    queries: await mcp.search_schema({
      search_term: featureName,
      type_filter: "query"
    }),
    
    mutations: await mcp.search_schema({
      search_term: featureName,
      type_filter: "mutation"
    }),
    
    fields: await mcp.search_schema({
      search_term: featureName,
      type_filter: "field"
    })
  };
  
  // Summary
  console.log(`Feature "${featureName}" includes:`);
  console.log(`- ${featureMap.types.total_matches} types`);
  console.log(`- ${featureMap.queries.total_matches} queries`);
  console.log(`- ${featureMap.mutations.total_matches} mutations`);
  console.log(`- ${featureMap.fields.total_matches} fields`);
  
  return featureMap;
}

// Usage Examples
async function main() {
  // Find patient operations
  await basicSearch();
  
  // Find specific mutations
  await filteredSearch();
  
  // Discover healthcare patterns
  const patterns = await discoverHealthcarePatterns();
  console.log("Healthcare patterns:", patterns);
  
  // Map relationships
  const relationships = await findFieldRelationships();
  console.log("Field relationships:", relationships);
  
  // Debug a field error
  await debugFieldName("patient_name");
  
  // Map entire features
  await mapFeature("billing");
}

// Export for use in other files
module.exports = {
  basicSearch,
  filteredSearch,
  findTypes,
  discoverHealthcarePatterns,
  findFieldRelationships,
  buildQueryFromSearch,
  debugFieldName,
  discoverEnums,
  batchSearchOperations,
  mapFeature
};