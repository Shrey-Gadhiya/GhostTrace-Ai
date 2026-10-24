import json
from typing import List, Dict, Optional, Tuple, Set
from backend.engine.models import (
    AuditStep, DeletionStatus, AuditPhase, AuditOperation, AuditState,
    VALID_OP_STATES, VALID_OP_PHASES
)
from backend.engine.step_ordering import PHASE_ORDER, OP_ORDER_BY_PHASE

class ValidationIssue:
    def __init__(self, code: str, message: str, step_no: Optional[int] = None):
        self.code = code
        self.message = message
        self.step_no = step_no

    def __repr__(self):
        prefix = f"[Step {self.step_no}] " if self.step_no is not None else ""
        return f"{prefix}{self.code}: {self.message}"

class CaseValidator:
    def __init__(self, valid_evidence_ids: Optional[Set[str]] = None):
        self.valid_evidence_ids = valid_evidence_ids or set()

    def validate_case(self, case_id: str, status: str, steps: List[AuditStep]) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []

        # 1. Status classification check
        if status not in [s.value for s in DeletionStatus]:
            issues.append(ValidationIssue("INVALID_STATUS", f"Unknown deletion status '{status}'"))
            return issues

        # 2. NOT_APPLICABLE checks
        if status == DeletionStatus.NOT_APPLICABLE.value:
            if len(steps) != 0:
                issues.append(ValidationIssue("NON_EMPTY_STEPS", "NOT_APPLICABLE status must have empty steps_json []"))
            return issues

        # 3. COMPLETE status checks
        if status == DeletionStatus.COMPLETE.value:
            if len(steps) == 0:
                issues.append(ValidationIssue("EMPTY_COMPLETE_STEPS", "COMPLETE status must contain verification steps"))
            for s in steps:
                phase_val = s.phase.value if isinstance(s.phase, AuditPhase) else str(s.phase)
                if phase_val != "VERIFICATION":
                    issues.append(ValidationIssue(
                        "INVALID_PHASE_FOR_COMPLETE",
                        f"COMPLETE status must only contain VERIFICATION phase steps, got '{phase_val}'",
                        s.step_no
                    ))
                if not s.evidence_id:
                    issues.append(ValidationIssue(
                        "MISSING_EVIDENCE_FOR_COMPLETE",
                        "COMPLETE verification steps must cite valid evidence_id proving the condition",
                        s.step_no
                    ))
                elif self.valid_evidence_ids and s.evidence_id not in self.valid_evidence_ids:
                    issues.append(ValidationIssue(
                        "UNKNOWN_EVIDENCE_REF",
                        f"Evidence ID '{s.evidence_id}' does not exist in evidence manifest",
                        s.step_no
                    ))

        # 4. INCOMPLETE status checks
        if status == DeletionStatus.INCOMPLETE.value:
            if len(steps) == 0:
                issues.append(ValidationIssue("EMPTY_INCOMPLETE_STEPS", "INCOMPLETE status must contain findings, remediation, and verification steps"))
            
            phases_present = set()
            for s in steps:
                phase_val = s.phase.value if isinstance(s.phase, AuditPhase) else str(s.phase)
                phases_present.add(phase_val)

                if phase_val == "FINDINGS":
                    if not s.evidence_id:
                        issues.append(ValidationIssue("MISSING_FINDING_EVIDENCE", "FINDINGS step must cite source evidence_id", s.step_no))
                    elif self.valid_evidence_ids and s.evidence_id not in self.valid_evidence_ids:
                        issues.append(ValidationIssue("UNKNOWN_EVIDENCE_REF", f"Evidence ID '{s.evidence_id}' does not exist in manifest", s.step_no))
                elif phase_val in ["REMEDIATION", "VERIFICATION"]:
                    if s.evidence_id != "":
                        issues.append(ValidationIssue(
                            "ILLEGAL_EVIDENCE_IN_PROPOSED",
                            f"Proposed {phase_val} step must have empty string '' as evidence_id, got '{s.evidence_id}'",
                            s.step_no
                        ))

            if "FINDINGS" not in phases_present:
                issues.append(ValidationIssue("MISSING_FINDINGS_PHASE", "INCOMPLETE status missing FINDINGS steps"))
            if "REMEDIATION" not in phases_present:
                issues.append(ValidationIssue("MISSING_REMEDIATION_PHASE", "INCOMPLETE status missing REMEDIATION steps"))
            if "VERIFICATION" not in phases_present:
                issues.append(ValidationIssue("MISSING_VERIFICATION_PHASE", "INCOMPLETE status missing VERIFICATION steps"))

        # 5. Consecutive step_no and operation/state validation
        expected_step = 1
        last_sort_tuple = None

        for s in steps:
            if s.step_no != expected_step:
                issues.append(ValidationIssue(
                    "NON_CONSECUTIVE_STEP_NO",
                    f"Expected step_no {expected_step}, got {s.step_no}",
                    s.step_no
                ))
            expected_step += 1

            op_val = s.operation.value if isinstance(s.operation, AuditOperation) else str(s.operation)
            state_val = s.state.value if isinstance(s.state, AuditState) else str(s.state)
            phase_val = s.phase.value if isinstance(s.phase, AuditPhase) else str(s.phase)

            if op_val not in VALID_OP_STATES:
                issues.append(ValidationIssue("UNKNOWN_OPERATION", f"Operation '{op_val}' is not in authoritative list", s.step_no))
            elif state_val != VALID_OP_STATES[op_val]:
                issues.append(ValidationIssue("INVALID_OP_STATE", f"Operation '{op_val}' requires state '{VALID_OP_STATES[op_val]}', got '{state_val}'", s.step_no))

            if op_val in VALID_OP_PHASES and phase_val != VALID_OP_PHASES[op_val]:
                issues.append(ValidationIssue("INVALID_OP_PHASE", f"Operation '{op_val}' belongs in phase '{VALID_OP_PHASES[op_val]}', got '{phase_val}'", s.step_no))

            # 6. Check strict sort ordering
            p_rank = PHASE_ORDER.get(phase_val, 99)
            op_rank = OP_ORDER_BY_PHASE.get(phase_val, {}).get(op_val, 99)
            current_tuple = (p_rank, op_rank, s.system_id, s.resource_id)

            if last_sort_tuple is not None and current_tuple < last_sort_tuple:
                issues.append(ValidationIssue(
                    "OUT_OF_ORDER_STEP",
                    f"Step is out of order compared to preceding step. Current: {current_tuple}, Previous: {last_sort_tuple}",
                    s.step_no
                ))
            last_sort_tuple = current_tuple

        return issues
