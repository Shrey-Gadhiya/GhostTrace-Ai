import pytest
import json
import csv
from backend.engine.models import (
    AuditStep, AuditPhase, AuditOperation, AuditState,
    VALID_OP_STATES, VALID_OP_PHASES
)
from backend.engine.validator import CaseValidator
from backend.engine.step_ordering import StepOrderer
from backend.engine.csv_writer import OutputCSVWriter
from backend.ai.provider import ai_service, EvidenceInterpretationOutput

def test_10_out_of_order_step_detection():
    """10 & 15. Verify CaseValidator rejects improperly sorted steps."""
    validator = CaseValidator()
    
    # Step 1: VERIFICATION, Step 2: FINDINGS (Violates Phase ordering!)
    bad_steps = [
        AuditStep(
            step_no=1,
            phase=AuditPhase.VERIFICATION,
            system_id="sys-crm-01",
            resource_id="res-1",
            operation=AuditOperation.VERIFY_RECORD_ABSENT,
            state=AuditState.ABSENT,
            evidence_id="EV-1"
        ),
        AuditStep(
            step_no=2,
            phase=AuditPhase.FINDINGS,
            system_id="sys-search-es",
            resource_id="res-2",
            operation=AuditOperation.REPORT_REMAINING_RECORD,
            state=AuditState.PRESENT,
            evidence_id="EV-2"
        )
    ]
    issues = validator.validate_case("test_case", "INCOMPLETE", bad_steps)
    assert any(i.code == "OUT_OF_ORDER_STEP" for i in issues)

def test_11_missing_evidence_reference_in_findings():
    """13. FINDINGS step must cite valid source evidence."""
    validator = CaseValidator(valid_evidence_ids={"EV-VALID-01"})
    
    steps = [
        AuditStep(
            step_no=1,
            phase=AuditPhase.FINDINGS,
            system_id="sys-auth-01",
            resource_id="res-1",
            operation=AuditOperation.REPORT_EXPOSED_PII,
            state=AuditState.PRESENT,
            evidence_id="" # Missing evidence!
        )
    ]
    issues = validator.validate_case("test_case", "INCOMPLETE", steps)
    assert any(i.code == "MISSING_FINDING_EVIDENCE" for i in issues)

def test_12_invalid_operation_state_combination():
    """14. Rejects invalid operation/state pair."""
    with pytest.raises(ValueError):
        # REPORT_REMAINING_RECORD requires PRESENT, not ABSENT!
        AuditStep(
            step_no=1,
            phase=AuditPhase.FINDINGS,
            system_id="sys-search-es",
            resource_id="res-1",
            operation=AuditOperation.REPORT_REMAINING_RECORD,
            state=AuditState.ABSENT,
            evidence_id="EV-1"
        )

def test_13_step_orderer_sorts_correctly():
    """15. StepOrderer deterministically re-orders phases, operation priorities, and resources."""
    unordered = [
        AuditStep(
            step_no=99,
            phase=AuditPhase.VERIFICATION,
            system_id="sys-search-es",
            resource_id="res-z",
            operation=AuditOperation.VERIFY_RECORD_ABSENT,
            state=AuditState.ABSENT,
            evidence_id=""
        ),
        AuditStep(
            step_no=88,
            phase=AuditPhase.FINDINGS,
            system_id="sys-search-es",
            resource_id="res-a",
            operation=AuditOperation.REPORT_REMAINING_RECORD,
            state=AuditState.PRESENT,
            evidence_id="EV-1"
        ),
        AuditStep(
            step_no=77,
            phase=AuditPhase.FINDINGS,
            system_id="sys-sync-worker",
            resource_id="res-flow",
            operation=AuditOperation.REPORT_ACTIVE_DATA_FLOW,
            state=AuditState.ACTIVE,
            evidence_id="EV-2"
        ),
        AuditStep(
            step_no=66,
            phase=AuditPhase.REMEDIATION,
            system_id="sys-sync-worker",
            resource_id="res-flow",
            operation=AuditOperation.DISABLE_DATA_FLOW,
            state=AuditState.DISABLED,
            evidence_id=""
        )
    ]

    ordered = StepOrderer.order_steps(unordered)
    assert len(ordered) == 4
    assert [s.step_no for s in ordered] == [1, 2, 3, 4]
    # Check phases order: FINDINGS (steps 1, 2), REMEDIATION (step 3), VERIFICATION (step 4)
    assert ordered[0].phase == AuditPhase.FINDINGS
    assert ordered[0].operation == AuditOperation.REPORT_ACTIVE_DATA_FLOW # Active flow has higher priority than remaining record
    assert ordered[1].phase == AuditPhase.FINDINGS
    assert ordered[1].operation == AuditOperation.REPORT_REMAINING_RECORD
    assert ordered[2].phase == AuditPhase.REMEDIATION
    assert ordered[3].phase == AuditPhase.VERIFICATION

def test_14_csv_roundtrip_parsing(tmp_path):
    """16. CSV quoting and round-trip parsing."""
    test_file = tmp_path / "test_roundtrip.csv"
    dummy_steps = [
        {
            "step_no": 1,
            "phase": "VERIFICATION",
            "system_id": "sys-auth-01",
            "resource_id": "user_1",
            "operation": "VERIFY_RECORD_ABSENT",
            "state": "ABSENT",
            "evidence_id": "EV-01"
        }
    ]

    with open(test_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["case_id", "deletion_status", "steps_json"])
        writer.writerow(["case_001", "COMPLETE", json.dumps(dummy_steps)])
        writer.writerow(["case_002", "NOT_APPLICABLE", json.dumps([])])

    # Validate with OutputCSVWriter
    count = OutputCSVWriter.validate_roundtrip(test_file, expected_count=2)
    assert count == 2
