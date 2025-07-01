/**
 * Patient Registration Example
 * 
 * What it demonstrates:
 * - Complete patient registration workflow
 * - Healthcare-specific validation
 * - HIPAA-compliant data handling
 * - Error handling and recovery
 * - Progressive form enhancement
 * 
 * Healthcare considerations:
 * - HIPAA minimum necessary principle
 * - Patient consent management
 * - Medical record number generation
 * - Insurance information handling
 * 
 * Prerequisites:
 * - Apollo Client setup
 * - Healthie MCP server running
 * - Basic React/JavaScript knowledge
 */

import React, { useState, useEffect } from 'react';
import { useMutation, gql } from '@apollo/client';
import { validatePatientData } from './validation-rules';

// GraphQL mutation for patient creation
// Generated using: query_templates workflow="patient_management"
const CREATE_PATIENT = gql`
  mutation CreatePatient($input: signUpInput!) {
    signUp(input: $input) {
      user {
        id
        email
        first_name
        last_name
        date_of_birth
        phone_number
        # HIPAA: Only include fields necessary for registration confirmation
      }
      errors {
        field
        message
      }
    }
  }
`;

// Validation patterns from MCP server
// Generated using: input_validation field_type="contact_information"
const VALIDATION_PATTERNS = {
  email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  phone: /^\+?1?[0-9]{10}$/,
  name: /^[a-zA-Z\s-']{2,50}$/,
  dateOfBirth: /^\d{4}-\d{2}-\d{2}$/
};

export const PatientRegistration = ({ 
  onSuccess, 
  onError,
  initialData = {},
  showOptionalFields = false 
}) => {
  // Form state management
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone_number: '',
    date_of_birth: '',
    gender: '',
    address: {
      street: '',
      city: '',
      state: '',
      zipCode: ''
    },
    emergencyContact: {
      name: '',
      phone: '',
      relationship: ''
    },
    insuranceInfo: {
      provider: '',
      memberNumber: '',
      groupNumber: ''
    },
    // Consent and legal
    consentForTreatment: false,
    hipaaAuthorization: false,
    communicationPreferences: {
      email: true,
      sms: false,
      phone: false
    },
    ...initialData
  });

  const [validationErrors, setValidationErrors] = useState({});
  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // GraphQL mutation hook
  const [createPatient, { loading, error }] = useMutation(CREATE_PATIENT, {
    onCompleted: (data) => {
      if (data.signUp.errors?.length > 0) {
        // Handle business logic errors from server
        const serverErrors = data.signUp.errors.reduce((acc, error) => {
          acc[error.field || 'general'] = error.message;
          return acc;
        }, {});
        setValidationErrors(serverErrors);
        setIsSubmitting(false);
      } else {
        // Success - patient created
        onSuccess?.(data.signUp.user);
      }
    },
    onError: (error) => {
      // Handle network/GraphQL errors
      console.error('Patient registration failed:', error);
      setIsSubmitting(false);
      onError?.(error);
    }
  });

  // Real-time validation as user types
  useEffect(() => {
    const errors = validatePatientData(formData);
    setValidationErrors(errors);
  }, [formData]);

  // Handle form field changes
  const handleInputChange = (field, value) => {
    setFormData(prev => {
      if (field.includes('.')) {
        // Handle nested fields (address.street, etc.)
        const [parent, child] = field.split('.');
        return {
          ...prev,
          [parent]: {
            ...prev[parent],
            [child]: value
          }
        };
      }
      return {
        ...prev,
        [field]: value
      };
    });
  };

  // Validate current step before proceeding
  const validateStep = (step) => {
    const requiredFieldsByStep = {
      1: ['first_name', 'last_name', 'email', 'date_of_birth'],
      2: ['phone_number', 'address.street', 'address.city', 'address.state'],
      3: ['consentForTreatment', 'hipaaAuthorization']
    };

    const required = requiredFieldsByStep[step] || [];
    const stepErrors = {};

    required.forEach(field => {
      const value = field.includes('.') 
        ? formData[field.split('.')[0]][field.split('.')[1]]
        : formData[field];
      
      if (!value || (typeof value === 'boolean' && !value)) {
        stepErrors[field] = 'This field is required';
      }
    });

    return Object.keys(stepErrors).length === 0;
  };

  // Move to next step
  const handleNextStep = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, 3));
    }
  };

  // Move to previous step
  const handlePrevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateStep(3) || Object.keys(validationErrors).length > 0) {
      return;
    }

    setIsSubmitting(true);

    // Prepare data for GraphQL mutation
    const patientInput = {
      first_name: formData.first_name.trim(),
      last_name: formData.last_name.trim(),
      email: formData.email.toLowerCase().trim(),
      phone_number: formData.phone_number.replace(/\D/g, ''), // Remove non-digits
      date_of_birth: formData.date_of_birth,
      gender: formData.gender || null,
      role: 'patient',
      
      // Address information
      address: {
        street: formData.address.street.trim(),
        city: formData.address.city.trim(),
        state: formData.address.state,
        zipCode: formData.address.zipCode.replace(/\D/g, '')
      },
      
      // Emergency contact (if provided)
      ...(formData.emergencyContact.name && {
        emergencyContact: {
          name: formData.emergencyContact.name.trim(),
          phoneNumber: formData.emergencyContact.phone.replace(/\D/g, ''),
          relationship: formData.emergencyContact.relationship
        }
      }),
      
      // Insurance information (if provided)
      ...(formData.insuranceInfo.provider && {
        insuranceInfo: {
          provider: formData.insuranceInfo.provider.trim(),
          memberNumber: formData.insuranceInfo.memberNumber.trim(),
          groupNumber: formData.insuranceInfo.groupNumber.trim()
        }
      }),
      
      // Consent and preferences
      consentForTreatment: formData.consentForTreatment,
      hipaaAuthorization: formData.hipaaAuthorization,
      communicationPreferences: formData.communicationPreferences
    };

    // Execute the mutation
    await createPatient({
      variables: { input: patientInput }
    });
  };

  // Render form step
  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="form-step">
            <h3>Basic Information</h3>
            
            <div className="form-row">
              <FormField
                label="First Name *"
                type="text"
                value={formData.first_name}
                onChange={(value) => handleInputChange('first_name', value)}
                error={validationErrors.first_name}
                maxLength={50}
              />
              
              <FormField
                label="Last Name *"
                type="text"
                value={formData.last_name}
                onChange={(value) => handleInputChange('last_name', value)}
                error={validationErrors.last_name}
                maxLength={50}
              />
            </div>
            
            <FormField
              label="Email Address *"
              type="email"
              value={formData.email}
              onChange={(value) => handleInputChange('email', value)}
              error={validationErrors.email}
              placeholder="patient@example.com"
            />
            
            <div className="form-row">
              <FormField
                label="Date of Birth *"
                type="date"
                value={formData.date_of_birth}
                onChange={(value) => handleInputChange('date_of_birth', value)}
                error={validationErrors.date_of_birth}
                max={new Date().toISOString().split('T')[0]} // Can't be future date
              />
              
              <FormField
                label="Gender"
                type="select"
                value={formData.gender}
                onChange={(value) => handleInputChange('gender', value)}
                options={[
                  { value: '', label: 'Select...' },
                  { value: 'male', label: 'Male' },
                  { value: 'female', label: 'Female' },
                  { value: 'other', label: 'Other' },
                  { value: 'prefer_not_to_say', label: 'Prefer not to say' }
                ]}
              />
            </div>
          </div>
        );
        
      case 2:
        return (
          <div className="form-step">
            <h3>Contact & Address Information</h3>
            
            <FormField
              label="Phone Number *"
              type="tel"
              value={formData.phone_number}
              onChange={(value) => handleInputChange('phone_number', value)}
              error={validationErrors.phone_number}
              placeholder="+1 (555) 123-4567"
            />
            
            <h4>Address</h4>
            <FormField
              label="Street Address *"
              type="text"
              value={formData.address.street}
              onChange={(value) => handleInputChange('address.street', value)}
              error={validationErrors['address.street']}
            />
            
            <div className="form-row">
              <FormField
                label="City *"
                type="text"
                value={formData.address.city}
                onChange={(value) => handleInputChange('address.city', value)}
                error={validationErrors['address.city']}
              />
              
              <FormField
                label="State *"
                type="select"
                value={formData.address.state}
                onChange={(value) => handleInputChange('address.state', value)}
                error={validationErrors['address.state']}
                options={US_STATES} // Import from constants
              />
              
              <FormField
                label="ZIP Code"
                type="text"
                value={formData.address.zipCode}
                onChange={(value) => handleInputChange('address.zipCode', value)}
                error={validationErrors['address.zipCode']}
                pattern="[0-9]{5}(-[0-9]{4})?"
              />
            </div>
            
            {showOptionalFields && (
              <>
                <h4>Emergency Contact (Optional)</h4>
                <FormField
                  label="Emergency Contact Name"
                  type="text"
                  value={formData.emergencyContact.name}
                  onChange={(value) => handleInputChange('emergencyContact.name', value)}
                />
                
                <div className="form-row">
                  <FormField
                    label="Emergency Contact Phone"
                    type="tel"
                    value={formData.emergencyContact.phone}
                    onChange={(value) => handleInputChange('emergencyContact.phone', value)}
                  />
                  
                  <FormField
                    label="Relationship"
                    type="select"
                    value={formData.emergencyContact.relationship}
                    onChange={(value) => handleInputChange('emergencyContact.relationship', value)}
                    options={[
                      { value: '', label: 'Select...' },
                      { value: 'spouse', label: 'Spouse' },
                      { value: 'parent', label: 'Parent' },
                      { value: 'child', label: 'Child' },
                      { value: 'sibling', label: 'Sibling' },
                      { value: 'friend', label: 'Friend' },
                      { value: 'other', label: 'Other' }
                    ]}
                  />
                </div>
              </>
            )}
          </div>
        );
        
      case 3:
        return (
          <div className="form-step">
            <h3>Consent & Authorization</h3>
            
            <div className="consent-section">
              <CheckboxField
                label="I consent to treatment at this healthcare facility *"
                checked={formData.consentForTreatment}
                onChange={(checked) => handleInputChange('consentForTreatment', checked)}
                error={validationErrors.consentForTreatment}
                required
              />
              
              <CheckboxField
                label="I authorize the use and disclosure of my health information as described in the HIPAA Notice of Privacy Practices *"
                checked={formData.hipaaAuthorization}
                onChange={(checked) => handleInputChange('hipaaAuthorization', checked)}
                error={validationErrors.hipaaAuthorization}
                required
              />
            </div>
            
            <h4>Communication Preferences</h4>
            <div className="communication-prefs">
              <CheckboxField
                label="Email communications"
                checked={formData.communicationPreferences.email}
                onChange={(checked) => handleInputChange('communicationPreferences.email', checked)}
              />
              
              <CheckboxField
                label="Text message (SMS) communications"
                checked={formData.communicationPreferences.sms}
                onChange={(checked) => handleInputChange('communicationPreferences.sms', checked)}
              />
              
              <CheckboxField
                label="Phone call communications"
                checked={formData.communicationPreferences.phone}
                onChange={(checked) => handleInputChange('communicationPreferences.phone', checked)}
              />
            </div>
            
            {showOptionalFields && (
              <>
                <h4>Insurance Information (Optional)</h4>
                <FormField
                  label="Insurance Provider"
                  type="text"
                  value={formData.insuranceInfo.provider}
                  onChange={(value) => handleInputChange('insuranceInfo.provider', value)}
                  placeholder="e.g., Blue Cross Blue Shield"
                />
                
                <div className="form-row">
                  <FormField
                    label="Member Number"
                    type="text"
                    value={formData.insuranceInfo.memberNumber}
                    onChange={(value) => handleInputChange('insuranceInfo.memberNumber', value)}
                  />
                  
                  <FormField
                    label="Group Number"
                    type="text"
                    value={formData.insuranceInfo.groupNumber}
                    onChange={(value) => handleInputChange('insuranceInfo.groupNumber', value)}
                  />
                </div>
              </>
            )}
          </div>
        );
        
      default:
        return null;
    }
  };

  return (
    <div className="patient-registration">
      <div className="registration-header">
        <h2>Patient Registration</h2>
        <div className="step-indicator">
          <span className={currentStep >= 1 ? 'active' : ''}>1. Basic Info</span>
          <span className={currentStep >= 2 ? 'active' : ''}>2. Contact</span>
          <span className={currentStep >= 3 ? 'active' : ''}>3. Consent</span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="registration-form">
        {renderStep()}

        <div className="form-actions">
          {currentStep > 1 && (
            <button 
              type="button" 
              onClick={handlePrevStep}
              className="btn btn-secondary"
              disabled={isSubmitting}
            >
              Previous
            </button>
          )}
          
          {currentStep < 3 ? (
            <button 
              type="button" 
              onClick={handleNextStep}
              className="btn btn-primary"
              disabled={!validateStep(currentStep)}
            >
              Next
            </button>
          ) : (
            <button 
              type="submit"
              className="btn btn-primary"
              disabled={isSubmitting || Object.keys(validationErrors).length > 0}
            >
              {isSubmitting ? 'Registering...' : 'Complete Registration'}
            </button>
          )}
        </div>

        {error && (
          <div className="error-message">
            <h4>Registration Error</h4>
            <p>{error.message}</p>
            <small>
              If this problem persists, please contact support with error code: REG_{Date.now()}
            </small>
          </div>
        )}
      </form>
    </div>
  );
};

// Reusable form field component
const FormField = ({ 
  label, 
  type, 
  value, 
  onChange, 
  error, 
  options = [], 
  ...props 
}) => {
  const renderInput = () => {
    switch (type) {
      case 'select':
        return (
          <select 
            value={value} 
            onChange={(e) => onChange(e.target.value)}
            className={error ? 'error' : ''}
            {...props}
          >
            {options.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );
      
      default:
        return (
          <input
            type={type}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            className={error ? 'error' : ''}
            {...props}
          />
        );
    }
  };

  return (
    <div className="form-field">
      <label>{label}</label>
      {renderInput()}
      {error && <span className="field-error">{error}</span>}
    </div>
  );
};

// Checkbox component for consent forms
const CheckboxField = ({ label, checked, onChange, error, required }) => (
  <div className="checkbox-field">
    <label className={error ? 'error' : ''}>
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        required={required}
      />
      <span className="checkmark"></span>
      {label}
    </label>
    {error && <span className="field-error">{error}</span>}
  </div>
);

// US States for address dropdown
const US_STATES = [
  { value: '', label: 'Select State...' },
  { value: 'AL', label: 'Alabama' },
  { value: 'AK', label: 'Alaska' },
  { value: 'AZ', label: 'Arizona' },
  // ... add all states
  { value: 'WY', label: 'Wyoming' }
];

export default PatientRegistration;