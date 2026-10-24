import pytest
from fastapi.testclient import TestClient
from backend.app import app
from backend.engine.loader import DatasetLoader
from backend.engine.audit_runner import AuditRunner

client = TestClient(app)

def test_17_full_dataset_execution_count():
    """18. Verify that all 518 cases process cleanly."""
    loader = DatasetLoader()
    loader.load_all()
    assert len(loader.requests) == 518, f"Expected 518 cases, got {len(loader.requests)}"
    
    runner = AuditRunner(loader)
    all_res = runner.audit_all()
    assert len(all_res) == 518
    assert all(r.case_id.startswith("case_") for r in all_res.values())

def test_18_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["total_cases"] == 518

def test_19_api_overview():
    res = client.get("/api/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["total_requests"] == 518
    assert len(data["systems_summary"]) > 0

def test_20_api_cases_pagination_and_detail():
    # List cases
    res = client.get("/api/cases?page=1&page_size=10")
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 10
    assert data["total"] == 518

    # Get case_001
    res_c1 = client.get("/api/cases/case_001")
    assert res_c1.status_code == 200
    data_c1 = res_c1.json()
    assert data_c1["case_id"] == "case_001"
    assert data_c1["deletion_status"] == "COMPLETE"
    assert len(data_c1["verifications"]) > 0

def test_21_api_evaluation():
    res = client.get("/api/evaluation")
    assert res.status_code == 200
    data = res.json()
    summary = data["benchmark_summary"]
    assert summary["total_benchmark_cases"] == 20
    assert summary["status_accuracy"] == 100.0
    assert summary["step_accuracy"] == 100.0

def test_22_api_csv_upload_and_export():
    csv_payload = "case_id,customer_id,requested_email,request_type,reported_status\ncase_test_up_1,CUST-2026-1001,alice.smith1@example.com,DELETION,COMPLETE\ncase_test_up_2,CUST-2026-1002,bob.davis2@example.com,DELETION,COMPLETE\n"
    files = {"file": ("custom_audit.csv", csv_payload.encode("utf-8"), "text/csv")}
    
    upload_res = client.post("/api/cases/upload-csv", files=files)
    assert upload_res.status_code == 200
    batch_data = upload_res.json()
    assert batch_data["total_cases"] == 2
    assert "batch_id" in batch_data
    
    # Test batch export download
    batch_id = batch_data["batch_id"]
    export_res = client.get(f"/api/cases/uploaded/export-csv?batch_id={batch_id}")
    assert export_res.status_code == 200
    assert "case_id,deletion_status,steps_json" in export_res.text

