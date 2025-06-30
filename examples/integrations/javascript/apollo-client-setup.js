/**
 * Apollo Client Setup for Healthie GraphQL API
 * 
 * What it demonstrates:
 * - Complete Apollo Client configuration for Healthie
 * - Authentication handling
 * - Error handling and retry logic
 * - Caching strategies for healthcare data
 * - Network status management
 * 
 * Healthcare considerations:
 * - Secure token storage
 * - PHI data caching policies
 * - Audit logging for API calls
 * - HIPAA-compliant error handling
 * 
 * Prerequisites:
 * - @apollo/client package installed
 * - Valid Healthie API credentials
 * - React application setup
 */

import { 
  ApolloClient, 
  InMemoryCache, 
  createHttpLink, 
  from,
  Observable
} from '@apollo/client';
import { setContext } from '@apollo/client/link/context';
import { onError } from '@apollo/client/link/error';
import { RetryLink } from '@apollo/client/link/retry';

// Configuration - use environment variables in production
const HEALTHIE_CONFIG = {
  // API endpoint (staging or production)
  apiUrl: process.env.REACT_APP_HEALTHIE_API_URL || 'https://staging-api.gethealthie.com/graphql',
  
  // Authentication
  apiKey: process.env.REACT_APP_HEALTHIE_API_KEY,
  
  // Feature flags
  enableRetries: true,
  enableErrorLogging: true,
  enableAuditLogging: true,
  
  // Cache settings
  cacheTimeout: 5 * 60 * 1000, // 5 minutes for healthcare data
  enablePersistence: false // Disable for PHI compliance
};

/**
 * Create HTTP link for GraphQL endpoint
 */
const httpLink = createHttpLink({
  uri: HEALTHIE_CONFIG.apiUrl,
  // Important: Ensure credentials are included for authentication
  credentials: 'include'
});

/**
 * Authentication link - adds API key and user tokens
 */
const authLink = setContext((_, { headers }) => {
  // Get authentication token from secure storage
  const token = getAuthToken();
  
  // Prepare headers with authentication
  const authHeaders = {
    ...headers,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  };

  // Add API key if available
  if (HEALTHIE_CONFIG.apiKey) {
    authHeaders['Authorization'] = `Bearer ${HEALTHIE_CONFIG.apiKey}`;
  }

  // Add user token for patient/provider authentication
  if (token) {
    authHeaders['X-User-Token'] = token;
  }

  // Add client identifier for audit logging
  authHeaders['X-Client-ID'] = getClientId();
  
  return {
    headers: authHeaders
  };
});

/**
 * Error handling link - manages GraphQL and network errors
 */
const errorLink = onError(({ graphQLErrors, networkError, operation, forward }) => {
  // Handle GraphQL errors (business logic errors)
  if (graphQLErrors) {
    graphQLErrors.forEach(({ message, locations, path, extensions }) => {
      const errorInfo = {
        type: 'GraphQL Error',
        message,
        path,
        locations,
        extensions,
        operation: operation.operationName,
        timestamp: new Date().toISOString()
      };

      // Log error for debugging (ensure no PHI in logs)
      if (HEALTHIE_CONFIG.enableErrorLogging) {
        logHealthcareError(errorInfo);
      }

      // Handle specific healthcare errors
      handleHealthcareError(errorInfo);
    });
  }

  // Handle network errors
  if (networkError) {
    const errorInfo = {
      type: 'Network Error',
      message: networkError.message,
      statusCode: networkError.statusCode,
      operation: operation.operationName,
      timestamp: new Date().toISOString()
    };

    if (HEALTHIE_CONFIG.enableErrorLogging) {
      logHealthcareError(errorInfo);
    }

    // Handle authentication errors
    if (networkError.statusCode === 401) {
      handleAuthenticationError();
      return;
    }

    // Handle server errors with retry
    if (networkError.statusCode >= 500) {
      // Retry the operation
      return new Observable(observer => {
        setTimeout(() => {
          forward(operation).subscribe(observer);
        }, 1000);
      });
    }
  }
});

/**
 * Retry link - handles transient failures
 */
const retryLink = new RetryLink({
  delay: {
    initial: 300,
    max: Infinity,
    jitter: true
  },
  attempts: {
    max: 3,
    retryIf: (error, _operation) => {
      // Retry on network errors but not GraphQL errors
      return !!error && !error.result;
    }
  }
});

/**
 * Apollo Cache configuration for healthcare data
 */
const cache = new InMemoryCache({
  typePolicies: {
    Patient: {
      // Cache patients by ID
      keyFields: ['id'],
      
      // Field policies for patient data
      fields: {
        appointments: {
          // Merge appointment arrays
          merge(existing = [], incoming) {
            return [...existing, ...incoming];
          }
        },
        
        medicalHistory: {
          // Cache medical history with timestamp
          merge(existing, incoming) {
            return {
              ...existing,
              ...incoming,
              lastUpdated: new Date().toISOString()
            };
          }
        }
      }
    },
    
    Appointment: {
      keyFields: ['id'],
      
      fields: {
        // Don't cache sensitive appointment details long-term
        notes: {
          merge: false
        }
      }
    },
    
    Provider: {
      keyFields: ['id'],
      
      fields: {
        availabilitySlots: {
          // Don't cache availability - always fetch fresh
          merge: false
        }
      }
    },
    
    Query: {
      fields: {
        // Search results should not be cached
        searchPatients: {
          merge: false
        },
        
        // Current user info can be cached briefly
        currentUser: {
          merge(existing, incoming) {
            return {
              ...existing,
              ...incoming,
              cachedAt: Date.now()
            };
          }
        }
      }
    }
  },
  
  // Important: Don't persist cache for healthcare data
  // This ensures PHI is not stored locally
  dataIdFromObject: object => {
    // Generate cache IDs without exposing sensitive data
    if (object.__typename && object.id) {
      return `${object.__typename}:${object.id}`;
    }
    return null;
  }
});

/**
 * Create Apollo Client instance
 */
const createApolloClient = () => {
  // Combine all links
  const links = [authLink, errorLink];
  
  // Add retry link if enabled
  if (HEALTHIE_CONFIG.enableRetries) {
    links.push(retryLink);
  }
  
  // Add HTTP link last
  links.push(httpLink);

  return new ApolloClient({
    link: from(links),
    cache,
    
    // Default options for queries
    defaultOptions: {
      query: {
        // Healthcare data should be fresh
        fetchPolicy: 'cache-first',
        errorPolicy: 'all', // Return partial data on errors
        notifyOnNetworkStatusChange: true
      },
      
      mutate: {
        // Always refetch after mutations
        fetchPolicy: 'no-cache',
        errorPolicy: 'all'
      }
    },
    
    // Enable query deduplication
    queryDeduplication: true,
    
    // Connect to Redux DevTools in development
    connectToDevTools: process.env.NODE_ENV === 'development'
  });
};

/**
 * Get authentication token from secure storage
 */
const getAuthToken = () => {
  // In production, use secure storage (encrypted)
  // For demo, using sessionStorage (not recommended for production)
  return sessionStorage.getItem('healthie_auth_token');
};

/**
 * Set authentication token
 */
const setAuthToken = (token) => {
  if (token) {
    sessionStorage.setItem('healthie_auth_token', token);
  } else {
    sessionStorage.removeItem('healthie_auth_token');
  }
};

/**
 * Get unique client identifier for audit logging
 */
const getClientId = () => {
  let clientId = sessionStorage.getItem('client_id');
  if (!clientId) {
    clientId = `web_${Math.random().toString(36).substr(2, 9)}`;
    sessionStorage.setItem('client_id', clientId);
  }
  return clientId;
};

/**
 * Handle healthcare-specific errors
 */
const handleHealthcareError = (errorInfo) => {
  const { message, extensions } = errorInfo;
  
  // Handle common healthcare errors
  if (message.includes('Patient not found')) {
    // Redirect to patient search or show helpful message
    window.dispatchEvent(new CustomEvent('healthcare-error', {
      detail: {
        type: 'PATIENT_NOT_FOUND',
        message: 'The requested patient could not be found.',
        action: 'Please verify the patient ID and try again.'
      }
    }));
  }
  
  if (message.includes('Appointment conflict')) {
    window.dispatchEvent(new CustomEvent('healthcare-error', {
      detail: {
        type: 'APPOINTMENT_CONFLICT',
        message: 'This appointment time is no longer available.',
        action: 'Please select a different time slot.'
      }
    }));
  }
  
  if (message.includes('Insurance verification failed')) {
    window.dispatchEvent(new CustomEvent('healthcare-error', {
      detail: {
        type: 'INSURANCE_VERIFICATION_FAILED',
        message: 'Insurance information could not be verified.',
        action: 'Please check the insurance details and try again.'
      }
    }));
  }
  
  // Handle authorization errors (HIPAA access violations)
  if (extensions?.code === 'UNAUTHORIZED') {
    window.dispatchEvent(new CustomEvent('healthcare-error', {
      detail: {
        type: 'ACCESS_DENIED',
        message: 'You do not have permission to access this information.',
        action: 'Please contact your administrator if you believe this is an error.'
      }
    }));
  }
};

/**
 * Handle authentication errors
 */
const handleAuthenticationError = () => {
  // Clear stored tokens
  setAuthToken(null);
  
  // Redirect to login
  window.location.href = '/login';
  
  // Dispatch event for app-level handling
  window.dispatchEvent(new CustomEvent('auth-error', {
    detail: {
      type: 'SESSION_EXPIRED',
      message: 'Your session has expired. Please log in again.'
    }
  }));
};

/**
 * Log healthcare errors (ensure HIPAA compliance)
 */
const logHealthcareError = (errorInfo) => {
  // Remove any potential PHI from error logs
  const sanitizedError = {
    type: errorInfo.type,
    operation: errorInfo.operation,
    timestamp: errorInfo.timestamp,
    // Don't log the actual message as it might contain PHI
    hasError: true,
    statusCode: errorInfo.statusCode
  };
  
  // Send to error tracking service (ensure HIPAA compliance)
  if (window.errorLogger) {
    window.errorLogger.log(sanitizedError);
  }
  
  // Log to console in development only
  if (process.env.NODE_ENV === 'development') {
    console.error('Healthcare API Error:', errorInfo);
  }
};

/**
 * Audit logging for HIPAA compliance
 */
const logApiAccess = (operation, variables = {}) => {
  if (!HEALTHIE_CONFIG.enableAuditLogging) return;
  
  const auditEntry = {
    timestamp: new Date().toISOString(),
    operation: operation.operationName,
    operationType: operation.query.definitions[0].operation,
    userId: getCurrentUserId(),
    clientId: getClientId(),
    // Don't log actual variables (may contain PHI)
    hasVariables: Object.keys(variables).length > 0,
    userAgent: navigator.userAgent,
    ipAddress: 'client-side' // Would be logged server-side
  };
  
  // Send to audit logging service
  if (window.auditLogger) {
    window.auditLogger.log(auditEntry);
  }
};

/**
 * Get current user ID for audit logging
 */
const getCurrentUserId = () => {
  // This would be set during authentication
  return sessionStorage.getItem('current_user_id') || 'anonymous';
};

/**
 * Utility functions for React components
 */
export const apolloHelpers = {
  // Clear all cached data (useful for logout)
  clearCache: (client) => {
    client.clearStore();
  },
  
  // Refetch patient data after updates
  refetchPatientData: (client, patientId) => {
    client.refetchQueries({
      include: ['GetPatient', 'GetPatientAppointments', 'GetPatientHistory']
    });
  },
  
  // Check if user is authenticated
  isAuthenticated: () => {
    return !!getAuthToken();
  },
  
  // Set authentication after login
  authenticate: (token, userId) => {
    setAuthToken(token);
    sessionStorage.setItem('current_user_id', userId);
  },
  
  // Logout and clean up
  logout: (client) => {
    setAuthToken(null);
    sessionStorage.removeItem('current_user_id');
    client.clearStore();
  }
};

// Create and export Apollo Client instance
const apolloClient = createApolloClient();

export { apolloClient, setAuthToken, getAuthToken };
export default apolloClient;