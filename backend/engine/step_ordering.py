from typing import List, Dict
from backend.engine.models import AuditStep, AuditPhase, AuditOperation

PHASE_ORDER: Dict[str, int] = {
    "FINDINGS": 1,
    "REMEDIATION": 2,
    "VERIFICATION": 3
}

OP_ORDER_BY_PHASE: Dict[str, Dict[str, int]] = {
    "FINDINGS": {
        "REPORT_ACTIVE_DATA_FLOW": 1,
        "REPORT_RESTORE_RISK": 2,
        "REPORT_REMAINING_RECORD": 3,
        "REPORT_EXPOSED_PII": 4
    },
    "REMEDIATION": {
        "DISABLE_DATA_FLOW": 1,
        "BLOCK_RESTORE": 2,
        "DELETE_RECORD": 3,
        "REDACT_RECORD": 4,
        "ANONYMIZE_RECORD": 5
    },
    "VERIFICATION": {
        "VERIFY_DATA_FLOW_DISABLED": 1,
        "VERIFY_RESTORE_BLOCKED": 2,
        "VERIFY_RECORD_ABSENT": 3,
        "VERIFY_RECORD_PRESENT": 4,
        "VERIFY_RECORD_REDACTED": 5,
        "VERIFY_RECORD_ANONYMIZED": 6
    }
}

class StepOrderer:
    @staticmethod
    def order_steps(steps: List[AuditStep]) -> List[AuditStep]:
        """
        Orders audit steps according to the authoritative Challenge Specification:
        1. Phase order (FINDINGS -> REMEDIATION -> VERIFICATION)
        2. Within phase operation priority
        3. system_id ascending
        4. resource_id ascending
        5. Re-numbers step_no consecutively starting at 1.
        """
        def sort_key(s: AuditStep):
            phase_val = s.phase.value if isinstance(s.phase, AuditPhase) else str(s.phase)
            op_val = s.operation.value if isinstance(s.operation, AuditOperation) else str(s.operation)
            
            p_rank = PHASE_ORDER.get(phase_val, 99)
            op_rank = OP_ORDER_BY_PHASE.get(phase_val, {}).get(op_val, 99)
            
            return (p_rank, op_rank, s.system_id, s.resource_id)

        sorted_steps = sorted(steps, key=sort_key)
        
        # Re-number consecutively from 1
        renumbered_steps = []
        for idx, step in enumerate(sorted_steps, start=1):
            renumbered_steps.append(AuditStep(
                step_no=idx,
                phase=step.phase,
                system_id=step.system_id,
                resource_id=step.resource_id,
                operation=step.operation,
                state=step.state,
                evidence_id=step.evidence_id
            ))
            
        return renumbered_steps
