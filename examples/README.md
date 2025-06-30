# Examples

This directory contains practical examples and sample code for using the Healthie MCP server in real-world applications.

## 📁 Directory Structure

### [🔄 Workflows](./workflows/)
Complete end-to-end workflow examples:
- **Patient Management** - Registration, profile updates, search
- **Appointment Scheduling** - Booking, availability, reminders
- **Clinical Documentation** - Notes, assessments, care plans
- **Billing & Insurance** - Verification, claims, payments

### [🔌 Integrations](./integrations/)
Language-specific integration examples:
- **JavaScript/React** - Frontend integration with Apollo Client
- **Python** - Backend integration with various GraphQL clients
- **Node.js** - Server-side integration patterns
- **cURL** - Direct API testing and debugging

### [📜 Scripts](./scripts/)
Utility scripts and tools:
- **Schema Tools** - Scripts for schema analysis and validation
- **Data Migration** - Examples for data import/export
- **Testing Utilities** - Helper scripts for testing workflows
- **Development Tools** - Local development and debugging scripts

## 🎯 Quick Start Examples

### For Frontend Developers (React)
```bash
# See complete patient management example
cat ./integrations/javascript/patient-management.js

# Run the appointment booking example
cd ./workflows/appointment-scheduling && npm install && npm start
```

### For Backend Developers (Python)
```bash
# Explore Python GraphQL client examples
ls ./integrations/python/

# Try the clinical documentation workflow
python ./workflows/clinical-documentation/example.py
```

### For API Testing
```bash
# Use ready-made cURL examples
./integrations/curl/test-patient-queries.sh

# Test appointment booking workflow
./workflows/appointment-scheduling/test-booking.sh
```

## 🏥 Healthcare-Specific Examples

### Patient Registration Form
```javascript
// Complete patient registration with validation
import { PatientRegistration } from './integrations/javascript/patient-registration';

<PatientRegistration 
  onSuccess={(patient) => navigate(`/patients/${patient.id}`)}
  validationRules={healthieValidation}
/>
```

### Appointment Booking Widget
```javascript
// Embeddable appointment booking component
import { AppointmentBooking } from './workflows/appointment-scheduling/booking-widget';

<AppointmentBooking 
  providerId="provider-123"
  patientId="patient-456"
  availableTimeSlots={true}
/>
```

### Clinical Notes Editor
```javascript
// HIPAA-compliant clinical documentation
import { ClinicalNotesEditor } from './workflows/clinical-documentation/notes-editor';

<ClinicalNotesEditor
  patientId="patient-123"
  template="SOAP"
  autoSave={true}
  complianceMode="HIPAA"
/>
```

## 🔍 Examples by Use Case

### Building a Patient Portal
1. **[Patient Dashboard](./workflows/patient-management/dashboard.js)** - Complete patient information view
2. **[Appointment Management](./workflows/appointment-scheduling/patient-view.js)** - Patient-facing appointment tools
3. **[Medical Records](./workflows/clinical-documentation/patient-records.js)** - Secure medical record access

### Creating a Provider Application
1. **[Provider Dashboard](./workflows/provider-management/dashboard.js)** - Provider scheduling and patient management
2. **[Clinical Workflow](./workflows/clinical-documentation/provider-workflow.js)** - Documentation and care planning
3. **[Billing Integration](./workflows/billing/provider-billing.js)** - Insurance and payment processing

### Developing Admin Tools
1. **[User Management](./workflows/admin/user-management.js)** - Managing patients and providers
2. **[System Integration](./workflows/admin/system-integration.js)** - EHR and third-party integrations
3. **[Reporting Dashboard](./workflows/admin/reporting.js)** - Analytics and compliance reporting

## 🛠️ Development Workflow Examples

### Testing Your Integration
```bash
# Run the complete test suite for an example
cd ./workflows/patient-management
npm test

# Test specific healthcare workflows
npm run test:patient-registration
npm run test:appointment-booking
```

### Local Development Setup
```bash
# Set up local development environment
./scripts/development-tools/setup-local-env.sh

# Start development server with MCP integration
./scripts/development-tools/start-dev-server.sh
```

### Debugging Common Issues
```bash
# Debug authentication issues
./scripts/debugging/test-auth.sh

# Validate GraphQL queries
./scripts/debugging/validate-queries.sh

# Test MCP server connectivity
./scripts/debugging/test-mcp-connection.sh
```

## 🎓 Learning Path

### Beginner (New to GraphQL/Healthcare APIs)
1. Start with [cURL examples](./integrations/curl/) to understand the API
2. Try [simple patient queries](./workflows/patient-management/simple-queries.js)
3. Explore [basic validation](./integrations/javascript/basic-validation.js)

### Intermediate (Building Healthcare Features)
1. Study [complete workflows](./workflows/) for your use case
2. Implement [authentication patterns](./integrations/javascript/auth-patterns.js)
3. Add [error handling](./integrations/javascript/error-handling.js)

### Advanced (Production Healthcare Applications)
1. Review [performance optimization](./integrations/javascript/performance.js) examples
2. Implement [HIPAA compliance](./workflows/compliance/hipaa-patterns.js) patterns
3. Study [enterprise integration](./workflows/admin/enterprise-integration.js) examples

## 📋 Example Categories

| Category | What You'll Learn | Best For |
|----------|------------------|----------|
| **Workflows** | Complete end-to-end processes | Understanding business logic |
| **Integrations** | Language-specific implementation | Getting code working quickly |
| **Scripts** | Utility tools and helpers | Development and debugging |

## 🤝 Contributing Examples

Have a great example or use case? We'd love to include it!

1. **Fork and create a new example**
2. **Follow the existing structure and patterns**
3. **Include comprehensive comments and documentation**
4. **Add tests and validation**
5. **Submit a pull request**

### Example Template
```javascript
/**
 * Example: [Brief Description]
 * 
 * What it demonstrates:
 * - Key feature 1
 * - Key feature 2
 * 
 * Healthcare considerations:
 * - HIPAA compliance notes
 * - Clinical workflow requirements
 * 
 * Prerequisites:
 * - Required dependencies
 * - Configuration needed
 */

// Your example code here...
```

## 💡 Tips for Using Examples

1. **Start with your use case** - Find the workflow that matches what you're building
2. **Understand the healthcare context** - Each example includes domain-specific guidance
3. **Customize for your needs** - Examples are starting points, not exact solutions
4. **Test thoroughly** - Healthcare applications require extensive testing
5. **Consider compliance** - Follow HIPAA and security best practices

Ready to dive in? Start with the [workflow examples](./workflows/) that match your use case!