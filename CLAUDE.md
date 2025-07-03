# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive Model Context Protocol (MCP) server that provides AI tools with advanced access to Healthie's GraphQL API. The project acts as an intelligent development assistant for healthcare applications, offering schema analysis, query optimization, healthcare workflow guidance, and extensive developer tools. It represents a complete transformation from a simple Node.js wrapper to a production-ready healthcare API development platform.

## Key Commands

```bash
# Install dependencies
uv sync

# Run the MCP server in development mode with inspector
uv run mcp dev src/healthie_mcp/server.py:mcp

# Install in Claude Desktop
uv run mcp install src/healthie_mcp/server.py:mcp --name "Healthie Development Assistant"

# Run all tests
uv run pytest

# Run tests without coverage requirement
uv run pytest --no-cov

# Run tests with coverage report
uv run pytest --cov=src/healthie_mcp --cov-report=term-missing

# Run specific test categories
uv run pytest -m unit          # Unit tests only
uv run pytest -m integration   # Integration tests only
uv run pytest -m e2e           # End-to-end tests only
uv run pytest -m "not slow"    # Skip slow tests
uv run pytest -m "not requires_api"   # Skip tests requiring external APIs
uv run pytest -m "not requires_auth"  # Skip tests requiring authentication

# Run a specific test file
uv run pytest tests/unit/test_config.py -v

# Run a single test
uv run pytest tests/unit/test_config.py::TestConfig::test_default_configuration -v

# Test server startup (useful for debugging)
uv run python -c "from src.healthie_mcp.server import mcp; print('✅ Server ready')"

# Test server with additional tools enabled
HEALTHIE_ENABLE_ADDITIONAL_TOOLS=true uv run python -c "from src.healthie_mcp.server import mcp; print('✅ Server ready with all 17 tools')"

# Quick test all 8 core tools
uv run python misc/test_phase_2_simple.py

# Run comprehensive tool testing
uv run python misc/test_phase_2_all_tools.py

# Run the main healthie-mcp command
healthie-mcp
```

## Project Structure

```
src/healthie_mcp/
├── __init__.py
├── server.py              # FastMCP server entry point
├── base.py               # Abstract base classes and protocols
├── exceptions.py         # Custom exception hierarchy
├── schema_manager.py     # GraphQL schema management
├── config/
│   ├── __init__.py
│   ├── settings.py       # Runtime configuration with Pydantic
│   ├── loader.py         # YAML configuration loader with caching
│   └── data/            # 11 YAML configuration files
├── models/              # Pydantic models for all tools
│   └── *.py            # One model file per tool
├── tools/               # Tool implementations
│   ├── __init__.py
│   ├── *.py            # 8 core tools (always available)
│   └── additional/     # 9 additional tools (dev environment only)
└── resources/           # MCP resource implementations
    └── healthie_schema.py

tests/                   # Comprehensive test suite
├── unit/               # Unit tests for individual components
├── integration/        # Integration tests for tool interactions
└── e2e/               # End-to-end workflow tests

misc/                   # Development utilities
├── test_phase_2_simple.py      # Quick test for all 8 tools
├── test_phase_2_all_tools.py   # Comprehensive tool testing
└── various test scripts

test_results/           # Detailed test execution results
└── *.md               # One file per tool with examples

```

## Architecture Overview

### Core Components

1. **FastMCP Server** (`server.py`): Entry point using the official Python MCP SDK that registers 8 working tools and 2 resources

2. **Schema Manager** (`schema_manager.py`): Intelligent GraphQL schema management with automatic downloading, caching, validation, and refresh logic

3. **Configuration System**: Two-tier architecture for maximum flexibility:
   - **Application Settings** (`config/settings.py`): Runtime configuration with Pydantic validation
   - **Tool Configuration** (`config/data/*.yaml`): 11 YAML files containing tool behavior, templates, patterns, and rules
   - **Configuration Loader** (`config/loader.py`): Cached YAML loading with error handling

4. **Base Architecture** (`base.py`): Abstract base classes and protocols ensuring consistent tool implementation with dependency injection

5. **Exception System** (`exceptions.py`): Custom exception hierarchy with structured error details for healthcare-aware error handling

### Tool Architecture

All tools follow a consistent pattern:
- Extend `BaseTool` abstract class with generic typing
- Implement required abstract methods: `get_tool_name()`, `get_tool_description()`, `execute()`
- Use dependency injection for `SchemaManagerProtocol`
- Return structured Pydantic models
- Configuration-driven behavior through YAML files

### Tool Categories (8 Core + 9 Additional)

**Core Tools** (always available - 8 total):
- `search_schema`: Advanced regex-based schema search with type filtering and context
- `query_templates`: Pre-built GraphQL queries organized by healthcare workflows  
- `code_examples`: Multi-language examples (JavaScript, Python, cURL) with authentication
- `introspect_type`: Comprehensive type information with fields, relationships, and metadata
- `error_decoder`: Intelligent error interpretation with healthcare-specific solutions
- `compliance_checker`: HIPAA and healthcare compliance validation
- `workflow_sequences`: Multi-step healthcare workflow guidance and best practices
- `field_relationships`: Deep schema relationship mapping and usage patterns

**Additional Tools** (dev environment only - 9 total):
Enable with `HEALTHIE_ENABLE_ADDITIONAL_TOOLS=true`
- `input_validation`: Healthcare-compliant validation with medical identifier support
- `query_performance`: Performance analysis with healthcare workflow optimization  
- `healthcare_patterns`: Healthcare workflow pattern detection with FHIR awareness
- `rate_limit_advisor`: API rate limiting guidance and optimization
- `field_usage`: Field usage recommendations with healthcare context
- `integration_testing`: Test generation and validation for API integrations
- `webhook_configurator`: Webhook setup and configuration guidance
- `api_usage_analytics`: API usage tracking and analytics guidance
- `environment_manager`: Environment configuration and management

### Configuration Architecture

**Configuration Files** in `config/data/`:
1. **`queries.yaml`**: GraphQL query templates by workflow category
2. **`patterns.yaml`**: Healthcare patterns, keywords, and FHIR mappings
3. **`errors.yaml`**: Error types, solutions, and code examples
4. **`validation.yaml`**: Validation rules, patterns, and healthcare-specific constraints
5. **`workflows.yaml`**: Multi-step workflow sequences for common operations
6. **`fields.yaml`**: Field relationships and usage patterns
7. **`performance.yaml`**: Performance thresholds and optimization rules
8. **`examples.yaml`**: Code examples for different programming languages
9. **`integration_testing.yaml`**: Test scenarios and validation rules
10. **`webhook_configurator.yaml`**: Webhook event types and configurations
11. **`compliance_checker.yaml`**: HIPAA and compliance rules

**Benefits of Configuration-Driven Design**:
- Healthcare experts can modify behavior without coding
- Environment-specific customizations
- Easy maintenance and updates
- Hot-reloadable configuration changes

## Environment Variables

### Setting Up Environment Variables

1. **Copy the example file**: 
   ```bash
   cp .env.development.example .env.development
   ```

2. **Add your Healthie API key** to `.env.development`:
   - Open `.env.development` in your editor
   - Replace `your-actual-api-key-here` with your real API key
   - The `.env.development` file is gitignored for security

### Available Environment Variables

```bash
# Required
HEALTHIE_API_URL="https://staging-api.gethealthie.com/graphql"
HEALTHIE_API_KEY="<your-api-key>"  # Required for schema downloads

# Optional Configuration
SCHEMA_DIR="./schemas"          # Local schema cache directory
CACHE_ENABLED="true"           # Enable schema caching
CACHE_DURATION_HOURS="24"      # Schema cache duration

# Logging and debugging
LOG_LEVEL="INFO"               # DEBUG, INFO, WARNING, ERROR, CRITICAL
DEBUG_MODE="false"             # Enable debug mode

# Network settings
REQUEST_TIMEOUT="30"           # HTTP request timeout in seconds
MAX_RETRIES="3"                # Maximum retry attempts

# Additional tools (dev environment)
HEALTHIE_ENABLE_ADDITIONAL_TOOLS="false"  # Enable 9 additional tools (17 total)
```

**Note**: Never commit your actual API key. The `.env.development` file is included in `.gitignore` to prevent accidental commits.

## Development Workflow

### Tool Development Process
1. **Create Pydantic Models**: Define input/output models in `models/`
2. **Extend BaseTool**: Implement required abstract methods
3. **Add Configuration**: Create/update YAML files for tool behavior
4. **Register Tool**: Add setup function call in `server.py`
5. **Write Tests**: Create comprehensive tests with multiple categories
6. **Documentation**: Update tool descriptions and examples

### Testing Strategy
- **89 tests currently passing** with comprehensive coverage
- **Test Categories**: 
  - `unit`: Individual component testing
  - `integration`: Component interaction testing
  - `e2e`: Complete workflow testing
  - `slow`: Tests taking >1 second
  - `requires_api`: Tests needing external API access
  - `requires_auth`: Tests needing valid credentials

### Configuration Management
- **Non-destructive updates**: Modify YAML files without code changes
- **Version control**: All configuration is tracked in git
- **Validation**: Configuration errors are caught at load time
- **Caching**: YAML files are cached for performance

## Healthcare Domain Specialization

### FHIR Integration
- **Resource Mapping**: Automatically identifies FHIR-compatible patterns
- **Standard Terminologies**: Integration with SNOMED, LOINC, ICD-10
- **Interoperability**: Recommendations for healthcare data exchange

### Healthcare Workflows
- **Patient Management**: Demographics, medical records, consent management
- **Appointment Scheduling**: Availability, booking, reminders, cancellations
- **Clinical Documentation**: Forms, assessments, notes, care plans, goals
- **Billing & Insurance**: Claims processing, payment workflows, authorization
- **Provider Management**: Credentials, licenses, organizations, specialties

### Compliance & Security
- **HIPAA Awareness**: Built into recommendations and validation rules
- **PHI Handling**: Guidance for proper handling of protected health information
- **Medical Identifiers**: Validation for NPI, DEA, medical record numbers
- **Audit Requirements**: Structured logging and error tracking

## Key Implementation Patterns

### 1. Dependency Injection
```python
class MyTool(BaseTool[MyResult]):
    def __init__(self, schema_manager: SchemaManagerProtocol):
        super().__init__(schema_manager)  # Schema access injected
```

### 2. Configuration-Driven Behavior
```python
# Tool loads behavior from YAML
config = self.config_loader.load_queries()
templates = self._process_config(config)
```

### 3. Structured Error Handling
```python
try:
    result = tool.execute(**params)
except ToolError as e:
    return structured_error_response(e)
```

### 4. Type-Safe Models
```python
class ToolInput(BaseModel):
    param: str = Field(description="Parameter description")

class ToolResult(BaseModel):
    data: List[str] = Field(description="Result data")
```

## Performance Considerations

### Schema Management
- **Intelligent Caching**: TTL-based with validation
- **Lazy Loading**: Schema loaded on first access
- **Background Refresh**: Automatic schema updates

### Configuration Loading
- **LRU Caching**: Frequently used configs cached in memory
- **Batch Loading**: Related configurations loaded together
- **Error Recovery**: Graceful fallback for invalid configurations

### Tool Execution
- **Async Support**: All tools support async execution
- **Resource Pooling**: Shared resources across tool instances
- **Memory Efficiency**: Large datasets processed in chunks

## Testing & Quality Assurance

### Current Test Status
- ✅ **89/89 tests passing** (100% pass rate)
- ✅ **Core functionality fully tested**
- ✅ **MCP server integration verified**
- ✅ **Configuration system validated**

### Quality Standards
- **Type Safety**: Full Pydantic validation throughout
- **Error Handling**: Comprehensive exception management
- **Code Coverage**: Aiming for 85% coverage (currently ~54%)
- **Healthcare Compliance**: HIPAA-aware design patterns

## Important Notes

### Technical Requirements
- **Python 3.13+**: Uses modern Python features and typing
- **UV Package Manager**: Preferred over pip for dependency management
- **FastMCP**: Official Python MCP SDK with async support
- **Pydantic**: Type validation and serialization
- **PyYAML**: Configuration file processing

### Operational Modes
- **Full Mode**: With Healthie API access and schema
- **Limited Mode**: Configuration-driven tools only (no schema required)
- **Development Mode**: Enhanced logging and debugging
- **Production Mode**: Optimized performance and error handling

### Healthcare Focus
- **Domain Expertise**: Built-in understanding of healthcare workflows
- **Compliance First**: HIPAA considerations in all recommendations
- **Interoperability**: FHIR-aware patterns and mappings
- **Clinical Context**: Medical terminology and identifier validation

## Healthie GraphQL API Reference

### Common Query Names

#### User & Authentication
- `currentUser`: Get the current authenticated user
- `basicUserInfoFromToken`: Get basic user info from a token
- `user`: Get a user by ID
- `users`: List users with filtering

#### Appointments
- `appointment`: Get appointment by ID
- `appointments`: List appointments with filtering
- `appointmentType`: Get appointment type details
- `appointmentTypes`: List appointment types
- `appointmentSetting`: Get appointment settings
- `availabilities`: List provider availabilities
- `availableSlotsForRange`: Find available appointment slots

#### Patient Care
- `carePlan`: Get care plan by ID
- `carePlans`: List care plans
- `entries`: List patient entries (food, metrics, etc.)
- `entry`: Get specific entry
- `goals`: List patient goals
- `medications`: List patient medications
- `allergySuggestions`: Get allergy/allergen suggestions
- `documents`: List documents
- `forms`: List form templates
- `formAnswerGroups`: List completed forms

#### Clinical Documentation
- `chartingNote`: Get charting note
- `chartingNotes`: List charting notes
- `customModuleForms`: List custom forms
- `smartPhrases`: List smart phrases for documentation

#### Billing & Insurance
- `billingItem`: Get billing item
- `billingItems`: List billing items
- `insurancePlans`: List insurance plans
- `superBills`: List super bills
- `cptCodes`: List CPT codes
- `icdCodes`: List ICD codes
- `claims`: List insurance claims

#### Organization & Provider
- `organization`: Get organization details
- `organizationMembers`: List organization members
- `providers`: List providers
- `groups`: List user groups
- `tags`: List tags for categorization

#### Messaging & Communication
- `conversation`: Get conversation
- `conversations`: List conversations
- `announcements`: List announcements
- `notifications`: List notifications

### Common Mutation Names

#### User Management
- `signUp`: Register new user
- `signIn`: Authenticate user
- `createClient`: Create new patient/client
- `updateClient`: Update patient/client
- `archiveClient`: Archive patient/client
- `bulkUpdateClients`: Bulk update multiple clients

#### Appointments
- `createAppointment`: Schedule new appointment
- `updateAppointment`: Modify appointment
- `deleteAppointment`: Cancel appointment
- `createAppointmentType`: Create appointment type
- `createAvailability`: Set provider availability
- `bulkCreateAvailability`: Set multiple availabilities

#### Clinical Documentation
- `createFormAnswerGroup`: Submit form responses
- `updateFormAnswerGroup`: Update form responses
- `createChartingNote`: Create clinical note
- `updateChartingNote`: Update clinical note
- `signChartingNote`: Sign/lock clinical note
- `createCarePlan`: Create care plan
- `updateCarePlan`: Update care plan

#### Patient Data
- `createEntry`: Log patient data (food, metrics)
- `updateEntry`: Update patient entry
- `deleteEntry`: Remove patient entry
- `createGoal`: Set patient goal
- `updateGoal`: Update patient goal
- `createMedication`: Add medication
- `updateMedication`: Update medication

#### Billing & Payments
- `createBillingItem`: Create billing item
- `createSuperBill`: Generate super bill
- `createPaymentIntent`: Initiate payment
- `createSubscription`: Set up recurring payment
- `createInsuranceClaim`: Submit insurance claim
- `createRequestedPayment`: Request payment from patient

#### Communication
- `createConversation`: Start new conversation
- `createComment`: Add comment to conversation
- `createAnnouncement`: Post announcement
- `createTask`: Assign task
- `updateTask`: Update task status

### Important GraphQL Types

#### Core User Types
- `User`: Base user type (patients, providers, staff)
- `Organization`: Healthcare organization
- `OrganizationMembership`: User's role in organization
- `Provider`: Healthcare provider with additional fields

#### Appointment Types
- `Appointment`: Appointment with attendees, provider, type
- `AppointmentType`: Template for appointments
- `AppointmentSetting`: Provider-specific settings
- `Availability`: Provider availability slots

#### Clinical Types
- `CarePlan`: Patient care plan with goals
- `ChartingNote`: Clinical documentation
- `FormAnswerGroup`: Completed form responses
- `Entry`: Patient logged data (food, metrics, etc.)
- `Goal`: Patient health goals
- `Medication`: Patient medications
- `AllergySensitivity`: Patient allergies

#### Billing Types
- `BillingItem`: Line item for billing
- `SuperBill`: Itemized billing statement
- `InsurancePlan`: Insurance plan details
- `InsuranceClaim`: Submitted claim
- `Payment`: Payment record
- `Subscription`: Recurring payment setup

#### Communication Types
- `Conversation`: Message thread
- `Comment`: Individual message
- `Task`: Assigned task
- `Notification`: System notification
- `Announcement`: Broadcast message

### Key Input Types

#### User Inputs
- `CreateClientInput`: Create new patient
- `UpdateClientInput`: Update patient details
- `SignUpInput`: User registration
- `SignInInput`: User authentication

#### Appointment Inputs
- `AppointmentInput`: Create/update appointment
- `AppointmentTypeInput`: Define appointment type
- `AvailabilityInput`: Set availability

#### Clinical Inputs
- `FormAnswerGroupInput`: Submit form responses
- `ChartingNoteInput`: Create/update clinical note
- `CarePlanInput`: Create/update care plan
- `EntryInput`: Log patient data
- `MedicationInput`: Add/update medication

#### Billing Inputs
- `BillingItemInput`: Create billing item
- `PaymentInput`: Process payment
- `InsuranceClaimInput`: Submit claim

### Common Field Patterns

#### Timestamp Fields
Most types include:
- `created_at`: Creation timestamp
- `updated_at`: Last modification timestamp
- `deleted_at`: Soft deletion timestamp (if applicable)

#### Relationship Fields
- `user`: Associated user/patient
- `provider`: Associated provider
- `organization`: Associated organization
- `created_by`: User who created the record

#### Status Fields
- `active`: Boolean for active/inactive
- `status`: Enum for various states
- `is_public`: Visibility flag
- `archived`: Soft deletion flag

#### Metadata Fields
- `id`: Unique identifier (usually ID type)
- `display_name`: Human-readable name
- `description`: Detailed description
- `metadata`: JSON field for custom data

### Healthcare-Specific Patterns

#### Medical Identifiers
- `npi`: National Provider Identifier
- `dea`: DEA number
- `medical_record_number`: MRN
- `insurance_member_id`: Insurance ID

#### Clinical Fields
- `icd10_codes`: Diagnosis codes
- `cpt_codes`: Procedure codes
- `units`: Medication/metric units
- `dosage`: Medication dosage
- `frequency`: Medication frequency

#### Compliance Fields
- `signed_at`: Document signature timestamp
- `signed_by`: Signing provider
- `locked`: Prevents modifications
- `requires_signature`: Signature requirement flag

## Debugging Tips

### Enable Debug Mode
```bash
export LOG_LEVEL="DEBUG"
export DEBUG_MODE="true"
```

### Common Issues
1. **Schema Download Fails**: Check `HEALTHIE_API_KEY` is set and valid
2. **Tool Not Found**: Ensure tool is registered in `server.py`
3. **YAML Config Errors**: Validate YAML syntax in `config/data/`
4. **Test Failures**: Run with `-v` flag for verbose output

### Development Workflow
1. Make changes to tool implementation
2. Update corresponding YAML configuration if needed
3. Run specific test: `uv run pytest tests/unit/test_your_tool.py -v`
4. Test with MCP inspector: `uv run mcp dev src/healthie_mcp/server.py:mcp`
5. Test all tools: `uv run python misc/test_phase_2_simple.py`

## Documentation

- **[README.md](README.md)**: Project overview and features
- **[QUICK_START.md](QUICK_START.md)**: 5-minute setup guide
- **[DEV_SETUP.md](DEV_SETUP.md)**: Comprehensive development setup
- **[IMPROVEMENTS.md](tasks/IMPROVEMENTS.md)**: Improvements over original Node.js version
- **[test_results/](test_results/)**: Detailed examples for each tool