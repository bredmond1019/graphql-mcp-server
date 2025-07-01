"""
Data models for the Compliance Checker Tool.

This module defines Pydantic models for validating HIPAA compliance,
checking data handling practices, and providing regulatory guidance.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ComplianceLevel(str, Enum):
    """Compliance levels for various checks."""
    COMPLIANT = "compliant"
    WARNING = "warning" 
    VIOLATION = "violation"
    UNKNOWN = "unknown"


class RegulatoryFramework(str, Enum):
    """Supported regulatory frameworks."""
    HIPAA = "hipaa"
    HITECH = "hitech"
    STATE_PRIVACY = "state_privacy"
    GDPR = "gdpr"
    SOC2 = "soc2"
    FDA = "fda"


class PHICategory(str, Enum):
    """Categories of Protected Health Information."""
    DIRECT_IDENTIFIERS = "direct_identifiers"
    QUASI_IDENTIFIERS = "quasi_identifiers"
    SENSITIVE_HEALTH_DATA = "sensitive_health_data"
    DEMOGRAPHIC_DATA = "demographic_data"
    FINANCIAL_DATA = "financial_data"
    CONTACT_INFO = "contact_info"


class AuditRequirement(str, Enum):
    """Types of audit requirements."""
    ACCESS_LOGGING = "access_logging"
    DATA_INTEGRITY = "data_integrity"
    AUTHORIZATION = "authorization"
    ENCRYPTION = "encryption"
    RETENTION = "retention"
    BREACH_DETECTION = "breach_detection"


class ComplianceViolation(BaseModel):
    """A specific compliance violation found."""
    
    severity: ComplianceLevel = Field(description="Severity of the violation")
    framework: RegulatoryFramework = Field(description="Regulatory framework violated")
    field: Optional[str] = Field(None, description="GraphQL field involved")
    message: str = Field(description="Description of the violation")
    recommendation: str = Field(description="How to fix the violation")
    regulation_reference: Optional[str] = Field(None, description="Specific regulation or code section")


class PHIExposureRisk(BaseModel):
    """Risk assessment for PHI exposure."""
    
    category: PHICategory = Field(description="Category of PHI at risk")
    fields: List[str] = Field(description="GraphQL fields that may expose PHI")
    risk_level: ComplianceLevel = Field(description="Level of exposure risk")
    description: str = Field(description="Description of the risk")
    mitigation: str = Field(description="How to mitigate the risk")


class DataHandlingPractice(BaseModel):
    """Assessment of data handling practices."""
    
    practice: str = Field(description="Name of the data handling practice")
    compliant: bool = Field(description="Whether the practice is compliant")
    framework: RegulatoryFramework = Field(description="Applicable regulatory framework")
    description: str = Field(description="Description of the practice")
    recommendation: Optional[str] = Field(None, description="Improvement recommendation")


class AuditRequirementCheck(BaseModel):
    """Check for audit requirements compliance."""
    
    requirement: AuditRequirement = Field(description="Type of audit requirement")
    met: bool = Field(description="Whether the requirement is met")
    description: str = Field(description="Description of the requirement")
    evidence_needed: List[str] = Field(description="Evidence needed to verify compliance")
    implementation_guide: str = Field(description="How to implement this requirement")


class StateRegulation(BaseModel):
    """State-specific regulation information."""
    
    state: str = Field(description="State abbreviation (e.g., 'CA', 'NY')")
    regulation_name: str = Field(description="Name of the state regulation")
    requirements: List[str] = Field(description="Specific requirements")
    applicability: str = Field(description="When this regulation applies")
    compliance_notes: str = Field(description="Notes about compliance")


class ComplianceCheckerInput(BaseModel):
    """Input for the compliance checker tool."""
    
    query: Optional[str] = Field(None, description="GraphQL query to analyze for compliance")
    operation_type: Optional[str] = Field(None, description="Type of operation (query, mutation, subscription)")
    fields: Optional[List[str]] = Field(None, description="Specific fields to check for compliance")
    frameworks: List[RegulatoryFramework] = Field(
        default=[RegulatoryFramework.HIPAA], 
        description="Regulatory frameworks to check against"
    )
    state: Optional[str] = Field(None, description="State for state-specific regulations (e.g., 'CA')")
    check_phi_exposure: bool = Field(True, description="Whether to check for PHI exposure risks")
    check_audit_requirements: bool = Field(True, description="Whether to validate audit requirements")
    data_handling_context: Optional[str] = Field(
        None, 
        description="Context about how data will be handled (e.g., 'patient_portal', 'provider_dashboard')"
    )


class ComplianceCheckerResult(BaseModel):
    """Result from the compliance checker tool."""
    
    overall_compliance: ComplianceLevel = Field(description="Overall compliance assessment")
    summary: str = Field(description="Summary of compliance findings")
    
    # Specific checks
    violations: List[ComplianceViolation] = Field(
        default=[], 
        description="List of compliance violations found"
    )
    phi_risks: List[PHIExposureRisk] = Field(
        default=[], 
        description="PHI exposure risks identified"
    )
    data_handling: List[DataHandlingPractice] = Field(
        default=[], 
        description="Data handling practices assessment"
    )
    audit_requirements: List[AuditRequirementCheck] = Field(
        default=[], 
        description="Audit requirements compliance"
    )
    state_regulations: List[StateRegulation] = Field(
        default=[], 
        description="State-specific regulations that apply"
    )
    
    # Guidance and recommendations
    recommendations: List[str] = Field(
        default=[], 
        description="Overall recommendations for compliance"
    )
    next_steps: List[str] = Field(
        default=[], 
        description="Specific next steps to achieve compliance"
    )
    resources: List[str] = Field(
        default=[], 
        description="Helpful resources for compliance"
    )
    
    # Metadata
    frameworks_checked: List[RegulatoryFramework] = Field(
        description="Regulatory frameworks that were checked"
    )
    query_analyzed: Optional[str] = Field(None, description="The GraphQL query that was analyzed")