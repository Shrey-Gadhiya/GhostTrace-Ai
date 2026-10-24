from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, model_validator

class DeletionStatus(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    NOT_APPLICABLE = "NOT_APPLICABLE"

class AuditPhase(str, Enum):
    FINDINGS = "FINDINGS"
    REMEDIATION = "REMEDIATION"
    VERIFICATION = "VERIFICATION"

class AuditOperation(str, Enum):
    # Findings
    REPORT_REMAINING_RECORD = "REPORT_REMAINING_RECORD"
    REPORT_EXPOSED_PII = "REPORT_EXPOSED_PII"
    REPORT_ACTIVE_DATA_FLOW = "REPORT_ACTIVE_DATA_FLOW"
    REPORT_RESTORE_RISK = "REPORT_RESTORE_RISK"
    
    # Remediation
    DISABLE_DATA_FLOW = "DISABLE_DATA_FLOW"
    BLOCK_RESTORE = "BLOCK_RESTORE"
    DELETE_RECORD = "DELETE_RECORD"
    REDACT_RECORD = "REDACT_RECORD"
    ANONYMIZE_RECORD = "ANONYMIZE_RECORD"
    
    # Verification
    VERIFY_RECORD_ABSENT = "VERIFY_RECORD_ABSENT"
    VERIFY_RECORD_PRESENT = "VERIFY_RECORD_PRESENT"
    VERIFY_RECORD_REDACTED = "VERIFY_RECORD_REDACTED"
    VERIFY_RECORD_ANONYMIZED = "VERIFY_RECORD_ANONYMIZED"
    VERIFY_DATA_FLOW_DISABLED = "VERIFY_DATA_FLOW_DISABLED"
    VERIFY_RESTORE_BLOCKED = "VERIFY_RESTORE_BLOCKED"

class AuditState(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    REDACTED = "REDACTED"
    ANONYMIZED = "ANONYMIZED"
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    BLOCKED = "BLOCKED"

# Valid operation to state mapping
VALID_OP_STATES: Dict[str, str] = {
    "REPORT_REMAINING_RECORD": "PRESENT",
    "REPORT_EXPOSED_PII": "PRESENT",
    "REPORT_ACTIVE_DATA_FLOW": "ACTIVE",
    "REPORT_RESTORE_RISK": "ACTIVE",
    
    "DISABLE_DATA_FLOW": "DISABLED",
    "BLOCK_RESTORE": "BLOCKED",
    "DELETE_RECORD": "ABSENT",
    "REDACT_RECORD": "REDACTED",
    "ANONYMIZE_RECORD": "ANONYMIZED",
    
    "VERIFY_RECORD_ABSENT": "ABSENT",
    "VERIFY_RECORD_PRESENT": "PRESENT",
    "VERIFY_RECORD_REDACTED": "REDACTED",
    "VERIFY_RECORD_ANONYMIZED": "ANONYMIZED",
    "VERIFY_DATA_FLOW_DISABLED": "DISABLED",
    "VERIFY_RESTORE_BLOCKED": "BLOCKED"
}

# Valid operation to phase mapping
VALID_OP_PHASES: Dict[str, str] = {
    "REPORT_REMAINING_RECORD": "FINDINGS",
    "REPORT_EXPOSED_PII": "FINDINGS",
    "REPORT_ACTIVE_DATA_FLOW": "FINDINGS",
    "REPORT_RESTORE_RISK": "FINDINGS",
    
    "DISABLE_DATA_FLOW": "REMEDIATION",
    "BLOCK_RESTORE": "REMEDIATION",
    "DELETE_RECORD": "REMEDIATION",
    "REDACT_RECORD": "REMEDIATION",
    "ANONYMIZE_RECORD": "REMEDIATION",
    
    "VERIFY_RECORD_ABSENT": "VERIFICATION",
    "VERIFY_RECORD_PRESENT": "VERIFICATION",
    "VERIFY_RECORD_REDACTED": "VERIFICATION",
    "VERIFY_RECORD_ANONYMIZED": "VERIFICATION",
    "VERIFY_DATA_FLOW_DISABLED": "VERIFICATION",
    "VERIFY_RESTORE_BLOCKED": "VERIFICATION"
}

class AuditStep(BaseModel):
    step_no: int = Field(..., description="Consecutive 1-based step number")
    phase: AuditPhase
    system_id: str
    resource_id: str
    operation: AuditOperation
    state: AuditState
    evidence_id: str = Field(default="", description="Evidence ID reference or empty string")

    @model_validator(mode="after")
    def validate_op_and_state(self):
        op_str = self.operation.value if isinstance(self.operation, AuditOperation) else str(self.operation)
        state_str = self.state.value if isinstance(self.state, AuditState) else str(self.state)
        phase_str = self.phase.value if isinstance(self.phase, AuditPhase) else str(self.phase)

        expected_state = VALID_OP_STATES.get(op_str)
        if expected_state and state_str != expected_state:
            raise ValueError(f"Operation '{op_str}' requires state '{expected_state}', got '{state_str}'")

        expected_phase = VALID_OP_PHASES.get(op_str)
        if expected_phase and phase_str != expected_phase:
            raise ValueError(f"Operation '{op_str}' belongs to phase '{expected_phase}', got '{phase_str}'")

        return self

class DeletionRequest(BaseModel):
    case_id: str
    customer_id: str
    requested_email: str
    request_type: str
    requested_at: str
    reported_status: str
    audit_at: str

class UserIdentity(BaseModel):
    identity_id: str
    primary_customer_id: str
    identifier_type: str
    identifier_value: str
    status: str
    source_system: str
    linked_at: str

class AuditLogEntry(BaseModel):
    log_id: str
    system_id: str
    resource_id: str
    event_type: str
    actor: str
    timestamp: str
    details: str

class DeletionRule(BaseModel):
    rule_id: str
    system_id: str
    data_category: str
    required_treatment: str
    retention_rationale: str
    prohibited_fields: str
    allowed_fields: str

class EvidenceFile(BaseModel):
    evidence_id: str
    system_id: str
    resource_id: str
    file_path: str
    file_type: str
    collected_at: str
    hash_sha256: str
    description: str

class CaseAuditResult(BaseModel):
    case_id: str
    customer_id: str
    requested_email: str
    request_type: str
    reported_status: str
    deletion_status: DeletionStatus
    steps: List[AuditStep]
    steps_json: str
    findings_count: int = 0
    remediation_count: int = 0
    verification_count: int = 0
    resolved_identities: List[str] = Field(default_factory=list)
    evidence_citations: List[str] = Field(default_factory=list)
    remediation_summary: str = ""
