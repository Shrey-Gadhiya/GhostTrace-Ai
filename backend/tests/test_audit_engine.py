import pytest
import json
import csv
from backend.engine.loader import DatasetLoader
from backend.engine.audit_runner import AuditRunner
from backend.engine.models import DeletionStatus, AuditPhase, AuditOperation, AuditState

@pytest.fixture(scope="module")
def runner():
    loader = DatasetLoader()
    loader.load_all()
    return AuditRunner(loader)

def test_01_benchmark_sample_output(runner):
    """1. Sample cases compared against supplied benchmark answers."""
    samples = {}
    with open("dataset/sample_output.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            samples[row["case_id"]] = row

    for cid, sample_row in samples.items():
        res = runner.audit_case(cid)
        assert res.deletion_status.value == sample_row["deletion_status"], f"Status mismatch for {cid}"
        pred_steps = json.loads(res.steps_json)
        expected_steps = json.loads(sample_row["steps_json"])
        assert pred_steps == expected_steps, f"Steps mismatch for {cid}"

def test_02_identity_change_and_historical_alias(runner):
    """2. Identity change and historical alias cases."""
    # case_008 has historical alias in CRM
    res = runner.audit_case("case_008")
    assert res.deletion_status == DeletionStatus.INCOMPLETE
    assert any("crm" in s.system_id.lower() for s in res.steps)
    assert any("legacymail.net" in s.resource_id.lower() or "alias" in str(s) for s in res.steps)

def test_03_deleted_primary_surviving_secondary(runner):
    """3. Deleted primary record with surviving secondary copy (e.g. search index)."""
    # case_002 has lingering search index
    res = runner.audit_case("case_002")
    assert res.deletion_status == DeletionStatus.INCOMPLETE
    finding = [s for s in res.steps if s.operation == AuditOperation.REPORT_REMAINING_RECORD]
    assert len(finding) > 0
    assert finding[0].system_id == "sys-search-es"
    assert finding[0].state == AuditState.PRESENT

def test_04_active_synchronization_data_flow(runner):
    """4. Active synchronization process that can recreate a record."""
    # case_003 has active CRM sync
    res = runner.audit_case("case_003")
    assert res.deletion_status == DeletionStatus.INCOMPLETE
    flow_finding = [s for s in res.steps if s.operation == AuditOperation.REPORT_ACTIVE_DATA_FLOW]
    assert len(flow_finding) > 0
    assert flow_finding[0].state == AuditState.ACTIVE
    
    # Check remediation is DISABLE_DATA_FLOW
    disable_step = [s for s in res.steps if s.operation == AuditOperation.DISABLE_DATA_FLOW]
    assert len(disable_step) > 0
    assert disable_step[0].state == AuditState.DISABLED
    assert disable_step[0].evidence_id == ""

def test_05_backup_restore_risk(runner):
    """5. Backup or restore risk without exclusion filters."""
    # case_007 has restore risk
    res = runner.audit_case("case_007")
    assert res.deletion_status == DeletionStatus.INCOMPLETE
    risk_finding = [s for s in res.steps if s.operation == AuditOperation.REPORT_RESTORE_RISK]
    assert len(risk_finding) > 0
    assert risk_finding[0].state == AuditState.ACTIVE
    
    block_step = [s for s in res.steps if s.operation == AuditOperation.BLOCK_RESTORE]
    assert len(block_step) > 0
    assert block_step[0].state == AuditState.BLOCKED
    assert block_step[0].evidence_id == ""

def test_06_policy_required_retained_record(runner):
    """6. Policy-required retained record (fiscal order transaction)."""
    # case_006 is COMPLETE with retained fiscal order
    res = runner.audit_case("case_006")
    assert res.deletion_status == DeletionStatus.COMPLETE
    retained_step = [s for s in res.steps if s.operation == AuditOperation.VERIFY_RECORD_PRESENT]
    assert len(retained_step) > 0
    assert retained_step[0].system_id == "sys-orders-db"
    assert retained_step[0].state == AuditState.PRESENT
    assert retained_step[0].evidence_id != ""

def test_07_tombstone_with_prohibited_identifiers(runner):
    """7. Tombstone with prohibited identifiers still present."""
    # case_005 has unredacted tombstone
    res = runner.audit_case("case_005")
    assert res.deletion_status == DeletionStatus.INCOMPLETE
    exposed = [s for s in res.steps if s.operation == AuditOperation.REPORT_EXPOSED_PII]
    assert len(exposed) > 0
    assert exposed[0].system_id == "sys-auth-01"
    
    redact_step = [s for s in res.steps if s.operation == AuditOperation.REDACT_RECORD]
    assert len(redact_step) > 0
    assert redact_step[0].state == AuditState.REDACTED

def test_08_correctly_redacted_tombstone(runner):
    """8. Correctly redacted tombstone without prohibited PII."""
    # case_001 has verified redacted tombstone
    res = runner.audit_case("case_001")
    assert res.deletion_status == DeletionStatus.COMPLETE
    tomb_step = [s for s in res.steps if s.operation == AuditOperation.VERIFY_RECORD_REDACTED and s.system_id == "sys-auth-01"]
    assert len(tomb_step) > 0
    assert tomb_step[0].evidence_id != ""

def test_09_non_deletion_request(runner):
    """9. Non-deletion request (e.g. DATA_EXPORT or ACCOUNT_INQUIRY)."""
    # case_004 is DATA_EXPORT
    res = runner.audit_case("case_004")
    assert res.deletion_status == DeletionStatus.NOT_APPLICABLE
    assert len(res.steps) == 0
    assert res.steps_json == "[]"

    # case_009 is ACCOUNT_INQUIRY
    res9 = runner.audit_case("case_009")
    assert res9.deletion_status == DeletionStatus.NOT_APPLICABLE
    assert len(res9.steps) == 0
