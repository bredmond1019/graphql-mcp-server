"""
Compliance Checker Tool for healthcare regulatory compliance.

This tool validates HIPAA compliance, checks data handling practices,
provides regulatory guidance, and identifies PHI exposure risks.
"""

import re
from typing import List, Dict, Any, Optional
from src.healthie_mcp.base import BaseTool, SchemaManagerProtocol
from src.healthie_mcp.models.compliance_checker import (
    ComplianceCheckerInput,
    ComplianceCheckerResult,
    ComplianceLevel,
    RegulatoryFramework,
    PHICategory,
    AuditRequirement,
    ComplianceViolation,
    PHIExposureRisk,
    DataHandlingPractice,
    AuditRequirementCheck,
    StateRegulation
)
from src.healthie_mcp.config.loader import ConfigLoader


class ComplianceCheckerTool(BaseTool[ComplianceCheckerResult]):
    """Tool for checking healthcare regulatory compliance."""

    def __init__(self, schema_manager: SchemaManagerProtocol):
        """Initialize the compliance checker tool."""
        super().__init__(schema_manager)
        self.config_loader = ConfigLoader()

    def get_tool_name(self) -> str:
        """Get the tool name."""
        return "compliance_checker"

    def get_tool_description(self) -> str:
        """Get the tool description."""
        return (
            "Validate HIPAA compliance in GraphQL queries, check data handling practices, "
            "provide regulatory guidance, identify PHI exposure risks, validate audit requirements, "
            "and support state-specific regulations for healthcare applications."
        )

    def execute(self, input_data: ComplianceCheckerInput) -> ComplianceCheckerResult:
        """Execute the compliance checker."""
        try:
            # Load configuration
            config = self._load_config()
            
            # Initialize result
            result = ComplianceCheckerResult(
                overall_compliance=ComplianceLevel.UNKNOWN,
                summary="",
                frameworks_checked=input_data.frameworks
            )
            
            # Store analyzed query
            if input_data.query:
                result.query_analyzed = input_data.query
            
            # Perform compliance checks
            if input_data.query:
                self._analyze_query_compliance(input_data, result, config)
            
            if input_data.check_phi_exposure and input_data.query:
                self._check_phi_exposure(input_data, result, config)
            
            if input_data.check_audit_requirements:
                self._validate_audit_requirements(input_data, result, config)
            
            if input_data.data_handling_context:
                self._assess_data_handling_practices(input_data, result, config)
            
            if input_data.state:
                self._check_state_regulations(input_data, result, config)
            
            # Generate overall assessment
            self._generate_overall_assessment(result, config)
            
            # Add recommendations and resources
            self._add_recommendations_and_resources(input_data, result, config)
            
            return result
            
        except Exception as e:
            # Return error result
            return ComplianceCheckerResult(
                overall_compliance=ComplianceLevel.UNKNOWN,
                summary=f"Error during compliance check: {str(e)}",
                frameworks_checked=input_data.frameworks,
                recommendations=["Unable to complete compliance check due to error"],
                next_steps=["Review input parameters and try again"]
            )

    def _load_config(self) -> Dict[str, Any]:
        """Load compliance checker configuration."""
        try:
            return self.config_loader.load_compliance_checker()
        except Exception:
            # Return minimal config if loading fails
            return {
                "phi_patterns": {},
                "regulatory_frameworks": {},
                "data_handling_practices": {},
                "audit_requirements": {},
                "recommendations": {"general": []},
                "resources": {},
                "messages": {
                    "compliant": "Analysis completed - appears compliant",
                    "warning": "Analysis completed - potential concerns identified",
                    "violation": "Analysis completed - violations found",
                    "unknown": "Unable to determine compliance status"
                }
            }

    def _analyze_query_compliance(
        self, 
        input_data: ComplianceCheckerInput, 
        result: ComplianceCheckerResult, 
        config: Dict[str, Any]
    ) -> None:
        """Analyze GraphQL query for compliance violations."""
        if not input_data.query:
            return
            
        query_lower = input_data.query.lower()
        phi_patterns = config.get("phi_patterns", {})
        
        # Check for PHI patterns in the query
        for category, pattern_config in phi_patterns.items():
            if pattern_config is None:
                continue
                
            patterns = pattern_config.get("patterns", [])
            if patterns is None:
                continue
                
            risk_level = pattern_config.get("risk_level", "warning")
            description = pattern_config.get("description", "")
            
            for pattern in patterns:
                if pattern and re.search(pattern, query_lower, re.IGNORECASE):
                    # Found a potential PHI pattern
                    violation = ComplianceViolation(
                        severity=ComplianceLevel(risk_level),
                        framework=RegulatoryFramework.HIPAA,  # Default to HIPAA
                        field=self._extract_field_from_pattern(input_data.query, pattern),
                        message=f"Query contains {category.replace('_', ' ')}: {description}",
                        recommendation=self._get_pattern_recommendation(category, risk_level),
                        regulation_reference="45 CFR 164.502 - Uses and disclosures of protected health information"
                    )
                    result.violations.append(violation)

    def _check_phi_exposure(
        self, 
        input_data: ComplianceCheckerInput, 
        result: ComplianceCheckerResult, 
        config: Dict[str, Any]
    ) -> None:
        """Check for PHI exposure risks in the query."""
        if not input_data.query:
            return
            
        query_lower = input_data.query.lower()
        phi_patterns = config.get("phi_patterns", {})
        
        for category_name, pattern_config in phi_patterns.items():
            if pattern_config is None:
                continue
                
            patterns = pattern_config.get("patterns", [])
            if patterns is None:
                continue
                
            description = pattern_config.get("description", "")
            
            # Find fields that match PHI patterns
            matching_fields = []
            for pattern in patterns:
                if pattern:
                    matches = re.findall(r'\b\w*' + pattern.replace('|', r'\w*|\w*') + r'\w*\b', 
                                       query_lower, re.IGNORECASE)
                    matching_fields.extend(matches)
            
            if matching_fields:
                # Map category name to PHICategory enum
                phi_category = self._map_to_phi_category(category_name)
                risk_level = self._determine_risk_level(pattern_config.get("risk_level", "warning"))
                
                phi_risk = PHIExposureRisk(
                    category=phi_category,
                    fields=list(set(matching_fields)),  # Remove duplicates
                    risk_level=risk_level,
                    description=f"Potential {category_name.replace('_', ' ')} exposure: {description}",
                    mitigation=self._get_phi_mitigation_strategy(phi_category)
                )
                result.phi_risks.append(phi_risk)

    def _validate_audit_requirements(
        self, 
        input_data: ComplianceCheckerInput, 
        result: ComplianceCheckerResult, 
        config: Dict[str, Any]
    ) -> None:
        """Validate audit requirements for the operation."""
        audit_requirements = config.get("audit_requirements", {})
        
        for req_name, req_config in audit_requirements.items():
            # Map requirement name to AuditRequirement enum
            audit_req = self._map_to_audit_requirement(req_name)
            if not audit_req:
                continue
                
            description = req_config.get("description", "")
            implementation_guide = req_config.get("implementation_guide", "")
            evidence_needed = req_config.get("evidence_needed", [])
            
            # Determine if requirement is met (simplified logic)
            met = self._assess_audit_requirement_compliance(input_data, req_name)
            
            audit_check = AuditRequirementCheck(
                requirement=audit_req,
                met=met,
                description=description,
                evidence_needed=evidence_needed,
                implementation_guide=implementation_guide
            )
            result.audit_requirements.append(audit_check)

    def _assess_data_handling_practices(
        self, 
        input_data: ComplianceCheckerInput, 
        result: ComplianceCheckerResult, 
        config: Dict[str, Any]
    ) -> None:
        """Assess data handling practices for compliance."""
        data_handling = config.get("data_handling_practices", {})
        
        for practice_name, practice_config in data_handling.items():
            if practice_config is None:
                continue
                
            name = practice_config.get("name", practice_name)
            frameworks = practice_config.get("frameworks", [])
            checks = practice_config.get("checks", [])
            
            if frameworks is None:
                frameworks = []
            if checks is None:
                checks = []
            
            for framework_name in frameworks:
                if framework_name in [f.value for f in input_data.frameworks]:
                    # Assess this practice for the framework
                    framework = RegulatoryFramework(framework_name)
                    
                    for check in checks:
                        if check is None:
                            continue
                            
                        description = check.get("description", "")
                        compliant_indicators = check.get("compliant_indicators", [])
                        
                        if compliant_indicators is None:
                            compliant_indicators = []
                        
                        # Simplified compliance assessment
                        compliant = self._assess_practice_compliance(
                            input_data.data_handling_context, 
                            compliant_indicators
                        )
                        
                        practice = DataHandlingPractice(
                            practice=name,
                            compliant=compliant,
                            framework=framework,
                            description=description,
                            recommendation=None if compliant else f"Implement {description.lower()}"
                        )
                        result.data_handling.append(practice)

    def _check_state_regulations(
        self, 
        input_data: ComplianceCheckerInput, 
        result: ComplianceCheckerResult, 
        config: Dict[str, Any]
    ) -> None:
        """Check state-specific regulations."""
        if not input_data.state:
            return
            
        regulatory_frameworks = config.get("regulatory_frameworks", {})
        if regulatory_frameworks is None:
            return
            
        state_privacy = regulatory_frameworks.get("state_privacy", {})
        if state_privacy is None:
            return
            
        state_regulations = state_privacy.get("state_regulations", {})
        if state_regulations is None:
            return
        
        state_regs = state_regulations.get(input_data.state, [])
        if state_regs is None:
            return
        
        for regulation in state_regs:
            if regulation is None:
                continue
                
            name = regulation.get("name", "")
            requirements = regulation.get("requirements", [])
            
            if requirements is None:
                requirements = []
            
            state_reg = StateRegulation(
                state=input_data.state,
                regulation_name=name,
                requirements=requirements,
                applicability=f"Applies to healthcare data processing in {input_data.state}",
                compliance_notes=f"Ensure compliance with {name} when processing patient data"
            )
            result.state_regulations.append(state_reg)

    def _generate_overall_assessment(
        self, 
        result: ComplianceCheckerResult, 
        config: Dict[str, Any]
    ) -> None:
        """Generate overall compliance assessment."""
        # Determine overall compliance level
        if any(v.severity == ComplianceLevel.VIOLATION for v in result.violations):
            result.overall_compliance = ComplianceLevel.VIOLATION
            result.summary = config.get("messages", {}).get("violation", "Compliance violations found")
        elif any(v.severity == ComplianceLevel.WARNING for v in result.violations) or \
             any(r.risk_level == ComplianceLevel.WARNING for r in result.phi_risks):
            result.overall_compliance = ComplianceLevel.WARNING
            result.summary = config.get("messages", {}).get("warning", "Potential compliance concerns")
        elif result.violations or result.phi_risks:
            result.overall_compliance = ComplianceLevel.COMPLIANT
            result.summary = config.get("messages", {}).get("compliant", "Appears compliant")
        elif result.audit_requirements and not any(req.met for req in result.audit_requirements):
            # If we have audit requirements but none are met, it's a warning
            result.overall_compliance = ComplianceLevel.WARNING
            result.summary = "Audit requirements need to be implemented for full compliance"
        else:
            # If we did some analysis and found no major issues
            result.overall_compliance = ComplianceLevel.COMPLIANT
            result.summary = config.get("messages", {}).get("compliant", "Analysis completed - appears compliant")

    def _add_recommendations_and_resources(
        self, 
        input_data: ComplianceCheckerInput, 
        result: ComplianceCheckerResult, 
        config: Dict[str, Any]
    ) -> None:
        """Add recommendations and helpful resources."""
        recommendations = config.get("recommendations", {}) or {}
        resources = config.get("resources", {}) or {}
        
        # Add general recommendations
        general_recs = recommendations.get("general", []) or []
        result.recommendations.extend(general_recs)
        
        # Add query-specific recommendations if we analyzed a query
        if input_data.query:
            query_recs = recommendations.get("query_specific", []) or []
            result.recommendations.extend(query_recs)
        
        # Add PHI protection recommendations if we found PHI risks
        if result.phi_risks:
            phi_recs = recommendations.get("phi_protection", []) or []
            result.recommendations.extend(phi_recs)
        
        # Add next steps based on findings
        if result.violations:
            result.next_steps.append("Address identified compliance violations")
            result.next_steps.append("Review and update data access policies")
        
        if result.phi_risks:
            result.next_steps.append("Implement PHI protection measures")
            result.next_steps.append("Conduct PHI risk assessment")
        
        if not result.violations and not result.phi_risks:
            result.next_steps.append("Continue monitoring for compliance")
            result.next_steps.append("Regular compliance audits recommended")
        
        # Add relevant resources
        for framework in input_data.frameworks:
            framework_resources = resources.get(framework.value, []) or []
            result.resources.extend(framework_resources)
        
        # Add general security resources
        general_security_resources = resources.get("general_security", []) or []
        result.resources.extend(general_security_resources)

    # Helper methods
    def _extract_field_from_pattern(self, query: str, pattern: str) -> Optional[str]:
        """Extract the specific field name that matched the pattern."""
        matches = re.findall(r'\b\w*(?:' + pattern.replace('|', '|') + r')\w*\b', 
                           query, re.IGNORECASE)
        return matches[0] if matches else None

    def _get_pattern_recommendation(self, category: str, risk_level: str) -> str:
        """Get recommendation for a specific PHI pattern category."""
        recommendations = {
            "direct_identifiers": "Implement strict access controls and audit logging for direct identifiers",
            "quasi_identifiers": "Consider data masking or aggregation to reduce identification risk",
            "sensitive_health_data": "Ensure appropriate authorization and minimum necessary access",
            "demographic_data": "Implement role-based access controls for demographic information",
            "financial_data": "Secure financial data with encryption and access controls",
            "contact_info": "Limit access to contact information to authorized personnel only"
        }
        return recommendations.get(category, "Review access controls and data handling practices")

    def _map_to_phi_category(self, category_name: str) -> PHICategory:
        """Map configuration category name to PHICategory enum."""
        mapping = {
            "direct_identifiers": PHICategory.DIRECT_IDENTIFIERS,
            "quasi_identifiers": PHICategory.QUASI_IDENTIFIERS,
            "sensitive_health_data": PHICategory.SENSITIVE_HEALTH_DATA,
            "demographic_data": PHICategory.DEMOGRAPHIC_DATA,
            "financial_data": PHICategory.FINANCIAL_DATA,
            "contact_info": PHICategory.CONTACT_INFO
        }
        return mapping.get(category_name, PHICategory.DEMOGRAPHIC_DATA)

    def _determine_risk_level(self, risk_level_str: str) -> ComplianceLevel:
        """Convert risk level string to ComplianceLevel enum."""
        mapping = {
            "violation": ComplianceLevel.VIOLATION,
            "warning": ComplianceLevel.WARNING,
            "compliant": ComplianceLevel.COMPLIANT
        }
        return mapping.get(risk_level_str, ComplianceLevel.WARNING)

    def _get_phi_mitigation_strategy(self, phi_category: PHICategory) -> str:
        """Get mitigation strategy for PHI category."""
        strategies = {
            PHICategory.DIRECT_IDENTIFIERS: "Implement tokenization, restrict access to authorized users only",
            PHICategory.QUASI_IDENTIFIERS: "Consider data aggregation, implement k-anonymity",
            PHICategory.SENSITIVE_HEALTH_DATA: "Encrypt data, implement audit logging, require specific authorization",
            PHICategory.DEMOGRAPHIC_DATA: "Implement field-level access controls, data masking for non-production",
            PHICategory.FINANCIAL_DATA: "Encrypt financial data, implement PCI DSS controls if applicable",
            PHICategory.CONTACT_INFO: "Limit access to business-necessary personnel, implement data retention policies"
        }
        return strategies.get(phi_category, "Implement appropriate access controls and monitoring")

    def _map_to_audit_requirement(self, req_name: str) -> Optional[AuditRequirement]:
        """Map configuration requirement name to AuditRequirement enum."""
        mapping = {
            "access_logging": AuditRequirement.ACCESS_LOGGING,
            "data_integrity": AuditRequirement.DATA_INTEGRITY,
            "authorization": AuditRequirement.AUTHORIZATION,
            "encryption": AuditRequirement.ENCRYPTION,
            "retention": AuditRequirement.RETENTION,
            "breach_detection": AuditRequirement.BREACH_DETECTION
        }
        return mapping.get(req_name)

    def _assess_audit_requirement_compliance(
        self, 
        input_data: ComplianceCheckerInput, 
        req_name: str
    ) -> bool:
        """Assess whether an audit requirement is met (simplified logic)."""
        # This is a simplified assessment - in practice, this would
        # integrate with actual system monitoring and configuration
        
        if input_data.query and input_data.operation_type and "mutation" in input_data.operation_type:
            # Mutations require more stringent audit controls
            return False
        
        # Default to requiring implementation
        return False

    def _assess_practice_compliance(
        self, 
        context: Optional[str], 
        indicators: List[str]
    ) -> bool:
        """Assess whether a data handling practice is compliant."""
        if not context:
            return False
            
        context_lower = context.lower()
        return any(indicator in context_lower for indicator in indicators)


def setup_compliance_checker_tool(mcp, schema_manager: SchemaManagerProtocol):
    """Setup the compliance checker tool."""
    tool = ComplianceCheckerTool(schema_manager)

    @mcp.tool(name=tool.get_tool_name())
    def compliance_checker(
        query: str = None,
        operation_type: str = None,
        fields: List[str] = None,
        frameworks: List[str] = None,
        state: str = None,
        check_phi_exposure: bool = True,
        check_audit_requirements: bool = True,
        data_handling_context: str = None
    ) -> dict:
        """
        Validate HIPAA compliance in GraphQL queries, check data handling practices,
        provide regulatory guidance, identify PHI exposure risks, validate audit requirements,
        and support state-specific regulations for healthcare applications.

        Args:
            query: GraphQL query to analyze for compliance
            operation_type: Type of operation (query, mutation, subscription)
            fields: Specific fields to check for compliance
            frameworks: Regulatory frameworks to check against (hipaa, hitech, gdpr, etc.)
            state: State for state-specific regulations (e.g., 'CA')
            check_phi_exposure: Whether to check for PHI exposure risks
            check_audit_requirements: Whether to validate audit requirements
            data_handling_context: Context about how data will be handled

        Returns:
            Comprehensive compliance analysis with violations, risks, and recommendations
        """
        # Convert string frameworks to enum values
        framework_enums = []
        if frameworks:
            for fw in frameworks:
                try:
                    framework_enums.append(RegulatoryFramework(fw.lower()))
                except ValueError:
                    # Skip invalid framework names
                    continue
        
        if not framework_enums:
            framework_enums = [RegulatoryFramework.HIPAA]  # Default to HIPAA

        input_data = ComplianceCheckerInput(
            query=query,
            operation_type=operation_type,
            fields=fields,
            frameworks=framework_enums,
            state=state,
            check_phi_exposure=check_phi_exposure,
            check_audit_requirements=check_audit_requirements,
            data_handling_context=data_handling_context
        )

        result = tool.execute(input_data)
        return result.model_dump()